# frontend/app.py
import os
import sys
import time
import re
from typing import Optional, Tuple, Dict, Any

import requests
import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import altair as alt
import plotly.express as px
import hashlib

# ---------------------------
# Local dataset loader
# ---------------------------
@st.cache_data(ttl=300)
def load_preferred_local_dataset() -> pd.DataFrame:
    """
    Load the preferred local CSV: cybersecurity_cases_india_combined.csv
    Expected input columns (any capitalization): Year, Day, Amount_Lost_INR, Incident_Type, City, Category
    Converts to canonical frontend columns: id, timestamp, title, description, category, location, amount_lost
    """
    project_root = os.path.dirname(os.path.dirname(__file__))
    backend_data_dir = os.path.join(project_root, "backend", "data")
    candidates = [
        os.path.join(backend_data_dir, "cybersecurity_cases_india_combined.csv"),
    ]
    path = None
    for p in candidates:
        if os.path.exists(p):
            path = p
            break
    if not path:
        return pd.DataFrame()

    try:
        df = pd.read_csv(path, low_memory=False)
    except Exception:
        return pd.DataFrame()

    # normalise column names (case-insens & whitespace)
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

    df = df.copy()

    # build timestamp from Year + Day (two strategies)
    ts = None
    if year_col and day_col and year_col in df.columns and day_col in df.columns:
        try:
            # if day looks numeric (day-of-year)
            if df[day_col].astype(str).str.match(r"^\s*\d+\s*$").all():
                yrs = pd.to_numeric(df[year_col], errors="coerce").fillna(1970).astype(int)
                days = pd.to_numeric(df[day_col], errors="coerce").fillna(1).astype(int)
                ts = pd.to_datetime(yrs.astype(str), format="%Y", errors="coerce") + pd.to_timedelta(days - 1, unit="D")
            else:
                # parse rows individually, append year if needed
                def parse_row(r):
                    try:
                        d = str(r[day_col]).strip()
                        y = str(int(r[year_col])) if pd.notnull(r[year_col]) else ""
                        parsed = pd.to_datetime(d, errors="coerce")
                        if pd.isna(parsed) and y:
                            parsed = pd.to_datetime(f"{d} {y}", errors="coerce")
                        return parsed
                    except Exception:
                        return pd.NaT

                ts = pd.to_datetime(df.apply(parse_row, axis=1), errors="coerce")
        except Exception:
            ts = None

    # fallback: try common date columns
    if ts is None or (hasattr(ts, "isnull") and ts.isnull().all()):
        for candidate in ["date", "timestamp", "reported_on", "datetime"]:
            c = find([candidate])
            if c and c in df.columns:
                try:
                    ts = pd.to_datetime(df[c], errors="coerce")
                    break
                except Exception:
                    pass

    df["timestamp"] = ts if ts is not None else pd.NaT

    # category/location/title/amount
    if cat_col and cat_col in df.columns:
        df["category"] = df[cat_col].astype(str)
    elif type_col and type_col in df.columns:
        df["category"] = df[type_col].astype(str)
    else:
        df["category"] = ""

    if city_col and city_col in df.columns:
        df["location"] = df[city_col].astype(str)
    else:
        df["location"] = ""

    if type_col and type_col in df.columns:
        df["title"] = df[type_col].astype(str)
    else:
        df["title"] = df["category"].astype(str)

    if amt_col and amt_col in df.columns:
        df["amount_lost"] = pd.to_numeric(
            df[amt_col].astype(str).str.replace(r"[^\d\.-]", "", regex=True), errors="coerce"
        ).fillna(0.0)
    else:
        df["amount_lost"] = 0.0

    df["id"] = df.index.astype(str)

    # trim strings
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = df[c].astype(str).str.strip()

    # ensure canonical columns exist
    cols_keep = ["id", "timestamp", "title", "category", "location", "amount_lost"]
    for c in cols_keep:
        if c not in df.columns:
            df[c] = "" if c != "timestamp" else pd.NaT

    # reorder
    canonical = cols_keep
    cols = [c for c in canonical if c in df.columns] + [c for c in df.columns if c not in canonical]
    return df[cols]

# ---------------------------
# Try to load environment variables from .env
# ---------------------------
try:
    from dotenv import load_dotenv
    env_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        os.path.join(os.path.dirname(__file__), ".env"),
    ]
    for path in env_paths:
        if os.path.exists(path):
            load_dotenv(path)
            break
