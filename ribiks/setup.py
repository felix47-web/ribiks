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


def run_config():
    cfg = load_config()
    print("\n  ╔══════════════════════════════════════╗")
    print("  ║         RIBIKS - Configuration        ║")
    print("  ╚══════════════════════════════════════╝\n")

    print(f"  [1] API ID    : {cfg.get('api_id', 'Not set')}")
    print(f"  [2] Phone     : {cfg.get('phone', 'Not set')}")
    print(f"  [3] Gender    : {(cfg.get('user_gender') or 'Not set').capitalize()}")
    print(f"  [4] AI Model  : {cfg.get('ai_model', 'free models')}")
    print(f"  [5] Reply Style: {cfg.get('reply_style', 'sweet and caring')}")
    print(f"  [6] Zen Key 2 : {'Set' if cfg.get('zen_api_key_2') else 'Not set'}")
    print(f"  [0] Back\n")

    choice = input("  > Select to edit: ").strip()

    if choice == "1":
        val = input(f"  > API ID [{cfg.get('api_id')}]: ").strip()
        if val:
            try:
                cfg["api_id"] = int(val)
            except ValueError:
                print("[!] Must be a number.")
                return
    elif choice == "2":
        val = input(f"  > Phone [{cfg.get('phone')}]: ").strip()
        if val:
            cfg["phone"] = val
    elif choice == "3":
        print("      [1] Male  [2] Female")
        val = input("  > Gender: ").strip()
        if val == "1":
            cfg["user_gender"] = "male"
        elif val == "2":
            cfg["user_gender"] = "female"
    elif choice == "4":
        val = input(f"  > Model [{cfg.get('ai_model', 'free models')}]: ").strip()
        if val:
            cfg["ai_model"] = val
    elif choice == "5":
        val = input(f"  > Style [{cfg.get('reply_style')}]: ").strip()
        if val:
            cfg["reply_style"] = val
    elif choice == "6":
        current = cfg.get("zen_api_key_2", "")
        masked = (current[:8] + "..." + current[-6:]) if current and len(current) > 14 else "Not set"
        print(f"  > Current: {masked}")
        val = input("  > Enter new Zen API Key 2 (or 'clear' to remove): ").strip()
        if val.lower() == "clear":
            cfg["zen_api_key_2"] = None
            print("[+] Key 2 cleared.")
        elif val:
            cfg["zen_api_key_2"] = val
            print("[+] Key 2 updated.")
    else:
        return

    save_config(cfg)
    print("[+] Config saved.")
