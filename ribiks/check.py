import asyncio
import json
import os
import sys
import time
from datetime import datetime

from telethon import events

from .core import get_client, ensure_connected
from .config import load_accounts, load_config, save_accounts


def generate_reply(msg_text, sender_name, style="sweet and caring"):
    import random
    import requests

    cfg = load_config()
    api_key = cfg.get("ai_api_key")
    model = cfg.get("ai_model", "gpt-4o-mini")
    max_len = cfg.get("max_reply_length", 200)

    if api_key:
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": f"You are a {style} girlfriend/boyfriend replying to your partner. Keep replies short, natural, and warm. Max {max_len} chars. Use emojis sparingly. Never break character. Never mention being AI."},
                    {"role": "user", "content": f"{sender_name} said: {msg_text}\n\nReply:"}
                ],
                "max_tokens": 100,
                "temperature": 0.9
            }
            resp = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

    fallbacks = [
        "Aww that's so sweet babe \U0001f496",
        "I love you so much \U0001f48b",
        "You always make my day better \U0001f60d",
        "Can't stop thinking about you \U0001f970",
        "You're the best thing that happened to me \U0001f495",
        "Missing you right now \U0001f61b",
        "You're literally the cutest \U0001f97a\U0001f496",
        "My heart belongs to you \u2764\ufe0f",
        "You just made me smile so hard \U0001f970",
        "I'm so lucky to have you \U0001f496",
    ]
    return random.choice(fallbacks)


async def run_check():
    accounts = load_accounts()
    enabled = [a for a in accounts if a.get("enabled", True)]

    if not enabled:
        print("[!] No accounts configured for auto-reply.")
        print("[i] Use 'ribiks accounts add <username>' to add targets.")
        return

    targets = [a["target"] for a in enabled]
    print(f"[*] Auto-reply enabled for: {', '.join(targets)}")

    client = await ensure_connected()
    if not client:
        return

    me = await client.get_me()
    print(f"[+] Logged in as: {me.first_name} (@{me.username})")

    replied = set()
    total_replied = 0

    for target in targets:
        try:
            entity = await client.get_entity(target)
            messages = []
            async for msg in client.iter_messages(entity, limit=5):
                if not msg.out and msg.text:
                    messages.append(msg)

            unread = [m for m in messages if m.id not in replied]

            if not unread:
                print(f"  [~] {target}: No new messages")
                continue

            for msg in unread:
                sender = await msg.get_sender()
                sender_name = getattr(sender, "first_name", "babe") or "babe"
                reply = generate_reply(msg.text, sender_name)
                await msg.reply(reply)
                replied.add(msg.id)
                total_replied += 1
                print(f"  [>] {target}: replied to '{msg.text[:50]}...' -> '{reply[:50]}...'")
                await asyncio.sleep(2)

        except Exception as e:
            print(f"  [!] {target}: Error - {e}")

    print(f"\n[+] Done. Replied to {total_replied} messages across {len(targets)} accounts.")
    await client.disconnect()


def check_main():
    asyncio.run(run_check())
