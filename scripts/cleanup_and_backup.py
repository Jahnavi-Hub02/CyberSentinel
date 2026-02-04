"""Safe cleanup script

Usage:
  python scripts/cleanup_and_backup.py --run

By default the script performs a dry-run and prints what it would delete.
With `--run` it will:
  - create `archives/backup_before_cleanup.zip` (full repo snapshot)
  - remove: .pytest_cache, .qodo, artifacts, tmp_reconstructed_demo, CyberSentinel-cleaned.zip

This script is for local use. Run it before committing if you want the cleanup applied.
"""
import argparse
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVES = ROOT / "archives"
TO_REMOVE = [
    ROOT / ".pytest_cache",
    ROOT / ".qodo",
    ROOT / "artifacts",
    ROOT / "tmp_reconstructed_demo",
    ROOT / "CyberSentinel-cleaned.zip",
]
EXCLUDE = {".git", "archives"}


def make_backup():
    ARCHIVES.mkdir(parents=True, exist_ok=True)
    archive_path = ARCHIVES / "backup_before_cleanup"
    print(f"Creating backup archive at: {archive_path}.zip")
    shutil.make_archive(str(archive_path), 'zip', str(ROOT))
    print("Backup created.")
    return archive_path.with_suffix('.zip')


def remove_paths(run=False):
    for p in TO_REMOVE:
        if p.exists():
            if run:
                try:
                    if p.is_dir():
                        shutil.rmtree(p)
                    else:
                        p.unlink()
                    print(f"Removed: {p}")
                except Exception as e:
                    print(f"Failed to remove {p}: {e}")
            else:
                print(f"Would remove: {p}")
        else:
            print(f"Not present (skipping): {p}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true', help='Execute deletion after making backup')
    args = parser.parse_args()

    print('Safe cleanup: dry-run by default. Use --run to actually delete files.')
    print('Targets:')
    for p in TO_REMOVE:
        print(' -', p)

    if not args.run:
        print('\nDry-run complete. To perform cleanup run: python scripts/cleanup_and_backup.py --run')
        return

    # perform backup
    zip_path = make_backup()
    # perform deletions
    remove_paths(run=True)
    print('\nCleanup complete. Backup stored at:', zip_path)


if __name__ == '__main__':
    main()
