import asyncio
import json
import os
import sys
import time
from datetime import datetime

from telethon import events

from .core import get_client, ensure_connected
from .config import load_accounts, load_config, save_accounts
from .gender import detect_gender, get_gender_emoji
from .evolution import (
    analyze_message_tone,
    update_romance_score,
    check_relationship_evolution,
    get_relationship_prompt,
    get_fallback_messages,
)


def generate_reply(msg_text, sender_name, sender_gender, user_gender, relationship):
    import requests

    cfg = load_config()
    api_key = cfg.get("ai_api_key")
    model = cfg.get("ai_model", "gpt-4o-mini")
    max_len = cfg.get("max_reply_length", 200)

    system_prompt = get_relationship_prompt(relationship, user_gender, sender_gender)

    if api_key:
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": f"{system_prompt} Max {max_len} chars. Use emojis sparingly. Never break character. Never mention being AI."},
                    {"role": "user", "content": f"{sender_name} ({sender_gender}) said: {msg_text}\n\nReply:"}
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

    return get_fallback_messages(relationship, sender_gender)


def find_account_index(accounts, target):
    for i, a in enumerate(accounts):
        if a["target"] == target:
            return i
    return -1


async def run_check():
    accounts = load_accounts()
    enabled = [a for a in accounts if a.get("enabled", True)]

    if not enabled:
        print("[!] No accounts configured for auto-reply.")
        print("[i] Use 'ribiks accounts add <username>' to add targets.")
        return

    cfg = load_config()
    user_gender = cfg.get("user_gender") or "male"
    api_key = cfg.get("ai_api_key")
    model = cfg.get("ai_model", "gpt-4o-mini")

    targets = [a["target"] for a in enabled]
    print(f"[*] Auto-reply enabled for: {', '.join(targets)}")
    print(f"[*] Your gender: {user_gender.capitalize()}")

    client = await ensure_connected()
    if not client:
        return

    me = await client.get_me()
    print(f"[+] Logged in as: {me.first_name} (@{me.username})")

    replied = set()
    total_replied = 0
    evolutions = []

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

            acc_idx = find_account_index(accounts, target)
            if acc_idx == -1:
                continue

            acc = accounts[acc_idx]
            current_relationship = acc.get("relationship", "romantic")
            current_score = acc.get("romance_score", 0)

            new_score = update_romance_score(current_score, unread)
            accounts[acc_idx]["romance_score"] = new_score

            new_relationship, evolved = check_relationship_evolution(
                target, current_relationship, new_score
            )

            if evolved:
                accounts[acc_idx]["relationship"] = new_relationship
                emoji = "💕" if new_relationship == "romantic" else "🤝"
                print(f"  {emoji} {target}: Relationship evolved: {current_relationship} -> {new_relationship}")
                evolutions.append((target, current_relationship, new_relationship))

            for msg in unread:
                sender = await msg.get_sender()
                sender_name = getattr(sender, "first_name", "") or ""
                if not sender_name:
                    sender_name = "friend"

                sender_gender = detect_gender(sender_name, api_key, model)
                gender_icon = get_gender_emoji(sender_gender)

                relationship = accounts[acc_idx].get("relationship", "romantic")

                tone, _ = analyze_message_tone(msg.text)

                reply = generate_reply(msg.text, sender_name, sender_gender, user_gender, relationship)

                await msg.reply(reply)
                replied.add(msg.id)
                total_replied += 1

                rel_icon = {"romantic": "💕", "friendly": "🤝", "polite": "👔"}.get(relationship, "❓")
                print(f"  [>] {target}: {gender_icon}{sender_name} [{relationship}{rel_icon}] tone:{tone}")
                print(f"      msg: '{msg.text[:60]}...'")
                print(f"      reply: '{reply[:60]}...'")
                await asyncio.sleep(2)

        except Exception as e:
            print(f"  [!] {target}: Error - {e}")

    save_accounts(accounts)

    print(f"\n[+] Done. Replied to {total_replied} messages across {len(targets)} accounts.")
    if evolutions:
        print("\n  Relationship evolutions:")
        for target, old_rel, new_rel in evolutions:
            print(f"    {target}: {old_rel} -> {new_rel}")

    await client.disconnect()


def check_main():
    asyncio.run(run_check())
