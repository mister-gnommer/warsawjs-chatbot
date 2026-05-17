#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from stages.embed import embed
from stages.parse import parse


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest scraped talk data into the pipeline"
    )
    parser.add_argument(
        "--override-duplicates",
        action="store_true",
        default=False,
        help="Skip DB dedup check in embed stage and re-embed all records (default: false)",
    )
    return parser.parse_args()


def _collect_records(input_dir: Path) -> list[dict]:
    if not input_dir.is_dir():
        print(f"Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    records = []
    for file in sorted(input_dir.iterdir()):
        if file.suffix.lower() not in (".md", ".txt") or not file.is_file():
            continue
        raw_text = file.read_text(encoding="utf-8")
        file_records = parse(raw_text)
        records.extend(file_records)
        print(f"  {file.name}: {len(file_records)} talks")

    return records


def _write_checkpoint(records: list[dict], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "talks.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Parsed {len(records)} talks total → {output_path}")
    return output_path


def main() -> None:
    parsed = _parse_args()
    script_dir = Path(__file__).parent

    records = _collect_records(script_dir / "input")
    _write_checkpoint(records, script_dir / "output")
    inserted = embed(records, parsed.override_duplicates)
    print(f"Inserted {inserted} records into database")


if __name__ == "__main__":
    main()