except Exception:
    pass

# ---------------------------
# Data normalization helpers
# ---------------------------
_CANONICAL_MAP = {
    "category": ["category", "cat", "incident_type", "type", "attack_type", "crime_type"],
    "location": ["location", "place", "city", "state", "district", "area", "location_name"],
    "title": ["title", "incident", "headline", "name"],
    "description": ["description", "desc", "details", "summary"],
    "timestamp": ["timestamp", "date", "incident_date", "reported_on", "datetime"],
    "date": ["date", "incident_date", "reported_on", "datetime"],
    "lat": ["lat", "latitude"],
    "lon": ["lon", "longitude", "long"],
    "source": ["source", "reported_by", "reporter"],
    "severity": ["severity", "level"],
    "status": ["status"],
    "id": ["id", "incident_id", "uid"],
}

def _norm_key(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).strip().lower())

def find_best_col(cols, candidates):
    cols_map = {c.strip().lower(): c for c in cols}
    for cand in candidates:
        key = cand.strip().lower()
        if key in cols_map:
            return cols_map[key]
    norm_map = {_norm_key(c): c for c in cols}
    for cand in candidates:
        nk = _norm_key(cand)
        if nk in norm_map:
            return norm_map[nk]
    return None

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    df = df.copy()
    cols = list(df.columns)
    rename_map = {}
    for canonical, alts in _CANONICAL_MAP.items():
        found = find_best_col(cols, alts)
        # Avoid creating duplicate column names: only rename if the canonical
        # name is not already present in the DataFrame.
        if found and found != canonical and canonical not in cols:
            rename_map[found] = canonical
    if rename_map:
        df = df.rename(columns=rename_map)
        cols = list(df.columns)
    # Drop any remaining duplicate columns, keeping the first occurrence only.
    if len(df.columns) != len(set(df.columns)):
        df = df.loc[:, ~pd.Index(df.columns).duplicated()]
        cols = list(df.columns)
    for canonical in _CANONICAL_MAP.keys():
        if canonical not in df.columns:
            if canonical in ("lat", "lon"):
                df[canonical] = None
            else:
                df[canonical] = ""
    if "id" not in df.columns or df["id"].isnull().all():
        df["id"] = df.index.astype(str)

    # Robustly trim string-like columns while avoiding issues with duplicate
    # column names (where df[c] can be a DataFrame instead of a Series).
    for c in list(df.columns):
        try:
            series = df[c]
            # Skip if this is a DataFrame (duplicate column name case)
            if isinstance(series, pd.DataFrame):
                continue
            if pd.api.types.is_object_dtype(series) or str(series.dtype).startswith("string"):
                df[c] = series.astype(str).str.strip()
        except Exception:
            # If anything goes wrong for a particular column, leave it as-is
            continue
    if "timestamp" in df.columns:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        except Exception:
            pass
    return df

# ---------------------------
# API URL logic
# ---------------------------
def get_api_url() -> str:
    """
    Resolve the backend API base URL.

    Priority:
      1. API_URL env var
      2. BACKEND_URL env var
      3. http://localhost:8000 (sensible default)

    When running OUTSIDE Docker but API_URL/BACKEND_URL still points to the
    Docker service host (e.g. "api:8000" or "http://api:8000"), we rewrite it
    transparently to "http://localhost:8000" so local development "just works".
    """
    in_docker = os.path.exists("/.dockerenv") or os.path.exists("/proc/self/cgroup")

    def _normalize(raw: str) -> str:
        raw = (raw or "").strip()
        if not raw:
            return ""
        # If it already has a scheme and is not the docker host name, keep it.
        if raw.startswith(("http://", "https://")) and "://api:" not in raw:
            return raw
        # Map docker-style host names to localhost when not running in Docker.
        if not in_docker:
            # "api:8000"
            if raw.startswith("api:"):
                _, _, port = raw.partition(":")
                port = port or "8000"
                return f"http://localhost:{port}"
            # "http://api:8000" or "https://api:8000"
            if raw.startswith(("http://api:", "https://api:")):
                # keep the declared port, but point to localhost
                _, _, host_and_port = raw.partition("://")
                _, _, port = host_and_port.partition(":")
                port = port or "8000"
                return f"http://localhost:{port}"
        # If it looks like a bare host:port, add http://
        if not raw.startswith(("http://", "https://")):
            return f"http://{raw}"
        return raw

    env_url = os.getenv("API_URL") or os.getenv("BACKEND_URL") or ""
    normalized = _normalize(env_url)
    if normalized:
        return normalized
    # final fallback
    return "http://localhost:8000"

