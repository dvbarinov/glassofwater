# Glass Of Water
Glass Of Water is a smart Telegram bot to help you track your daily water intake, stay hydrated, and build a healthy habit — with multi-language support, reminders, and beautiful statistics.**

---

## ✨ Features

- **💧 Water Tracking**: Log water intake via messages, commands, or quick buttons.
- **📊 Statistics**: View daily progress and weekly trends with ASCII bars or beautiful charts (Matplotlib).
- **🔔 Smart Reminders**: Get notified **100 minutes after your last drink** (not fixed intervals!).
- **🌐 Multi-language**: English, Russian (easy to add more via JSON or Crowdin).
- **🔄 Hot-reload Translations**: Edit `.json` files — changes apply instantly without restart.
- **⚙️ Customizable**: Set your own daily goal, change language anytime.
- **📱 User-Friendly**: Inline keyboards, progress visualization, intuitive UX.

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- pip
- [Telegram Bot Token](https://t.me/BotFather)

### 1. Clone the repo


### 2. Set up virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Create `.env` file:
```env
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
# Optional: I18N_AUTO_GENERATE=1 (enabled by default)
```

> 💡 Get your `BOT_TOKEN` from [@BotFather](https://t.me/BotFather).

### 5. Run the bot (Polling mode)
```bash
python main.py
```

Now open Telegram, find your bot, and send `/start`!

---

## 🌍 Localization (i18n)

### Add a new language
1. Create `locales/xx.json` (e.g., `fr.json`)
2. Add translations:
   ```json
   {
     "start.greeting": "👋 Salut !"
   }
   ```
3. Add language code to `SUPPORTED_LANGUAGES` in `utils/i18n.py`

### Auto-generate missing keys
- When you use `get_text("new.key")` in code, missing keys are **automatically added** to all `.json` files as:
  ```json
  "new.key": "MISSING: new.key"
  ```

> 💧 **Stay hydrated, stay healthy!**  
> This bot is designed to gently nudge you toward better hydration habits — because even robots care about your well-being.