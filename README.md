# Ribiks

Telegram Chat Autoreply & Group Scanner

Automated Telegram chat replying with AI-powered responses and group member scanning.

## Features

- **AI Auto-Reply** - Generates humanlike, context-aware, time-sensitive replies to specified accounts
- **AI Relationship Detection** - Automatically determines relationship status from chat history
- **Gender Detection** - Detects sender gender from 1000+ names (Nigerian, American, European)
- **Group Scanner** - Extracts member info from all groups in your account
- **Target Accounts** - Only replies to accounts you specify
- **Auto-Updater** - Built-in update system
- **Interactive Menu** - Clean terminal UI for easy management
- **CLI Commands** - Direct commands for scripting and automation

## Installation

```bash
git clone https://github.com/felix47-web/ribiks.git
cd ribiks
chmod +x install.sh
./install.sh
```

## Updating

```bash
# If installed via git
ribiks update

# Or one-liner
curl -fsSL https://raw.githubusercontent.com/felix47-web/ribiks/main/update.sh | bash
```

## Quick Start

```bash
# First-time setup (now asks for your gender)
ribiks setup

# Add target accounts
ribiks accounts add @username
ribiks accounts add @friend

# Check and auto-reply
ribiks check

# Scan groups
ribiks groups -check

# Interactive menu
ribiks
```

## Commands

| Command | Description |
|---------|-------------|
| `ribiks` | Launch interactive menu |
| `ribiks setup` | First-time setup (API, phone, gender) |
| `ribiks check` | Refresh & auto-reply to target accounts |
| `ribiks groups -check` | Scan groups for member info |
| `ribiks accounts list` | List targets with relationship info |
| `ribiks accounts add <user>` | Add target account |
| `ribiks accounts remove <user>` | Remove target account |
| `ribiks accounts toggle <user>` | Enable/disable target |
| `ribiks update` | Check for and install updates |
| `ribiks update --check` | Check only (don't install) |
| `ribiks --help` | Show help |
| `ribiks --version` | Show version |

## Configuration

During setup, you'll need:
1. **Telegram API ID** - Get from https://my.telegram.org
2. **Telegram API Hash** - Get from https://my.telegram.org
3. **Phone Number** - Your Telegram phone number
4. **OTP Code** - Sent to your Telegram
5. **Your Gender** - Male/Female (used to tailor reply personality)

### Optional: OpenAI API Key

For intelligent AI replies, add your OpenAI API key:
```bash
ribiks setup
# Enter your OpenAI API key when prompted
```

Without an API key, Ribiks uses pre-set messages based on relationship type.

## Relationship Types

| Type | Reply Style |
|------|-------------|
| `romantic` | Sweet, affectionate, pet names (babe, love, sweetheart) |
| `friendly` | Casual, fun, slang, jokes - no romantic pet names |
| `polite` | Courteous, respectful, brief, no slang |
| `professional` | Work-focused, formal tone, proper grammar |

### AI Relationship Detection

Ribiks automatically determines the relationship type by analyzing your last 20 messages with each contact. The AI considers conversation tone, language, pet names, topics, and emotional closeness to classify the relationship as romantic, friendly, polite, or professional. Each classification includes a confidence level (high/medium/low).

## Requirements

- Python 3.8+
- telethon
- requests

## Platform

- Kali Linux (recommended)
- Ubuntu/Debian
- Termux (Android)

## License

MIT
