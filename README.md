# Telegram Bot v1.0.1
<img width="717" height="202" alt="image" src="https://github.com/user-attachments/assets/1a4994d4-d84c-4f18-bb37-5bb5079e16e8" />




A comprehensive and powerful Python-based Telegram bot designed for efficient message management, forwarding, and automation. Built with **Telethon**, this bot offers a rich terminal interface for managing your Telegram chats.

## 🚀 Features

### 🔄 Advanced Forwarding
- **Live Forward**: Real-time forwarding of new messages from source to destination chats.
- **Past Forward**: Forward historical messages from chat history.
- **Clone Channel (Wizard)**: A guided, step-by-step wizard to clone all content from one channel to another easily.

### 📨 Message Management
- **Broadcast Message**: Send a single message to multiple selected chats simultaneously. Great for announcements.
- **Export Chat History**: Export full chat history to local files in **JSON** (complete data) or **TXT** (readable) formats.
- **Delete Messages**: Bulk delete your own messages from specific groups.
- **Find User Messages**: Track, find, and download messages/media from specific users across your chats.

### 📊 Insights & Utilities
- **Statistics Dashboard**: View real-time stats about your cached chats, active rules, and storage usage.
- **Multi-Account Support**: Seamlessly switch between multiple Telegram accounts.
- **Rich CLI**: Beautiful, colorful, and interactive terminal interface.

---

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Telegram-Bot-v1.0.1.git
   cd Telegram-Bot-v1.0.1
   ```

2. **Install dependencies**
   Ensure you have Python 3.7+ installed.
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up directories**
   The bot will automatically create necessary folders (`resources`, `sessions`, `media`, `exports`) on the first run, but you can create them manually if preferred.

---

## ⚙️ Configuration

1. **Get API Credentials**
   - Go to [my.telegram.org](https://my.telegram.org/apps)
   - Log in and create a new application.
   - Copy your **App api_id** and **App api_hash**.

2. **First Run**
   ```bash
   python main.py
   ```
   - The bot will prompt you to enter your `API_ID`, `API_HASH`, and Phone Number.
   - Enter the verification code sent to your Telegram account.
   - These credentials are saved locally for future use.

---

## 📖 Usage Guide

Run the bot using:
```bash
python main.py
```

### Main Menu Options:

1.  **Add/Update Credentials**: Setup or change your API keys.
2.  **List Chats**: Fetch and cache your current list of groups, channels, and chats. **(Run this first!)**
3.  **Delete My Messages**: Bulk delete messages you sent in specific groups.
4.  **Find User Messages**: Search for messages from a specific user ID/username.
5.  **Live Forward Messages**: Configure and start real-time forwarding rules.
6.  **Past Forward Messages**: Forward old messages from history based on saved configs.
7.  **Switch Account**: Log out and switch to a different saved session.
8.  **Export Chat History**: Save chat logs to `exports/` folder.
9.  **Broadcast Message**: Send a mass message to selected chats.
10. **Clone Channel (Wizard)**: Quickly clone one channel to another.
11. **Statistics**: View bot usage and storage stats.
0.  **Exit**: Close the application.

---

## 📂 Project Structure

```
.
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── bot_activity.log        # Runtime logs
├── media/                  # Downloaded media files
├── exports/                # Exported chat history files
├── sessions/               # Telegram session files (DO NOT SHARE)
├── resources/              # JSON configs (chats, rules, etc.)
└── source/
    ├── core/               # Core bot logic (Telegram client)
    ├── dialog/             # Interactive UI menus
    ├── menu/               # Menu handlers
    ├── model/              # Data models
    ├── service/            # Business logic services
    └── utils/              # Helpers and constants
```

## 🔒 Security & Privacy

- **Session Files**: Your `sessions/` folder contains your login session. **NEVER share these files** or commit them to public repositories.
- **API Credentials**: Keep your `API_ID` and `API_HASH` private.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
