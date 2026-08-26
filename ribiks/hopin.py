import asyncio
import json
import random

from .core import ensure_connected
from .config import load_config
from .llm import zen_chat

CATEGORIES = [
    "football",
    "music",
    "entertainment",
    "news",
    "politics",
    "art",
    "trucking",
]

COUNTRIES = {
    "1": ("US", "United States"),
    "2": ("DE", "Germany"),
}


async def generate_search_queries(category, country_code, country_name):
    from .check import FREE_MODELS, ZEN_URL

    prompt = f"""Generate Telegram search queries for finding public group chats about {category} for people in {country_name}.

Requirements:
- At least 100 words total across all queries
- Mix of group names, slang, abbreviations, topic phrases
- For Germany: German AND English terms
- For US: English + some Spanish

{country_name} and topic: {category}

IMPORTANT: Output ONLY a JSON array. No explanation, no reasoning, no other text.
["query1", "query2", "query3"]"""

    messages = [
        {"role": "system", "content": "You output ONLY a JSON array. Nothing else. No explanation."},
        {"role": "user", "content": prompt},
    ]

    response = await zen_chat(messages, base_timeout=45)

    if not response:
        return get_fallback_queries(category, country_code)

    queries = parse_query_array(response)
    if queries and len(queries) >= 10:
        return queries

    return get_fallback_queries(category, country_code)


def parse_query_array(text):
    if not text:
        return None

    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end > start:
        try:
            result = json.loads(text[start:end + 1])
            if isinstance(result, list):
                cleaned = []
                for q in result:
                    q = str(q).strip().strip('"').strip("'")
                    if q and len(q) > 2 and len(q) < 80:
                        cleaned.append(q)
                if cleaned:
                    return cleaned
        except json.JSONDecodeError:
            pass

    skip_prefixes = (
        "i ", "the ", "you ", "for ", "reply", "generate", "include",
        "requirements", "output", "here", "let me", "first", "since",
        "wait", "at least", "queries should", "let's", "i need",
        "i'll", "i should", "the user", "this is", "i'm", "okay",
        "now", "my ", "so ", "to ", "a ", "an ", "if ", "but ",
    )
    skip_words = {"json", "array", "example", "note", "see above", "see below"}

    lines = text.split('\n')
    queries = []
    for line in lines:
        line = line.strip()
        line = line.strip('"').strip("'").strip(',').strip('-').strip('*').strip()
        line = line.strip('0123456789.): ')
        if not line or len(line) < 4 or len(line) > 80:
            continue
        lower = line.lower()
        if any(lower.startswith(p) for p in skip_prefixes):
            continue
        if lower in skip_words:
            continue
        if '{' in line or '}' in line or '//' in line:
            continue
        queries.append(line)
    return queries if queries else None


