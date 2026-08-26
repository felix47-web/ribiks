import json
import os

GITHUB_REPO = "felix47-web/ribiks"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
SESSION_DIR = os.path.join(BASE_DIR, "sessions")
ACCOUNTS_PATH = os.path.join(BASE_DIR, "accounts.json")
CHATS_DIR = os.path.join(BASE_DIR, "chats")

DEFAULT_CONFIG = {
    "api_id": None,
    "api_hash": None,
    "phone": None,
    "session_name": "ribiks_session",
    "proxy": None,
    "ai_provider": "opencode",
    "ai_model": None,
    "ai_api_key": None,
    "zen_api_key_2": None,
    "reply_style": "sweet and caring",
    "max_reply_length": 200,
    "user_gender": None,
}

_config_cache = None
_accounts_cache = None


def load_config():
    global _config_cache
    if _config_cache is not None:
        return _config_cache.copy()
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    merged = DEFAULT_CONFIG.copy()
    merged.update(cfg)
    _config_cache = merged
    return merged.copy()


def save_config(cfg):
    global _config_cache
    _config_cache = None
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def load_accounts():
    global _accounts_cache
    if _accounts_cache is not None:
        return [a.copy() for a in _accounts_cache]
    if not os.path.exists(ACCOUNTS_PATH):
        return []
    with open(ACCOUNTS_PATH) as f:
        _accounts_cache = json.load(f)
    return [a.copy() for a in _accounts_cache]


def save_accounts(accounts):
    global _accounts_cache
    _accounts_cache = [a.copy() for a in accounts]
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


def get_chat_path(target):
    safe = target.replace("@", "").replace("/", "_")
    return os.path.join(CHATS_DIR, f"{safe}.json")


def load_chat_history(target):
    path = get_chat_path(target)
    if not os.path.exists(path):
        return {"target": target, "messages": [], "last_checked": None}
    with open(path) as f:
        return json.load(f)


def save_chat_history(target, messages, last_checked=None):
    os.makedirs(CHATS_DIR, exist_ok=True)
    path = get_chat_path(target)
    data = {
        "target": target,
        "messages": messages[-20:],
        "last_checked": last_checked,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
