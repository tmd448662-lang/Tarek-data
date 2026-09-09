#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import logging
from datetime import datetime
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import requests

# ==================== কনফিগ ───
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
API_URL = "https://api.bdg88zf.com/api/webapi/GetGameIssue"
ADMIN_ID = 5012028880

# ==================== LOGIC ───
LOGIC = {
    0: {"n": "5", "s": "BIG"},
    1: {"n": "2", "s": "SMALL"},
    2: {"n": "4", "s": "SMALL"},
    3: {"n": "7", "s": "BIG"},
    4: {"n": "8", "s": "BIG"},
    5: {"n": "9", "s": "BIG"},
    6: {"n": "0", "s": "SMALL"},
    7: {"n": "3", "s": "SMALL"},
    8: {"n": "6", "s": "BIG"},
    9: {"n": "1", "s": "SMALL"}
}

# ==================== ডেটা ───
history = []
total_wins = 0
total_losses = 0
current_streak = 0
best_win_streak = 0
worst_loss_streak = 0
hourly_stats = {"win": 0, "loss": 0, "total": 0}
last_hour = datetime.now().hour
current_period = None
last_result = None

# ==================== লগিং ───
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== ওয়েব সার্ভার ───
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"BOT is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ==================== API ───
def fetch_period():
    try:
        payload = {
            "typeId": 1,
            "language": 0,
            "random": "40079dcba93a48769c6ee9d4d4fae23f",
            "signature": "D12108C4F57C549D82B23A91E0FA20AE",
            "timestamp": 1727792520
        }
        response = requests.post(API_URL, json=payload, timeout=5)
        data = response.json()
        if data and data.get("code") == 0:
            return data.get("data", {}).get("issueNumber")
    except Exception as e:
        logger.error(f"API Error: {e}")
    return None

def get_prediction(period):
    if not period:
        return None
    last_digit = int(str(period)[-1])
    return LOGIC.get(last_digit)

# ==================== Handlers ───
def start(update, context):
    user = update.effective_user
    welcome_text = f"""
🦋 BDT BD SHANTO 2K - WINGO BOT

👤 User: {user.first_name}
🆔 ID: `{user.id}`

📌 Commands:
/prediction - 🔮 Current Prediction
/status - 📊 Live Status
/history - 📜 Last 10 Results
/hourly - 📈 Hourly Report
/help - ❓ Help

⚡ 1 Min Wingo Prediction Engine Active
    """
    keyboard = [
        [InlineKeyboardButton("🔮 Prediction", callback_data="prediction"),
         InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("📜 History", callback_data="history"),
         InlineKeyboardButton("📈 Hourly", callback_data="hourly")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

def prediction(update, context):
    period = fetch_period()
    if not period:
        update.message.reply_text("❌ API Error! Please try again.")
        return
    
    pred = get_prediction(period)
    if not pred:
        update.message.reply_text("❌ Prediction Error!")
        return
    
    last_digit = int(str(period)[-1])
    
    result_text = f"""
🔮 WINGO PREDICTION

📌 Period: `{period}`
🔢 Last Digit: `{last_digit}`
📈 Prediction: `{pred['s']} → {pred['n']}`

📊 Confidence: `{85 + (last_digit % 15)}%`

⚡ BDT BD SHANTO 2K VIP
    """
    
    keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="prediction")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        update.callback_query.message.edit_text(result_text, reply_markup=reply_markup, parse_mode="Markdown")
        update.callback_query.answer()
    else:
        update.message.reply_text(result_text, reply_markup=reply_markup, parse_mode="Markdown")

def status(update, context):
    global total_wins, total_losses, best_win_streak, worst_loss_streak, current_streak
    
    period = fetch_period()
    if not period:
        update.message.reply_text("❌ API Error!")
        return
    
    pred = get_prediction(period)
    if not pred:
        update.message.reply_text("❌ Error!")
        return
    
    total = total_wins + total_losses
    win_rate = (total_wins / total * 100) if total > 0 else 0
    
    status_text = f"""
📊 LIVE STATUS
━━━━━━━━━━━━━━━━━━━━
📌 PERIOD: #{period[-5:]}
🎯 PREDICTION: {pred['s']} → {pred['n']}
━━━━━━━━━━━━━━━━━━━━
📊 WIN RATE: {win_rate:.1f}% ({total_wins}W/{total_losses}L)
🔥 BEST WIN: {best_win_streak}x
📉 WORST LOSS: {worst_loss_streak}x
📉 CURRENT: {current_streak}x
━━━━━━━━━━━━━━━━━━━━
⚡ BDT BD SHANTO 2K
    """
    
    keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="status")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        update.callback_query.message.edit_text(status_text, reply_markup=reply_markup, parse_mode="Markdown")
        update.callback_query.answer()
    else:
        update.message.reply_text(status_text, reply_markup=reply_markup, parse_mode="Markdown")

