#!/usr/bin/env python3
"""
Rebuilds PMSoc-Instagram-Feed.html from build/ig_posts.json +
build/ig_profile.json + build/canvas_template_ig_feed.html.

Run from the REPO ROOT:
    python3 build/build_canvas_html_ig_feed.py

Output: PMSoc-Instagram-Feed.html at the repo root (what GitHub Pages
serves, embedded as its own Canvas iframe separate from PMSoc-Instagram.html).

This is the "scrollable feed" variant of the Instagram widget: the same
profile header + bio as the grid widget, then every post in
build/ig_posts.json rendered as a full-size card (photo/video, action
icons, date, full caption, "View on Instagram" link) stacked vertically
so the whole thing scrolls like a real Instagram feed — no 3x3 grid, no
side detail panel, and no pinned-post special-casing (pinning is a
grid-only concept on the real profile; this view is purely chronological,
newest first).

Shares its data source with the grid widget (build_canvas_html_ig.py /
PMSoc-Instagram.html) — edit build/ig_posts.json and build/ig_profile.json
the same way for both, then re-run both build scripts. See README.md's
"PMSoc Instagram Feed Widget" section for how to add/update posts.
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

# Feather Icons (MIT licensed) — same action-bar icons as the grid widget.
HEART_ICON = '<svg viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>'
COMMENT_ICON = '<svg viewBox="0 0 24 24"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>'
SEND_ICON = '<svg viewBox="0 0 24 24"><path d="M22 2L11 13"></path><path d="M22 2l-7 20-4-9-9-4 20-7z"></path></svg>'
BOOKMARK_ICON = '<svg viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>'


def kind_label(p):
    # Same rule as the grid widget: a carousel still reads as "post" in
    # the "View ... on Instagram" link, only a reel reads as "reel".
    return "reel" if p.get("type") == "reel" else "post"


def media_html(p):
    img_src = asset(p["img_asset"])
    alt = html.escape(p.get("caption", "").strip().replace("\n", " ")[:120], quote=True)
    if p.get("video_asset"):
        return '<video controls playsinline preload="metadata" poster="{poster}" src="{src}"></video>'.format(
            poster=img_src, src=asset(p["video_asset"])
        )
    return '<img src="{src}" alt="{alt}" loading="lazy">'.format(src=img_src, alt=alt)


post_card_tpl = """    <div class="ig-post">
      <div class="ig-post-header">
        <img class="ig-post-avatar" src="{logo}" alt="pmsoc.usyd avatar">
        <a class="ig-post-handle" href="{url}" target="_blank" rel="noopener">pmsoc.usyd</a>
      </div>
      <div class="ig-post-media">
        {media}
      </div>
      <div class="ig-post-actions">
        <a class="action" href="{url}" target="_blank" rel="noopener" aria-label="Like">{heart}</a>
        <a class="action" href="{url}" target="_blank" rel="noopener" aria-label="Comment">{comment}</a>
        <a class="action" href="{url}" target="_blank" rel="noopener" aria-label="Send">{send}</a>
        <span class="spacer"></span>
        <a class="action" href="{url}" target="_blank" rel="noopener" aria-label="Save">{bookmark}</a>
      </div>
      <div class="ig-post-date" data-iso="{date_iso}"></div>
      <div class="ig-post-caption-wrap">
        <p class="ig-post-caption"><span class="handle-inline">pmsoc.usyd</span>{caption_html}</p>
      </div>
      <a class="ig-post-link" href="{url}" target="_blank" rel="noopener">View {kind} on Instagram &#8599;</a>
    </div>"""

# Chronological, newest first — no pinned special-casing (see module docstring).
posts_by_date = sorted(posts, key=lambda p: p["date_iso"], reverse=True)

feed_html = "\n".join(
    post_card_tpl.format(
        logo=logo,
        url=p["url"],
        media=media_html(p),
        heart=HEART_ICON,
        comment=COMMENT_ICON,
        send=SEND_ICON,
        bookmark=BOOKMARK_ICON,
        date_iso=p["date_iso"],
        caption_html=html.escape(p.get("caption", ""), quote=True),
        kind=kind_label(p),
    )
    for p in posts_by_date
)

# Linkify the @mention in the bio, same as the grid widget.
bio_html = profile["bio"]
mention = profile.get("mention_handle")
if mention:
    bio_html = bio_html.replace(
        mention,
        '<a href="{}" target="_blank" rel="noopener">{}</a>'.format(profile.get("mention_url", "#"), mention),
    )

with open(os.path.join(HERE, "canvas_template_ig_feed.html")) as f:
    template = f.read()

out = template.replace("{{FEED}}", feed_html)
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

out_path = os.path.join(REPO_ROOT, "PMSoc-Instagram-Feed.html")
with open(out_path, "w") as f:
    f.write(out)

print("done:", out_path, len(out), "bytes,", len(posts_by_date), "posts")
