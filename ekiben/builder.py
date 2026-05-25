from __future__ import annotations
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx
import yaml
from jinja2 import Environment, PackageLoader, select_autoescape
from markupsafe import Markup
from pydantic import ValidationError

from .fetchers import (
    SocialProfile,
    fetch_github_profile,
    fetch_misskey_profile,
    fetch_ogp_image,
    fetch_x_profile,
)
from .models import (
    Block,
    LinkBlock,
    SiteConfig,
    SocialBlock,
    SpacerBlock,
    TextBlock,
)


@dataclass
class RenderedLink:
    type: str = "link"
    size: str = "1x1"
    color: Optional[str] = None
    title: str = ""
    url: str = ""
    resolved_image: Optional[str] = None


@dataclass
class RenderedText:
    type: str = "text"
    size: str = "1x1"
    color: Optional[str] = None
    content: str = ""


@dataclass
class RenderedSocial:
    type: str = "social"
    size: str = "1x1"
    color: Optional[str] = None
    platform: str = ""
    profile: SocialProfile = field(default_factory=lambda: SocialProfile("", "", "", "", ""))


@dataclass
class RenderedSpacer:
    type: str = "spacer"
    size: str = "1x1"


PLATFORM_ICONS = {
    "github": """<svg class="social-platform-badge" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
    </svg>""",
    "x": """<svg class="social-platform-badge" viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.737-8.835L1.254 2.25H8.08l4.213 5.567L18.244 2.25zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77z"/>
    </svg>""",
    "misskey": """<svg class="social-platform-badge" viewBox="0 0 24 24" fill="currentColor">
      <path d="M22.197 0H16.65l-4.65 8.05L7.35 0H1.803L0 2.743v18.514L1.803 24h4.544l1.803-2.743V9.993l4.5 7.793 4.5-7.793v11.264L18.953 24h4.544L25.3 21.257V2.743L22.197 0z" transform="scale(0.96)"/>
    </svg>""",
}


def _platform_icon(platform: str) -> Markup:
    return Markup(PLATFORM_ICONS.get(platform, ""))


def load_config(site_yaml: Path) -> SiteConfig:
    raw = yaml.safe_load(site_yaml.read_text(encoding="utf-8"))
    try:
        return SiteConfig.model_validate(raw)
    except ValidationError as e:
        raise SystemExit(f"site.yaml validation error:\n{e}") from e


def _resolve_image_path(image: str, source_dir: Path, assets_dir: Path) -> Optional[str]:
    """Copy a local image to assets and return the relative path, or return URL as-is."""
    if image.startswith("http://") or image.startswith("https://"):
        return image
    src = source_dir / image
    if src.exists():
        dest = assets_dir / src.name
        shutil.copy2(src, dest)
        return f"assets/{src.name}"
    return None


def _download_remote_image(url: str, assets_dir: Path, stem: str) -> Optional[str]:
    try:
        ext = Path(urlparse(url).path).suffix or ".jpg"
        filename = f"{stem}{ext}"
        dest = assets_dir / filename
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            r = client.get(url, headers={"User-Agent": "ekiben/0.1"})
            r.raise_for_status()
            dest.write_bytes(r.content)
        return f"assets/{filename}"
    except Exception:
        return None


def build(source_dir: Path, output_dir: Path) -> None:
    site_yaml = source_dir / "site.yaml"
    if not site_yaml.exists():
        raise SystemExit(f"site.yaml not found in {source_dir}")

    config = load_config(site_yaml)

    output_dir.mkdir(parents=True, exist_ok=True)
    assets_out = output_dir / "assets"
    assets_out.mkdir(exist_ok=True)

    # Copy local assets folder if exists
    local_assets = source_dir / "assets"
    if local_assets.exists():
        for f in local_assets.iterdir():
            if f.is_file():
                shutil.copy2(f, assets_out / f.name)

    # Resolve profile avatar
    resolved_avatar: Optional[str] = None
    if config.profile.avatar:
        resolved_avatar = _resolve_image_path(config.profile.avatar, source_dir, assets_out)

    # Render blocks
    rendered_blocks = []
    for i, block in enumerate(config.blocks):
        if isinstance(block, SpacerBlock):
            rendered_blocks.append(RenderedSpacer(size=block.size))

        elif isinstance(block, TextBlock):
            rendered_blocks.append(RenderedText(
                size=block.size,
                color=block.color,
                content=block.content,
            ))

        elif isinstance(block, LinkBlock):
            resolved_image: Optional[str] = None
            if block.image:
                resolved_image = _resolve_image_path(block.image, source_dir, assets_out)
            else:
                ogp_url = fetch_ogp_image(block.url)
                if ogp_url:
                    resolved_image = _download_remote_image(ogp_url, assets_out, f"ogp_{i}")
            rendered_blocks.append(RenderedLink(
                size=block.size,
                color=block.color,
                title=block.title,
                url=block.url,
                resolved_image=resolved_image,
            ))

        elif isinstance(block, SocialBlock):
            print(f"  Fetching {block.platform} profile for @{block.username}...")
            try:
                if block.platform == "github":
                    profile = fetch_github_profile(block.username)
                elif block.platform == "x":
                    profile = fetch_x_profile(block.username)
                elif block.platform == "misskey":
                    if not block.instance:
                        raise ValueError("misskey block requires 'instance' field")
                    profile = fetch_misskey_profile(block.username, block.instance)
                else:
                    raise ValueError(f"Unknown platform: {block.platform}")

                # Download avatar
                if profile.avatar_url:
                    local_avatar = _download_remote_image(
                        profile.avatar_url, assets_out, f"social_{block.platform}_{block.username}"
                    )
                    if local_avatar:
                        profile.avatar_url = local_avatar

                rendered_blocks.append(RenderedSocial(
                    size=block.size,
                    color=block.color,
                    platform=block.platform,
                    profile=profile,
                ))
            except Exception as e:
                print(f"  Warning: failed to fetch {block.platform} profile: {e}")
                rendered_blocks.append(RenderedSpacer(size=block.size))

    # Render HTML
    env = Environment(
        loader=PackageLoader("ekiben", "templates"),
        autoescape=select_autoescape(["html"]),
    )
    env.globals["platform_icon"] = _platform_icon

    profile_data = dict(config.profile)
    if resolved_avatar:
        profile_data["avatar"] = resolved_avatar

    template = env.get_template("index.html.jinja")
    html = template.render(
        profile=type("P", (), profile_data)(),
        theme=config.theme,
        rendered_blocks=rendered_blocks,
    )

    (output_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"  Built → {output_dir / 'index.html'}")
