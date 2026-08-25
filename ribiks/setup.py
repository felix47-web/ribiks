import os
import sys
import asyncio

from .config import load_config, save_config, SESSION_DIR
from .core import setup_auth


def run_setup():
    print("\n  ╔══════════════════════════════════════╗")
    print("  ║        RIBIKS - Initial Setup         ║")
    print("  ╚══════════════════════════════════════╝\n")

    cfg = load_config()

    if cfg["api_id"] and cfg["api_hash"] and cfg["phone"]:
        print(f"[i] Current config:")
        print(f"    API ID  : {cfg['api_id']}")
        print(f"    Phone   : {cfg['phone']}")
        print(f"    Gender  : {cfg.get('user_gender') or 'Not set'}")
        change = input("[?] Reconfigure? (y/N): ").strip().lower()
        if change != "y":
            print("[i] Keeping existing config.")
            return

    print("[1] Get your API credentials from https://my.telegram.org")
    print("    - Login with your phone number")
    print("    - Go to 'API Development Tools'\n")

    api_id = input("[?] Enter API ID: ").strip()
    try:
        api_id = int(api_id)
    except ValueError:
        print("[!] API ID must be a number.")
        return

    api_hash = input("[?] Enter API Hash: ").strip()
    phone = input("[?] Enter phone number (e.g. +234...): ").strip()

    cfg["api_id"] = api_id
    cfg["api_hash"] = api_hash
    cfg["phone"] = phone

    print("\n  [?] Your gender (used to tailor replies):")
    print("      [1] Male")
    print("      [2] Female")
    gender_choice = input("  > Select (1/2): ").strip()
    if gender_choice == "1":
        cfg["user_gender"] = "male"
    elif gender_choice == "2":
        cfg["user_gender"] = "female"
    else:
        print("[!] Invalid choice, defaulting to Male.")
        cfg["user_gender"] = "male"

    print(f"[i] Gender set to: {cfg['user_gender'].capitalize()}")

    save_config(cfg)

    print("\n[*] Authenticating with Telegram...")
    ok = asyncio.run(setup_auth(phone))
    if ok:
        print("[+] Setup complete! Run 'ribiks' to start.")
    else:
        print("[!] Setup failed. Try again with 'ribiks setup'.")
