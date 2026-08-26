import asyncio
import json
import os
import aiohttp
from datetime import datetime, timezone

from .config import BASE_DIR

ZEN_MODELS_URL = "https://opencode.ai/zen/v1/models"
ZEN_CHAT_URL = "https://opencode.ai/zen/v1/chat/completions"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
TOGETHER_CHAT_URL = "https://api.together.ai/v1/chat/completions"

HEALTH_PATH = os.path.join(BASE_DIR, "model_health.json")
HEALTH_EXPIRY = 300

ZEN_FALLBACK_MODELS = ["hy3-free", "laguna-s-2.1-free", "big-pickle", "mimo-v2.5-free"]
GROQ_MODELS = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
TOGETHER_MODELS = ["Prism-ML/Ternary-Bonsai-27B"]

RACE_TIMEOUT = 10
FALLBACK_TIMEOUT = 8

_health = {}


def _load_health():
    global _health
    if _health:
        return
    if os.path.exists(HEALTH_PATH):
        try:
            with open(HEALTH_PATH) as f:
                raw = json.load(f)
            for model, info in raw.items():
                if "failed" in info and "time" in info:
                    t = datetime.fromisoformat(info["time"])
                    _health[model] = (info["failed"], t)
        except Exception:
            _health = {}


def _save_health():
    raw = {}
    for model, (failed, t) in _health.items():
        raw[model] = {"failed": failed, "time": t.isoformat()}
    try:
        with open(HEALTH_PATH, "w") as f:
            json.dump(raw, f)
    except Exception:
        pass


def _is_healthy(model):
    if model not in _health:
        return True
    last_fail, fail_time = _health[model]
    if not last_fail:
        return True
    return (datetime.now(timezone.utc) - fail_time).total_seconds() > HEALTH_EXPIRY


def _mark_failed(model):
    _health[model] = (True, datetime.now(timezone.utc))
    _save_health()


def _mark_ok(model):
    _health[model] = (False, datetime.now(timezone.utc))
    _save_health()


async def _discover_zen_models():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                ZEN_MODELS_URL,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    return ZEN_FALLBACK_MODELS
                data = await resp.json()
                models = [
                    m["id"] for m in data.get("data", [])
                    if m["id"].endswith("-free")
                ]
                return models if models else ZEN_FALLBACK_MODELS
    except Exception:
        return ZEN_FALLBACK_MODELS


async def _try_zen(session, model, messages, timeout):
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.8,
    }
    try:
        async with session.post(
            ZEN_CHAT_URL, json=payload,
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                content = data["choices"][0]["message"]["content"].strip()
                if content:
                    _mark_ok(model)
                    return content
            else:
                _mark_failed(model)
    except (asyncio.TimeoutError, Exception):
        _mark_failed(model)
    return None


async def _try_groq(session, model, messages, timeout, api_key):
    if not api_key:
        return None
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.8,
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        async with session.post(
            GROQ_CHAT_URL, json=payload, headers=headers,
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                content = data["choices"][0]["message"]["content"].strip()
                if content:
                    _mark_ok(f"groq:{model}")
                    return content
            else:
                _mark_failed(f"groq:{model}")
    except (asyncio.TimeoutError, Exception):
        _mark_failed(f"groq:{model}")
    return None


async def _try_together(session, model, messages, timeout, api_key):
    if not api_key:
        return None
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.8,
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        async with session.post(
            TOGETHER_CHAT_URL, json=payload, headers=headers,
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                content = data["choices"][0]["message"]["content"].strip()
                if content:
                    _mark_ok(f"together:{model}")
                    return content
            else:
                _mark_failed(f"together:{model}")
    except (asyncio.TimeoutError, Exception):
        _mark_failed(f"together:{model}")
    return None


async def zen_chat(messages, timeout=None):
    from .config import load_config

    _load_health()

    if timeout is None:
        timeout = RACE_TIMEOUT

    cfg = load_config()
    groq_key = cfg.get("groq_api_key")
    together_key = cfg.get("together_api_key")

    zen_models = await _discover_zen_models()
    healthy_zen = [m for m in zen_models if _is_healthy(m)]
    all_zen = healthy_zen + [m for m in zen_models if not _is_healthy(m)]

    async with aiohttp.ClientSession() as session:
        pairs = []
        models_copy = all_zen[:]
        while models_copy:
            m1 = models_copy.pop(0)
            m2 = models_copy.pop(0) if models_copy else None
            pairs.append((m1, m2))

        for i, (m1, m2) in enumerate(pairs):
            tasks = [_try_zen(session, m1, messages, timeout)]
            if m2:
                tasks.append(_try_zen(session, m2, messages, timeout))

            done = await asyncio.gather(*tasks)
            for result in done:
                if result:
                    return result

        for model in all_zen:
            result = await _try_zen(session, model, messages, FALLBACK_TIMEOUT)
            if result:
                return result

    print("    [!] Zen failed, trying Groq fallback...")
    async with aiohttp.ClientSession() as session:
        for model in GROQ_MODELS:
            result = await _try_groq(session, model, messages, FALLBACK_TIMEOUT, groq_key)
            if result:
                return result

    print("    [!] Groq failed, trying Together fallback...")
    async with aiohttp.ClientSession() as session:
        for model in TOGETHER_MODELS:
            result = await _try_together(session, model, messages, FALLBACK_TIMEOUT, together_key)
            if result:
                return result

    return None
