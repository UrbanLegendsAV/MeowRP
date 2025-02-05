import telebot
import os
import pandas as pd
import requests
from flask import Flask, request

# Load API keys from environment variables
TELEGRAM_BOT_TOKEN = "8136389864:AAH__u-8QlPHsQRyiwqs-f8I4XYd5V7pwrM"


bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, parse_mode="HTML")
server = Flask(__name__)

# Full paths to local CSV files
START_COMMANDS_CSV = "/Users/luisleite/Desktop/meowrp-ai-agent-telegram-prompt-guide/Start_Commands.csv"
BOT_COMMANDS_CSV = "/Users/luisleite/Desktop/meowrp-ai-agent-telegram-prompt-guide/Bot_Commands.csv"

# Load Google Sheets Data
def load_commands():
    try:
        bot_commands_df = pd.read_csv(BOT_COMMANDS_CSV)
        return bot_commands_df
    except Exception as e:
        print(f"❌ Error loading commands: {e}")
        return None

# Fetch All Responses for a Category
def get_bot_response(category, bot_commands_df):
    if bot_commands_df is None:
        return "⚠️ Error: Commands not loaded. Please check Google Sheets format!"

    # Match Category from first column
    result_df = bot_commands_df[bot_commands_df.iloc[:, 0].str.lower() == category.lower()]

    if result_df.empty:
        return "❌ No results found for this category. Try another!"

    # Combine all responses from the "Description" column
    responses = "\n\n".join(result_df["Description"].tolist())
    return responses

# Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🐾 Welcome to MewFi! Your XRPL companion! Type a command to get started 🚀")

# Handle Bot Commands
@bot.message_handler(func=lambda message: message.text.startswith("/"))
def handle_command(message):
    command = message.text.lower().replace("/", "").strip()  # Remove slash and trim spaces
    bot_commands_df = load_commands()

    if bot_commands_df is None:
        bot.reply_to(message, "⚠️ Error: I couldn't load my command database. Please try again later!")
        return

    response = get_bot_response(command, bot_commands_df)
    bot.reply_to(message, response)

# Webhook for Telegram (Now Handled by Heroku)
@server.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def get_message():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "", 200

# Start Flask Server
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

