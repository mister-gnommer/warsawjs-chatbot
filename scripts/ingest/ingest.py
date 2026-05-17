#!/usr/bin/env python3
# 🤖 AI-generated
import sys
import json
from pathlib import Path
from stages.parse import parse


def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <input_file>", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    raw_text = input_path.read_text(encoding="utf-8")

    records = parse(raw_text)

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "talks.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Parsed {len(records)} talks → {output_path}")


if __name__ == "__main__":
    main()
