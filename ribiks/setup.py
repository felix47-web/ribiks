import os
import sys
import asyncio

from .config import load_config, save_config, SESSION_DIR
from .core import setup_auth


def prompt_api_key(cfg):
    if cfg.get("ai_api_key"):
        masked = cfg["ai_api_key"][:6] + "..." + cfg["ai_api_key"][-4:]
        print(f"  [i] API Key: {masked}")
        change = input("  [?] Change API key? (y/N): ").strip().lower()
        if change != "y":
            return cfg

    print(f"\n  [?] AI API Key (OpenCode Zen):")
    print(f"      Get yours free at https://opencode.ai/zen")
    api_key = input("  > Enter API key: ").strip()
    if api_key:
        cfg["ai_api_key"] = api_key
        print(f"  [+] API key saved.")
    else:
        print("  [i] Skipped.")
    return cfg


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
        has_key = "Set" if cfg.get("ai_api_key") else "Not set"
        print(f"    AI Key  : {has_key}")
        change = input("[?] Reconfigure? (y/N): ").strip().lower()
        if change != "y":
            if not cfg.get("ai_api_key"):
                print("\n[i] AI API key is required for auto-replies.")
                cfg = prompt_api_key(cfg)
                save_config(cfg)
            else:
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

    cfg = prompt_api_key(cfg)

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

    has_key = "Set" if cfg.get("ai_api_key") else "Not set"
    print(f"  [1] API ID    : {cfg.get('api_id', 'Not set')}")
    print(f"  [2] Phone     : {cfg.get('phone', 'Not set')}")
    print(f"  [3] Gender    : {(cfg.get('user_gender') or 'Not set').capitalize()}")
    print(f"  [4] AI Key    : {has_key}")
    print(f"  [5] AI Model  : {cfg.get('ai_model', 'big-pickle')}")
    print(f"  [6] Reply Style: {cfg.get('reply_style', 'sweet and caring')}")
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
        cfg = prompt_api_key(cfg)
    elif choice == "5":
        val = input(f"  > Model [{cfg.get('ai_model', 'big-pickle')}]: ").strip()
        if val:
            cfg["ai_model"] = val
    elif choice == "6":
        val = input(f"  > Style [{cfg.get('reply_style')}]: ").strip()
        if val:
            cfg["reply_style"] = val
    else:
        return

    save_config(cfg)
    print("[+] Config saved.")