def get_fallback_queries(category, country_code):
    fallback = {
        "football": {
            "US": [
                "NFL fans", "football chat", "american football", "fantasy football",
                "football Sunday", "gridiron", "touchdown", "nfl memes",
                "football discussion", "sports football", "gridiron football",
                "football community", "nfl live", "football nation",
            ],
            "DE": [
                "fußball", "bundesliga", "football germany", "fußball fans",
                "bundesliga chat", "fußball community", "dfb pokal", "soccer germany",
                "fußball discussion", "football deutschland", "champions league deutsch",
            ],
        },
        "music": {
            "US": [
                "music lovers", "hip hop", "rap music", "pop music fans",
                "rock music", "r&b", "country music", "music discovery",
                "new music", "music chat", "concerts", "vinyl collectors",
                "music production", "beat makers", "rap battles",
            ],
            "DE": [
                "musik deutschland", "deutsche musik", "music germany",
                "rap deutsch", "schlager", "techno", "edm germany",
                "musik chat", "german rap", "metal deutsch", "pop musik",
                "music lovers DE", "konzerte deutschland",
            ],
        },
        "entertainment": {
            "US": [
                "movies", "tv shows", "netflix", "anime", "gaming",
                "streaming", "hollywood", "pop culture", "celebrity",
                "entertainment news", "binge watching", "marvel", "dc comics",
                "podcast fans", "anime community", "gaming discord",
            ],
            "DE": [
                "film", "serien", "entertainment deutschland", "anime deutsch",
                "gaming germany", "netflix", "deutsche serien", "kino",
                "popkultur", "musik entertainment", "anime community DE",
                "gaming chat", "streaming deutschland",
            ],
        },
        "news": {
            "US": [
                "news", "breaking news", "world news", "us news",
                "politics", "current events", "reddit news", "media news",
                "tech news", "business news", "headlines", "news live",
                "independent news", "citizen journalism", "news alerts",
            ],
            "DE": [
                "nachrichten", "deutsche nachrichten", "aktuelle nachrichten",
                "politik deutschland", "news germany", "tagesschau",
                "welt nachrichten", "nachrichten chat", "deutschland aktuell",
                "breaking news DE", "deutsche medien", "zeitgeist",
            ],
        },
        "politics": {
            "US": [
                "politics", "us politics", "democrats", "republicans",
                "conservative", "libertarian", "political discussion",
                "vote", "election", "political debate", "left wing",
                "right wing", "centrist", "gun rights", "political news",
            ],
            "DE": [
                "politik", "deutsche politik", "bundestag", "cdu", "spd",
                "grüne", "afd", "fdp", "political discussion germany",
                "deutsche parteien", "politik chat", "wahl",
                "eu politik", "politik deutschland", "demokratie",
            ],
        },
        "art": {
            "US": [
                "art", "digital art", "photography", "painting",
                "art community", "illustration", "design", "graphic design",
                "street art", "nft art", "art gallery", "creative",
                "art share", "art critics", "artists community",
            ],
            "DE": [
                "kunst", "deutsche kunst", "fotografie", "digital kunst",
                "kunst chat", "malerei", "illustration", "design",
                "kunst deutschland", "street art", "künstler",
                "kreativ", "kunst gemeinde", "kunst galerie",
            ],
        },
        "trucking": {
            "US": [
                "trucking", "truckers", "trucker life", "semi trucks",
                "18 wheeler", "trucking community", "cdl", "truck driver",
                "trucking news", "freight", "logistics", "ocean trucking",
                "trucking lifestyle", "owner operator", "trucking usa",
            ],
            "DE": [
                "LKW", "truckers deutschland", "LKW fahrer", "spedition",
                "truckers", "fernfahrer", "logistik", "LKW chat",
                "trucking germany", "spedition chat", "lkw fahrer",
                "güterverkehr", "transport deutschland", "trucker life DE",
            ],
        },
    }

    country_key = "US" if country_code in ("US", "us") else "DE"
    return fallback.get(category, fallback["entertainment"]).get(country_key, [])


async def search_groups(client, queries, limit_per_query=20):
    from telethon.tl.functions.contacts import SearchRequest

    all_results = []
    seen_ids = set()
    shuffled = queries[:]
    random.shuffle(shuffled)

    for query in shuffled[:10]:
        try:
            result = await client(SearchRequest(
                q=query,
                limit=limit_per_query,
            ))

            if hasattr(result, 'chats'):
                for chat in result.chats:
                    if chat.id in seen_ids:
                        continue
                    if not hasattr(chat, 'username') or not chat.username:
                        continue
                    if getattr(chat, 'bot', False):
                        continue
                    if not getattr(chat, 'megagroup', False):
                        continue

                    seen_ids.add(chat.id)
                    all_results.append({
                        "id": chat.id,
                        "title": chat.title,
                        "username": chat.username,
                        "participants_count": getattr(chat, 'participants_count', None),
                        "about": getattr(chat, 'about', '') or '',
                    })

            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"    [~] Search error for '{query}': {type(e).__name__}")
            continue

    return all_results


