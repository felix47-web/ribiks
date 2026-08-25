import json
import os
import subprocess
import sys
import urllib.request

from . import __version__
from .config import GITHUB_REPO

API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
INSTALL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_local_version():
    return __version__


def get_remote_version():
    try:
        req = urllib.request.Request(API_URL)
        req.add_header("Accept", "application/vnd.github.v3+json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            tag = data.get("tag_name", "")
            return tag.lstrip("v"), data
    except Exception as e:
        print(f"[!] Failed to check for updates: {e}")
        return None, None


def version_tuple(v):
    try:
        return tuple(int(x) for x in v.split("."))
    except (ValueError, AttributeError):
        return (0,)


def is_newer(remote, local):
    return version_tuple(remote) > version_tuple(local)


def detect_install_type():
    git_dir = os.path.join(INSTALL_DIR, ".git")
    if os.path.isdir(git_dir):
        return "git"

    launcher = os.path.join(os.path.expanduser("~"), ".ribiks", "ribiks.pyz")
    if os.path.exists(launcher):
        return "pyz"

    return "unknown"


def update_git():
    print("[*] Updating via git pull...")
    try:
        result = subprocess.run(
            ["git", "pull"],
            cwd=INSTALL_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print(f"[+] Updated successfully!")
            if result.stdout.strip():
                print(f"    {result.stdout.strip()}")
            return True
        else:
            print(f"[!] Git pull failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"[!] Update failed: {e}")
        return False


def update_pyz(remote_data):
    print("[*] Downloading latest .pyz...")

    assets = remote_data.get("assets", [])
    pyz_asset = None
    for asset in assets:
        if asset["name"].endswith(".pyz"):
            pyz_asset = asset
            break

    if not pyz_asset:
        print("[!] No .pyz asset found in release")
        return False

    download_url = pyz_asset["browser_download_url"]
    pyz_dir = os.path.join(os.path.expanduser("~"), ".ribiks")
    pyz_path = os.path.join(pyz_dir, "ribiks.pyz")

    try:
        req = urllib.request.Request(download_url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()

        os.makedirs(pyz_dir, exist_ok=True)
        with open(pyz_path, "wb") as f:
            f.write(b"#!/usr/bin/env python3\n" + data)
        os.chmod(pyz_path, 0o755)

        print("[+] Updated successfully!")
        return True
    except Exception as e:
        print(f"[!] Download failed: {e}")
        return False


def check_for_updates(silent=False):
    local = get_local_version()
    remote, remote_data = get_remote_version()

    if remote is None:
        if not silent:
            print("[!] Could not reach GitHub. Check your internet connection.")
        return False

    if not is_newer(remote, local):
        if not silent:
            print(f"[i] Already up to date (v{local})")
        return False

    if not silent:
        print(f"[i] New version available: v{remote} (current: v{local})")
    return True


def do_update():
    local = get_local_version()
    remote, remote_data = get_remote_version()

    if remote is None:
        print("[!] Could not reach GitHub. Check your internet connection.")
        return False

    if not is_newer(remote, local):
        print(f"[i] Already up to date (v{local})")
        return False

    print(f"[i] Updating: v{local} -> v{remote}")

    install_type = detect_install_type()

    if install_type == "git":
        success = update_git()
    elif install_type == "pyz":
        success = update_pyz(remote_data)
    else:
        print("[!] Unknown installation type.")
        print("[i] Reinstall manually:")
        print(f"    curl -fsSL https://raw.githubusercontent.com/{GITHUB_REPO}/main/install_ribiks.sh | bash")
        return False

    if success:
        print(f"\n[+] Ribiks updated to v{remote}")

    return success