API_URL = get_api_url()

# ---------------------------
# Safe rerun helper (modern API)
# ---------------------------
def safe_rerun():
    """
    Robust safe rerun that works across Streamlit versions.
    Tries st.rerun() then falls back to st.query_params setter, then st.stop().
    """
    # Prefer the experimental rerun if available (more stable across versions)
    try:
        if hasattr(st, "experimental_rerun"):
            try:
                st.experimental_rerun()
                return
            except Exception:
                pass

        # Try the standard rerun API
        if hasattr(st, "rerun"):
            try:
                st.rerun()
                return
            except Exception:
                pass

        # Fallback: bump query params to force a refresh, then stop
        try:
            qp = dict(st.query_params)
            qp["_rerun"] = str(int(time.time() * 1000))
            st.query_params = qp
            st.stop()
            return
        except Exception:
            pass

        # Final fallback: stop the script (best-effort)
        try:
            st.stop()
        except Exception:
            pass
    except Exception:
        try:
            st.stop()
        except Exception:
            pass

# ---------------------------
# Data fetching (tries backend -> fallback to local CSV)
# ---------------------------
@st.cache_data(ttl=30)
def fetch_incidents(params: Dict[str, Any]) -> pd.DataFrame:
    try:
        resp = requests.get(f"{API_URL}/api/incidents/", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict):
            if "incidents" in data and isinstance(data["incidents"], list):
                records = data["incidents"]
            elif "data" in data and isinstance(data["data"], list):
                records = data["data"]
            else:
                records = []
        elif isinstance(data, list):
            records = data
        else:
            records = []
        df = pd.DataFrame(records)
        if not df.empty:
            df = normalize_df(df)
        if "api_error" in st.session_state:
            del st.session_state["api_error"]
        return df
    except requests.exceptions.ConnectionError:
        st.session_state["api_error"] = f"Unable to connect to backend API at {API_URL}. Please ensure the backend is running."
        return pd.DataFrame()
    except requests.exceptions.Timeout:
        st.session_state["api_error"] = f"Request to backend API timed out. The backend may be slow or unavailable."
        return pd.DataFrame()
    except requests.exceptions.HTTPError as e:
        st.session_state["api_error"] = f"Backend API returned error: {e.response.status_code} - {e.response.text}"
        return pd.DataFrame()
    except Exception as e:
        st.session_state["api_error"] = f"Error fetching incidents: {str(e)}"
        return pd.DataFrame()

# ---------------------------
# Sidebar filters / helpers
# ---------------------------
def sidebar_filters() -> dict:
    st.sidebar.header("Filters")
    category = st.sidebar.selectbox("Category", ["", "phishing", "ransomware", "data_leak", "defacement", "ddos"], index=0)
    severity = st.sidebar.selectbox("Severity", ["", "Low", "Medium", "High", "Critical"], index=0)
    status = st.sidebar.selectbox("Status", ["", "Active", "Resolved"], index=0)
    st.sidebar.caption("Smart Filters")
    st.session_state.setdefault("filter_locations", [])
    st.session_state.setdefault("filter_sources", [])
    loc_selected = st.sidebar.multiselect("Locations", options=st.session_state.get("locations_options", []), default=st.session_state.get("filter_locations", []))
    src_selected = st.sidebar.multiselect("Sources", options=st.session_state.get("sources_options", []), default=st.session_state.get("filter_sources", []))
    st.session_state["filter_locations"] = loc_selected
    st.session_state["filter_sources"] = src_selected
    params: dict = {}
    if category:
        params["category"] = category
    if severity:
        params["severity"] = severity
    if status:
        params["status"] = status
    return params

