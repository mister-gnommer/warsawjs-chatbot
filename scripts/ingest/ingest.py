#!/usr/bin/env python3
# 🤖 AI-generated
import argparse
import json
import sys
from pathlib import Path
from stages.parse import parse


def main():
    parser = argparse.ArgumentParser(description="Ingest scraped talk data into the pipeline")
    parser.add_argument(
        "--override-duplicates",
        action="store_true",
        default=False,
        help="Skip DB dedup check in embed stage and re-embed all records (default: false)",
    )
    args = parser.parse_args()

    _ = args  # consumed by future embed stage

    script_dir = Path(__file__).parent
    input_dir = script_dir / "input"

    if not input_dir.is_dir():
        print(f"Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    records = []
    for file in sorted(input_dir.iterdir()):
        if file.suffix.lower() not in (".md", ".txt"):
            continue
        if not file.is_file():
            continue
        raw_text = file.read_text(encoding="utf-8")
        file_records = parse(raw_text)
        records.extend(file_records)
        print(f"  {file.name}: {len(file_records)} talks")

    output_dir = script_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "talks.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Parsed {len(records)} talks total → {output_path}")


if __name__ == "__main__":
    main()
