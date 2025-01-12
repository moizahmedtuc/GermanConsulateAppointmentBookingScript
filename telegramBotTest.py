import telegram
import asyncio

# Telegram bot token and chat ID
BOT_TOKEN = '8170088016:AAEYWvDPdpUWeLRh56f8_53nNielfmXKZyQ'
CHAT_ID = '5591971533'

# Telegram bot setup
bot = telegram.Bot(token=BOT_TOKEN)

async def test_telegram_notification():
    message = "This is a test notification from your bot."
    await bot.send_message(chat_id=CHAT_ID, text=message)

# Call the asynchronous function
if __name__ == "__main__":
    asyncio.run(test_telegram_notification())