# ---------------------------
# Rendering helpers
# ---------------------------
def render_summary(df: pd.DataFrame) -> None:
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    def count_incident_type(incident_type: str) -> int:
        """Count incidents by matching incident type (case-insensitive, handles variations)."""
        if df.empty:
            return 0
        try:
            # Check for Incident_Type column (from CSV), fallback to category or title
            col_to_use = None
            if "Incident_Type" in df.columns:
                col_to_use = "Incident_Type"
            elif "incident_type" in df.columns:
                col_to_use = "incident_type"
            elif "category" in df.columns:
                col_to_use = "category"
            elif "title" in df.columns:
                col_to_use = "title"
            
            if col_to_use is None:
                return 0
            
            # Create a mask for matching (case-insensitive substring matching)
            def match_incident(val):
                if pd.isna(val):
                    return False
                val_str = str(val).lower().strip()
                search_str = incident_type.lower().strip()
                return search_str in val_str
            
            mask = df[col_to_use].apply(match_incident)
            return int(mask.sum())
        except Exception:
            return 0
    
    def stat_card(col, title, value, icon):
        with col:
            st.markdown(
                "<div class='cs-card' style='border-radius:12px;'>"
                f"<div style='display:flex;align-items:center;gap:8px'><span style='font-size:20px'>{icon}</span><b>{title}</b></div>"
                f"<div style='font-size:28px;margin-top:6px'>{value}</div>"
                "</div>",
                unsafe_allow_html=True,
            )
    
    # Count incident types
    phishing_count = count_incident_type("phishing")
    ransomware_count = count_incident_type("ransomware")
    data_breach_count = count_incident_type("data breach") + count_incident_type("data_leak")
    malware_count = count_incident_type("malware")
    hacking_count = count_incident_type("hacking")
    total_attacks = len(df) if not df.empty else 0
    
    stat_card(c1, "Phishing", phishing_count, "🎣")
    stat_card(c2, "Ransomware", ransomware_count, "🔒")
    stat_card(c3, "Data Breach", data_breach_count, "💾")
    stat_card(c4, "Malware", malware_count, "🦠")
    stat_card(c5, "Hacking", hacking_count, "⚔️")
    stat_card(c6, "Total Attacks", total_attacks, "📊")

