"""
Run this ONCE to create MODELS/class_names.json from your dataset folder.

Usage:
    python export_class_names.py --data_dir Artifacts/train
                                 --out      MODELS/class_names.json
"""
import argparse, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", required=True,
                    help="ImageFolder-style directory (one sub-folder per class)")
    ap.add_argument("--out", default="MODELS/class_names.json")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"ERROR: data_dir does not exist: {data_dir}")
        print("Available top-level directories:")
        for p in sorted(Path('.').iterdir()):
            if p.is_dir():
                print(f"  {p}")
        raise SystemExit(1)

    if not data_dir.is_dir():
        raise SystemExit(f"ERROR: {data_dir} is not a directory.")

    classes = sorted([d.name for d in data_dir.iterdir() if d.is_dir()])
    print(f"Found {len(classes)} classes")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(classes, f, indent=2)

    print(f"Saved → {out}")
    for i, c in enumerate(classes):
        print(f"  {i:3d}: {c}")

if __name__ == "__main__":
    main()