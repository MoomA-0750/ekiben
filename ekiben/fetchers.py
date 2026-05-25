from __future__ import annotations
import os
import re
from typing import Optional
import httpx


class SocialProfile:
    def __init__(self, username: str, display_name: str, bio: str, avatar_url: str, profile_url: str):
        self.username = username
        self.display_name = display_name
        self.bio = bio
        self.avatar_url = avatar_url
        self.profile_url = profile_url


def fetch_github_profile(username: str) -> SocialProfile:
    with httpx.Client(timeout=10) as client:
        r = client.get(
            f"https://api.github.com/users/{username}",
            headers={"Accept": "application/vnd.github+json"},
        )
        r.raise_for_status()
        data = r.json()
    return SocialProfile(
        username=data["login"],
        display_name=data.get("name") or data["login"],
        bio=data.get("bio") or "",
        avatar_url=data["avatar_url"],
        profile_url=data["html_url"],
    )


def fetch_x_profile(username: str) -> SocialProfile:
    token = os.environ.get("TWITTER_BEARER_TOKEN")
    if not token:
        raise EnvironmentError("TWITTER_BEARER_TOKEN is not set")
    clean = username.lstrip("@")
    with httpx.Client(timeout=10) as client:
        r = client.get(
            f"https://api.twitter.com/2/users/by/username/{clean}",
            params={"user.fields": "name,description,profile_image_url"},
            headers={"Authorization": f"Bearer {token}"},
        )
        r.raise_for_status()
        data = r.json()["data"]
    avatar = data.get("profile_image_url", "")
    # Use original size instead of _normal thumbnail
    avatar = avatar.replace("_normal.", "_400x400.")
    return SocialProfile(
        username=clean,
        display_name=data.get("name") or clean,
        bio=data.get("description") or "",
        avatar_url=avatar,
        profile_url=f"https://x.com/{clean}",
    )


def fetch_misskey_profile(username: str, instance: str) -> SocialProfile:
    clean_instance = instance.rstrip("/")
    with httpx.Client(timeout=10) as client:
        r = client.post(
            f"https://{clean_instance}/api/users/show",
            json={"username": username},
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
        data = r.json()
    avatar = data.get("avatarUrl") or ""
    return SocialProfile(
        username=username,
        display_name=data.get("name") or username,
        bio=_strip_misskey_mfm(data.get("description") or ""),
        avatar_url=avatar,
        profile_url=f"https://{clean_instance}/@{username}",
    )


def _strip_misskey_mfm(text: str) -> str:
    # Remove MFM syntax tags like $[xxx ...]
    text = re.sub(r"\$\[[\w.]+ ([^\]]+)\]", r"\1", text)
    return text


def fetch_ogp_image(url: str) -> Optional[str]:
    try:
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            r = client.get(url, headers={"User-Agent": "ekiben/0.1 (OGP fetcher)"})
            r.raise_for_status()
            html = r.text
        match = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](.*?)["\']', html)
        if not match:
            match = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:image["\']', html)
        return match.group(1) if match else None
    except Exception:
        return None
