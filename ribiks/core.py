import asyncio
import os
import sys

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

from .config import load_config, save_config, get_session_path


PROXY = None


def get_client():
    cfg = load_config()
    session_path = get_session_path()
    proxy = cfg.get("proxy") or PROXY
    return TelegramClient(session_path, cfg["api_id"], cfg["api_hash"], proxy=proxy)


async def setup_auth(phone=None):
    cfg = load_config()
    if not cfg["api_id"] or not cfg["api_hash"]:
        print("[!] API ID and API Hash not configured. Run 'ribiks setup' first.")
        return False

    client = get_client()
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"[+] Already authorized: {me.first_name} (@{me.username})")
        await client.disconnect()
        return True

    if not phone:
        phone = cfg["phone"]
    if not phone:
        phone = input("[?] Enter phone number (e.g. +234...): ").strip()

    sent = await client.send_code_request(phone)
    code = input(f"[?] Enter OTP code sent to {phone}: ").strip()

    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=sent.phone_code_hash)
    except SessionPasswordNeededError:
        pwd = input("[?] 2FA password required: ").strip()
        await client.sign_in(password=pwd)
    except PhoneCodeInvalidError:
        print("[!] Invalid code. Try again.")
        await client.disconnect()
        return False

    me = await client.get_me()
    cfg["phone"] = phone
    save_config(cfg)
    print(f"[+] Logged in: {me.first_name} (@{me.username}) ID:{me.id}")
    await client.disconnect()
    return True


async def ensure_connected():
    client = get_client()
    await client.connect()
    if not await client.is_user_authorized():
        print("[!] Not authorized. Run 'ribiks setup' first.")
        await client.disconnect()
        return None
    return client
