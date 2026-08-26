import asyncio
import json
import re
from datetime import datetime, timezone

import aiohttp

from .core import ensure_connected
from .config import (
    load_accounts,
    load_config,
    save_accounts,
    load_chat_history,
    save_chat_history,
)
from .gender import detect_gender, get_gender_emoji
from .evolution import (
    detect_relationship_via_ai,
    get_fallback_relationship,
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

CHAT_HISTORY_LIMIT = 20


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


def format_chat_for_ai(messages, my_name="You"):
    now = datetime.now(timezone.utc)
    now_str = now.strftime("%A, %B %d, %Y at %H:%M UTC")

    if not messages:
        return "No previous conversation history."

    lines = [f"Current time: {now_str}"]
    for m in reversed(messages):
        ts = m.get("date", "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts)
                ts = dt.strftime("%a %b %d, %H:%M")
            except (ValueError, TypeError):
                ts = ""
        speaker = my_name if m.get("from_me") else m.get("sender", "Them")
        text = m.get("text", "")
        if ts:
            lines.append(f"[{ts}] {speaker}: {text}")
        else:
            lines.append(f"{speaker}: {text}")
    return "\n".join(lines)


async def save_chat_from_telegram(client, entity, target):
    messages = []
    my_id = (await client.get_me()).id

    async for msg in client.iter_messages(entity, limit=CHAT_HISTORY_LIMIT):
        if not msg.text:
            continue

        sender = await msg.get_sender()
        sender_name = ""
        if sender:
            sender_name = getattr(sender, "first_name", "") or ""
        if not sender_name:
            sender_name = "friend"

        from_me = msg.sender_id == my_id or msg.out

        messages.append({
            "id": msg.id,
            "from_me": from_me,
            "sender": sender_name,
            "text": msg.text,
            "date": msg.date.isoformat() if msg.date else None,
        })

    save_chat_history(target, messages, last_checked=datetime.now(timezone.utc).isoformat())
    return messages


async def analyze_message_intent(message_text, sender_name, sender_gender, chat_context=""):
    context_block = ""
    if chat_context and chat_context != "No previous conversation history.":
        context_block = f"\nConversation history:\n{chat_context}\n"

    prompt = f'''Analyze this Telegram message and respond with ONLY a valid JSON object (no markdown, no explanation, no code blocks):
{context_block}
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


async def generate_ai_reply(msg_text, sender_name, sender_gender, user_gender, relationship, intent_analysis, chat_context=""):
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

    history_block = ""
    if chat_context and chat_context != "No previous conversation history.":
        history_block = f"""
Chat history with {sender_name}:
---
{chat_context}
---

Use this history to understand the conversation flow. Reference earlier messages when relevant. Do NOT repeat something already said in the history.
"""

    prompt = f'''You are replying to a Telegram message. Your persona and context:

{persona}
{history_block}
Message intent: {intent}
Message sentiment: {sentiment}
Message summary: {summary}

What to do: {instruction}

Original message from {sender_name}: "{msg_text}"

TIME AWARENESS (critical):
- The chat history includes timestamps — use them
- If the message was sent today, reply as if its happening now
- If the message was sent yesterday or earlier, acknowledge the gap naturally (e.g. "sorry just seeing this", "oh i missed this", "just saw this")
- Match your tense to when the message was sent — dont say "that sounds great" about something from 3 days ago
- If they messaged days ago and you're replying now, its okay to shift topics or just acknowledge the late reply casually
- Pay attention to day names in timestamps (Mon, Tue, etc) to figure out relative timing

Generate a reply that sounds like a real person texting:
- Be natural, conversational, and authentic
- Match the way real people text — casual, imperfect, human
- Use contractions (dont, cant, youre, im)
- Vary your sentence length — some short, some longer
- Occasionally use casual filler like "haha", "lol", "ngl", "tbh" where it fits
- Mirror the energy and tone of the original message
- Never use more than 1 emoji per reply, and only if the other person uses emojis
- Never starts sentences with emojis
- Never mentions being AI or a bot
- Never breaks character
- Keep it 1-2 sentences max
- Sound like you actually care about what they said

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


async def generate_reply(msg_text, sender_name, sender_gender, user_gender, relationship, chat_context=""):
    intent_analysis = await analyze_message_intent(msg_text, sender_name, sender_gender, chat_context)
    reply = await generate_ai_reply(
        msg_text, sender_name, sender_gender, user_gender, relationship, intent_analysis, chat_context
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
    my_name = me.first_name or "You"
    print(f"[+] Logged in as: {me.first_name} (@{me.username})")

    total_replied = 0
    skipped = 0
    relationship_updates = []

    for target in targets:
        try:
            entity = await client.get_entity(target)

            acc_idx = find_account_index(accounts, target)
            if acc_idx == -1:
                continue

            acc = accounts[acc_idx]
            current_relationship = acc.get("relationship", "undetermined")

            chat_messages = await save_chat_from_telegram(client, entity, target)

            if not chat_messages:
                print(f"  [~] {target}: No messages in chat")
                continue

            last_msg_data = chat_messages[0]

            if last_msg_data["from_me"]:
                print(f"  [~] {target}: Last message is ours, skipping")
                continue

            last_text = last_msg_data["text"]
            sender_name = last_msg_data["sender"]

            sender_gender = detect_gender(sender_name)
            gender_icon = get_gender_emoji(sender_gender)

            chat_context = format_chat_for_ai(chat_messages, my_name)

            new_relationship, confidence, reasoning = await detect_relationship_via_ai(
                chat_context, sender_name, sender_gender, user_gender
            )

            if not new_relationship:
                new_relationship, confidence, reasoning = get_fallback_relationship(chat_context)

            if new_relationship != current_relationship:
                accounts[acc_idx]["relationship"] = new_relationship
                relationship_updates.append((target, current_relationship, new_relationship, confidence))
                print(f"  [*] {target}: Relationship updated: {current_relationship} -> {new_relationship} (confidence: {confidence})")

            relationship = accounts[acc_idx].get("relationship", "polite")

            reply = await generate_reply(last_text, sender_name, sender_gender, user_gender, relationship, chat_context)

            if not reply:
                skipped += 1
                print(f"  [-] {target}: {gender_icon}{sender_name} - API unavailable, skipping")
                continue

            last_msg_id = last_msg_data["id"]
            await client.send_message(entity, reply, reply_to=last_msg_id)
            total_replied += 1

            accounts[acc_idx]["replied_messages"] = accounts[acc_idx].get("replied_messages", [])
            accounts[acc_idx]["replied_messages"].append(last_msg_id)
            accounts[acc_idx]["replied_messages"] = accounts[acc_idx]["replied_messages"][-100:]

            rel_icon = {"romantic": "💕", "friendly": "🤝", "polite": "👔", "professional": "💼"}.get(relationship, "❓")
            print(f"  [>] {target}: {gender_icon}{sender_name} [{relationship}{rel_icon}]")
            print(f"      msg: '{last_text[:60]}...'")
            print(f"      reply: '{reply[:60]}...'")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"  [!] {target}: Error - {e}")

    save_accounts(accounts)

    print(f"\n[+] Done. Replied to {total_replied} messages across {len(targets)} accounts.")
    if skipped:
        print(f"  Skipped {skipped} message(s) - API unavailable.")
    if relationship_updates:
        print("\n  Relationship updates:")
        for target, old_rel, new_rel, conf in relationship_updates:
            print(f"    {target}: {old_rel} -> {new_rel} (confidence: {conf})")

    await client.disconnect()


def check_main():
    asyncio.run(run_check())
