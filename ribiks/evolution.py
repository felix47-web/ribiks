async def detect_relationship_via_ai(chat_context, sender_name, sender_gender, user_gender):
    from .check import zen_chat, parse_json_response

    if not chat_context or chat_context == "No previous conversation history.":
        return None, None, None

    prompt = f'''Analyze this conversation between two people and determine their relationship.

Chat history:
---
{chat_context}
---

Based on the conversation tone, language, pet names, topics, and emotional closeness, classify the relationship.

Reply with ONLY a valid JSON object:
{{"relationship": "romantic|friendly|polite|professional", "confidence": "high|medium|low", "reasoning": "one sentence explaining why"}}

Classification guide:
- romantic: intimate, pet names (babe, love, darling), deep emotional connection, flirting
- friendly: casual, fun, slang, jokes, relaxed closeness, no romantic language
- polite: respectful, brief, surface-level, no slang or intimacy
- professional: work-related topics, formal tone, business context, career discussions'''

    messages = [
        {"role": "system", "content": "You are a relationship classifier. Reply with only valid JSON."},
        {"role": "user", "content": prompt},
    ]
    response = await zen_chat(messages)
    result = parse_json_response(response)

    if result and "relationship" in result:
        rel = result["relationship"]
        if rel in ("romantic", "friendly", "polite", "professional"):
            confidence = result.get("confidence", "medium")
            reasoning = result.get("reasoning", "")
            return rel, confidence, reasoning

    return None, None, None


def get_fallback_relationship(chat_context):
    if not chat_context or chat_context == "No previous conversation history.":
        return "polite", "low", "No conversation history available"

    text = chat_context.lower()

    romantic_count = 0
    romantic_words = [
        "love", "babe", "baby", "darling", "sweetheart", "honey",
        "miss you", "kiss", "heart", "my love", "soulmate", "forever",
        "together", "beautiful", "handsome", "adorable",
    ]
    for w in romantic_words:
        if w in text:
            romantic_count += 1

    professional_count = 0
    professional_words = [
        "meeting", "deadline", "project", "report", "office", "client",
        "schedule", "proposal", "budget", "team", "manager", "presentation",
        "invoice", "contract", "quarter", "review",
    ]
    for w in professional_words:
        if w in text:
            professional_count += 1

    polite_count = 0
    polite_words = [
        "thank you", "please", "excuse me", "sorry", "appreciate",
        "kindly", "respectfully", "regards", "sir", "ma'am",
    ]
    for w in polite_words:
        if w in text:
            polite_count += 1

    scores = {
        "romantic": romantic_count,
        "professional": professional_count,
        "polite": polite_count,
        "friendly": 0,
    }

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "polite", "low", "Could not determine relationship from context"

    return best, "low", f"Keyword-based detection (AI unavailable)"


def get_relationship_prompt(relationship, user_gender, sender_gender):
    prompts = {
        "romantic": {
            ("male", "female"): "You are a boyfriend texting his girlfriend. Be warm and affectionate but sound like a real person, not a love poem. Use pet names occasionally (babe, love) but not every sentence. Be playful, teasing, genuine. Text like you actually know her.",
            ("male", "male"): "You are a boyfriend texting his boyfriend. Be warm and affectionate but sound like a real person. Use pet names occasionally (babe, love, bro) but not every sentence. Be playful, genuine. Text like you actually know him.",
            ("female", "male"): "You are a girlfriend texting your boyfriend. Be sweet and caring but sound like a real person, not a script. Use pet names occasionally (babe, love) but not every sentence. Be playful, teasing, genuine. Text like you actually know him.",
            ("female", "female"): "You are a girlfriend texting your girlfriend. Be sweet and caring but sound like a real person. Use pet names occasionally (babe, love) but not every sentence. Be playful, genuine. Text like you actually know her.",
        },
        "friendly": {
            "default": "You are a close friend texting casually. Be chill, use slang naturally, crack jokes, match their energy. Talk like you would with your actual friend. No pet names, no flirting, no formal language.",
        },
        "polite": {
            "default": "You are an acquaintance having a polite conversation. Be friendly but measured. Keep it brief and respectful. No slang, no jokes, no pet names.",
        },
        "professional": {
            "default": "You are a colleague texting about work. Be clear, concise, and professional. Use proper grammar. Keep it focused on the topic. No slang, no pet names, no humor.",
        },
    }

    if relationship == "romantic":
        key = (user_gender or "male", sender_gender or "female")
        return prompts["romantic"].get(key, prompts["romantic"][("male", "female")])

    return prompts.get(relationship, prompts["friendly"]).get("default", prompts["friendly"]["default"])
