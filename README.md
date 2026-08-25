# Ribiks

Telegram Chat Autoreply & Group Scanner

Automated Telegram chat replying with AI-powered responses and group member scanning.

## Features

- **AI Auto-Reply** - Generates context-aware replies to specified accounts
- **Group Scanner** - Extracts member info from all groups in your account
- **Target Accounts** - Only replies to accounts you specify
- **Interactive Menu** - Clean terminal UI for easy management
- **CLI Commands** - Direct commands for scripting and automation

## Installation

```bash
git clone https://github.com/felix47-web/ribiks.git
cd ribiks
chmod +x install.sh
./install.sh
```

## Quick Start

```bash
# First-time setup
ribiks setup

# Add target accounts
ribiks accounts add @username

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
| `ribiks setup` | First-time setup (API ID, hash, phone, OTP) |
| `ribiks check` | Refresh & auto-reply to target accounts |
| `ribiks groups -check` | Scan groups for member info |
| `ribiks accounts list` | List target accounts |
| `ribiks accounts add <user>` | Add target account |
| `ribiks accounts remove <user>` | Remove target account |
| `ribiks --help` | Show help |
| `ribiks --version` | Show version |

## Configuration

During setup, you'll need:
1. **Telegram API ID** - Get from https://my.telegram.org
2. **Telegram API Hash** - Get from https://my.telegram.org
3. **Phone Number** - Your Telegram phone number
4. **OTP Code** - Sent to your Telegram

### Optional: OpenAI API Key

For intelligent AI replies, add your OpenAI API key:
```bash
ribiks setup
# Enter your OpenAI API key when prompted
```

Without an API key, Ribiks uses pre-set sweet messages.

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
