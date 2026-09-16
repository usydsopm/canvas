#!/usr/bin/env python3
"""
Rebuilds PMSoc-Instagram.html from build/ig_posts.json + build/ig_profile.json
+ build/canvas_template_ig.html.

Run from the REPO ROOT:
    python3 build/build_canvas_html_ig.py

Output: PMSoc-Instagram.html at the repo root (what GitHub Pages serves).

To add a new post: add a new object to the FRONT of the list in
build/ig_posts.json (newest first) with date_iso / caption / url / type /
img_asset, and save its post photo as a base64 data URI text file under
build/assets/ (see README.md in the repo root for the exact steps + how to
fetch a photo from an authenticated Instagram browser session). Keep at
most 5 posts in ig_posts.json so the page doesn't grow unbounded — drop
the oldest one off the end (and delete its asset file) when adding a new one.

To update the profile header (bio, follower/following/post counts, link),
edit build/ig_profile.json.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))       # .../repo/build
REPO_ROOT = os.path.dirname(HERE)                        # .../repo
ASSETS_DIR = os.path.join(HERE, "assets")


def asset(name):
    with open(os.path.join(ASSETS_DIR, name)) as f:
        return f.read().strip()


with open(os.path.join(HERE, "ig_posts.json")) as f:
    posts = json.load(f)

with open(os.path.join(HERE, "ig_profile.json")) as f:
    profile = json.load(f)

logo = asset("logo_datauri.txt")

# Feather Icons (MIT licensed) — simple line icons for the action bar, the
# reel "play" badge, and the carousel "copy" badge used in the grid.
HEART_ICON = '<svg viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>'
COMMENT_ICON = '<svg viewBox="0 0 24 24"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>'
SEND_ICON = '<svg viewBox="0 0 24 24"><path d="M22 2L11 13"></path><path d="M22 2l-7 20-4-9-9-4 20-7z"></path></svg>'
BOOKMARK_ICON = '<svg viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>'
PLAY_ICON = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"></path></svg>'
COPY_ICON = '<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'

card_tpl = """
    <div class="feed-item">
      <div class="feed-item-header">
        <img class="feed-item-avatar" src="{logo}" alt="PMSoc logo">
        <span class="feed-item-handle">pmsoc.usyd</span>
      </div>
      <div class="feed-item-photo">
        <img src="{img}" alt="{alt}" loading="lazy">
        {reel_badge}
      </div>
      <div class="feed-item-actions">
        <a class="action" href="{url}" target="_blank" rel="noopener" aria-label="Like">{heart}</a>
        <a class="action" href="{url}" target="_blank" rel="noopener" aria-label="Comment">{comment}</a>
        <a class="action" href="{url}" target="_blank" rel="noopener" aria-label="Send">{send}</a>
        <span class="spacer"></span>
        <a class="action" href="{url}" target="_blank" rel="noopener" aria-label="Save">{bookmark}</a>
      </div>
      <div class="feed-item-text">
        <div class="feed-item-date"><span class="date-text" data-iso="{date_iso}"></span></div>
        <p class="feed-item-caption"><span class="handle-inline">pmsoc.usyd</span>{caption}</p>
        <a class="feed-item-link" href="{url}" target="_blank" rel="noopener">View {kind} on Instagram &#8599;</a>
      </div>
    </div>"""

grid_item_tpl = """    <a class="ig-grid-item" href="{url}" target="_blank" rel="noopener">
      <img src="{img}" alt="{alt}" loading="lazy">
      {badge}
    </a>"""

REEL_BADGE_TPL = '<span class="reel-badge">{play} REEL</span>'
GRID_REEL_BADGE = '<svg class="ig-grid-badge" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"></path></svg>'
GRID_CAROUSEL_BADGE = COPY_ICON.replace('<svg viewBox="0 0 24 24">', '<svg class="ig-grid-badge" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">')


def alt_text(caption, limit=80):
    caption = caption.strip().replace("\n", " ")
    return (caption[:limit] + "...") if len(caption) > limit else caption


def kind_label(p):
    t = p.get("type")
    if t == "reel":
        return "reel"
    if t == "carousel":
        return "post"
    return "post"


def grid_badge(p):
    t = p.get("type")
    if t == "reel":
        return GRID_REEL_BADGE
    if t == "carousel":
        return GRID_CAROUSEL_BADGE
    return ""


cards_html = "\n".join(
    card_tpl.format(
        date_iso=p["date_iso"],
        caption=p["caption"],
        url=p["url"],
        img=asset(p["img_asset"]),
        alt=alt_text(p.get("caption", "")),
        logo=logo,
        heart=HEART_ICON, comment=COMMENT_ICON, send=SEND_ICON, bookmark=BOOKMARK_ICON,
        kind=kind_label(p),
        reel_badge=REEL_BADGE_TPL.format(play=PLAY_ICON) if p.get("type") == "reel" else "",
    )
    for p in posts
)

grid_html = "\n".join(
    grid_item_tpl.format(
        url=p["url"],
        img=asset(p["img_asset"]),
        alt=alt_text(p.get("caption", "")),
        badge=grid_badge(p),
    )
    for p in posts
)

# Linkify the @mention in the bio (e.g. "@sydney_uni" -> a link), preserving
# the rest of the bio text (and its literal newlines, via white-space:
# pre-line on .ig-bio-text) exactly as written in ig_profile.json.
bio_html = profile["bio"]
mention = profile.get("mention_handle")
if mention:
    bio_html = bio_html.replace(
        mention,
        '<a href="{}" target="_blank" rel="noopener">{}</a>'.format(profile.get("mention_url", "#"), mention),
    )

with open(os.path.join(HERE, "canvas_template_ig.html")) as f:
    template = f.read()

out = template.replace("{{CARDS}}", cards_html)
out = out.replace("{{GRID}}", grid_html)
out = out.replace("{logo}", logo)
out = out.replace("{profile_url}", profile["profile_url"])
out = out.replace("{reels_url}", profile["reels_url"])
out = out.replace("{tagged_url}", profile["tagged_url"])
out = out.replace("{handle}", profile["handle"])
out = out.replace("{posts_count}", profile["posts_count"])
out = out.replace("{followers_count}", profile["followers_count"])
out = out.replace("{following_count}", profile["following_count"])
out = out.replace("{display_name}", profile["display_name"])
out = out.replace("{bio_html}", bio_html)
out = out.replace("{link_url}", profile["link_url"])
out = out.replace("{link_text}", profile["link_text"])

out_path = os.path.join(REPO_ROOT, "PMSoc-Instagram.html")
with open(out_path, "w") as f:
    f.write(out)

print("done:", out_path, len(out), "bytes,", len(posts), "posts")
