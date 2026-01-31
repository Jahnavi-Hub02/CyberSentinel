"""Ingest CSV into MongoDB (simple script)
Usage:
  python scripts/ingest_csv.py --uri mongodb://localhost:27017 --db cybersentinel --drop
"""
import argparse
import pandas as pd
from pymongo import MongoClient
from pathlib import Path
import hashlib

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_CANDIDATES = [
    DATA_DIR / "cybersecurity_cases_india_combined.csv",
]


def canonicalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cols_map = {c.strip().lower(): c for c in df.columns}

    def find(cands):
        for cand in cands:
            k = cand.strip().lower()
            if k in cols_map:
                return cols_map[k]
        return None

    year_col = find(["year"])
    day_col = find(["day"])
    amt_col = find(["amount_lost_inr", "amount_lost", "amount"])
    type_col = find(["incident_type", "incident", "type"])
    city_col = find(["city", "location", "place"])
    cat_col = find(["category"])

    # Basic transformations
    df['title'] = df[type_col] if type_col in df.columns else (df[cat_col] if cat_col in df.columns else "")
    df['category'] = df[cat_col] if cat_col in df.columns else (df[type_col] if type_col in df.columns else "")
    df['location'] = df[city_col] if city_col in df.columns else ""
    if amt_col and amt_col in df.columns:
        df['amount_lost'] = pd.to_numeric(df[amt_col].astype(str).str.replace(r"[^\d\.-]", "", regex=True), errors="coerce").fillna(0.0)
    else:
        df['amount_lost'] = 0.0

    # Timestamp handling (best-effort)
    if 'timestamp' not in df.columns:
        for candidate in [year_col, 'date', 'timestamp', 'reported_on', 'datetime']:
            if candidate and candidate in df.columns:
                try:
                    df['timestamp'] = pd.to_datetime(df[candidate], errors='coerce')
                    break
                except Exception:
                    pass
    df['timestamp'] = df.get('timestamp')

    # Create stable id
    def make_id(row):
        s = str(row.get('title','')) + '|' + str(row.get('timestamp','')) + '|' + str(row.get('location',''))
        return hashlib.md5(s.encode()).hexdigest()

    df['id'] = df.apply(make_id, axis=1)

    # Keep canonical columns
    cols_keep = ['id', 'timestamp', 'title', 'category', 'location', 'amount_lost']
    for c in cols_keep:
        if c not in df.columns:
            df[c] = "" if c != 'timestamp' else pd.NaT
    return df[cols_keep]


def run(uri: str, dbname: str, drop: bool = False):
    client = MongoClient(uri)
    db = client[dbname]
    col = db['incidents']

    # find csv
    path = None
    for c in CSV_CANDIDATES:
        if c.exists():
            path = c
            break
    if path is None:
        print('No CSV found to ingest in data/.')
        return

    print(f'Loading CSV: {path}')
    df = pd.read_csv(path, low_memory=False)
    df = canonicalize(df)

    if drop:
        print('Dropping existing incidents collection...')
        col.drop()

    # Upsert by id
    print(f'Inserting/Updating {len(df)} incidents...')
    ops = 0
    for _, row in df.iterrows():
        filter_ = {'id': row['id']}
        doc = row.to_dict()
        col.replace_one(filter_, doc, upsert=True)
        ops += 1
    print(f'Done. {ops} upserts performed.')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--uri', default='mongodb://localhost:27017', help='MongoDB URI')
    p.add_argument('--db', default='cybersentinel', help='DB name')
    p.add_argument('--drop', action='store_true', help='Drop collection before insert')
    args = p.parse_args()
    run(args.uri, args.db, args.drop)
