# Atlas AI – Personal Financial Assistant

Atlas AI is a Telegram-based personal financial assistant that helps users monitor stocks, receive financial news, manage a watchlist, and get personalized financial briefings.

The application uses Gemini for conversational AI and financial intent detection, while SQLite/SQLAlchemy stores user profiles, conversations, watchlists, and briefing preferences.

## Features

* 🤖 AI-powered financial conversation
* 👤 User onboarding and personalized profiles
* 📈 Real-time stock price lookup
* 🏢 Company research
* 📰 Financial news
* 📋 Personal stock watchlist
* 🚨 Automated watchlist price-movement alerts
* 📊 Personalized financial briefings
* ⏰ Scheduled daily briefings
* 💬 Conversation history
* 🛡️ Duplicate alert prevention
* 📱 Telegram bot interface

## Tech Stack

* **Python**
* **python-telegram-bot**
* **Google Gemini API**
* **SQLAlchemy**
* **SQLite**
* **yfinance**
* **APScheduler**
* **Pydantic Settings**

## Project Structure

```text
atlas-finance-assistant/
│
├── app/
│   ├── ai/
│   │   ├── gemini_client.py
│   │   ├── intent_detector.py
│   │   └── profile_extractor.py
│   │
│   ├── bot/
│   │   └── bot.py
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   └── models.py
│   │
│   └── services/
│       ├── alert_service.py
│       ├── briefing_service.py
│       ├── company_service.py
│       ├── conversation_service.py
│       ├── finance_service.py
│       ├── news_service.py
│       ├── onboarding_service.py
│       ├── scheduler_service.py
│       ├── user_service.py
│       └── watchlist_service.py
│
├── test_alert.py
├── init_db.py
├── run_bot.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Environment Variables

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./atlas.db
```

Never commit the `.env` file or API keys to GitHub.

## Installation

Clone the repository:

```bash
git clone https://github.com/Yash82005/atlas-finance-assistant.git
cd atlas-finance-assistant
```

Create and activate a virtual environment:

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Initialize the database:

```powershell
python init_db.py
```

## Running the Bot

Start Atlas AI:

```powershell
python run_bot.py
```

The bot should start with:

```text
🤖 Atlas AI Bot Started...
```

Open Telegram and send `/start` to begin onboarding.

## Main Commands

```text
/start       Start Atlas AI and complete onboarding
/briefing    Generate a personalized financial briefing
/setbriefing Set the daily briefing time
/watchlist   View the current watchlist
/myprofile   View the user profile
/help        Display available commands
```

## Watchlist Alerts

Atlas AI periodically checks stocks in the user's watchlist.

When a stock's daily movement reaches the configured threshold, the bot sends a Telegram notification.

Example:

```text
🚨 Atlas Alert

🚨 NVDA 📈 UP
Price: $223.96
Daily change: +2.27%
```

The alert service also stores the latest alert identifier to prevent the same alert from being repeatedly sent.

## Personalized Briefings

Users can request a briefing using:

```text
/briefing
```

The briefing combines:

* User profile
* Financial interests
* Watchlist
* Current market data
* Recent financial news

Gemini generates a concise Telegram-friendly briefing based only on the supplied market and news data.

## AI Architecture

The application separates AI responsibilities into dedicated modules:

```text
Telegram Message
       │
       ▼
Intent Detection
       │
       ├── Stock Price
       ├── Company Research
       ├── Financial News
       ├── Watchlist
       └── General AI Chat
                    │
                    ▼
              Gemini API
                    │
                    ▼
             Telegram Response
```

Personalized briefings follow a separate flow:

```text
User Profile
     +
Watchlist
     +
Market Data
     +
Financial News
     │
     ▼
Gemini Briefing Generator
     │
     ▼
Telegram Briefing
```

## Scheduling

The Telegram bot uses scheduled background jobs for:

* Daily personalized briefings
* Periodic watchlist alert checks

Watchlist alerts are checked periodically rather than only when the user sends a message.

## Testing

To manually test the watchlist alert system:

```powershell
python test_alert.py
```

Example successful output:

```text
ALERTS:
🚨 NVDA 📈 UP
Price: $223.96
Daily change: +2.27%
```

Running the test again without a new alert condition should not produce the same duplicate alert.

## Security

* API credentials are stored in environment variables.
* `.env` is excluded through `.gitignore`.
* Database files are excluded from Git.
* API keys should never be committed to the repository.

## Financial Disclaimer

Atlas AI provides educational financial information only.

The information provided by the application is not financial, investment, tax, or legal advice. Market data can change and may contain inaccuracies. Users should conduct their own research and consult a qualified financial professional before making financial decisions.

## Project Status

Core functionality has been implemented and tested, including:

* Telegram interaction
* User onboarding
* AI chat
* Stock data
* Company research
* Financial news
* Watchlists
* Personalized briefings
* Scheduled briefings
* Watchlist alerts
* Duplicate alert prevention
* Database persistence

## Repository

GitHub:

https://github.com/Yash82005/atlas-finance-assistant
