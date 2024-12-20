import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler
import speedtest

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = "7817412794:AAEkHoi-vn3MVC7n_RFtDaGSIfe3e6v33ko"
bot = Bot(token=BOT_TOKEN)

# Initialize Flask app
app = Flask(__name__)

# Initialize Dispatcher (single-threaded for serverless)
dispatcher = Dispatcher(bot, None, workers=0)

# Define bot commands
def start(update: Update, context):
    update.message.reply_text("Welcome to Speed Test Bot! Use /speedtest to check your internet speed.")

def speedtest_command(update: Update, context):
    update.message.reply_text("Testing your internet speed. Please wait...")

    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        ping = st.results.ping

        result = (
            f"**Speed Test Results:**\n"
            f"Download Speed: {download_speed:.2f} Mbps\n"
            f"Upload Speed: {upload_speed:.2f} Mbps\n"
            f"Ping: {ping:.2f} ms"
        )
        update.message.reply_text(result)
    except Exception as e:
        logger.error(f"Error during speed test: {e}")
        update.message.reply_text("Failed to perform speed test. Please try again later.")

# Add commands to the dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("speedtest", speedtest_command))

# Webhook route for Telegram
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        json_update = request.get_json(force=True)
        update = Update.de_json(json_update, bot)
        dispatcher.process_update(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return "Internal Server Error", 500

# Health check route
@app.route("/", methods=["GET"])
def index():
    return "Speed Test Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
    
