# ekiben

bento.me-like personal profile page static site generator.

Define your layout in YAML, run one command, get a deployable HTML page.

[日本語版 README はこちら](README.ja.md)

## Installation

```bash
pip install ekiben
```

## Quick start

```bash
mkdir my-site && cd my-site
ekiben init
# Edit site.yaml and place images in assets/
ekiben serve       # preview at http://localhost:8080 with live reload
ekiben build       # output to dist/
```

## site.yaml

```yaml
profile:
  name: "Your Name"
  avatar: "./assets/avatar.png"  # optional
  bio: "Engineer / Tokyo"        # optional

theme:
  background: "#f5f5f0"
  card_background: "#ffffff"
  accent: "#3b82f6"
  font_family: "system-ui, sans-serif"
  border_radius: 16
  card_shadow: true

blocks:
  - type: text
    size: 2x1
    content: "👋 Hi, I'm Your Name"

  - type: link
    size: 1x1
    title: "My Blog"
    url: "https://example.com"
    # image: "./assets/blog.png"  # optional; falls back to OGP

  - type: social
    size: 1x1
    platform: github
    username: "your-username"

  - type: social
    size: 1x1
    platform: x
    username: "your-handle"

  - type: social
    size: 1x1
    platform: misskey
    username: "your-username"
    instance: "misskey.io"

  - type: spacer
    size: 1x1
```

### Block types

| Type | Description |
|------|-------------|
| `text` | Text card for headings, bio, freeform copy |
| `link` | Clickable card with title and image (OGP auto-fetched if no image specified). Supports GIF. |
| `social` | Profile card fetched from X, GitHub, or Misskey at build time |
| `spacer` | Empty grid cell for layout gaps |

### Sizes

`1x1` · `2x1` · `1x2` · `2x2` — width × height in grid units.

Grid is 4 columns on desktop, 2 columns on mobile. Blocks fill left-to-right, top-to-bottom.

### Per-card color

Any block (except `spacer`) accepts an optional `color` field to override the card background:

```yaml
- type: text
  size: 1x1
  color: "#fef3c7"
  content: "Highlighted card"
```

## Social platforms

| Platform | Auth required |
|----------|---------------|
| GitHub | None (public API) |
| X | `TWITTER_BEARER_TOKEN` environment variable |
| Misskey | None (requires `instance:` field in YAML) |

## Deploy to GitHub Pages

The easiest way is to use **[ekiben-template](https://github.com/MoomA-0750/ekiben-template)** — a ready-made repository template that handles the GitHub Actions workflow for you. No local ekiben installation needed.

### Using ekiben-template (recommended)

**One-time setup:**

1. Open [ekiben-template](https://github.com/MoomA-0750/ekiben-template) and click **"Use this template" → "Create a new repository"**
2. Clone your new repository:
   ```bash
   git clone git@github.com:<your-username>/<your-repo>.git
   cd <your-repo>
   ```
3. Enable GitHub Pages: **Settings → Pages → Source → GitHub Actions**
4. *(X blocks only)* Add `TWITTER_BEARER_TOKEN` to **Settings → Secrets and variables → Actions**

**Everyday workflow:**

```bash
# Edit site.yaml or add images to assets/
git add .
git commit -m "Update profile"
git push
# GitHub Actions rebuilds and redeploys automatically
```

Your site is live at `https://<your-username>.github.io/<your-repo>/`.

---

### Manual setup (without the template)

If you prefer to set things up from scratch:

**Step 1 — Create your site repository**

Create a new repository on GitHub (e.g. `my-profile`), then:

```bash
mkdir my-profile && cd my-profile
ekiben init --with-actions
# Edit site.yaml and place images in assets/
git init -b main
git add .
git commit -m "Initial site"
git remote add origin git@github.com:<your-username>/my-profile.git
git push -u origin main
```

**Step 2 — Enable GitHub Pages**

1. Open your repository on GitHub
2. Go to **Settings → Pages**
3. Under **Source**, select **GitHub Actions**

**Step 3 — Add secrets (X blocks only)**

1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `TWITTER_BEARER_TOKEN` / Value: your Bearer Token from the [X Developer Portal](https://developer.twitter.com/)

## CLI reference

```
ekiben init [--with-actions]            Generate site.yaml template (and GitHub Actions workflow)
ekiben build [--input .] [--output dist]   Build site into output directory
ekiben serve [--input .] [--port 8080]     Build and serve locally with live reload
```
