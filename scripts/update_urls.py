#!/usr/bin/env python3
"""
Script to keep MOMENTS video URLs fresh by detecting unavailable videos,
finding replacements (optionally via the YouTube Data API v3), and producing
an updated dataset JSON plus a report summarising the changes.

Usage
-----
```bash
python update_urls.py \
  --yt_key YOUR_KEY \
  --annotations  data_in.json \
  --output data_out.json \
  --report_output report.json
```

If `--yt_key` is omitted the script falls back to the environment variable
`YOUTUBE_API_KEY`. When no key is available the script still checks whether
the original URLs are live but *does not* attempt to search for alternatives.

"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

# Third‑party
from rapidfuzz import fuzz

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    build = None
    HttpError = Exception

# The YouTube API client will be initialised in main()
YT = None

# ---------------- Global configuration -------------------------
SEARCH_SUFFIXES = [" short film", " Omeleto"]
SIMILARITY_THRESHOLD = 80  # %
MAX_DURATION_DELTA = 15    # Seconds ± allowed when matching durations
MAX_SEARCH_RESULTS = 5    # Each `search.list` call consumes 100 units of quota
PAUSE_BETWEEN_CALLS = 1  # Throttle to avoid quota exhaustion

# ---------------- Generic helpers -----------------------------

def normalize(text: str) -> str:
    t = text.lower()
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def bucket(sec: int) -> str:
    return "short" if sec <= 240 else "medium" if sec <= 1200 else "long"


def extract_video_id(url: str) -> Optional[str]:
    p = urlparse(url)
    if p.hostname == "youtu.be":
        return p.path.lstrip("/")
    if "youtube" in (p.hostname or "") and p.path == "/watch":
        return parse_qs(p.query).get("v", [None])[0]
    return None

# ---------------- Availability check with yt‑dlp -----------------

def is_live(url: str) -> bool:
    try:
        subprocess.run(
            ["yt-dlp", "--skip-download", "--quiet", "--no-warnings", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

# ---------------- YouTube Data API helpers ---------------------

def seconds_from_iso8601(iso: str) -> int:
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not m:
        return 0
    h, m_, s = [int(x or 0) for x in m.groups()]
    return h * 3600 + m_ * 60 + s


def yt_duration(video_id: str) -> Optional[int]:
    if not YT:
        return None
    try:
        resp = YT.videos().list(part="contentDetails", id=video_id).execute()
        iso = resp["items"][0]["contentDetails"]["duration"]
        return seconds_from_iso8601(iso)
    except Exception:
        return None

# ---------------- Replacement search ---------------------------

def search_replacement(title: str, dur_s: int) -> Optional[str]:
    if not YT:
        return None

    bucket_tag = bucket(dur_s)
    title_variants = {suf: normalize(f"{title}{suf}") for suf in SEARCH_SUFFIXES}
    variant_omeleto = title_variants[" Omeleto"]

    best_score, best_vid = -1, None

    for suf in SEARCH_SUFFIXES:
        query = f"{title}{suf}"
        is_from_omeleto = None
        best_dur = None
        try:
            resp = (
                YT.search()
                .list(q=query, type="video", videoDuration=bucket_tag,
                      part="snippet", maxResults=MAX_SEARCH_RESULTS)
                .execute()
            )
        except HttpError:
            continue

        for item in resp.get("items", []):
            vid = item["id"]["videoId"]
            cand_title = item["snippet"]["title"]
            cand_norm = normalize(cand_title)
            cand_dur = yt_duration(vid)

            title_wo_omeleto = cand_title[:cand_title.find('|')-1]
            twoo_normalized = normalize(title_wo_omeleto)

            if (normalize(title) == twoo_normalized) and ("omeleto" in cand_norm) and (abs(cand_dur - dur_s) < MAX_DURATION_DELTA):
                is_from_omeleto = True
                return f"https://www.youtube.com/watch?v={vid}", cand_dur, is_from_omeleto
            else:
                score = max(
                    fuzz.token_sort_ratio(cand_norm, v)
                    for v in title_variants.values()
                )

            if score < SIMILARITY_THRESHOLD:
                continue


            if cand_dur is None:
                continue
            if abs(cand_dur - dur_s) > MAX_DURATION_DELTA:
                continue

            if score > best_score:
                best_score, best_vid, best_dur = score, vid, cand_dur
                if "omeleto" in cand_norm:
                    is_from_omeleto = True
                else:
                    is_from_omeleto = False

        time.sleep(PAUSE_BETWEEN_CALLS)

    return f"https://www.youtube.com/watch?v={best_vid}" if best_vid else None, best_dur, is_from_omeleto

# ---------------- File I/O helpers -----------------------------

def load_json(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        sys.exit("[ERROR] El JSON debe ser una lista de objetos.")
    return data


def write_json(path: str, data: List[dict]):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
# ---------------- Main -------------------------

def parse_args() -> argparse.Namespace:
    """Parse command‑line arguments."""
    parser = argparse.ArgumentParser(
        description="Update YouTube links in a dataset and generate a report."
    )
    parser.add_argument("--yt_key", dest="api_key", default=None,
                        help="YouTube Data API v3 key. If omitted, uses $YOUTUBE_API_KEY.")
    parser.add_argument("--annotations", required=True, help="Path to input JSON dataset.")
    parser.add_argument("--output", required=True, help="Path to updated dataset JSON.")
    parser.add_argument("--report_output", required=True, help="Path to JSON change report.")
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    api_key = args.api_key or os.getenv("YOUTUBE_API_KEY")
    if api_key:
        if build is None:
            sys.exit("Google API Client library not installed. Run `pip install google-api-python-client`")
        global YT
        YT = build("youtube", "v3", developerKey=api_key, cache_discovery=False)
    else:
        print("[WARN] No API key provided. Replacement search is disabled.")
        YT = None

    records = load_json(args.annotations)

    # Group by (title, url, duration) to remove duplicate API calls
    groups: Dict[Tuple[str, str, int], List[dict]] = defaultdict(list)
    for obj in records:
        key = (
            obj.get("movie_title") or "",
            obj.get("video_url") or "",
            int(obj.get("video_length") or 0),
        )
        groups[key].append(obj)

    report: List[dict] = []

    for (title, url, dur_s), objs in groups.items():
        # Extract video id from url
        vid = extract_video_id(url)
        is_available = is_live(url)

        # For convenience gather question ids or other identifiers if present
        video_ids = [o.get("question_id") or o.get("id") for o in objs]

        if is_available:
            # Video is still live – no change required
            continue

        replacement_url, cand_dur, is_from_omeleto = (None, None, False)
        if YT and vid:  # Only attempt replacement when API client is available
            replacement_url, cand_dur, is_from_omeleto = search_replacement(title, dur_s)
            
        length_difference = abs(dur_s - cand_dur) if cand_dur is not None else None

        if replacement_url:
            # Update objects with new url
            for o in objs:
                o["video_url"] = replacement_url
                o["video_status"] = "replaced"
                if cand_dur is not None:
                    o["video_length"] = cand_dur
            report.append(
                {
                    "title": title,
                    "old_url": url,
                    "new_url": replacement_url,
                    "video_status": "replaced",
                    "occurrences": len(objs),
                    "question_ids": video_ids,
                    "length_difference": length_difference,
                    "is_from_omeleto": is_from_omeleto,
                }
            )
            print(f"[REPLACED] {title[:45]}…")
        else:
            # No replacement found – mark as unavailable
            for o in objs:
                o["video_status"] = "unavailable"
            report.append(
                {
                    "title": title,
                    "old_url": url,
                    "new_url": "",
                    "video_status": "unavailable",
                    "occurrences": len(objs),
                    "question_ids": video_ids,
                    "length_difference": length_difference,
                    "is_from_omeleto": is_from_omeleto,
                }
            )
            print(f"[UNAVAILABLE] {title[:45]}…")

    write_json(args.output, records)
    write_json(args.report_output, report)
    print(f"Dataset updated: {args.output}")
    print(f"Change report : {args.report_output}")


if __name__ == "__main__":
    main()
