from .config import load_accounts, add_account, remove_account, list_accounts, save_accounts


def accounts_main(args=None):
    if not args:
        args = []

    if len(args) < 1:
        print("\n  RIBIKS - Account Management\n")
        print("  Usage:")
        print("    ribiks accounts list                          - List targets")
        print("    ribiks accounts add <username>                - Add target")
        print("    ribiks accounts remove <username>             - Remove target")
        print("    ribiks accounts toggle <user>                 - Enable/Disable")
        print()
        return

    action = args[0]

    if action == "list":
        accounts = list_accounts()
        if not accounts:
            print("[!] No accounts configured.")
            print("[i] Use 'ribiks accounts add <username>' to add targets.")
            return
        print("\n  Auto-reply Targets:")
        print(f"  {'#':<3} {'Target':<25} {'Status':<10} {'Relation':<12}")
        print(f"  {'-'*50}")
        for i, a in enumerate(accounts, 1):
            status = "ON" if a.get("enabled", True) else "OFF"
            relationship = a.get("relationship", "undetermined")
            print(f"  {i:<3} {a['target']:<25} {status:<10} {relationship:<12}")

    elif action == "add":
        if len(args) < 2:
            print("[!] Usage: ribiks accounts add <username_or_link>")
            return
        target = args[1]

        accounts = load_accounts()
        entry = {
            "target": target,
            "enabled": True,
            "relationship": "undetermined",
        }
        if not any(a["target"] == target for a in accounts):
            accounts.append(entry)
            save_accounts(accounts)
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

    elif action == "toggle":
        if len(args) < 2:
            print("[!] Usage: ribiks accounts toggle <username>")
            return
        target = args[1]
        accounts = load_accounts()
        for a in accounts:
            if a["target"] == target:
                a["enabled"] = not a.get("enabled", True)
                status = "ON" if a["enabled"] else "OFF"
                print(f"[+] {target}: {status}")
                save_accounts(accounts)
                return
        print(f"[!] Target not found: {target}")

    else:
        print(f"[!] Unknown action: {action}")
        print("[i] Run 'ribiks accounts' for help")
