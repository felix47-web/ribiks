import re

ROMANCE_KEYWORDS = [
    "love", "miss you", "miss u", "babe", "baby", "darling", "sweetheart",
    "honey", "boo", "adorable", "precious", "beautiful", "handsome",
    "kiss", "kisses", "hug", "cuddle", "date", "relationship",
    "together", "forever", "always", "heart", "soul", "my love",
    "i love", "love you", "luv u", "luv you", "iloveyou", "ily",
    "xoxo", "hun", "loveeee", "lovveee", "bae", "hubby", "wifey",
    "my person", "my everything", "complete me", "soulmate",
    "good morning beautiful", "good night baby", "thinking of you",
    "dream about you", "cant wait to see you", "counting down",
    "you mean everything", "youre my world", "cant live without",
    "need you", "want you", "youre mine", "mine forever",
    "hottie", "cutie", "sweetie", "gorgeous", "stunning",
    "wish you were here", "come over", "miss your face",
    "❤️", "💕", "💗", "💖", "💘", "💝", "😍", "🥰", "😘", "💋",
    "心跳", "爱你", "宝贝", "亲爱的", "想你",
    "te amo", "mi amor", "cariño", "mi vida", "corazon",
    "ich liebe", "schatz", "liebling",
    "je t'aime", "mon coeur", "ma chere",
]

ROMANTIC_EMOJI = {"❤️", "💕", "💗", "💖", "💘", "💝", "😍", "🥰", "😘", "💋", "💑", "💏", "💏"}

ROMANCE_SCORE_PER_KEYWORD = 10
ROMANCE_SCORE_PER_EMOJI = 5
UPGRADE_THRESHOLD = 70
DOWNGRADE_THRESHOLD = 20
SCORE_DECAY = 5


def analyze_message_tone(text):
    if not text:
        return "neutral", 0

    text_lower = text.lower()
    score = 0

    for kw in ROMANCE_KEYWORDS:
        if kw in text_lower:
            score += ROMANCE_SCORE_PER_KEYWORD

    for char in text:
        if char in ROMANTIC_EMOJI:
            score += ROMANCE_SCORE_PER_EMOJI

    if score >= 30:
        return "romantic", min(score, 100)
    elif score >= 10:
        return "flirty", min(score, 100)

    return "neutral", score


def calculate_romance_score(messages):
    if not messages:
        return 0

    total = 0
    for msg in messages:
        if msg and not getattr(msg, "out", True):
            text = getattr(msg, "text", "") or ""
            _, score = analyze_message_tone(text)
            total += score

    avg = total // max(len(messages), 1)
    return min(avg, 100)


def update_romance_score(current_score, new_messages):
    new_score = calculate_romance_score(new_messages)

    if new_score > current_score:
        return min(current_score + new_score, 100)
    else:
        return max(current_score - SCORE_DECAY, 0)


def check_relationship_evolution(target, current_relationship, romance_score):
    if current_relationship == "friendly" and romance_score >= UPGRADE_THRESHOLD:
        return "romantic", True

    if current_relationship == "romantic" and romance_score <= DOWNGRADE_THRESHOLD:
        return "friendly", True

    return current_relationship, False


def get_relationship_prompt(relationship, user_gender, sender_gender):
    prompts = {
        "romantic": {
            ("male", "female"): "You are a sweet and caring boyfriend replying to your girlfriend. She is female. Use pet names like babe, love, sweetheart, darling. Be warm, affectionate, and romantic. Keep it short and natural.",
            ("male", "male"): "You are a sweet and caring boyfriend replying to your boyfriend. He is male. Use pet names like babe, love, handsome, darling. Be warm, affectionate, and romantic. Keep it short and natural.",
            ("female", "male"): "You are a sweet and caring girlfriend replying to your boyfriend. He is male. Use pet names like babe, love, handsome, darling. Be warm, affectionate, and romantic. Keep it short and natural.",
            ("female", "female"): "You are a sweet and caring girlfriend replying to your girlfriend. She is female. Use pet names like babe, love, sweetheart, darling. Be warm, affectionate, and romantic. Keep it short and natural.",
        },
        "friendly": {
            "default": "You are a close friend having a casual chat. Be fun, use slang, crack jokes, match their energy. Keep it relaxed and natural. Do NOT use romantic pet names like babe, love, or sweetheart. No flirting.",
        },
        "polite": {
            "default": "You are a polite and respectful acquaintance. Be friendly but professional. Keep it brief and courteous. No slang, no jokes, no pet names.",
        },
    }

    if relationship == "romantic":
        key = (user_gender or "male", sender_gender or "female")
        return prompts["romantic"].get(key, prompts["romantic"][("male", "female")])

    return prompts.get(relationship, prompts["friendly"]).get("default", prompts["friendly"]["default"])


def get_fallback_messages(relationship, sender_gender):
    fallbacks = {
        "romantic": {
            "female": [
                "Aww that's so sweet babe 💕",
                "I love you so much 😘",
                "You always make my day better 😍",
                "Can't stop thinking about you 🥰",
                "You're the best thing that happened to me 💗",
                "Missing you right now 😢",
                "You're literally the cutest 🥺💕",
                "My heart belongs to you ❤️",
                "You just made me smile so hard 🥰",
                "I'm so lucky to have you 💕",
                "You're everything to me babe 💖",
                "Come here and give me a hug 🤗",
            ],
            "male": [
                "Hey handsome 😍",
                "You always know how to make me smile ❤️",
                "I'm so lucky to have you babe 💕",
                "Miss you already 🥺",
                "You're my favorite person 💗",
                "Can't wait to see you 😘",
                "You're so sweet to me 🥰",
                "My heart is all yours 💖",
                "You make me so happy 🥺💕",
                "I love you more than words can say ❤️",
                "Hey cutie, thinking of you 😍",
                "You're the sweetest babe 💕",
            ],
        },
        "friendly": [
            "Haha that's hilarious 😂",
            "No way, that's wild 😂",
            "That's crazy! 🔥",
            "I swear 😂😂",
            "Lol true true",
            "For real though 🔥",
            "I feel you 💯",
            "Haha you're too much 😂",
            "Bruh 💀",
            "That's insane 😂",
            "LMAOOO 😂",
            "You're something else 😂",
            "Say less 🔥",
            "That's mad 😂",
            "Dead 💀",
            "I can't 💀",
        ],
        "polite": [
            "That's nice, thank you for sharing.",
            "I appreciate you letting me know.",
            "Sounds good!",
            "Noted, thanks.",
            "That's great to hear.",
            "Thank you!",
            "I see, that makes sense.",
            "Okay, got it.",
            "That's interesting.",
            "Thanks for the update.",
        ],
    }

    options = fallbacks.get(relationship, fallbacks["friendly"])
    if isinstance(options, dict):
        options = options.get(sender_gender, options.get("female", list(options.values())[0]))

    import random
    return random.choice(options)
