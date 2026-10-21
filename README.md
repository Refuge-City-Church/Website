# Refuge City Church website (preview)

Plain static site: HTML + one CSS file, no build step, no backend, no payment code.
Mobile first (designed at 390px wide). Every page is marked `noindex` until launch.

Yellow `[PLACEHOLDER]`, `[NEEDED FROM CHURCH]`, `[TBD]` and `[CONFIRM]` tags mark anything not yet confirmed by the church.
See `../placeholders.md` for the full list.

## Pages

| URL | File |
| --- | --- |
| `/` | `index.html` |
| `/visit/` | `visit/index.html` (form is a preview only, it does not submit) |
| `/give/` | `give/index.html` (giving link is a placeholder) |
| `/watch/` | `watch/index.html` (coming soon) |
| `/next-steps/` | `next-steps/index.html` |
| `/kids/` | `kids/index.html` |
| `/members/` | `members/index.html` |
| `/about/` | `about/index.html` |
| `/privacy/` | `privacy/index.html` |
| 404 | `404.html` |

Shared styles: `assets/css/site.css`. Logo: `assets/img/logo.png`.
The header, footer and menu are repeated on every page, so update them on all pages together.

## Run locally

```
cd site
python3 -m http.server 8080
# open http://localhost:8080
```

Links are root relative (`/visit/`), so serve from this folder instead of opening files directly.

## Deploy to Cloudflare Pages later (not done yet)

1. Push this folder to the church's GitHub repo (`refugecity-site`).
2. In the church's Cloudflare account: Workers & Pages > Create > Pages > Connect to Git, pick the repo.
3. Build settings: Framework preset "None", build command empty, output directory `/` (or `site` if the repo root is one level up).
4. Each pull request gets its own preview URL. Merge to `main` to publish.
5. Custom domain (refugecity.cc) only after the pastor says go. Follow the cutover steps in `build-plan.md`, and keep the Google email (MX) records exactly as they are.

## Editing later

`.pages.yml` is a starter config for Pages CMS (pagescms.org). It is not connected.
Weekly things (events, groups, giving, signups) stay in Planning Center and get linked from the site.

## Rules for this site

- No TikTok links.
- No payment code. Give buttons only link out to the church's giving tool.
- The site never stores form data. Forms link to or embed Planning Center forms.
- No em or en dashes in copy.
