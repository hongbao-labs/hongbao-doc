# Hongbao Documentation Site

Starlight-powered documentation site for the Hongbao protocol. Source content lives in bilingual Markdown under `../CN/` and `../EN/`; the built site is served from `web/`.

## Prerequisites

- Node.js 20+
- npm 10+

## Local development

```bash
cd web
npm install
npm run dev
```

Open http://localhost:4321 — English at `/en/`, Chinese at `/zh/`.

## Project layout

```
web/
├── astro.config.mjs      # Starlight config (locales, sidebar, theme)
├── src/
│   ├── assets/           # Logo and static assets
│   ├── content/docs/
│   │   ├── en/           # English pages
│   │   └── zh/           # Chinese pages
│   └── styles/custom.css # Brand accent color (#D42020)
├── scripts/migrate.py    # One-shot migration from ../CN and ../EN
├── Dockerfile
└── docker-compose.yml
```

## Updating documentation

### Edit an existing page

1. Open the page under `src/content/docs/en/` or `src/content/docs/zh/`.
2. Edit the Markdown body below the frontmatter (`title`, `description`).
3. Keep both locales in sync when content changes.

Example frontmatter:

```yaml
---
title: Claim Guide
description: Step-by-step claim guide for Hongbao cardholders
draft: false
---
```

> `draft: false` is required for pages to appear in production builds.

### Add a new page

1. Create `src/content/docs/en/your-section/your-page.md` with frontmatter.
2. Mirror the file at `src/content/docs/zh/your-section/your-page.md`.
3. Register the page in `astro.config.mjs` under the correct sidebar group:

```js
{ slug: 'your-section/your-page' }
```

4. Use relative links without `.md` extensions, e.g. `[Guide](guide)` or `[Overview](../)`.

### Re-sync from legacy Markdown

If you edit the canonical copies in `../CN/` or `../EN/` first, re-run:

```bash
python3 scripts/migrate.py
```

This overwrites generated files under `src/content/docs/`. Review link transformations after a bulk re-sync.

## Docker

### Dev server (hot reload)

```bash
docker compose up dev
```

Visit http://localhost:4321

### Production build (nginx)

```bash
docker compose --profile production up --build web
```

Visit http://localhost:8080

## Build & preview (without Docker)

```bash
npm run build
npm run preview
```

Static output is written to `dist/`.

## Deployment notes

- Set `site` in `astro.config.mjs` to your production URL before release.
- The nginx image serves the `dist/` folder produced by `npm run build`.
- Pagefind search is included automatically in production builds.
