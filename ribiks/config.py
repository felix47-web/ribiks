import json
import os
import sys

GITHUB_REPO = "felix47-web/ribiks"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
SESSION_DIR = os.path.join(BASE_DIR, "sessions")
ACCOUNTS_PATH = os.path.join(BASE_DIR, "accounts.json")

DEFAULT_CONFIG = {
    "api_id": None,
    "api_hash": None,
    "phone": None,
    "session_name": "ribiks_session",
    "proxy": None,
    "ai_provider": "openai",
    "ai_model": "gpt-4o-mini",
    "ai_api_key": None,
    "reply_style": "sweet and caring",
    "max_reply_length": 200,
    "user_gender": None,
}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    merged = DEFAULT_CONFIG.copy()
    merged.update(cfg)
    return merged


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def load_accounts():
    if not os.path.exists(ACCOUNTS_PATH):
        return []
    with open(ACCOUNTS_PATH) as f:
        return json.load(f)


def save_accounts(accounts):
    with open(ACCOUNTS_PATH, "w") as f:
        json.dump(accounts, f, indent=2)


def add_account(name_or_username):
    accounts = load_accounts()
    entry = {"target": name_or_username, "enabled": True}
    if entry not in accounts:
        accounts.append(entry)
        save_accounts(accounts)
        return True
    return False


def remove_account(name_or_username):
    accounts = load_accounts()
    accounts = [a for a in accounts if a["target"] != name_or_username]
    save_accounts(accounts)


def list_accounts():
    return load_accounts()


def get_session_path():
    cfg = load_config()
    os.makedirs(SESSION_DIR, exist_ok=True)
    return os.path.join(SESSION_DIR, cfg.get("session_name", "ribiks_session"))
