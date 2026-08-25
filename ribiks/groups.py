import asyncio
import csv
import os
import sys
from datetime import datetime

from .core import ensure_connected
from .config import load_config


async def run_groups_check():
    client = await ensure_connected()
    if not client:
        return

    me = await client.get_me()
    print(f"[+] Scanning groups for: {me.first_name} (@{me.username})\n")

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = os.path.join(output_dir, f"groups_{timestamp}.csv")

    all_members = []

    async for dialog in client.iter_dialogs():
        if not dialog.is_group:
            continue

        group_name = dialog.name
        group_id = dialog.id
        print(f"[*] Scanning: {group_name} (ID: {group_id})")

        try:
            members = []
            async for member in client.iter_participants(dialog.entity):
                info = {
                    "group": group_name,
                    "group_id": group_id,
                    "user_id": member.id,
                    "first_name": member.first_name or "",
                    "last_name": member.last_name or "",
                    "username": member.username or "",
                    "phone": member.phone or "",
                    "is_bot": member.bot,
                    "is_admin": member.admin if hasattr(member, "admin") else False,
                    "is_restricted": member.restricted if hasattr(member, "restricted") else False,
                    "is_scam": member.scam if hasattr(member, "scam") else False,
                    "is_fake": member.fake if hasattr(member, "fake") else False,
                    "is_premium": member.premium if hasattr(member, "premium") else False,
                    "status": str(member.status) if member.status else "",
                    "profile_url": f"https://t.me/{member.username}" if member.username else "",
                }
                members.append(info)
                all_members.append(info)

            print(f"    Found {len(members)} members")
        except Exception as e:
            print(f"    [!] Error: {e}")

    if all_members:
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_members[0].keys())
            writer.writeheader()
            writer.writerows(all_members)

        print(f"\n[+] Total members scanned: {len(all_members)}")
        print(f"[+] Results saved to: {csv_file}")
    else:
        print("\n[!] No groups found in this account.")

    await client.disconnect()


def groups_main():
    asyncio.run(run_groups_check())
