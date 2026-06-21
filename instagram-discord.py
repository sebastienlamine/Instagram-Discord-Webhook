#!/usr/bin/python

# DESCRIPTION:
# Uses Apify's Instagram scraper (residential proxies, no account needed).
# 1.) Calls Apify API to get the latest post from the target Instagram account.
# 2.) If a new post is detected, sends it to Discord via webhook.
# 3.) Saves state between GitHub Actions runs via state.txt.

# REQUIREMENTS:
# - Python v3.9+
# - pip install requests

# ENVIRONMENT VARIABLES (GitHub Actions secrets):
#   APIFY_TOKEN : your Apify API token (free at apify.com)
#   IG_TARGET   : Instagram account to monitor (e.g. "lebronjames")
#   WEBHOOK_URL : Discord webhook URL

import os
import json
import requests

STATE_FILE  = "state.txt"
APIFY_TOKEN = os.environ["APIFY_TOKEN"]
IG_TARGET   = os.environ["IG_TARGET"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

ACTOR_ID = "apify~instagram-scraper"


def get_latest_post() -> dict:
    """Run Apify Instagram scraper and return the latest post."""
    url = (
        f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items"
        f"?token={APIFY_TOKEN}&timeout=60&memory=256"
    )
    payload = {
        "directUrls": [f"https://www.instagram.com/{IG_TARGET}/"],
        "resultsType": "posts",
        "resultsLimit": 1,
    }
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()

    items = resp.json()
    if not items:
        raise ValueError("No posts returned by Apify.")

    post = items[0]
    return {
        "id":        post.get("id") or post.get("shortCode"),
        "post_url":  post.get("url") or f"https://www.instagram.com/p/{post.get('shortCode')}/",
        "image_url": post.get("displayUrl"),
        "caption":   (post.get("caption") or "")[:2000],
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
        "title":       f"Nouveau post de @{IG_TARGET} ! Va vite le voir !",
        "url":         post["post_url"],
        "description": post["caption"],
    }
    if post["image_url"]:
        embed["image"] = {"url": post["image_url"]}

    resp = requests.post(
        WEBHOOK_URL,
        json={
            "content": "@everyone",
            "allowed_mentions": {"parse": ["everyone"]},
            "embeds": [embed],
        },
        timeout=10,
    )
    resp.raise_for_status()
    print(f"Posted to Discord (HTTP {resp.status_code}): {post['post_url']}")


def main():
    print(f"Checking @{IG_TARGET} via Apify …")

    post    = get_latest_post()
    post_id = str(post["id"])
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
    required = ["APIFY_TOKEN", "IG_TARGET", "WEBHOOK_URL"]
    missing  = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        raise SystemExit(1)

    main()
