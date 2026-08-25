from .config import load_accounts, add_account, remove_account, list_accounts, save_accounts

VALID_RELATIONSHIPS = ["romantic", "friendly", "polite"]


def accounts_main(args=None):
    if not args:
        args = []

    if len(args) < 1:
        print("\n  RIBIKS - Account Management\n")
        print("  Usage:")
        print("    ribiks accounts list                          - List targets")
        print("    ribiks accounts add <username>                - Add target")
        print("    ribiks accounts remove <username>             - Remove target")
        print("    ribiks accounts relationship <user> <type>    - Set relationship")
        print("    ribiks accounts toggle <user>                 - Enable/Disable")
        print()
        print("  Relationship types: romantic, friendly, polite")
        return

    action = args[0]

    if action == "list":
        accounts = list_accounts()
        if not accounts:
            print("[!] No accounts configured.")
            print("[i] Use 'ribiks accounts add <username>' to add targets.")
            return
        print("\n  Auto-reply Targets:")
        print(f"  {'#':<3} {'Target':<25} {'Status':<10} {'Relation':<12} {'Score':<6}")
        print(f"  {'-'*56}")
        for i, a in enumerate(accounts, 1):
            status = "ON" if a.get("enabled", True) else "OFF"
            relationship = a.get("relationship", "romantic")
            score = a.get("romance_score", 0)
            print(f"  {i:<3} {a['target']:<25} {status:<10} {relationship:<12} {score:<6}")

    elif action == "add":
        if len(args) < 2:
            print("[!] Usage: ribiks accounts add <username_or_link>")
            return
        target = args[1]

        rel = "romantic"
        if len(args) >= 4 and args[2] == "--relationship":
            if args[3] in VALID_RELATIONSHIPS:
                rel = args[3]
            else:
                print(f"[!] Invalid relationship. Use: {', '.join(VALID_RELATIONSHIPS)}")
                return

        accounts = load_accounts()
        entry = {
            "target": target,
            "enabled": True,
            "relationship": rel,
            "romance_score": 0,
            "replied_messages": []
        }
        if not any(a["target"] == target for a in accounts):
            accounts.append(entry)
            save_accounts(accounts)
            print(f"[+] Added: {target} (relationship: {rel})")
        else:
            print(f"[i] Already exists: {target}")

    elif action == "remove":
        if len(args) < 2:
            print("[!] Usage: ribiks accounts remove <username>")
            return
        target = args[1]
        remove_account(target)
        print(f"[+] Removed: {target}")

    elif action == "relationship":
        if len(args) < 3:
            print("[!] Usage: ribiks accounts relationship @username <type>")
            print(f"[i] Types: {', '.join(VALID_RELATIONSHIPS)}")
            return
        target = args[1]
        new_rel = args[2].lower()

        if new_rel not in VALID_RELATIONSHIPS:
            print(f"[!] Invalid relationship. Use: {', '.join(VALID_RELATIONSHIPS)}")
            return

        accounts = load_accounts()
        found = False
        for a in accounts:
            if a["target"] == target:
                old_rel = a.get("relationship", "romantic")
                a["relationship"] = new_rel
                if new_rel == "romantic":
                    a["romance_score"] = max(a.get("romance_score", 0), 70)
                elif new_rel == "friendly":
                    a["romance_score"] = min(a.get("romance_score", 0), 30)
                found = True
                print(f"[+] {target}: {old_rel} -> {new_rel}")
                break

        if not found:
            print(f"[!] Target not found: {target}")
            print("[i] Add it first with: ribiks accounts add " + target)
            return

        save_accounts(accounts)

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
