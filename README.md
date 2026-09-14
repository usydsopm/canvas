# PMSoc LinkedIn Feed Widget

A static HTML page that mimics a LinkedIn company feed for the Sydney
University Project Management Society (PMSoc), styled to the SoPM x PMSoc
BBQ flyer palette. Built as a static snapshot (not a live LinkedIn embed) so
it can be embedded via `<iframe>` in Canvas (Instructure) without CSP/framing
issues.

- **Live file:** `PMSoc-LinkedIn.html` (repo root) — this is what GitHub
  Pages serves and what Canvas iframes point at.
- **Pages URL:** `https://usydsopm.github.io/canvas/PMSoc-LinkedIn.html`
  (once GitHub Pages is enabled on this repo — see below).

## Repo layout

```
PMSoc-LinkedIn.html      <- generated output, do not hand-edit
build/
  posts.json             <- the 5 posts shown, newest first
  canvas_template.html   <- page shell/CSS/JS (hand-edit this for style changes)
  build_canvas_html.py   <- reads posts.json + template -> writes PMSoc-LinkedIn.html
  assets/                <- base64 data-URI text files (post photos, logos, font)
```

## How dates work

Each post in `posts.json` has a real `date_iso` (e.g. `"2026-09-05"`), not a
frozen "2 days ago" string. The page computes "X days/months/years ago" in
JavaScript every time it's opened, so it never goes stale — you only need to
rebuild when the actual list of posts changes, not on a schedule for dates
alone.

## Adding a new post (manual or automated)

1. Grab the new post's permalink URL, headline/caption text, and photo from
   PMSoc's LinkedIn company page
   (https://www.linkedin.com/company/sydney-university-project-management-society/) —
   only ever use posts marked public ("Visible to anyone on or off LinkedIn").
2. Save the photo as a base64 data URI text file under `build/assets/`
   (resize to ~480px wide, JPEG quality ~78, to keep the page small — a data
   URI string starting `data:image/jpeg;base64,...`, no line breaks).
3. Add a new object to the **front** of the array in `build/posts.json`:
   ```json
   {
     "date_iso": "YYYY-MM-DD",
     "title": "...",
     "text": "...",
     "img_asset": "postN_datauri.txt",
     "url": "https://www.linkedin.com/feed/update/urn:li:activity:.../"
   }
   ```
4. Drop the oldest post off the end of the list if there are now more than 5,
   and delete its now-unused asset file from `build/assets/`.
5. From the repo root, run:
   ```
   python3 build/build_canvas_html.py
   ```
6. Commit and push `PMSoc-LinkedIn.html`, `build/posts.json`, and any new/removed
   files under `build/assets/`.

## GitHub Pages setup (one-time, manual)

GitHub Pages can't be turned on via this repo's automation token (it doesn't
have the `pages` permission). A repo admin needs to enable it once:
Settings → Pages → Build and deployment → Source: "Deploy from a branch" →
Branch: `main` / `(root)` → Save. After that, every push to `main` updates
the live Pages URL automatically — no further manual steps.

## Embedding in Canvas

In the Canvas Rich Content Editor, switch to the HTML view and add:
```html
<iframe src="https://usydsopm.github.io/canvas/PMSoc-LinkedIn.html"
        style="width:100%;height:1400px;border:0;"></iframe>
```
Adjust `height` to taste. Check with USYD's Canvas/LMS admin team first that
custom iframe embeds from github.io are permitted (some Canvas instances
restrict embeddable domains to an allowlist).


---

# PMSoc Instagram Feed Widget

A static HTML page that mimics an Instagram feed for the Sydney University
Project Management Society (PMSoc), styled to match the SoPM x PMSoc BBQ
flyer palette used by the LinkedIn widget above. Built as a static snapshot
(not a live Instagram embed) so it can be embedded via `<iframe>` in Canvas
(Instructure) without CSP/framing issues.

- **Live file:** `PMSoc-Instagram.html` (repo root) — this is what GitHub
  Pages serves and what Canvas iframes point at.
- **Pages URL:** `https://usydsopm.github.io/canvas/PMSoc-Instagram.html`
  (once GitHub Pages is enabled on this repo — see the GitHub Pages section
  above; the same one-time setup covers both widgets).

## Repo layout

```
PMSoc-Instagram.html        <- generated output, do not hand-edit
build/
  ig_posts.json             <- the up-to-5 posts shown, newest first
  canvas_template_ig.html   <- page shell/CSS/JS (hand-edit this for style changes)
  build_canvas_html_ig.py   <- reads ig_posts.json + template -> writes PMSoc-Instagram.html
  assets/                   <- base64 data-URI text files (post photos; reuses
                                logo_datauri.txt and fraunces_b64.txt from the
                                LinkedIn widget's asset set)
```

## How dates work

Same approach as the LinkedIn widget: each post in `ig_posts.json` has a real
`date_iso` (e.g. `"2026-09-05"`), and the page computes "X days/months/years
ago" in JavaScript every time it's opened, so it never goes stale.

## Adding a new post (manual or automated)

1. Grab the new post's permalink URL (`instagram.com/p/<shortcode>/` for a
   normal post or `instagram.com/reel/<shortcode>/` for a reel), its caption
   text, and its main photo from PMSoc's Instagram profile
   (https://www.instagram.com/pmsoc.usyd/) — use judgment on what counts as a
   normal public grid post/reel: skip Story/Highlight-only content, anything
   that looks private or restricted, and reposts that add no original PMSoc
   content.
2. Use Instagram's own displayed date where possible (it usually shows the
   exact date on hover/title over a relative "X weeks ago" string) rather
   than estimating from the relative string alone.
3. Save the photo as a base64 data URI text file under `build/assets/`
   (resize to ~480px wide, JPEG quality ~78, to keep the page small — a data
   URI string starting `data:image/jpeg;base64,...`, no line breaks).
4. Add a new object to the **front** of the array in `build/ig_posts.json`:
   ```json
   {
     "date_iso": "YYYY-MM-DD",
     "caption": "...",
     "img_asset": "postN_ig_datauri.txt",
     "url": "https://www.instagram.com/p/.../",
     "type": "post"
   }
   ```
   Use `"type": "reel"` for a reel (adds a small "REEL" badge on the
   thumbnail); omit or set `"post"` otherwise.
5. Drop the oldest post off the end of the list if there are now more than 5,
   and delete its now-unused asset file from `build/assets/`.
6. From the repo root, run:
   ```
   python3 build/build_canvas_html_ig.py
   ```
7. Commit and push `PMSoc-Instagram.html`, `build/ig_posts.json`, and any
   new/removed files under `build/assets/`.

## Embedding in Canvas

In the Canvas Rich Content Editor, switch to the HTML view and add:
```html
<iframe src="https://usydsopm.github.io/canvas/PMSoc-Instagram.html"
        style="width:100%;height:1400px;border:0;"></iframe>
```
Adjust `height` to taste. Check with USYD's Canvas/LMS admin team first that
custom iframe embeds from github.io are permitted (some Canvas instances
restrict embeddable domains to an allowlist).
