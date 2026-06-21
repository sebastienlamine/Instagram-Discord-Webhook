#!/usr/bin/python

# Copyright (c) 2020 Fernando — updated 2026
# License: MIT

# DESCRIPTION:
# Scrapes a public Instagram profile via a third-party viewer (no Instagram
# account required, works from GitHub Actions IPs).
# 1.) Fetches latest post from the target account via picuki.com.
# 2.) If a new post is detected, sends it to Discord via webhook.
# 3.) Saves state between GitHub Actions runs via state.txt.

# REQUIREMENTS:
# - Python v3.9+
# - pip install requests beautifulsoup4

# ENVIRONMENT VARIABLES (GitHub Actions secrets):
#   IG_TARGET   : Instagram account to monitor (e.g. "lebronjames")
#   WEBHOOK_URL : Discord webhook URL

import os
import json
import time
import requests
from bs4 import BeautifulSoup

STATE_FILE  = "state.txt"
IG_TARGET   = os.environ["IG_TARGET"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def get_latest_post():
    """Fetch the latest post from picuki.com for the target account."""
    url  = f"https://www.picuki.com/profile/{IG_TARGET}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup  = BeautifulSoup(resp.text, "html.parser")
    posts = soup.select("div.box-photo")

    if not posts:
        raise ValueError("No posts found — picuki.com page structure may have changed.")

    first = posts[0]

    # Post URL → extract shortcode from the picuki link
    link_tag = first.select_one("a[href*='/media/']")
    picuki_url = link_tag["href"] if link_tag else None
    shortcode  = picuki_url.split("/media/")[1].rstrip("/") if picuki_url else None
    post_url   = f"https://www.instagram.com/p/{shortcode}/" if shortcode else None

    # Image
    img_tag   = first.select_one("img")
    image_url = img_tag["src"] if img_tag else None

    # Caption
    caption_tag = first.select_one(".photo-description")
    caption     = caption_tag.get_text(strip=True) if caption_tag else ""

    return {
        "id":        shortcode or image_url,
        "post_url":  post_url,
        "image_url": image_url,
        "caption":   caption,
    }


def load_last_id() -> str | None:
    if os.path.exists(STATE_FILE):
        content = open(STATE_FILE).read().strip()
        return content if content else None
    return None


def save_last_id(post_id: str) -> None:
    with open(STATE_FILE, "w") as f:
        f.write(post_id)


def send_to_discord(post: dict) -> None:
    embed = {
        "color":       15467852,
        "title":       f"New post from @{IG_TARGET}",
        "url":         post["post_url"],
        "description": post["caption"][:2000],
    }
    if post["image_url"]:
        embed["image"] = {"url": post["image_url"]}

    result = requests.post(
        WEBHOOK_URL,
        data=json.dumps({"embeds": [embed]}),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    result.raise_for_status()
    print(f"Posted to Discord (HTTP {result.status_code}): {post['post_url']}")


def main():
    print(f"Checking @{IG_TARGET} …")
    post    = get_latest_post()
    post_id = post["id"]
    print(f"Latest post ID: {post_id}")

    last_id = load_last_id()

    if last_id is None:
        save_last_id(post_id)
        print("First run — state recorded, nothing sent to Discord.")
    elif post_id != last_id:
        print("New post detected!")
        send_to_discord(post)
        save_last_id(post_id)
    else:
        print("No new post.")


if __name__ == "__main__":
    required = ["IG_TARGET", "WEBHOOK_URL"]
    missing  = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        raise SystemExit(1)

    main()
