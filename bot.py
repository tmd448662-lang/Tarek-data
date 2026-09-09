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
current_period = None
last_result = None
last_prediction = None
history = []

# ==================== হাওয়ারলি ডেটা ───
hourly_stats = {
    "win": 0, 
    "loss": 0, 
    "total": 0,
    "win_streak": 0,
    "loss_streak": 0,
    "current_streak": 0,
    "streak_type": "WIN"
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
def fetch_period():
    try:
        url = API_URL + "?t=" + str(int(time.time() * 1000))
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and data.get("data") and data["data"].get("list"):
                latest = data["data"]["list"][0]
                return latest.get("issueNumber")
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
    global total_wins, total_losses, current_streak, best_win_streak, worst_loss_streak, current_period, last_result, last_prediction, history, hourly_stats, last_hour
    
    print("🤖 Bot Started!")
    print(f"📌 Bot Token: {BOT_TOKEN[:10]}...")
    print("⚡ Waiting for signals...")
    
    send_telegram_message("🤖 *BDT BD SHANTO 2K Bot Started!*\n⚡ Waiting for signals...")
    
    while True:
        try:
            period = fetch_period()
            
            if period:
                print(f"📡 Period: {period}")
                
                if period != current_period:
                    current_period = period
                    pred = get_prediction(period)
                    
                    if pred:
                        # ==================== 📢 PREDICTION MESSAGE ====================
                        pred_msg = f"""
🔮 *WINGO PREDICTION*

📌 Period: `{period}`
🔢 Last Digit: `{str(period)[-1]}`
📈 Prediction: `{pred['s']} → {pred['n']}`

⚡ BDT BD SHANTO 2K VIP
"""
                        send_telegram_message(pred_msg)
                        print(f"✅ Prediction sent: {pred['s']} → {pred['n']}")
                        
                        # ==================== 📊 RESULT CHECK ====================
                        if last_result and last_prediction:
                            win = last_prediction == pred["s"]
                            
                            if win:
                                total_wins += 1
                                current_streak += 1
                                if current_streak > best_win_streak:
                                    best_win_streak = current_streak
                                hourly_stats["win"] += 1
                                
                                # হাওয়ারলি উইন স্ট্রিক আপডেট
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
                                
                                # হাওয়ারলি লস স্ট্রিক আপডেট
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
                            
                            # ==================== 📊 RESULT MESSAGE ====================
                            result_msg = f"""
🎯 *RESULT UPDATE*
━━━━━━━━━━━━━━━━━━━━
🎯 PREDICTED: `{last_prediction}`
🎰 ACTUAL: `{pred['s']}` → `{pred['n']}`
📌 RESULT: `{'✅ WIN' if win else '❌ LOSS'}`
━━━━━━━━━━━━━━━━━━━━
📊 WIN RATE: `{win_rate:.1f}%` ({total_wins}W/{total_losses}L)
📉 STREAK: `{current_streak}x`
━━━━━━━━━━━━━━━━━━━━
⚡ BDT BD SHANTO 2K
"""
                            send_telegram_message(result_msg)
                            print(f"📊 Result sent: {'WIN' if win else 'LOSS'}")
                            
                            # ==================== 📈 HOURLY REPORT ====================
                            current_hour = datetime.now().hour
                            if current_hour != last_hour:
                                last_hour = current_hour
                                
                                if hourly_stats["total"] > 0:
                                    win_rate_hourly = (hourly_stats["win"] / hourly_stats["total"] * 100)
                                    
                                    # স্ট্রিক এমোজি
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
{streak_emoji} CURRENT STREAK: `{hourly_stats['current_streak']}x {hourly_stats['streak_type']}`
━━━━━━━━━━━━━━━━━━━━
⚡ BDT BD SHANTO 2K
"""
                                    send_telegram_message(hourly_msg)
                                    print(f"📈 Hourly report sent")
                                
                                # রিসেট হাওয়ারলি স্ট্যাটস
                                hourly_stats = {
                                    "win": 0, 
                                    "loss": 0, 
                                    "total": 0,
                                    "win_streak": 0,
                                    "loss_streak": 0,
                                    "current_streak": 0,
                                    "streak_type": "WIN"
                                }
                        
                        last_result = {"period": period, "pred": pred["s"], "number": pred["n"]}
                        last_prediction = pred["s"]
            else:
                print("⚠️ No period received")
            
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Main loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
