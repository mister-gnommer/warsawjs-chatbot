from stages.embed import Talk


def parse(raw_text: str) -> list[Talk]:
    records = []
    lines = raw_text.split("\n")
    i = 0

    while i < len(lines):
        # Detect start of a new entry
        line = lines[i].strip()
        if not line.startswith("Avatar of "):
            i += 1
            continue

        # Extract speaker name
        speaker = line.removeprefix("Avatar of ")
        i += 1

        # Skip blank lines before the redundant speaker-name line
        while i < len(lines) and not lines[i].strip():
            i += 1
        # Skip the redundant speaker-name line itself
        i += 1

        # Skip blank lines before the title
        while i < len(lines) and not lines[i].strip():
            i += 1

        # If no title follows, record what we have and stop
        if i >= len(lines):
            records.append(Talk(speaker=speaker, title="", description=""))
            break

        # Extract title
        title = lines[i].strip()
        i += 1

        # Collect description lines until the next entry
        desc_lines = []
        while i < len(lines):
            stripped = lines[i].strip()
            # Next entry starts — stop collecting
            if stripped.startswith("Avatar of "):
                break
            if stripped:
                desc_lines.append(stripped)
            # Preserve blank lines inside the description as paragraph breaks
            elif desc_lines:
                desc_lines.append("")
            i += 1

        description = "\n".join(desc_lines).strip()
        records.append(Talk(speaker=speaker, title=title, description=description))

    return records
