from __future__ import annotations
from pathlib import Path

import click
from dotenv import load_dotenv

load_dotenv()

SITE_YAML_TEMPLATE = """\
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

  - type: social
    size: 1x1
    platform: github
    username: "your-github-username"

  # - type: social
  #   size: 1x1
  #   platform: x
  #   username: "your-x-handle"

  # - type: social
  #   size: 1x1
  #   platform: misskey
  #   username: "your-username"
  #   instance: "misskey.io"

  # - type: spacer
  #   size: 1x1
"""

GITHUB_ACTIONS_TEMPLATE = """\
name: Deploy ekiben site

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ekiben
      - run: ekiben build
        env:
          TWITTER_BEARER_TOKEN: ${{ secrets.TWITTER_BEARER_TOKEN }}
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist
      - uses: actions/deploy-pages@v4
"""


@click.group()
def cli() -> None:
    """ekiben — personal profile page generator."""


@cli.command()
@click.option("--with-actions", is_flag=True, help="Also generate GitHub Actions workflow.")
def init(with_actions: bool) -> None:
    """Generate a site.yaml template in the current directory."""
    site_yaml = Path("site.yaml")
    if site_yaml.exists():
        click.echo("site.yaml already exists. Skipping.")
    else:
        site_yaml.write_text(SITE_YAML_TEMPLATE, encoding="utf-8")
        click.echo("Created site.yaml")

    Path("assets").mkdir(exist_ok=True)
    click.echo("Created assets/")

    if with_actions:
        wf_dir = Path(".github/workflows")
        wf_dir.mkdir(parents=True, exist_ok=True)
        wf_file = wf_dir / "deploy.yml"
        if wf_file.exists():
            click.echo("deploy.yml already exists. Skipping.")
        else:
            wf_file.write_text(GITHUB_ACTIONS_TEMPLATE, encoding="utf-8")
            click.echo(f"Created {wf_file}")


@cli.command()
@click.option("--input", "input_dir", default=".", show_default=True,
              help="Directory containing site.yaml and assets/.")
@click.option("--output", "output_dir", default="dist", show_default=True,
              help="Output directory.")
def build(input_dir: str, output_dir: str) -> None:
    """Build the site into the output directory."""
    from .builder import build as _build
    click.echo("Building...")
    _build(Path(input_dir), Path(output_dir))
    click.echo("Done.")


@cli.command()
@click.option("--input", "input_dir", default=".", show_default=True,
              help="Directory containing site.yaml and assets/.")
@click.option("--port", default=8080, show_default=True, help="Port to serve on.")
def serve(input_dir: str, port: int) -> None:
    """Build and serve the site locally with live reload."""
    import http.server
    import io
    import json
    import threading
    import time
    from functools import partial
    from .builder import build as _build

    source = Path(input_dir).resolve()
    output_dir = source / ".ekiben_preview"

    state = {"version": 0}
    state_lock = threading.Lock()

    RELOAD_SCRIPT = (
        b"<script>(function(){"
        b"var v=null;"
        b"setInterval(function(){"
        b"fetch('/_ekiben_reload').then(r=>r.json()).then(function(d){"
        b"if(v===null){v=d.v;return;}"
        b"if(d.v!==v){location.reload();}"
        b"}).catch(function(){});"
        b"},1000);"
        b"})();</script>"
    )

    def _do_build() -> bool:
        try:
            _build(source, output_dir)
            with state_lock:
                state["version"] += 1
            return True
        except Exception as e:
            click.echo(f"  Build error: {e}")
            return False

    def _watched_mtimes() -> dict:
        mtimes: dict = {}
        f = source / "site.yaml"
        if f.exists():
            mtimes[str(f)] = f.stat().st_mtime
        assets = source / "assets"
        if assets.exists():
            for p in assets.iterdir():
                if p.is_file():
                    mtimes[str(p)] = p.stat().st_mtime
        return mtimes

    def _watcher() -> None:
        last = _watched_mtimes()
        while True:
            time.sleep(1)
            current = _watched_mtimes()
            if current != last:
                last = current
                click.echo("Change detected, rebuilding...")
                if _do_build():
                    click.echo("  Rebuilt.")

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(output_dir), **kwargs)

        def do_GET(self) -> None:
            if self.path == "/_ekiben_reload":
                with state_lock:
                    v = state["version"]
                body = json.dumps({"v": v}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            if self.path in ("/", "/index.html"):
                html_path = output_dir / "index.html"
                if html_path.exists():
                    content = html_path.read_bytes().replace(b"</body>", RELOAD_SCRIPT + b"</body>")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return

            super().do_GET()

        def log_message(self, *args) -> None:
            pass

    click.echo("Building...")
    _do_build()
    click.echo(f"Serving at http://localhost:{port}  (Ctrl+C to stop)")

    t = threading.Thread(target=_watcher, daemon=True)
    t.start()

    with http.server.HTTPServer(("", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            click.echo("\nStopped.")
