#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import os
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ==================== কনফিগ ───
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
ADMIN_ID = 5012028880

# ==================== API ───
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

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
total_wins = 0
total_losses = 0
current_streak = 0
best_win_streak = 0
worst_loss_streak = 0
last_checked_period = None
last_prediction = None
last_pred_number = None
last_pred_period = None
prediction_sent = False  # 🆕 প্রেডিকশন পাঠানো হয়েছে কিনা
history = []

# ==================== হাওয়ারলি ───
hourly_stats = {
    "win": 0, "loss": 0, "total": 0,
    "win_streak": 0, "loss_streak": 0,
    "current_streak": 0, "streak_type": "WIN"
}
last_hour = datetime.now().hour

# ==================== ওয়েব সার্ভার ───
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    print(f"Web server running on port {port}")
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ==================== API ───
def fetch_data():
    try:
        url = API_URL + "?t=" + str(int(time.time() * 1000))
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and data.get("data") and data["data"].get("list"):
                return data["data"]["list"]
    except Exception as e:
        print(f"API Error: {e}")
    return None

def get_prediction(period):
    if not period:
        return None
    last_digit = int(str(period)[-1])
    return LOGIC.get(last_digit)

# ==================== Telegram সেন্ড ───
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": ADMIN_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Send error: {e}")
        return False

# ==================== মেইন লুপ ───
def main():
    global total_wins, total_losses, current_streak, best_win_streak, worst_loss_streak
    global last_checked_period, last_prediction, last_pred_number, last_pred_period, prediction_sent
    global history, hourly_stats, last_hour
    
    print("🤖 Bot Started!")
    print("⚡ Order: RESULT → PREDICTION")
    
    send_telegram_message("🤖 *BDT BD SHANTO 2K Bot Started!*\n⚡ Order: RESULT → PREDICTION")
    
    while True:
        try:
            data_list = fetch_data()
            
            if data_list:
                latest = data_list[0]
                period = latest.get("issueNumber")
                actual_num = int(latest.get("number"))
                actual_type = "BIG" if actual_num >= 5 else "SMALL"
                
                # =====================================================
                # নতুন পিরিয়ড চেক
                # =====================================================
                if period != last_checked_period:
                    last_checked_period = period
                    prediction_sent = False  # 🆕 রিসেট
                    print(f"📡 New Period: {period}, Number: {actual_num}")
                    
                    # =====================================================
                    # STEP 1: RESULT CHECK
                    # =====================================================
                    if last_pred_period and last_pred_period == period:
                        win = last_prediction == actual_type
                        
                        if win:
                            total_wins += 1
                            current_streak += 1
                            if current_streak > best_win_streak:
                                best_win_streak = current_streak
                            hourly_stats["win"] += 1
                            
                            if hourly_stats["streak_type"] == "WIN":
                                hourly_stats["current_streak"] += 1
                            else:
                                hourly_stats["current_streak"] = 1
                                hourly_stats["streak_type"] = "WIN"
                            if hourly_stats["current_streak"] > hourly_stats["win_streak"]:
                                hourly_stats["win_streak"] = hourly_stats["current_streak"]
                        else:
                            total_losses += 1
                            current_streak = 0
                            if current_streak < worst_loss_streak:
                                worst_loss_streak = current_streak
                            hourly_stats["loss"] += 1
                            
                            if hourly_stats["streak_type"] == "LOSS":
                                hourly_stats["current_streak"] += 1
                            else:
                                hourly_stats["current_streak"] = 1
                                hourly_stats["streak_type"] = "LOSS"
                            if hourly_stats["current_streak"] > hourly_stats["loss_streak"]:
                                hourly_stats["loss_streak"] = hourly_stats["current_streak"]
                        
                        hourly_stats["total"] += 1
                        
                        total = total_wins + total_losses
                        win_rate = (total_wins / total * 100) if total > 0 else 0
                        
                        result_msg = f"""
🎯 *RESULT UPDATE*
━━━━━━━━━━━━━━━━━━━━
🆔 PERIOD: `#{period[-5:]}`
🎯 PREDICTED: `{last_prediction}` → `{last_pred_number}`
🎰 ACTUAL: `{actual_num}` (`{actual_type}`)
📌 RESULT: `{'✅ WIN' if win else '❌ LOSS'}`
━━━━━━━━━━━━━━━━━━━━
📊 WIN RATE: `{win_rate:.1f}%` ({total_wins}W/{total_losses}L)
📉 STREAK: `{current_streak}x`
━━━━━━━━━━━━━━━━━━━━
⚡ BDT BD SHANTO 2K
"""
                        send_telegram_message(result_msg)
                        print(f"📊 Result sent: {'WIN' if win else 'LOSS'}")
                        
                        last_pred_period = None
                        last_prediction = None
                        last_pred_number = None
                        
                        # ==================== HOURLY REPORT ====================
                        current_hour = datetime.now().hour
                        if current_hour != last_hour:
                            last_hour = current_hour
                            if hourly_stats["total"] > 0:
                                win_rate_hourly = (hourly_stats["win"] / hourly_stats["total"] * 100)
                                streak_emoji = "🔥" if hourly_stats["streak_type"] == "WIN" else "📉"
                                
                                hourly_msg = f"""
📊 *HOURLY REPORT* - {current_hour:02d}:00
━━━━━━━━━━━━━━━━━━━━
🔄 TOTAL: `{hourly_stats['total']}`
✅ WINS: `{hourly_stats['win']}`
❌ LOSSES: `{hourly_stats['loss']}`
📈 WIN RATE: `{win_rate_hourly:.1f}%`
━━━━━━━━━━━━━━━━━━━━
🔥 BEST WIN STREAK: `{hourly_stats['win_streak']}x`
📉 WORST LOSS STREAK: `{hourly_stats['loss_streak']}x`
{streak_emoji} CURRENT: `{hourly_stats['current_streak']}x {hourly_stats['streak_type']}`
━━━━━━━━━━━━━━━━━━━━
⚡ BDT BD SHANTO 2K
"""
                                send_telegram_message(hourly_msg)
                                print(f"📈 Hourly report sent")
                            
                            hourly_stats = {
                                "win": 0, "loss": 0, "total": 0,
                                "win_streak": 0, "loss_streak": 0,
                                "current_streak": 0, "streak_type": "WIN"
                            }
                
                # =====================================================
                # STEP 2: NEW PREDICTION (শুধু ১ বার)
                # =====================================================
                if not last_pred_period and not prediction_sent:
                    next_period = str(int(period) + 1)
                    pred = get_prediction(next_period)
                    
                    if pred:
                        pred_msg = f"""
🔮 *WINGO PREDICTION*

📌 Period: `{next_period}`
🔢 Last Digit: `{str(next_period)[-1]}`
📈 Prediction: `{pred['s']}` → `{pred['n']}`

⚡ BDT BD SHANTO 2K VIP
"""
                        send_telegram_message(pred_msg)
                        print(f"✅ Prediction sent: {pred['s']} → {pred['n']} for {next_period}")
                        
                        last_pred_period = next_period
                        last_prediction = pred['s']
                        last_pred_number = pred['n']
                        prediction_sent = True  # 🆕 প্রেডিকশন পাঠানো হয়েছে
            
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Main loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
