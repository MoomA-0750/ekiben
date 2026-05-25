# ekiben

bento.me-like personal profile page static site generator.

Define your layout in YAML, run one command, get a deployable HTML page.

## Installation

```bash
pip install ekiben
```

## Quick start

```bash
mkdir my-site && cd my-site
ekiben init
# Edit site.yaml and assets/
ekiben serve       # preview at http://localhost:8080 with live reload
ekiben build       # output to dist/
```

## site.yaml

```yaml
profile:
  name: "Your Name"
  avatar: "./assets/avatar.png"
  bio: "Engineer / Tokyo"

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

| Platform | Auth |
|----------|------|
| GitHub | None (public API) |
| X | `TWITTER_BEARER_TOKEN` env var |
| Misskey | None (requires `instance:` field in YAML) |

## GitHub Actions

```bash
ekiben init --with-actions
```

Generates `.github/workflows/deploy.yml` for GitHub Pages deployment. Add `TWITTER_BEARER_TOKEN` to your repository secrets if you use X blocks.

## CLI reference

```
ekiben init [--with-actions]       Generate site.yaml template
ekiben build [--input .] [--output dist]
ekiben serve [--input .] [--port 8080]
```