def render_table(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No incidents found for selected filters.")
        return
    show_cols = ["title", "category", "severity", "location", "source", "timestamp", "status"]
    existing = [c for c in show_cols if c in df.columns]
    df_sorted = df.sort_values(by="timestamp", ascending=False) if "timestamp" in df.columns else df
    selected_title = st.selectbox("Select an incident for actions/report:", ["-"] + df_sorted.get("title", pd.Series([])).tolist())
    if selected_title != "-":
        sel = df_sorted[df_sorted["title"] == selected_title].head(1)
        if not sel.empty:
            row = sel.iloc[0]
            cols = st.columns(2)
            with cols[0]:
                if row.get("status") == "Active" and st.button("Resolve", key=f"resolve_{row.get('id', row.name)}"):
                    st.success("Marked as resolved (demo mode)")
            with cols[1]:
                if st.button("Investigate", key=f"investigate_{row.get('id', row.name)}"):
                    st.info("Opening investigation workflow (demo mode)")
            st.markdown("<div class='cs-card' style='margin-top:8px;border-radius:12px'>", unsafe_allow_html=True)
            st.markdown("<b>Incident Report</b>")
            st.write({
                "Summary": row.get("description", "Detailed narrative not available in demo."),
                "Artifacts": ["ip:203.0.113.5", "hash:abcd1234...", "domain:mal.example"],
                "Timeline": [
                    "T-30m: Anomaly detected", "T-20m: Alert triaged", "T-10m: Containment initiated", "T-0: Status updated"
                ],
            })
            st.markdown("</div>", unsafe_allow_html=True)
    st.dataframe(df_sorted[existing], use_container_width=True, hide_index=True)

_CITY_COORDS = {
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "kolkata": (22.5726, 88.3639),
    "chennai": (13.0827, 80.2707),
    "lucknow": (26.8467, 80.9462),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
    "surat": (21.1702, 72.8311),
    "noida": (28.5355, 77.3910),
    "gurugram": (28.4595, 77.0266),
    "gurgaon": (28.4595, 77.0266),
    "coimbatore": (11.0168, 76.9558),
    "kochi": (9.9312, 76.2673),
}

def to_lat_lon(loc: str) -> Tuple[Optional[float], Optional[float]]:
    if not isinstance(loc, str) or not loc.strip():
        return None, None
    token = loc.split(",")[0].strip().lower()
    return _CITY_COORDS.get(token, (None, None))

@st.cache_data(ttl=60)
def geocode_india_locations(df: pd.DataFrame) -> pd.DataFrame:
    """Map human-friendly Indian city names to lat/lon.

    Cached to avoid recomputing on each rerun and improve dashboard responsiveness.
    """
    if df.empty or "location" not in df.columns:
        return pd.DataFrame()
    df = df.copy()
    try:
        latlon = df["location"].astype(str).apply(lambda s: to_lat_lon(s))
        df["lat"] = latlon.apply(lambda t: t[0])
        df["lon"] = latlon.apply(lambda t: t[1])
    except Exception:
        df["lat"] = None
        df["lon"] = None
    # Drop rows without valid numeric coordinates
    df = df.dropna(subset=["lat", "lon"])
    # Ensure numeric types
    try:
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    except Exception:
        pass
    df = df.dropna(subset=["lat", "lon"])
    return df

def _deterministic_jitter(uid: str, scale: float = 0.02) -> float:
    """Deterministic small offset based on an id string to avoid exact overlapping markers."""
    try:
        h = int(hashlib.md5(str(uid).encode()).hexdigest()[:8], 16)
        val = (h % 10000) / 10000.0  # 0..0.9999
        return (val - 0.5) * scale
    except Exception:
        return 0.0


def render_map(df: pd.DataFrame, selected_id: Optional[str] = None) -> None:
    st.subheader("Live Threat Map")
    geo = geocode_india_locations(df)
    if geo.empty:
        st.info("No mappable incidents yet. Add incidents with a known Indian city in 'location'.")
        return

    # Sidebar control: limit markers to avoid long render times
    st.sidebar.caption("Map display options")
    max_markers = st.sidebar.slider("Max map markers", min_value=50, max_value=2000, value=500, step=50)

    # Center map on India by default
    center_lat, center_lon = 21.1466, 79.0889
    zoom_level = 4

    # If a specific incident is selected, center on it
    if selected_id and selected_id in set(geo.get("id", [])):
        match = geo[geo["id"] == selected_id].iloc[0]
        center_lat, center_lon = float(match["lat"]), float(match["lon"])
        zoom_level = 8

    # Create Folium map with dark tiles (better match dashboard theme)
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles="CartoDB dark_matter",
        control_scale=True,
    )

    # Use a MarkerCluster to improve performance and prevent overlap
    marker_cluster = MarkerCluster(name="Incidents", disableClusteringAtZoom=10).add_to(m)

    # Severity configuration
    severity_color = {
        "Low": "#FFE600",
        "Medium": "#FFA500",
        "High": "#FF6347",
        "Critical": "#FF0000",
    }

    severity_radius = {
        "Low": 8,
        "Medium": 12,
        "High": 16,
        "Critical": 20,
    }

    # Limit markers for performance
    to_show = geo.head(max_markers)

    bounds = []

    # Add markers for each incident (clustered)
    for idx, row in to_show.iterrows():
        severity = str(row.get("severity", "Medium")).title()
        color = severity_color.get(severity, "#9999FF")
        radius = severity_radius.get(severity, 10)

        # Apply a tiny deterministic jitter to avoid overlapping exact coordinates
        jitter_lat = _deterministic_jitter(row.get("id", idx), scale=0.02)
        jitter_lon = _deterministic_jitter(f"{row.get('id', idx)}_lon", scale=0.02)
        lat = float(row["lat"]) + jitter_lat
        lon = float(row["lon"]) + jitter_lon

        # Build popup (keep compact) and tooltip for quick hover
        popup_text = f"<div style='font-family: Arial; width: 240px;'>" \
                    f"<b>{row.get('title', 'Unknown')}</b><br/><small>{row.get('category', 'N/A')}</small><br/>" \
                    f"<small>{row.get('location', 'N/A')}</small>" \
                    "</div>"
        popup = folium.Popup(popup_text, max_width=280)
        tooltip = str(row.get('title', ''))

        # Use CircleMarker inside the cluster
        marker = folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            popup=popup,
            tooltip=tooltip,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            weight=1,
        )
        marker.add_to(marker_cluster)
        bounds.append([lat, lon])

    # Fit map to bounds if we have them
    if bounds:
        try:
            m.fit_bounds(bounds, padding=(40, 40))
        except Exception:
            pass

    # If dataset is very large, render map in a collapsed expander by default
    if len(geo) > 1000:
        with st.expander(f"Live threat map ({len(geo)} incidents) - expand to view (recommended for large datasets)"):
            st_folium(m, width=None, height=550)
    else:
        st_folium(m, width=None, height=550)

    with st.expander("Incident details"):
        cols = ["id", "title", "category", "severity", "status", "location", "source", "timestamp"]
        existing = [c for c in cols if c in geo.columns]
        # Limit details table for performance
        st.dataframe(to_show[existing], use_container_width=True, hide_index=True)

