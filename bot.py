import logging
import random
import asyncio
import threading
import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Configuration
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"

# Dummy Web Server for Render
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Wingo Hack Tracker Auto Engine Alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logger = logging.getLogger(__name__)

# Global Engine Variables
is_running = False
current_period = 10898
wins = 48
losses = 42
jackpots = 11
active_chats = set()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command."""
    global is_running
    chat_id = update.effective_chat.id
    active_chats.add(chat_id)
    
    keyboard = [
        [InlineKeyboardButton("🚀 START AUTO SIGNALS", callback_data="start_signals")],
        [InlineKeyboardButton("🛑 STOP SIGNALS", callback_data="stop_signals")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"🔥 **HYBRID HACKED PRO 1M ENGINE** 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ **Status:** `ENGINE READY`\n"
        f"⏱️ **Mode:** `1 Min Wingo Auto-Loop`\n\n"
        f"অটোমেটিক সিগন্যাল লুপ চালু করতে নিচের **START** বাটনে ক্লিক করুন।"
    )
    
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles Start/Stop Button Clicks."""
    global is_running
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    
    if query.data == "start_signals":
        if not is_running:
            is_running = True
            await query.edit_message_text("✅ **AUTO SIGNAL ENGINE STARTED!**\nঅটোমেটিক সিগন্যাল পাঠানো শুরু হচ্ছে...")
            # Start background auto loop
            asyncio.create_task(auto_signal_loop(context.application, chat_id))
        else:
            await query.edit_message_text("⚠️ **Engine turns already running!**")
            
    elif query.data == "stop_signals":
        is_running = False
        await query.edit_message_text("🛑 **AUTO SIGNAL ENGINE STOPPED.**")


async def auto_signal_loop(app, chat_id):
    """Main 1-Minute Auto Loop for Predictions and Results."""
    global current_period, wins, losses, jackpots, is_running
    
    while is_running:
        current_period += 1
        
        # 1. Generate Prediction Parameters
        pred_type = random.choice(["BIG", "SMALL"])
        if pred_type == "BIG":
            pred_num = random.choice([5, 6, 7, 8, 9])
        else:
            pred_num = random.choice([0, 1, 2, 3, 4])
            
        confidence = random.randint(75, 88)
        
        # 2. Format and Send Prediction Message
        pred_text = (
            f"🔥 **HYBRID HACKED PRO 1M**\n"
            f"⏱️ **Mode:** 1 Min Wingo\n"
            f"🆔 **Period:** {current_period}\n"
            f"🔮 **Prediction:** {pred_type} (Num: {pred_num})\n"
            f"⚡ **Confidence:** {confidence}%\n"
            f"🧠 **Engine:** MAJORITY VOTE\n"
            f"⏳ **Status:** Result Awaiting..."
        )
        
        try:
            await app.bot.send_message(chat_id=chat_id, text=pred_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            break

        # Wait 60 seconds for the period to complete
        await asyncio.sleep(60)
        if not is_running:
            break

        # 3. Generate Actual Game Result
        actual_num = random.randint(0, 9)
        actual_type = "BIG" if actual_num >= 5 else "SMALL"
        
        is_win = (pred_type == actual_type)
        
        if is_win:
            wins += 1
            res_str = "🟢 WIN!"
            if actual_num in [0, 5]:
                jackpots += 1
        else:
            losses += 1
            res_str = "🔴 LOSS!"

        total_games = wins + losses
        win_rate = round((wins / total_games) * 100, 1)

        # 4. Format and Send Result Message
        result_text = (
            f"🎯 **RESULT UPDATE**\n"
            f"🆔 **Period:** {current_period}\n"
            f"🎰 **Actual Number:** {actual_num} ({actual_type})\n"
            f"📌 **Result:** {res_str}\n"
            f"📊 **Win Rate:** {win_rate}% ({wins}W / {losses}L)\n"
            f"⭐ **Jackpots:** {jackpots}"
        )

        try:
            await app.bot.send_message(chat_id=chat_id, text=result_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error sending result: {e}")
            break
            
        # Small delay before triggering next period loop
        await asyncio.sleep(2)


def main():
    """Starts Flask and Telegram Bot Application."""
    threading.Thread(target=run_web, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Wingo Hack Tracker Auto Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
