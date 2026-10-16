import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import urlopen

from youtube_transcript_api import YouTubeTranscriptApi

VIDEO_ID_RE = re.compile(r"[A-Za-z0-9_-]{11}")


def extract_video_id(url: str) -> str:
    """Return the 11-character video ID from a YouTube URL (or a bare ID)."""
    url = url.strip()
    if VIDEO_ID_RE.fullmatch(url):
        return url

    parsed = urlparse(url if "://" in url else "https://" + url)
    host = (parsed.hostname or "").lower()
    parts = [p for p in parsed.path.split("/") if p]

    candidate = None
    if host == "youtu.be" and parts:
        # https://youtu.be/<id>
        candidate = parts[0]
    elif host.endswith("youtube.com") or host.endswith("youtube-nocookie.com"):
        if parts[:1] == ["watch"]:
            # https://www.youtube.com/watch?v=<id>&list=...&index=...
            candidate = parse_qs(parsed.query).get("v", [None])[0]
        elif len(parts) >= 2 and parts[0] in {"shorts", "embed", "live", "v"}:
            # https://www.youtube.com/shorts/<id>, /embed/<id>, /live/<id>
            candidate = parts[1]

    if candidate and VIDEO_ID_RE.fullmatch(candidate):
        return candidate
    raise ValueError(f"Could not extract a YouTube video ID from: {url}")


def get_video_title(video_id: str) -> str:
    """Look up the video's title via YouTube's oEmbed endpoint (no API key needed)."""
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    oembed_url = f"https://www.youtube.com/oembed?format=json&url={quote(watch_url, safe='')}"
    with urlopen(oembed_url, timeout=10) as resp:
        return json.load(resp)["title"]


def title_to_filename(title: str) -> str:
    """Join the title's words with '_', dropping punctuation and path characters.

    "Beginner System Design Interview: Design Bitly w/ a Ex-Meta Staff Engineer"
      -> "Beginner_System_Design_Interview_Design_Bitly_w_a_Ex_Meta_Staff_Engineer"
    '+' is kept so titles like "C++ Coroutines" stay "C++_Coroutines".
    """
    return "_".join(re.findall(r"[\w+]+", title))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a YouTube video's transcript as a Markdown file."
    )
    parser.add_argument("--url", help="YouTube video URL (a bare video ID also works)")
    parser.add_argument("--output_dir", type=Path, help="Folder to write the transcript into")
    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)
    except ValueError as e:
        parser.error(str(e))

    try:
        title = get_video_title(video_id)
    except Exception as e:
        print(f"Warning: could not get the video title ({e}); using the video ID instead.",
              file=sys.stderr)
        title = None

    file_stem = (title and title_to_filename(title)) or video_id

    output_dir = args.output_dir.expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{file_stem}.md"

    transcript = YouTubeTranscriptApi().fetch(video_id).to_raw_data()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {title or video_id}\n\n")
        f.write(f"Source: https://www.youtube.com/watch?v={video_id}\n\n")
        for item in transcript:
            seconds = int(item["start"])
            minutes, secs = divmod(seconds, 60)
            timestamp = f"[{minutes:02d}:{secs:02d}]"
            f.write(f"{timestamp} {item['text']}\n")

    print(f"Transcript written to {output_path}")


if __name__ == "__main__":
    main()
