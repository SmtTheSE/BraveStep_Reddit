#!/usr/bin/env python3
"""Import data/r_*/posts.csv into SQLite (when live scrape 403s but CSV exists)."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from export.database import get_connection, init_database, save_posts_batch


def import_csv(csv_path: Path, subreddit: str) -> int:
    init_database()
    rows = list(csv.DictReader(csv_path.open()))
    posts = []
    for r in rows:
        pid = (r.get("id") or "").strip()
        if not pid:
            continue
        posts.append(
            {
                "id": pid,
                "title": r.get("title") or "",
                "author": r.get("author") or "",
                "created_utc": r.get("created_utc") or "",
                "permalink": r.get("permalink") or "",
                "url": r.get("url") or "",
                "score": int(float(r.get("score") or 0)),
                "upvote_ratio": float(r.get("upvote_ratio") or 0),
                "num_comments": int(float(r.get("num_comments") or 0)),
                "num_crossposts": int(float(r.get("num_crossposts") or 0)),
                "selftext": r.get("selftext") or "",
                "post_type": r.get("post_type") or "text",
                "is_nsfw": str(r.get("is_nsfw", "")).lower() in ("1", "true", "yes"),
                "is_spoiler": str(r.get("is_spoiler", "")).lower() in ("1", "true", "yes"),
                "flair": r.get("flair") or "",
                "total_awards": int(float(r.get("total_awards") or 0)),
                "has_media": str(r.get("has_media", "")).lower() in ("1", "true", "yes"),
                "media_downloaded": False,
                "source": r.get("source") or "csv_import",
            }
        )
    saved = save_posts_batch(posts, subreddit)
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO subreddits(name, last_scraped, total_posts, total_comments)
            VALUES (?, datetime('now'), ?, 0)
            ON CONFLICT(name) DO UPDATE SET
              last_scraped=excluded.last_scraped,
              total_posts=(SELECT COUNT(*) FROM posts WHERE lower(subreddit)=lower(excluded.name))
            """,
            (subreddit, saved),
        )
        conn.commit()
    finally:
        conn.close()
    return saved


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--sub", required=True)
    args = p.parse_args()
    n = import_csv(Path(args.csv), args.sub.lstrip("r/"))
    print(f"imported {n} posts into SQLite for r/{args.sub.lstrip('r/')}")


if __name__ == "__main__":
    main()
