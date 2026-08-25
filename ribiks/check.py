import asyncio
import json
import re

import aiohttp

from .core import ensure_connected
from .config import load_accounts, load_config, save_accounts
from .gender import detect_gender, get_gender_emoji
from .evolution import (
    update_romance_score,
    check_relationship_evolution,
    get_relationship_prompt,
)

ZEN_URL = "https://opencode.ai/zen/v1/chat/completions"
FREE_MODELS = [
    "nemotron-3-ultra-free",
    "laguna-s-2.1-free",
    "x-preview-f-free",
    "hy3-free",
    "big-pickle",
    "mimo-v2.5-free",
    "nemotron-3.5-lightning-free",
]


async def zen_chat(messages, timeout=30):
    payload = {
        "messages": messages,
        "max_tokens": 256,
        "temperature": 0.8,
    }
    for model in FREE_MODELS:
        payload["model"] = model
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    ZEN_URL, json=payload, timeout=aiohttp.ClientTimeout(total=timeout)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        content = data["choices"][0]["message"]["content"].strip()
                        if content:
                            return content
        except Exception:
            continue
    return None


def parse_json_response(text):
    if not text:
        return None
    match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


async def analyze_message_intent(message_text, sender_name, sender_gender):
    prompt = f'''Analyze this Telegram message and respond with ONLY a valid JSON object (no markdown, no explanation, no code blocks):

Message: "{message_text}"
Sender: {sender_name} ({sender_gender})

Required JSON format:
{{"intent": "question|joke|complaint|compliment|flirt|story|emotion|reply_to_question|other", "sentiment": "positive|negative|neutral", "needs_answer": true, "is_reply_to_question": false, "summary": "one sentence summary"}}

Valid intent values:
- question: user is asking something that needs an answer
- joke: user is being funny or telling a joke
- complaint: user is venting, frustrated, or upset
- compliment: user is praising or saying something nice
- flirt: user is being romantic or flirtatious
- story: user is sharing news, an experience, or telling a story
- emotion: user needs comfort, support, or is expressing deep feelings
- reply_to_question: user is answering a question you previously asked
- other: general casual conversation

Reply with ONLY the JSON object:'''

    messages = [
        {"role": "system", "content": "You are a message intent analyzer. Reply with only valid JSON."},
        {"role": "user", "content": prompt},
    ]
    response = await zen_chat(messages, timeout=30)
    return parse_json_response(response)


async def generate_ai_reply(msg_text, sender_name, sender_gender, user_gender, relationship, intent_analysis):
    intent = intent_analysis.get("intent", "other") if intent_analysis else "other"
    sentiment = intent_analysis.get("sentiment", "neutral") if intent_analysis else "neutral"
    summary = intent_analysis.get("summary", "") if intent_analysis else ""

    persona = get_relationship_prompt(relationship, user_gender, sender_gender)

    intent_instructions = {
        "question": "The sender is asking a question. Provide a helpful, direct answer. Be specific and relevant.",
        "joke": "The sender is being funny or told a joke. Match their humor. Laugh, play along, or roast back.",
        "complaint": "The sender is venting or upset. Be empathetic, validate their feelings, offer support.",
        "compliment": "The sender is giving a compliment. Be grateful, humble, maybe flirt back if appropriate.",
        "flirt": "The sender is flirting. Match their romantic energy, be playful and affectionate.",
        "story": "The sender is sharing news or a story. Engage with their experience, ask follow-up questions.",
        "emotion": "The sender needs emotional support. Be warm, caring, comforting. Listen and validate.",
        "reply_to_question": "The sender is answering a question you asked earlier. Acknowledge their answer naturally.",
        "other": "General conversation. Be natural, engaging, and match the vibe.",
    }

    instruction = intent_instructions.get(intent, intent_instructions["other"])

    prompt = f'''You are replying to a Telegram message. Your persona and context:

{persona}

Message intent: {intent}
Message sentiment: {sentiment}
Message summary: {summary}

What to do: {instruction}

Original message from {sender_name}: "{msg_text}"

Generate a natural, contextual reply that:
- Directly addresses what the message is about
- Matches the intent and sentiment
- Fits the {relationship} relationship style
- Is 1-2 sentences max
- Uses emojis sparingly and naturally
- Never mentions being AI or a bot
- Never breaks character
- Sounds like a real person texting

Reply with ONLY the reply text, nothing else:'''

    messages = [
        {"role": "system", "content": persona},
        {"role": "user", "content": prompt},
    ]
    response = await zen_chat(messages, timeout=30)
    if response:
        cleaned = response.strip().strip('"').strip("'")
        if cleaned and len(cleaned) > 2:
            return cleaned

    return None


async def generate_reply(msg_text, sender_name, sender_gender, user_gender, relationship):
    intent_analysis = await analyze_message_intent(msg_text, sender_name, sender_gender)
    reply = await generate_ai_reply(
        msg_text, sender_name, sender_gender, user_gender, relationship, intent_analysis
    )
    return reply


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

    print(f"[*] AI Backend: Free models (no key required)")

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
    skipped = 0

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

                sender_gender = detect_gender(sender_name)
                gender_icon = get_gender_emoji(sender_gender)

                relationship = accounts[acc_idx].get("relationship", "romantic")

                reply = await generate_reply(msg.text, sender_name, sender_gender, user_gender, relationship)

                if not reply:
                    skipped += 1
                    print(f"  [-] {target}: {gender_icon}{sender_name} - API unavailable, skipping")
                    continue

                await msg.reply(reply)
                replied.add(msg.id)
                total_replied += 1

                rel_icon = {"romantic": "💕", "friendly": "🤝", "polite": "👔"}.get(relationship, "❓")
                print(f"  [>] {target}: {gender_icon}{sender_name} [{relationship}{rel_icon}]")
                print(f"      msg: '{msg.text[:60]}...'")
                print(f"      reply: '{reply[:60]}...'")
                await asyncio.sleep(2)

        except Exception as e:
            print(f"  [!] {target}: Error - {e}")

    save_accounts(accounts)

    print(f"\n[+] Done. Replied to {total_replied} messages across {len(targets)} accounts.")
    if skipped:
        print(f"  Skipped {skipped} message(s) - API unavailable.")
    if evolutions:
        print("\n  Relationship evolutions:")
        for target, old_rel, new_rel in evolutions:
            print(f"    {target}: {old_rel} -> {new_rel}")

    await client.disconnect()


def check_main():
    asyncio.run(run_check())
