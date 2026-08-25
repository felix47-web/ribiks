from .config import load_accounts, add_account, remove_account, list_accounts


def accounts_main(args=None):
    if not args:
        args = []

    if len(args) < 1:
        print("\n  RIBIKS - Account Management\n")
        print("  Usage:")
        print("    ribiks accounts list              - List auto-reply targets")
        print("    ribiks accounts add <username>    - Add target account")
        print("    ribiks accounts remove <username> - Remove target account")
        return

    action = args[0]

    if action == "list":
        accounts = list_accounts()
        if not accounts:
            print("[!] No accounts configured.")
            print("[i] Use 'ribiks accounts add <username>' to add targets.")
            return
        print("\n  Auto-reply Targets:")
        for i, a in enumerate(accounts, 1):
            status = "ON" if a.get("enabled", True) else "OFF"
            print(f"  {i}. {a['target']} [{status}]")

    elif action == "add":
        if len(args) < 2:
            print("[!] Usage: ribiks accounts add <username_or_link>")
            return
        target = args[1]
        if add_account(target):
            print(f"[+] Added: {target}")
        else:
            print(f"[i] Already exists: {target}")

    elif action == "remove":
        if len(args) < 2:
            print("[!] Usage: ribiks accounts remove <username>")
            return
        target = args[1]
        remove_account(target)
        print(f"[+] Removed: {target}")

    else:
        print(f"[!] Unknown action: {action}")
