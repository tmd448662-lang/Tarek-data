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
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

# ==================== ১. RGB (ANSH BOSS) ───
RGB_PATTERN = [
    {"s": "BIG", "n": "7"}, {"s": "SMALL", "n": "2"},
    {"s": "SMALL", "n": "4"}, {"s": "BIG", "n": "9"},
    {"s": "BIG", "n": "6"}, {"s": "SMALL", "n": "0"},
    {"s": "BIG", "n": "8"}, {"s": "SMALL", "n": "3"},
    {"s": "SMALL", "n": "1"}, {"s": "BIG", "n": "5"},
    {"s": "BIG", "n": "7"}, {"s": "SMALL", "n": "4"}
]

def rgb_algorithm(period):
    idx = int(str(period)[-3:]) % 12
    return RGB_PATTERN[idx]

# ==================== ২. SHANTO (মার্কভ চেইন) ───
def shanto_algorithm(last_results):
    if len(last_results) < 2:
        return {"s": "BIG", "n": "7"}
    
    last1 = last_results[-1]
    last2 = last_results[-2]
    
    if last1 == "SMALL" and last2 == "SMALL":
        return {"s": "BIG", "n": "8"}
    elif last1 == "BIG" and last2 == "BIG":
        return {"s": "SMALL", "n": "3"}
    elif last1 == "SMALL" and last2 == "BIG":
        return {"s": "BIG", "n": "7"}
    elif last1 == "BIG" and last2 == "SMALL":
        return {"s": "SMALL", "n": "4"}
    return {"s": "BIG", "n": "7"}

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
prediction_sent = False
last_results = []

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
    global last_results, hourly_stats, last_hour
    
    print("🤖 Bot Started!")
    print("⚡ Order: RESULT → PREDICTION")
    print("🧠 2 Algorithms: SHANTO + RGB (ANSH BOSS)")
    print("📊 Match = PREDICTION | No Match = SKIP")
    
    send_telegram_message("🤖 *BDT BD SHANTO 2K Bot Started!*\n🧠 SHANTO + RGB\n📊 2 Match System")
    
    while True:
        try:
            data_list = fetch_data()
            
            if data_list:
                latest = data_list[0]
                period = latest.get("issueNumber")
                actual_num = int(latest.get("number"))
                actual_type = "BIG" if actual_num >= 5 else "SMALL"
                
                if period != last_checked_period:
                    last_checked_period = period
                    prediction_sent = False
                    print(f"📡 New Period: {period}, Number: {actual_num}")
                    
                    # ==================== RESULT CHECK ====================
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
                        last_results.append(actual_type)
                        if len(last_results) > 20:
                            last_results = last_results[-20:]
                        
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
                
                # ==================== NEW PREDICTION ====================
                if not last_pred_period and not prediction_sent:
                    next_period = str(int(period) + 1)
                    
                    # 🧠 ২টি অ্যালগরিদম
                    rgb_pred = rgb_algorithm(next_period)
                    shanto_pred = shanto_algorithm(last_results)
                    
                    # ✅ ম্যাচ চেক
                    if rgb_pred["s"] == shanto_pred["s"]:
                        # ✅ MATCH FOUND
                        pred_msg = f"""
🔮 *WINGO PREDICTION* 🟢
━━━━━━━━━━━━━━━━━━━━
📌 Period: `{next_period}`
📈 Prediction: `{rgb_pred['s']}` → `{rgb_pred['n']}`
━━━━━━━━━━━━━━━━━━━━
🧠 SHANTO: `{shanto_pred['s']}` → `{shanto_pred['n']}`
🧠 RGB: `{rgb_pred['s']}` → `{rgb_pred['n']}`
📊 STATUS: `✅ MATCH FOUND`
━━━━━━━━━━━━━━━━━━━━
💡 TIP: Both algorithms agree! HIGH CONFIDENCE

⚡ BDT BD SHANTO 2K VIP
"""
                        send_telegram_message(pred_msg)
                        print(f"✅ MATCH! Prediction sent: {rgb_pred['s']} → {rgb_pred['n']}")
                        
                        last_pred_period = next_period
                        last_prediction = rgb_pred['s']
                        last_pred_number = rgb_pred['n']
                        prediction_sent = True
                        
                    else:
                        # ❌ NO MATCH - SKIP
                        skip_msg = f"""
⏭️ *PREDICTION SKIPPED* 🔴
━━━━━━━━━━━━━━━━━━━━
📌 Period: `{next_period}`
━━━━━━━━━━━━━━━━━━━━
🧠 SHANTO: `{shanto_pred['s']}` → `{shanto_pred['n']}`
🧠 RGB: `{rgb_pred['s']}` → `{rgb_pred['n']}`
📊 STATUS: `❌ NO MATCH (SKIP)`
━━━━━━━━━━━━━━━━━━━━
💡 TIP: Algorithms disagree! Waiting for next period.

⚡ BDT BD SHANTO 2K VIP
"""
                        send_telegram_message(skip_msg)
                        print(f"❌ NO MATCH! Skipped: SHANTO={shanto_pred['s']}, RGB={rgb_pred['s']}")
                        prediction_sent = True
            
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Main loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
