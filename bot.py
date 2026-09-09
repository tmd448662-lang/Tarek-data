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
total_wins = 0
total_losses = 0
current_streak = 0
best_win_streak = 0
worst_loss_streak = 0
current_period = None
last_result = None
last_prediction = None

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
        payload = {
            "typeId": 1,
            "language": 0,
            "random": "40079dcba93a48769c6ee9d4d4fae23f",
            "signature": "D12108C4F57C549D82B23A91E0FA20AE",
            "timestamp": 1727792520
        }
        response = requests.post(API_URL, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and data.get("code") == 0:
                return data.get("data", {}).get("issueNumber")
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
    global total_wins, total_losses, current_streak, best_win_streak, worst_loss_streak, current_period, last_result, last_prediction
    
    print("🤖 Bot Started!")
    print(f"📌 Bot Token: {BOT_TOKEN[:10]}...")
    print(f"📌 Admin ID: {ADMIN_ID}")
    print("⚡ Waiting for signals...")
    
    # Start message
    send_telegram_message("🤖 *BDT BD SHANTO 2K Bot Started!*\n⚡ Waiting for signals...")
    
    while True:
        try:
            period = fetch_period()
            
            if period and period != current_period:
                current_period = period
                pred = get_prediction(period)
                
                if pred:
                    # Send prediction
                    pred_msg = f"""
🔮 *WINGO PREDICTION*

📌 Period: `{period}`
🔢 Last Digit: `{str(period)[-1]}`
📈 Prediction: `{pred['s']} → {pred['n']}`

⚡ BDT BD SHANTO 2K VIP
"""
                    send_telegram_message(pred_msg)
                    
                    # Check result if we have previous prediction
                    if last_result and last_prediction:
                        win = last_prediction == pred["s"]
                        
                        if win:
                            total_wins += 1
                            current_streak += 1
                            if current_streak > best_win_streak:
                                best_win_streak = current_streak
                        else:
                            total_losses += 1
                            current_streak = 0
                            if current_streak < worst_loss_streak:
                                worst_loss_streak = current_streak
                        
                        total = total_wins + total_losses
                        win_rate = (total_wins / total * 100) if total > 0 else 0
                        
                        result_msg = f"""
🎯 *RESULT UPDATE*
━━━━━━━━━━━━━━━━━━━━
🆔 PERIOD: #{period[-5:]}
🎯 PREDICTED: {last_prediction}
🎰 ACTUAL: {pred['s']}
📌 RESULT: {'✅ WIN' if win else '❌ LOSS'}
━━━━━━━━━━━━━━━━━━━━
📊 WIN RATE: {win_rate:.1f}% ({total_wins}W/{total_losses}L)
📉 STREAK: {current_streak}x
━━━━━━━━━━━━━━━━━━━━
⚡ BDT BD SHANTO 2K
"""
                        send_telegram_message(result_msg)
                    
                    last_result = {"period": period, "pred": pred["s"], "number": pred["n"]}
                    last_prediction = pred["s"]
            
            time.sleep(5)
            
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