async def rank_best_group(groups, category, country_code, country_name):
    if not groups:
        return None, None

    if len(groups) == 1:
        return groups[0], "Only one result found"

    group_list = "\n".join([
        f"- @{g['username']} ({g['title']}) - {g.get('participants_count', '?')} members - {g.get('about', '')[:80]}"
        for g in groups[:20]
    ])

    prompt = f"""You are selecting the BEST Telegram group for a user from {country_name} interested in {category}.

Available groups:
{group_list}

Pick the ONE best group that:
1. Is most relevant to {category} in {country_name}
2. Has the most active community (more members = better)
3. Has a matching description

Reply with ONLY a JSON object:
{{"username": "group_username", "reason": "one sentence why"}}"""

    messages = [
        {"role": "system", "content": "You are a group selector. Reply with only valid JSON."},
        {"role": "user", "content": prompt},
    ]

    response = await zen_chat(messages, base_timeout=45)

    if response:
        from .check import parse_json_response
        result = parse_json_response(response)
        if result and "username" in result:
            target_username = result["username"].lower().replace("@", "").strip()
            for g in groups:
                if g["username"].lower() == target_username:
                    return g, result.get("reason", "Best match")

            for g in groups:
                if target_username in g["username"].lower() or g["username"].lower() in target_username:
                    return g, result.get("reason", "Best match")

    scored = []
    for g in groups:
        score = g.get("participants_count") or 0
        about = (g.get("about") or "").lower()
        title = (g.get("title") or "").lower()
        if category in about or category in title:
            score += 50000
        if country_name.lower() in about or country_name.lower() in title:
            score += 30000
        scored.append((score, g))
    scored.sort(key=lambda x: x[0], reverse=True)

    if scored:
        best_score, best = scored[0]
        return best, f"Keyword-scored match (score: {best_score})"

    return groups[0], "Top search result"


async def join_group(client, group):
    from telethon.tl.functions.channels import JoinChannelRequest

    try:
        entity = await client.get_entity(f"@{group['username']}")
        await client(JoinChannelRequest(entity))
        return True, "joined"
    except Exception as e:
        error_msg = str(e).lower()
        if "already" in error_msg or "you are already" in error_msg:
            print(f"    [i] Already in @{group['username']}")
            return True, "already_in"
        if "request" in error_msg or "pending" in error_msg:
            print(f"    [i] Join request sent to @{group['username']} (approval needed)")
            return True, "requested"
        print(f"    [!] Failed to join @{group['username']}: {e}")
        return False, "failed"


async def show_group_info(client, group):
    from telethon.tl.functions.channels import GetFullChannelRequest

    try:
        entity = await client.get_entity(f"@{group['username']}")
        full = await client(GetFullChannelRequest(entity))
        channel = full.chats[0] if full.chats else None
        full_chat = full.full_chat

        print(f"\n  +{'='*48}+")
        print(f"  | {'GROUP JOINED':^46} |")
        print(f"  +{'='*48}+")
        print(f"  | Name     : {group['title']}")
        print(f"  | Username : @{group['username']}")
        print(f"  | Members  : {getattr(full_chat, 'participants_count', 'N/A')}")
        print(f"  | About    : {getattr(full_chat, 'about', 'No description')}")
        print(f"  | Link     : https://t.me/{group['username']}")
        print(f"  +{'='*48}+")

    except Exception:
        print(f"\n  [+] Joined: {group['title']}")
        print(f"      @{group['username']} - https://t.me/{group['username']}")


