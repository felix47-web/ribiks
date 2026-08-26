# Ribiks

Telegram Chat Autoreply & Group Scanner

## Installation

### Termux (Android)

```bash
# Install Termux from F-Droid or GitHub

# Install git and python
pkg update && pkg install git python

# Clone and install
git clone https://github.com/felix47-web/ribiks.git
cd ribiks
chmod +x install.sh
./install.sh
```

### Linux (Ubuntu/Debian/Kali)

```bash
# Install dependencies
sudo apt update && sudo apt install git python3 python3-venv python3-pip

# Clone and install
git clone https://github.com/felix47-web/ribiks.git
cd ribiks
chmod +x install.sh
./install.sh
```

## Setup

### 1. Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Go to **API Development Tools**
4. Create a new application
5. Copy your **API ID** and **API Hash**

### 2. First-Time Setup

```bash
ribiks setup
```

You'll be asked for:
1. **API ID** - From step above
2. **API Hash** - From step above
3. **Phone Number** - Your Telegram number (e.g. +234...)
4. **OTP Code** - Sent to your Telegram
5. **Your Gender** - Male/Female (tailors reply personality)

### 3. Start Using

```bash
# Launch interactive menu
ribiks

# Or use commands directly
ribiks check              # Auto-reply to target accounts
ribiks accounts add @user # Add target account
ribiks groups -check      # Scan groups
ribiks hopin              # Join a random group
```

## Commands

| Command | Description |
|---------|-------------|
| `ribiks` | Launch interactive menu |
| `ribiks setup` | First-time setup |
| `ribiks check` | Auto-reply to targets |
| `ribiks accounts add @user` | Add target |
| `ribiks accounts list` | List targets |
| `ribiks groups -check` | Scan groups |
| `ribiks hopin` | Join random group |
| `ribiks update` | Update ribiks |
| `ribiks --version` | Show version |

## Updating

```bash
ribiks update
```

## Requirements

- Python 3.8+
- Telegram account
