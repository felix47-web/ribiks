#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ribiks.menu import menu_main, run_check_cmd, run_groups_cmd, run_setup_cmd
from ribiks.accounts import accounts_main


USAGE = """
  RIBIKS - Telegram Chat Autoreply & Group Scanner

  Usage:
    ribiks                  Launch interactive menu
    ribiks check            Refresh & auto-reply to target accounts
    ribiks groups -check    Scan groups for member info
    ribiks setup            First-time setup / reconfigure
    ribiks accounts list    List auto-reply targets
    ribiks accounts add     Add target account
    ribiks accounts remove  Remove target account
    ribiks update           Check for and install updates
    ribiks update --check   Check only (don't install)
"""


def main():
    args = sys.argv[1:]

    if not args:
        menu_main()
        return

    cmd = args[0].lower()

    if cmd == "check":
        run_check_cmd()
    elif cmd == "groups":
        if "-check" in args or "--check" in args:
            run_groups_cmd()
        else:
            print("[!] Usage: ribiks groups -check")
    elif cmd == "setup":
        run_setup_cmd()
    elif cmd == "update":
        from ribiks.updates import check_for_updates, do_update
        if "--check" in args:
            check_for_updates()
        else:
            do_update()
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
