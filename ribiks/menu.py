import os
import sys
import subprocess
from datetime import datetime

from .config import load_config, load_accounts
from . import __version__, __codename__


BANNER = r"""
  ╔══════════════════════════════════════════════╗
  ║            ____  _ ____  _                   ║
  ║           |  _ \(_)  _ \(_)                  ║
  ║           | |_) | | |_) | |                  ║
  ║           |  _ <| |  __/| |                  ║
  ║           |_| \_\_|_|   |_|                  ║
  ║                                              ║
  ║   Telegram Chat Autoreply & Group Scanner    ║
  ╚══════════════════════════════════════════════╝
"""


def clear():
    os.system("clear" if os.name == "posix" else "cls")


def show_status():
    cfg = load_config()
    accounts = load_accounts()
    enabled = [a for a in accounts if a.get("enabled", True)]

    print(f"\n  [i] Version  : {__version__} ({__codename__})")
    print(f"  [i] Phone    : {cfg.get('phone', 'Not set')}")
    print(f"  [i] API ID   : {'Set' if cfg.get('api_id') else 'Not set'}")
    print(f"  [i] Targets  : {len(enabled)} account(s)")
    if enabled:
        for a in enabled:
            print(f"      - {a['target']}")
    print()


def run_check_cmd():
    from .check import check_main
    check_main()


def run_groups_cmd():
    from .groups import groups_main
    groups_main()


def run_accounts_cmd():
    from .accounts import accounts_main
    accounts_main()


def run_setup_cmd():
    from .setup import run_setup
    run_setup()


MENU_OPTIONS = {
    "1": ("Check & Auto-Reply", run_check_cmd),
    "2": ("Scan Groups", run_groups_cmd),
    "3": ("Manage Accounts", run_accounts_cmd),
    "4": ("Setup / Reconfigure", run_setup_cmd),
    "5": ("Status", show_status),
}


def show_menu():
    print(BANNER)
    print("  Commands:")
    for k, (desc, _) in MENU_OPTIONS.items():
        print(f"    [{k}] {desc}")
    print(f"    [0] Exit")
    print()


def menu_main():
    while True:
        clear()
        show_menu()
        choice = input("  > Select: ").strip()
        if choice == "0":
            print("\n  Bye!")
            sys.exit(0)
        if choice in MENU_OPTIONS:
            print()
            try:
                MENU_OPTIONS[choice][1]()
            except KeyboardInterrupt:
                print("\n  [i] Interrupted.")
            input("\n  [Enter] Back to menu...")
        else:
            print("  [!] Invalid choice.")
            input("  [Enter] Try again...")
