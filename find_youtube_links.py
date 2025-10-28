# add_youtube_links.py
import unicodedata
from urllib.parse import quote_plus
from pathlib import Path

INPUT_FILE = Path("playlist_songs.txt")
OUTPUT_FILE = Path("playlist_songs_with_links.txt")

def normalize_text(s: str) -> str:
    # Normalize unicode (e.g., curly quotes) and squeeze spaces
    s = unicodedata.normalize("NFKC", s).strip()
    # Common typographic apostrophe -> ASCII
    s = s.replace("’", "'").replace("‘", "'")
    # Collapse internal whitespace
    return " ".join(s.split())

def is_separator(line: str) -> bool:
    # Detect lines that are just dashes (your separator row)
    stripped = line.strip()
    return stripped and set(stripped) == {"-"}
    
def build_link(song: str, artist: str) -> str:
    query = f"{normalize_text(song)} {normalize_text(artist)}"
    return "https://www.youtube.com/results?search_query=" + quote_plus(query)

def main():
    if not INPUT_FILE.exists():
        raise SystemExit(f"Input file not found: {INPUT_FILE}")

    lines = INPUT_FILE.read_text(encoding="utf-8").splitlines()

    out_rows = []
    header_seen = False

    for line in lines:
        if not line.strip():
            continue  # skip blank lines
        if is_separator(line):
            # skip original separator; we'll regenerate later
            continue

        # Expect header first
        if not header_seen:
            # Build new header with Link column
            header_seen = True
            header = "Artist | Song | Album | Year | Link"
            out_rows.append(header)
            # Separator sized to the header length (looks tidy)
            out_rows.append("-" * len(header))
            # Now process this same line as potential header—if it is a header, skip adding it as data
            # Detect if the first non-separator line is actually a header by checking it contains 'Artist' etc.
            if "Artist" in line and "Song" in line:
                continue  # don't treat the header as data

        # Parse data rows
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            # Not enough columns; skip or warn
            continue

        artist, song, album, year = parts[:4]
        link = build_link(song, artist)
        out_line = f"{artist} | {song} | {album} | {year} | {link}"
        out_rows.append(out_line)

    OUTPUT_FILE.write_text("\n".join(out_rows) + "\n", encoding="utf-8")
    print(f"Done. Wrote: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
