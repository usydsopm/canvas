#!/usr/bin/env python3
"""
Rebuilds PMSoc-LinkedIn.html from build/posts.json + build/canvas_template.html.

Run from the REPO ROOT:
    python3 build/build_canvas_html.py

Output: PMSoc-LinkedIn.html at the repo root (what GitHub Pages serves).

To add a new post: add a new object to the FRONT of the list in
build/posts.json (newest first) with date_iso / title / text / url, and
save its post image as a base64 data URI text file under build/assets/
(see README.md in the repo root for the exact steps + how to fetch a
photo from an authenticated LinkedIn browser session). Keep at most ~5-6
posts in posts.json so the page doesn't grow unbounded — drop the oldest
one off the end when adding a new one.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))       # .../repo/build
REPO_ROOT = os.path.dirname(HERE)                        # .../repo
ASSETS_DIR = os.path.join(HERE, "assets")


def asset(name):
    with open(os.path.join(ASSETS_DIR, name)) as f:
        return f.read().strip()


with open(os.path.join(HERE, "posts.json")) as f:
    posts = json.load(f)

logo = asset("logo_datauri.txt")
li_logo = asset("li_logo_datauri.txt")
fraunces_font = asset("fraunces_b64.txt")

# Feather Icons (MIT licensed) — simple line icons for the globe + action bar
GLOBE_ICON = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>'
LIKE_ICON = '<svg viewBox="0 0 24 24"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"></path><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>'
COMMENT_ICON = '<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>'
REPOST_ICON = '<svg viewBox="0 0 24 24"><path d="M17 1l4 4-4 4"></path><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><path d="M7 23l-4-4 4-4"></path><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>'
SEND_ICON = '<svg viewBox="0 0 24 24"><path d="M22 2L11 13"></path><path d="M22 2l-7 20-4-9-9-4 20-7z"></path></svg>'

card_tpl = """
    <div class="feed-item">
      <div class="feed-item-body">
        <div class="feed-item-text">
          <div class="feed-item-head">
            <img class="feed-item-logo" src="{logo}" alt="PMSoc logo">
            <div class="feed-item-headtext">
              <div class="feed-item-date">{globe} <span class="date-text" data-iso="{date_iso}"></span></div>
              <h3>{title}</h3>
            </div>
          </div>
          <p>{text}</p>
          <a class="feed-item-link" href="{url}" target="_blank" rel="noopener">View post on LinkedIn &#8599;</a>
        </div>
        <div class="feed-item-photo">
          <img src="{img}" alt="{title}" loading="lazy">
        </div>
      </div>
      <div class="feed-item-actions">
        <a class="action" href="{url}" target="_blank" rel="noopener">{like} Like</a>
        <a class="action" href="{url}" target="_blank" rel="noopener">{comment} Comment</a>
        <a class="action" href="{url}" target="_blank" rel="noopener">{repost} Repost</a>
        <a class="action" href="{url}" target="_blank" rel="noopener">{send} Send</a>
      </div>
    </div>"""

cards_html = "\n".join(
    card_tpl.format(
        date_iso=p["date_iso"], title=p["title"], text=p["text"], url=p["url"],
        img=asset(p["img_asset"]), logo=logo,
        globe=GLOBE_ICON, like=LIKE_ICON, comment=COMMENT_ICON, repost=REPOST_ICON, send=SEND_ICON,
    )
    for p in posts
)

with open(os.path.join(HERE, "canvas_template.html")) as f:
    template = f.read()

out = template.replace("{{CARDS}}", cards_html)
out = out.replace("{li_logo}", li_logo)
out = out.replace("{fraunces_font}", fraunces_font)

out_path = os.path.join(REPO_ROOT, "PMSoc-LinkedIn.html")
with open(out_path, "w") as f:
    f.write(out)

print("done:", out_path, len(out), "bytes,", len(posts), "posts")
