#!/usr/bin/env python3

import os
import sys
import subprocess
import py_compile
import zipfile
import json
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "ribiks")
BUILD_DIR = os.path.expanduser("~/.ribiks_build")
TOKEN_FILE = os.path.expanduser("~/.github_token")
REPO = "felix47-web/ribiks"


def load_token():
    if not os.path.exists(TOKEN_FILE):
        print("[!] No GitHub token found at ~/.github_token")
        print("[i] Run: echo 'ghp_YOUR_TOKEN' > ~/.github_token")
        sys.exit(1)
    with open(TOKEN_FILE) as f:
        return f.read().strip()


def recompile():
    print("[*] Recompiling source...")
    os.makedirs(BUILD_DIR, exist_ok=True)
    count = 0
    for f in os.listdir(SRC_DIR):
        if not f.endswith(".py"):
            continue
        src_path = os.path.join(SRC_DIR, f)
        dst_path = os.path.join(BUILD_DIR, f.replace(".py", ".pyc"))
        py_compile.compile(src_path, dst_path, src_path)
        count += 1
    print(f"    Compiled {count} files")


def build_pyz(version):
    print(f"[*] Building ribiks-{version}.pyz...")
    pyz_path = os.path.join(BASE_DIR, f"ribiks-{version}.pyz")

    with zipfile.ZipFile(pyz_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in os.listdir(BUILD_DIR):
            if f.endswith(".pyc"):
                with open(os.path.join(BUILD_DIR, f), "rb") as pf:
                    data = pf.read()
                zf.writestr(f"ribiks/{f}", data)

        # Create __main__.py
        main_py = os.path.join(BUILD_DIR, "__main__.py")
        with open(main_py, "w") as mf:
            mf.write("from ribiks.cli import main\nmain()\n")
        main_pyc = os.path.join(BUILD_DIR, "__main__.pyc")
        py_compile.compile(main_py, main_pyc, main_py)
        with open(main_pyc, "rb") as pf:
            data = pf.read()
        zf.writestr("__main__.pyc", data)

    # Add shebang
    with open(pyz_path, "rb") as f:
        content = f.read()
    with open(pyz_path, "wb") as f:
        f.write(b"#!/usr/bin/env python3\n" + content)

    os.chmod(pyz_path, 0o755)
    size = os.path.getsize(pyz_path)
    print(f"    Created: {pyz_path} ({size} bytes)")
    return pyz_path


def github_api(endpoint, method="GET", data=None, token=None, content_type=None):
    url = f"https://api.github.com{endpoint}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    if content_type:
        headers["Content-Type"] = content_type

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"[!] GitHub API error: {e.code} - {error_body[:200]}")
        sys.exit(1)


def create_release(token, version, pyz_path):
    print(f"[*] Creating release v{version}...")

    release = github_api(f"/repos/{REPO}/releases", "POST", {
        "tag_name": f"v{version}",
        "name": f"Ribiks v{version}",
        "body": f"Ribiks v{version} - Telegram Chat Autoreply & Group Scanner",
    }, token)

    release_id = release["id"]
    upload_url = release["upload_url"]

    # Upload .pyz
    print("[*] Uploading ribiks.pyz...")
    filename = os.path.basename(pyz_path)
    upload_url_asset = upload_url.replace("{?name,label}", f"?name={filename}")
    with open(pyz_path, "rb") as f:
        file_data = f.read()
    req = urllib.request.Request(upload_url_asset, data=file_data, method="POST")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Content-Type", "application/octet-stream")
    with urllib.request.urlopen(req) as resp:
        resp.read()
    print("    Uploaded ribiks.pyz")

    print(f"[+] Release created: https://github.com/{REPO}/releases/tag/v{version}")
    return release_id


def get_current_version():
    init_file = os.path.join(SRC_DIR, "__init__.py")
    with open(init_file) as f:
        for line in f:
            if "__version__" in line:
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"


def update_version(new_version):
    init_file = os.path.join(SRC_DIR, "__init__.py")
    with open(init_file) as f:
        content = f.read()
    content = content.replace(
        f'__version__ = "{get_current_version()}"',
        f'__version__ = "{new_version}"'
    )
    with open(init_file, "w") as f:
        f.write(content)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: ribiks dev <command>")
        print()
        print("Commands:")
        print("  build [version]    Recompile and build .pyz")
        print("  release [version]  Build and push to GitHub release")
        print("  version            Show current version")
        print("  bump <version>     Update version number")
        print()
        print("Examples:")
        print("  ribiks dev build           # Build with current version")
        print("  ribiks dev build 1.1.0     # Build with new version")
        print("  ribiks dev release 1.1.0   # Build + release to GitHub")
        return

    cmd = sys.argv[1]
    token = load_token()

    if cmd == "version":
        print(f"Current version: {get_current_version()}")

    elif cmd == "bump":
        if len(sys.argv) < 3:
            print("[!] Usage: ribiks dev bump <version>")
            return
        new_ver = sys.argv[2]
        old_ver = get_current_version()
        update_version(new_ver)
        print(f"[+] Version: {old_ver} -> {new_ver}")

    elif cmd == "build":
        version = sys.argv[2] if len(sys.argv) > 2 else get_current_version()
        recompile()
        build_pyz(version)
        print(f"\n[+] Build complete: ribiks-{version}.pyz")

    elif cmd == "release":
        version = sys.argv[2] if len(sys.argv) > 2 else get_current_version()
        recompile()
        pyz_path = build_pyz(version)
        create_release(token, version, pyz_path)
        # Cleanup local pyz
        os.remove(pyz_path)
        print(f"\n[+] Released v{version}!")

    else:
        print(f"[!] Unknown command: {cmd}")
        print("[i] Run 'ribiks dev --help' for usage")


if __name__ == "__main__":
    main()
