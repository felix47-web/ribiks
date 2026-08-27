# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ribiks.menu import menu_main, run_check_cmd, run_groups_cmd, run_setup_cmd, run_config_cmd
from ribiks.accounts import accounts_main
from ribiks.hopin import hopin_main
from ribiks.config import load_config
from ribiks.tor import ensure_tor, stop_tor, is_tor_installed


USAGE = """
  RIBIKS - Telegram Chat Autoreply & Group Scanner

  Usage:
    ribiks                  Launch interactive menu
    ribiks check            Refresh & auto-reply to target accounts
    ribiks config           View/edit configuration
    ribiks groups -check    Scan groups for member info
    ribiks setup            First-time setup / reconfigure
    ribiks accounts list    List auto-reply targets
    ribiks accounts add     Add target account
    ribiks accounts remove  Remove target account
    ribiks hopin            Hop in a random group (US/Germany)
    ribiks update           Check for and install updates
    ribiks update --check   Check only (don't install)
"""


def _needs_telegram(cmd, args):
    """Which commands actually open a Telegram connection and thus need Tor."""
    if cmd == "check":
        return True
    if cmd == "groups":
        return "-check" in args or "--check" in args
    if cmd == "hopin":
        return True
    if cmd == "accounts":
        action = args[1].lower() if len(args) > 1 else ""
        # list reads the local file only; add/remove/toggle contact Telegram.
        return action in ("add", "remove", "toggle")
    return False


def _start_tor_for_session():
    """Start Tor if anonymity is enabled, returning False if it cannot run.

    Called before any Telegram work so the MTProto connection uses the chosen
    location (us|de). The `setup` command prompts for location itself, so it
    is excluded here to avoid double-prompting.
    """
    cfg = load_config()
    if not cfg.get("anonymity", True):
        return True

    if not is_tor_installed():
        print("[!] Anonymity is enabled but Tor is not installed.")
        print("[i] Install it, then run 'ribiks setup' again:")
        print("    - Termux : pkg install tor")
        print("    - Debian / Ubuntu / Kali : sudo apt install tor")
        return True

    return ensure_tor(cfg.get("exit_location", "us"))


def main():
    args = sys.argv[1:]

    if not args:
        try:
            menu_main()
        finally:
            stop_tor()
        return

    cmd = args[0].lower()

    if cmd == "setup":
        # setup prompts for anonymity/location interactively; core.setup_auth
        # routes the OTP login through Tor automatically via get_client().
        run_setup_cmd()
        return

    if _needs_telegram(cmd, args) and not _start_tor_for_session():
        print("[!] Tor could not be started; aborting to protect your location.")
        sys.exit(1)

    try:
        _run_command(cmd, args)
    finally:
        stop_tor()


def _run_command(cmd, args):
    if cmd == "check":
        run_check_cmd()
    elif cmd == "config":
        run_config_cmd()
    elif cmd == "groups":
        if "-check" in args or "--check" in args:
            run_groups_cmd()
        else:
            print("[!] Usage: ribiks groups -check")
    elif cmd == "update":
        from ribiks.updates import check_for_updates, do_update
        if "--check" in args:
            check_for_updates()
        else:
            do_update()
    elif cmd == "hopin":
        hopin_main()
    elif cmd == "accounts":
        accounts_main(args[1:])
    elif cmd in ("-h", "--help", "help"):
        print(USAGE)
    elif cmd in ("-v", "--version"):
        from ribiks import __version__, __codename__
        print(f"Ribiks {__version__} ({__codename__})")
    else:
        print(f"[!] Unknown command: {cmd}")
        print(USAGE)


if __name__ == "__main__":
    main()
