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


def _ensure_tor_installed():
    """Ensure the `tor` binary is present (required for anonymity)."""
    import shutil
    if shutil.which("tor"):
        return True
    print("[i] Tor not found. Installing (required for anonymity)...")
    try:
        if shutil.which("pkg"):
            subprocess.run(["pkg", "install", "-y", "tor"],
                           check=False)
        elif shutil.which("apt"):
            subprocess.run(["sudo", "apt", "install", "-y", "tor"],
                           check=False)
        else:
            print("[!] Please install Tor manually: pkg install tor  (or: sudo apt install tor)")
            return False
    except Exception as e:
        print(f"[!] Tor install failed: {e}")
        return False
    return shutil.which("tor") is not None


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
            _ensure_tor_installed()
            _ensure_python_socks()
            return True
        else:
            print(f"[!] Git pull failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"[!] Update failed: {e}")
        return False


def _ensure_python_socks():
    """Install python-socks into the venv if ribbons (Telethon proxy) needs it."""
    launcher_py = os.path.join(INSTALL_DIR, "venv", "bin", "python")
    if not os.path.exists(launcher_py):
        return
    try:
        subprocess.run(
            [launcher_py, "-m", "pip", "install", "python-socks", "telethon",
             "requests", "aiohttp"],
            capture_output=True, text=True, timeout=120)
    except Exception:
        pass


def _ensure_python_socks_system():
    """Install python-socks for the system python (.pyz launcher uses it)."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "python-socks"],
            capture_output=True, text=True, timeout=120)
    except Exception:
        pass


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
        _ensure_tor_installed()
        _ensure_python_socks_system()
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
