#!/usr/bin/python

# Copyright (c) 2020 Fernando — updated 2026
# License: MIT

# DESCRIPTION:
# One-shot script designed to run via GitHub Actions cron schedule.
# 1.) Loads last known post ID from state.txt (persisted between runs).
# 2.) Checks Instagram for new posts on the target account.
# 3.) If a new post is found, sends it to Discord via webhook.
# 4.) Saves the new post ID to state.txt for the next run.

# REQUIREMENTS:
# - Python v3.9+
# - pip install instagrapi requests

# ENVIRONMENT VARIABLES (set as GitHub Actions secrets):
#   IG_USERNAME  : your Instagram login username
#   IG_PASSWORD  : your Instagram login password
#   IG_TARGET    : account to monitor (defaults to IG_USERNAME)
#   WEBHOOK_URL  : Discord webhook URL

import os
import json
import requests
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

SESSION_FILE = "ig_session.json"
STATE_FILE   = "state.txt"

IG_USERNAME = os.environ["IG_USERNAME"]
IG_PASSWORD = os.environ["IG_PASSWORD"]
IG_TARGET   = os.environ.get("IG_TARGET", IG_USERNAME)
WEBHOOK_URL = os.environ["WEBHOOK_URL"]


def login(client: Client) -> None:
    if os.path.exists(SESSION_FILE):
        try:
            client.load_settings(SESSION_FILE)
            client.login(IG_USERNAME, IG_PASSWORD)
            client.get_timeline_feed()
            print("Session restored.")
            return
        except LoginRequired:
            print("Session expired, re-logging in.")
            client.set_settings({})

    client.login(IG_USERNAME, IG_PASSWORD)
    client.dump_settings(SESSION_FILE)
    print("Logged in and session saved.")


def load_last_post_id() -> str | None:
    if os.path.exists(STATE_FILE):
        content = open(STATE_FILE).read().strip()
        return content if content else None
    return None


def save_last_post_id(post_id: str) -> None:
    with open(STATE_FILE, "w") as f:
        f.write(post_id)


def send_to_discord(post) -> None:
    caption  = post.caption_text or ""
    post_url = f"https://www.instagram.com/p/{post.code}/"

    image_url = None
    if post.thumbnail_url:
        image_url = str(post.thumbnail_url)
    elif post.resources:
        image_url = str(post.resources[0].thumbnail_url)

    embed = {
        "color": 15467852,
        "title": f"New post from @{IG_TARGET}",
        "url": post_url,
        "description": caption[:2000],
    }
    if image_url:
        embed["image"] = {"url": image_url}

    result = requests.post(
        WEBHOOK_URL,
        data=json.dumps({"embeds": [embed]}),
        headers={"Content-Type": "application/json"},
    )
    try:
        result.raise_for_status()
        print(f"Posted to Discord (HTTP {result.status_code}): {post_url}")
    except requests.exceptions.HTTPError as err:
        print(f"Discord webhook error: {err}")


def main():
    client = Client()
    login(client)

    user_id = client.user_id_from_username(IG_TARGET)
    posts   = client.user_medias(user_id, amount=1)

    if not posts:
        print("No posts found.")
        return

    latest      = posts[0]
    post_id     = str(latest.pk)
    last_post_id = load_last_post_id()

    if last_post_id is None:
        # First run — just record the current post, don't send
        save_last_post_id(post_id)
        print(f"First run. Recorded latest post: {latest.code}")
    elif post_id != last_post_id:
        print(f"New post detected: {latest.code}")
        send_to_discord(latest)
        save_last_post_id(post_id)
    else:
        print("No new post.")


if __name__ == "__main__":
    required = ["IG_USERNAME", "IG_PASSWORD", "WEBHOOK_URL"]
    missing  = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        raise SystemExit(1)

    main()
