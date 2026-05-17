def parse(raw_text: str) -> list[dict]:
    records = []
    lines = raw_text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line.startswith("Avatar of "):
            i += 1
            continue

        speaker = line.removeprefix("Avatar of ")
        i += 1

        # Skip the redundant speaker name line
        while i < len(lines) and not lines[i].strip():
            i += 1
        i += 1  # skip the name line itself

        # Skip empty lines before title
        while i < len(lines) and not lines[i].strip():
            i += 1

        if i >= len(lines):
            records.append({"speaker": speaker, "title": "", "description": ""})
            break

        title = lines[i].strip()
        i += 1

        # Collect description
        desc_lines = []
        while i < len(lines):
            stripped = lines[i].strip()
            if stripped.startswith("Avatar of "):
                break
            if stripped:
                desc_lines.append(stripped)
            elif desc_lines:
                desc_lines.append("")
            i += 1

        description = "\n".join(desc_lines).strip()
        records.append({"speaker": speaker, "title": title, "description": description})

    return records