async def verify_real_group(client, group, category):
    from telethon.tl.functions.channels import GetFullChannelRequest

    title = group.get('title', '')
    members = group.get('participants_count') or 0
    about = ''
    group_username = group.get('username', '')

    try:
        entity = await client.get_entity(f"@{group_username}")
        full = await client(GetFullChannelRequest(entity))
        full_chat = full.full_chat
        about = getattr(full_chat, 'about', '') or ''
    except Exception:
        about = group.get('about', '') or ''

    title_lower = title.lower()
    about_lower = about.lower()

    hard_reject_keywords = [
        "bot", "auto post", "rss feed", "webhook", "automated",
        "notification bot", "alert bot", "play to earn", "mining bot", "captcha bot"
    ]

    for kw in hard_reject_keywords:
        if kw in title_lower:
            return False, f"Title contains '{kw}'"
        if kw in about_lower:
            return False, f"Description contains '{kw}'"

    if "@" in about and "bot" in about_lower:
        return False, "Description references bot accounts"

    if members and members < 15:
        return False, f"Too few members ({members})"

    if not about or len(about.strip()) < 5:
        return False, "No description"

    prompt = f"""Is this a real human Telegram group or a bot/spam/auto-post group?

Group: @{group_username}
Title: {title}
Members: {members}
Description: {about[:300]}

Reply with ONLY a JSON object:
{{"is_real": true/false, "reason": "one sentence why"}}"""

    messages = [
        {"role": "system", "content": "You are a bot group detector. Reply with only valid JSON."},
        {"role": "user", "content": prompt},
    ]

    response = await zen_chat(messages, base_timeout=30)

    if response:
        from .check import parse_json_response
        result = parse_json_response(response)
        if result and "is_real" in result:
            return result["is_real"], result.get("reason", "AI decision")

    return True, "Passed all checks"


async def run_hopin():
    print("\n  ╔══════════════════════════════════════╗")
    print("  ║          HOP IN GROUP                ║")
    print("  ╚══════════════════════════════════════╝\n")

    print("  Select your country:")
    print("    [1] United States")
    print("    [2] Germany")
    country_choice = input("\n  > Select (1/2): ").strip()

    if country_choice not in COUNTRIES:
        print("[!] Invalid choice. Defaulting to US.")
        country_choice = "1"

    country_code, country_name = COUNTRIES[country_choice]

    category = random.choice(CATEGORIES)
    print(f"\n[*] Category: {category.upper()}")
    print(f"[*] Country: {country_name}")

    print("[*] Generating search queries with AI...")
    queries = await generate_search_queries(category, country_code, country_name)
    print(f"[+] Generated {len(queries)} search queries")

    client = await ensure_connected()
    if not client:
        return

    try:
        me = await client.get_me()
        print(f"[+] Logged in as: {me.first_name}\n")

        print("[*] Searching Telegram for public groups...")
        groups = await search_groups(client, queries)
        print(f"[+] Found {len(groups)} public groups")

        if not groups:
            print("[!] No groups found. Try again later.")
            return

        print("[*] AI selecting best group...")
        best_group, reason = await rank_best_group(groups, category, country_code, country_name)

        if not best_group:
            print("[!] Could not determine best group.")
            return

        print(f"[*] Best match: @{best_group['username']}")
        print(f"    Reason: {reason}")

        remaining = [g for g in groups if g["username"] != best_group["username"]]

        print("[*] Verifying group is not a bot group...")
        is_real, verify_reason = await verify_real_group(client, best_group, category)
        if not is_real:
            print(f"    [!] Rejected: {verify_reason}")
            print("[*] Looking for a real group...")
            for alt in remaining[:5]:
                is_real, verify_reason = await verify_real_group(client, alt, category)
                if is_real:
                    best_group = alt
                    print(f"    [+] Verified: @{alt['username']}")
                    break
            else:
                print("[!] No verified human groups found. Joining best match anyway...")
                is_real = True

        print("[*] Joining group...")
        joined, status = await join_group(client, best_group)

        if joined:
            await show_group_info(client, best_group)
            if status == "requested":
                print("  [i] Waiting for admin approval to join.")
        else:
            print("[!] Failed to join. Trying next best group...")
            for alt in remaining[:3]:
                print(f"    [~] Trying @{alt['username']}...")
                joined, status = await join_group(client, alt)
                if joined:
                    best_group = alt
                    await show_group_info(client, best_group)
                    if status == "requested":
                        print("  [i] Waiting for admin approval to join.")
                    break

    finally:
        await client.disconnect()


def hopin_main():
    asyncio.run(run_hopin())
