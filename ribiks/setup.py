import asyncio

from .config import load_config, save_config
from .core import setup_auth
from .tor import is_tor_installed


def prompt_anonymity(cfg):
    """Prompt for Tor-based anonymity and the connection location (US/Germany).

    New users choose a concrete country (us or de). The location becomes the
    Tor exit country Telegram sees for the MTProto connection.
    """
    print("\n  ── Anonymity ───────────────────────────")
    print("  Route your Telegram connection through Tor")
    print("  so Telegram sees a location you choose,")
    print("  not your device's real location/country.")

    if not is_tor_installed():
        print("\n  [!] Tor is required for anonymity but is not installed.")
        print("      - Termux : pkg install tor")
        print("      - Debian / Ubuntu / Kali : sudo apt install tor")

    anon = input("\n  [?] Route Telegram through Tor? (Y/n): ").strip().lower()
    if anon in ("n", "no"):
        cfg["anonymity"] = False
        print("  [i] Anonymity disabled. Telegram will use your real location.")
        return

    cfg["anonymity"] = True

    while True:
        print("\n  [?] Select connection location (Tor exit country):")
        print("      [1] United States")
        print("      [2] Germany")
        loc = input("  > Select (1/2): ").strip()
        if loc == "1":
            cfg["exit_location"] = "us"
            break
        elif loc == "2":
            cfg["exit_location"] = "de"
            break
        else:
            print("  [!] Invalid choice.")

    print(f"  [i] Location set to: {cfg['exit_location'].upper()}")



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

    prompt_anonymity(cfg)

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
    print(f"  [6] Anonymity : {'ON (Tor)' if cfg.get('anonymity', True) else 'OFF'}")
    print(f"  [7] Location  : {cfg.get('exit_location', 'us').upper()}")
    print(f"  [8] Groq Key  : {'Set' if cfg.get('groq_api_key') else 'Not set'}")
    print(f"  [9] Together  : {'Set' if cfg.get('together_api_key') else 'Not set'}")
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
        prompt_anonymity(cfg)
    elif choice == "7":
        if not cfg.get("anonymity", True):
            print("  [!] Anonymity is OFF. Enable it (option 6) first.")
        else:
            while True:
                print("      [1] United States")
                print("      [2] Germany")
                loc = input("  > Connection location (1/2): ").strip()
                if loc == "1":
                    cfg["exit_location"] = "us"
                    break
                elif loc == "2":
                    cfg["exit_location"] = "de"
                    break
                else:
                    print("  [!] Invalid choice.")
            print(f"  [i] Location set to: {cfg['exit_location'].upper()}")
    elif choice == "8":
        current = cfg.get("groq_api_key", "")
        masked = (current[:8] + "..." + current[-6:]) if current and len(current) > 14 else "Not set"
        print(f"  > Current: {masked}")
        print("  > Get free key at: https://console.groq.com")
        val = input("  > Enter Groq API Key (or 'clear' to remove): ").strip()
        if val.lower() == "clear":
            cfg["groq_api_key"] = None
            print("[+] Groq key cleared.")
        elif val:
            cfg["groq_api_key"] = val
            print("[+] Groq key updated.")
    elif choice == "9":
        current = cfg.get("together_api_key", "")
        masked = (current[:8] + "..." + current[-6:]) if current and len(current) > 14 else "Not set"
        print(f"  > Current: {masked}")
        print("  > Get free key at: https://api.together.ai")
        val = input("  > Enter Together API Key (or 'clear' to remove): ").strip()
        if val.lower() == "clear":
            cfg["together_api_key"] = None
            print("[+] Together key cleared.")
        elif val:
            cfg["together_api_key"] = val
            print("[+] Together key updated.")
    else:
        return

    save_config(cfg)
    print("[+] Config saved.")