@st.cache_data(ttl=60)
def _category_counts(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "category" not in df.columns:
        return pd.DataFrame()
    return df.groupby("category").size().reset_index(name="count")


def render_category_chart(df: pd.DataFrame) -> None:
    if df.empty or "category" not in df.columns:
        st.info("No data for category chart.")
        return
    count_df = _category_counts(df)
    if count_df.empty:
        st.info("No data for category chart.")
        return
    fig = px.pie(count_df, names="category", values="count", hole=0.35)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#0B1221", font_color="#FFFFFF")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def apply_global_style() -> None:
    st.markdown(
        """
        <style>
            :root { --bg: #0B1221; --accent: #A855F7; --fg: #FFFFFF; }
            .stApp { background-color: var(--bg); color: var(--fg); }
            .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

            /* Buttons and cards */
            .cs-button { background: var(--accent); color: #fff; padding: 0.6rem 1rem; border-radius: 10px; border: none; transition: transform .15s ease, box-shadow .15s ease; }
            .cs-button:hover { transform: translateY(-1px); box-shadow: 0 8px 22px rgba(168,85,247,.25); }
            .cs-card { background: #111a33; border: 1px solid #1e2a4a; padding: 1rem; border-radius: 14px; transition: transform .15s ease, border-color .15s ease; }
            .cs-card:hover { transform: translateY(-2px); border-color: var(--accent); }
            .cs-hero-title { font-size: 2.2rem; font-weight: 800; margin-bottom: 0.5rem; }
            .cs-hero-sub { color: #cbd5e1; }
            .cs-feature-title { font-weight: 700; }

            /* DataFrame and table readability (dark theme) */
            div[data-testid="stDataFrame"] table, div[data-testid="stTable"] table {
                background-color: #0b1221 !important;
                color: #e6eef8 !important;
            }
            div[data-testid="stDataFrame"] table th, div[data-testid="stTable"] table th {
                color: #cbd5e1 !important;
            }
            div[data-testid="stDataFrame"] table td, div[data-testid="stTable"] table td {
                color: #e6eef8 !important;
            }
            /* Ensure selection and header borders remain visible */
            div[data-testid="stDataFrame"] table td, div[data-testid="stDataFrame"] table th {
                border-color: rgba(255,255,255,0.06) !important;
            }

            /* Small tweaks to common Streamlit widgets for dark theme */
            .stMetricValue, .stMetricLabel { color: #e6eef8 !important; }
            .stButton>button { background-color: var(--accent) !important; color: #fff !important; }

            /* Folium map / iframe styling to blend with dark UI */
            .folium-map, .leaflet-container { border-radius: 12px; overflow: hidden; }
            iframe[src*="openstreetmap"], iframe[src*="cartodb"], iframe[src*="tile"] { border-radius: 12px; border: 1px solid rgba(255,255,255,0.04); }

            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
            html, body, [class*="css"] { font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_home(df: pd.DataFrame) -> None:
    c1, c2 = st.columns([1, 1])
    with c1:
        logo_path = os.path.join(os.path.dirname(__file__), "logo.svg")
        if os.path.exists(logo_path):
            st.image(logo_path, width=38)
        st.markdown("<div style='font-weight:800;font-size:20px; display:inline-block; margin-left:8px;'>CyberSentinel</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='text-align:right'><button class='cs-button'>Log In</button></div>", unsafe_allow_html=True)

    st.markdown("<div class='cs-hero-title'>India’s Real-Time Cyber Threat Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='cs-hero-sub'>CyberSentinel centralizes incident data, offering live monitoring and ML-driven classification to protect India’s digital frontier.</div>", unsafe_allow_html=True)

    b1, b2 = st.columns([1, 1])
    with b1:
        if st.button("View Live Dashboard", use_container_width=True):
            st.session_state["page_override"] = "Dashboard"
            safe_rerun()
    with b2:
        if st.button("Sign Up for Free", use_container_width=True):
            st.session_state["show_signup"] = True

    if st.session_state.get("show_signup"):
        with st.form("signup_form"):
            st.subheader("Create your account")
            name = st.text_input("Name")
            email = st.text_input("Email")
            pwd = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign Up")
            if submitted:
                st.success(f"Welcome, {name or 'User'}! This is a placeholder sign-up.")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("A Unified Command Center")
    st.caption("All the tools you need to monitor, classify, and respond to cyber threats.")
    icons = ["🌐", "🤖", "📡", "⚡", "🔐", "📈"]
    titles = [
        "Real-time Incident Mapping",
        "ML-Powered Classification",
        "Live Incident Feed",
        "Instant Alert System",
        "Secure by Design",
        "Admin Analytics",
    ]
    cols = st.columns(3)
    for i, title in enumerate(titles):
        with cols[i % 3]:
            st.markdown(f"<div class='cs-card'><div style='font-size:28px'>{icons[i]}</div><div class='cs-feature-title'>{title}</div><div style='color:#cbd5e1'>Production-style component placeholder</div></div>", unsafe_allow_html=True)

def main() -> None:
    st.set_page_config(page_title="CyberSentinel", layout="wide", page_icon="🛡️")
    apply_global_style()
    st.sidebar.title("CyberSentinel")
    page_options = ["Home", "Dashboard", "Incidents", "Admin", "Profile"]
    default_page = st.session_state.get("page_override", "Home")
    try:
        page_index = page_options.index(default_page)
    except ValueError:
        page_index = 0
    page = st.sidebar.radio("Navigation", page_options, index=page_index)
    st.session_state.pop("page_override", None)

    params = sidebar_filters()
    auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", value=False)

    # Manual refresh button (useful when auto-refresh is off)
    if st.sidebar.button("Refresh now"):
        try:
            qp = dict(st.query_params)
            qp["_"] = int(time.time())
            st.query_params = qp
        except Exception:
            pass

    if auto_refresh:
        try:
            qp = dict(st.query_params)
            qp["_"] = int(time.time() // 60)
            st.query_params = qp
        except Exception:
            pass

    # try backend first
    df = fetch_incidents(params)

    # always prepare local fallback
    local_df = load_preferred_local_dataset()

    # show API error in sidebar if any
    if st.session_state.get("api_error"):
        with st.sidebar:
            st.error("⚠️ Backend Offline")
            st.caption(f"API: {API_URL}")

    # if backend returned nothing, fallback to local CSV
    if df.empty:
        if not local_df.empty:
            df = local_df
            with st.sidebar:
                st.info(f"Using local dataset ({len(df)} rows) because backend is unavailable.")
        else:
            # keep df empty; UI will show guidance
            df = pd.DataFrame()
            if st.session_state.get("api_error"):
                st.error(f"❌ Backend API unavailable at `{API_URL}` and no local dataset found. Please start the backend server.")

    # normalize dataframe to canonical columns
    if not df.empty:
        df = normalize_df(df)

    # routing
    if page == "Home":
        render_home(df)
    elif page == "Dashboard":
        st.title("Dashboard")
        if not df.empty:
            st.session_state["locations_options"] = sorted(df["location"].dropna().astype(str).unique().tolist()) if "location" in df.columns else []
            st.session_state["sources_options"] = sorted(df["source"].dropna().astype(str).unique().tolist()) if "source" in df.columns else []
            locs = set(st.session_state.get("filter_locations", []))
            srcs = set(st.session_state.get("filter_sources", []))
            if locs:
                df = df[df["location"].astype(str).isin(locs)]
            if srcs:
                df = df[df["source"].astype(str).isin(srcs)]
        render_summary(df)
        col1, col2 = st.columns((2, 1))
        with col1:
            render_map(df)
        with col2:
            st.subheader("Incident Categories")
            render_category_chart(df)
        st.subheader("Recent Incidents")
        render_table(df)
    elif page == "Incidents":
        st.title("All Incidents")
        incident_titles = ["-"]
        if not df.empty and "title" in df.columns:
            incident_titles.extend(df["title"].dropna().unique().tolist())
        selected_title = st.selectbox("Jump to incident", incident_titles)
        selected_id = None
        if selected_title != "-" and not df.empty:
            row = df[df["title"] == selected_title].head(1)
            if not row.empty:
                selected_id = row.iloc[0].get("id")
        render_map(df, selected_id=selected_id)
        render_table(df)
    elif page == "Admin":
        st.title("Admin Management")
        tab1, tab2, tab3, tab4 = st.tabs(["Incident Management", "Analytics", "System Status", "Settings"])
        with tab1:
            st.subheader("Incident Management")
            if not df.empty:
                st.metric("Total Incidents", len(df))
                # Count active incidents (those with status "Active" or without explicit "Closed" status)
                active_count = len(df[df["status"].astype(str).str.lower() == "active"]) if "status" in df.columns else 0
                # Count resolved/closed incidents
                resolved_count = len(df[df["status"].astype(str).str.lower().isin(["resolved", "closed"])]) if "status" in df.columns else len(df)
                
                st.metric("Active Incidents", active_count)
                st.metric("Resolved Incidents", resolved_count)
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Incidents by Category")
                    if "category" in df.columns:
                        category_counts = df["category"].value_counts()
                        st.bar_chart(category_counts)
                with col2:
                    st.subheader("Incidents by Severity")
                    if "severity" in df.columns:
                        severity_counts = df["severity"].value_counts()
                        st.bar_chart(severity_counts)
                st.subheader("Recent Incidents")
                render_table(df.head(10))
            else:
                st.info("No incidents data available. Connect to backend API or load local dataset.")
        with tab2:
            st.subheader("Analytics Dashboard")
            if not df.empty:
                st.subheader("Incident Trends")
                if "timestamp" in df.columns:
                    df_with_date = df.copy()
                    df_with_date["date"] = pd.to_datetime(df_with_date["timestamp"]).dt.date
                    daily_counts = df_with_date.groupby("date").size().reset_index(name="count")
                    st.line_chart(daily_counts.set_index("date"))
                st.subheader("Geographic Distribution")
                if "location" in df.columns:
                    location_counts = df["location"].value_counts().head(10)
                    st.bar_chart(location_counts)
            else:
                st.info("No data available for analytics.")
        with tab3:
            st.subheader("System Status")
            col1, col2, col3 = st.columns(3)
            with col1:
                try:
                    health_resp = requests.get(f"{API_URL}/api/health", timeout=5)
                    if health_resp.status_code == 200:
                        st.success("✅ Backend API: Online")
                    else:
                        st.error("❌ Backend API: Error")
                except Exception:
                    st.error("❌ Backend API: Offline")
            with col2:
                try:
                    test_resp = requests.get(f"{API_URL}/api/incidents/", params={}, timeout=5)
                    if test_resp.status_code == 200:
                        st.success("✅ Database: Connected")
                    else:
                        st.warning("⚠️ Database: Connection Issues")
                except Exception:
                    st.error("❌ Database: Unable to verify")
            with col3:
                st.info("ℹ️ Frontend: Running")
            st.subheader("System Information")
            st.json(
                {
                    "API URL": API_URL,
                    "Python Version": f"{sys.version.split()[0]}",
                    "Streamlit Version": st.__version__,
                }
            )
        with tab4:
            st.subheader("Admin Settings")
            with st.form("admin_settings"):
                st.write("Configure system-wide settings")
                api_url_input = st.text_input("API URL", value=API_URL)
                auto_refresh_enabled = st.checkbox("Enable Auto-refresh", value=True)
                refresh_interval = st.slider("Refresh Interval (seconds)", 5, 60, 10)
                if st.form_submit_button("Save Settings"):
                    st.session_state["api_url"] = api_url_input
                    st.session_state["auto_refresh"] = auto_refresh_enabled
                    st.session_state["refresh_interval"] = refresh_interval
                    st.success("Settings saved (demo mode - changes not persisted)")
    else:
        st.title("My Profile")
        with st.form("profile_form"):
            name = st.text_input("Full Name", value=st.session_state.get("prof_name", ""))
            email = st.text_input("Email", value=st.session_state.get("prof_email", ""))
            tz = st.selectbox("Timezone", ["IST (UTC+5:30)", "UTC", "CET", "EST"], index=0)
            st.subheader("Password Management")
            pwd = st.text_input("New Password", type="password")
            st.subheader("Notification Preferences")
            notif_high = st.checkbox("Email me for High/Critical incidents", value=st.session_state.get("notif_high", True))
            submitted = st.form_submit_button("Update Profile")
            if submitted:
                st.session_state.update({"prof_name": name, "prof_email": email, "notif_high": notif_high, "prof_tz": tz})
                st.success("Profile updated (demo mode)")

if __name__ == "__main__":
    main()
