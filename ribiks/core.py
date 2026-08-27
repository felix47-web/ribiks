from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

from .config import load_config, save_config, get_session_path
from .tor import ensure_tor, get_socks_proxy, is_tor_installed


PROXY = None


class AnonymityError(Exception):
    """Raised when anonymity is required but Tor cannot be established.

    Anonymity (Tor) is a hard dependency: when enabled, ribiks refuses to
    connect to Telegram directly rather than exposing the device's location.
    """


def _resolve_proxy(cfg):
    """Return the proxy Telethon should use, honoring the anonymity setting.

    When anonymity is enabled the Telegram MTProto connection is routed
    through Tor so Telegram sees an exit IP from the chosen country (us|de)
    instead of the device's real location. AI API calls are unaffected.
    """
    if not cfg.get("anonymity", True):
        return cfg.get("proxy") or PROXY

    if not is_tor_installed():
        raise AnonymityError(
            "Anonymity is enabled but Tor is not installed. "
            "Install it (pkg install tor / sudo apt install tor), or disable "
            "anonymity in 'ribiks config'."
        )

    exit_location = cfg.get("exit_location", "us")
    if ensure_tor(exit_location):
        proxy = get_socks_proxy()
        if proxy:
            return proxy

    raise AnonymityError(
        "Could not establish a Tor connection. Anonymity is a hard "
        "dependency, so ribiks will not connect to Telegram directly."
    )


def get_client():
    cfg = load_config()
    session_path = get_session_path()
    proxy = _resolve_proxy(cfg)
    return TelegramClient(session_path, cfg["api_id"], cfg["api_hash"], proxy=proxy)


def try_client():
    """Return a Telethon client, or None if anonymity (Tor) cannot be set up."""
    try:
        return get_client()
    except AnonymityError as e:
        print(f"[!] {e}")
        return None


async def setup_auth(phone=None):
    cfg = load_config()
    if not cfg["api_id"] or not cfg["api_hash"]:
        print("[!] API ID and API Hash not configured. Run 'ribiks setup' first.")
        return False

    client = try_client()
    if not client:
        return False
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
    client = try_client()
    if not client:
        return None
    await client.connect()
    if not await client.is_user_authorized():
        print("[!] Not authorized. Run 'ribiks setup' first.")
        await client.disconnect()
        return None
    return client
