from app.bot.bot import create_bot

app = create_bot()

print("🤖 Atlas AI Bot Started...")

app.run_polling()