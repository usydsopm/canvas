#!/usr/bin/env python3
"""
Rebuilds PMSoc-Instagram.html from build/ig_posts.json + build/ig_profile.json
+ build/canvas_template_ig.html.

Run from the REPO ROOT:
    python3 build/build_canvas_html_ig.py

Output: PMSoc-Instagram.html at the repo root (what GitHub Pages serves).

The page shows a 3-column grid (3 pinned posts + the 6 most recent, mirroring
how Instagram's own profile grid orders pinned vs. chronological posts) next
to a detail panel that displays whichever post was last clicked, bigger, with
its full caption. Clicking a grid tile never navigates away (a plain click is
intercepted by canvas_template_ig.html's own script); middle-click/cmd-click
still opens the real Instagram post, and every action icon, the caption link,
and the Follow/Message buttons always link out to the real pmsoc.usyd profile
or post.

To add/update posts: edit build/ig_posts.json (see its "pinned" field below).
Keep exactly the pinned posts currently pinned on the real profile at the
front (mark them "pinned": true, in the order they appear on the real grid),
then the most recent non-pinned posts after them, newest first. Save each
post's photo as a base64 data URI text file under build/assets/ (see
README.md for the exact steps + how to fetch a photo from an authenticated
Instagram browser session).

To update the profile header (bio, follower/following/post counts, link),
edit build/ig_profile.json.
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))       # .../repo/build
REPO_ROOT = os.path.dirname(HERE)                         # .../repo
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
# reel "play" badge, the carousel "copy" badge, and the pinned-post "pin"
# badge used in the grid.
HEART_ICON = '<svg viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>'
COMMENT_ICON = '<svg viewBox="0 0 24 24"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>'
SEND_ICON = '<svg viewBox="0 0 24 24"><path d="M22 2L11 13"></path><path d="M22 2l-7 20-4-9-9-4 20-7z"></path></svg>'
BOOKMARK_ICON = '<svg viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>'
COPY_ICON = '<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'
PIN_ICON = '<svg viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>'

GRID_REEL_BADGE = '<svg class="ig-grid-badge" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"></path></svg>'
GRID_CAROUSEL_BADGE = COPY_ICON.replace(
    '<svg viewBox="0 0 24 24">',
    '<svg class="ig-grid-badge" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
)
GRID_PIN_BADGE = PIN_ICON.replace(
    '<svg viewBox="0 0 24 24">',
    '<svg class="ig-grid-pin" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
)

grid_item_tpl = """      <a class="ig-grid-item{active}" href="{url}" target="_blank" rel="noopener" data-url="{url}" data-kind="{kind}" data-date-iso="{date_iso}">
        <img src="{img}" alt="{alt}" loading="lazy">
        {pin_badge}{badge}
        <template>{caption_html}</template>
      </a>"""


def alt_text(caption, limit=80):
    caption = caption.strip().replace("\n", " ")
    return (caption[:limit] + "...") if len(caption) > limit else caption


def kind_label(p):
    # "carousel" posts are still a normal feed post (just multi-photo), so
    # they read as "post" in the "View ... on Instagram" link, same as a
    # single-photo post; only a reel reads as "reel".
    return "reel" if p.get("type") == "reel" else "post"


def grid_badge(p):
    t = p.get("type")
    if t == "reel":
        return GRID_REEL_BADGE
    if t == "carousel":
        return GRID_CAROUSEL_BADGE
    return ""


grid_html = "\n".join(
    grid_item_tpl.format(
        active=" active" if i == 0 else "",
        url=p["url"],
        img=asset(p["img_asset"]),
        alt=html.escape(alt_text(p.get("caption", "")), quote=True),
        kind=kind_label(p),
        date_iso=p["date_iso"],
        pin_badge=GRID_PIN_BADGE if p.get("pinned") else "",
        badge=grid_badge(p),
        caption_html=html.escape(p.get("caption", ""), quote=True),
    )
    for i, p in enumerate(posts)
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

out = template.replace("{{GRID}}", grid_html)
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
out = out.replace("{heart}", HEART_ICON)
out = out.replace("{comment}", COMMENT_ICON)
out = out.replace("{send}", SEND_ICON)
out = out.replace("{bookmark}", BOOKMARK_ICON)

out_path = os.path.join(REPO_ROOT, "PMSoc-Instagram.html")
with open(out_path, "w") as f:
    f.write(out)

print("done:", out_path, len(out), "bytes,", len(posts), "posts",
      "(", sum(1 for p in posts if p.get("pinned")), "pinned )")