def history_cmd(update, context):
    global history
    
    if not history:
        update.message.reply_text("📜 No history yet!")
        return
    
    last_10 = history[-10:][::-1]
    text = "📜 Last 10 Results\n━━━━━━━━━━━━━━━━━━━━\n"
    
    for i, h in enumerate(last_10, 1):
        emoji = "✅" if h.get("win", False) else "❌"
        text += f"{i}. #{h['period'][-5:]} → {h['pred']} ({h['number']}) {emoji}\n"
    
    total = len(history)
    wins = sum(1 for h in history if h.get("win", False))
    text += f"\n📊 Total: {total} | Wins: {wins} | Losses: {total - wins}"
    
    keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="history")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        update.callback_query.answer()
    else:
        update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

def hourly(update, context):
    global history, hourly_stats, best_win_streak, worst_loss_streak
    
    now = datetime.now()
    hour_start = now.replace(minute=0, second=0, microsecond=0)
    
    hourly_results = [h for h in history if h.get("timestamp", 0) >= hour_start.timestamp()]
    
    wins = sum(1 for h in hourly_results if h.get("win", False))
    total = len(hourly_results)
    losses = total - wins
    win_rate = (wins / total * 100) if total > 0 else 0
    
    current_time = now.strftime("%I:%M %p")
    
    message = f"""
📊 HOURLY PERFORMANCE REPORT
━━━━━━━━━━━━━━━━━━━━
🕐 TIME: {current_time}
━━━━━━━━━━━━━━━━━━━━
🔄 TOTAL ROUNDS: {total}
✅ TOTAL WINS: {wins}
❌ TOTAL LOSSES: {losses}
📈 WIN RATE: {win_rate:.1f}%
━━━━━━━━━━━━━━━━━━━━
🔥 BEST WIN STREAK: {best_win_streak}x
📉 WORST LOSS STREAK: {worst_loss_streak}x
━━━━━━━━━━━━━━━━━━━━
⚡ BDT BD SHANTO 2K
    """
    
    keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="hourly")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        update.callback_query.message.edit_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        update.callback_query.answer()
    else:
        update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")

def help_cmd(update, context):
    help_text = """
❓ HELP - WINGO PREDICTION BOT

📌 Commands:
/prediction - 🔮 Get current prediction
/status - 📊 Live status & stats
/history - 📜 Last 10 results
/hourly - 📈 Hourly report
/help - ❓ Show this help

⚠️ Disclaimer:
This is for entertainment only.
No guarantee of winnings.
Play responsibly.

🦋 BDT BD SHANTO 2K
    """
    update.message.reply_text(help_text, parse_mode="Markdown")

def button_handler(update, context):
    query = update.callback_query
    data = query.data
    
    if data == "prediction":
        prediction(update, context)
    elif data == "status":
        status(update, context)
    elif data == "history":
        history_cmd(update, context)
    elif data == "hourly":
        hourly(update, context)

# ==================== Auto Update ───
def auto_update():
    global history, hourly_stats, last_hour, current_period, last_result, total_wins, total_losses, current_streak, best_win_streak, worst_loss_streak
    
    while True:
        try:
            period = fetch_period()
            if period and period != current_period:
                current_period = period
                pred = get_prediction(period)
                
                if pred:
                    if last_result:
                        win = last_result.get("pred") == pred["s"]
                        
                        history.append({
                            "period": period,
                            "pred": pred["s"],
                            "number": pred["n"],
                            "win": win,
                            "timestamp": datetime.now().timestamp()
                        })
                        
                        if win:
                            total_wins += 1
                            current_streak += 1
                            if current_streak > best_win_streak:
                                best_win_streak = current_streak
                            hourly_stats["win"] += 1
                        else:
                            total_losses += 1
                            current_streak = 0
                            if current_streak < worst_loss_streak:
                                worst_loss_streak = current_streak
                            hourly_stats["loss"] += 1
                        hourly_stats["total"] += 1
                    
                    last_result = {"period": period, "pred": pred["s"], "number": pred["n"]}
                    
                    current_hour = datetime.now().hour
                    if current_hour != last_hour:
                        last_hour = current_hour
                        hourly_stats = {"win": 0, "loss": 0, "total": 0}
                
                if len(history) > 100:
                    history = history[-100:]
        
        except Exception as e:
            logger.error(f"Auto update error: {e}")
        
        time.sleep(2)

# ==================== Main ───
def main():
    # Create updater
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("prediction", prediction))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("history", history_cmd))
    dp.add_handler(CommandHandler("hourly", hourly))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    # Start auto update in background
    threading.Thread(target=auto_update, daemon=True).start()
    
    print("🤖 BDT BD SHANTO 2K Bot Started!")
    print(f"📌 Bot Token: {BOT_TOKEN[:10]}...")
    print("⚡ Waiting for commands...")
    
    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
