import os
import requests
import json
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ─── DUMMY WEB SERVER FOR RENDER ───
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ─── ১. TELEGRAM BOT INFO ───
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"

# ─── ২. DIRECT API ───
API_1M = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?t="

PATTERN = [
    {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 2}, {"s": "SMALL", "n": 4}, {"s": "BIG", "n": 9},
    {"s": "BIG", "n": 6}, {"s": "SMALL", "n": 0}, {"s": "BIG", "n": 8}, {"s": "SMALL", "n": 3},
    {"s": "SMALL", "n": 1}, {"s": "BIG", "n": 5}, {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 4}
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Telegram Send Error:", e)

def get_vip_prediction():
    now = datetime.now(timezone.utc)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    diff = int((now - start_of_day).total_seconds())
    
    interval = 60
    idx = (diff // interval) + 1
    
    y = now.strftime("%Y")
    m = now.strftime("%m")
    d = now.strftime("%d")
    period_id = f"{y}{m}{d}{idx:05d}"
    
    pattern_index = (idx + 5) % len(PATTERN)
    pred = PATTERN[pattern_index]
    
    return period_id, pred["s"], pred["n"]

def fetch_real_result():
    try:
        url = API_1M + str(int(time.time() * 1000))
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*"
        }
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            list_data = data.get("data", {}).get("list", [])
            if list_data:
                latest = list_data[0]
                return str(latest.get("issueNumber")), int(latest.get("number"))
    except Exception as e:
        print("Fetch Error:", e)
    return None, None

# ─── GLOBAL VARIABLES FOR STREAK ───
total_wins = 0
total_losses = 0
current_win_streak = 0
current_loss_streak = 0

def check_result_in_background(period_to_check, pred_signal):
    global total_wins, total_losses, current_win_streak, current_loss_streak
    
    # পিরিয়ডের খেলা শেষ হওয়া পর্যন্ত অপেক্ষা (মিনিট শেষ হওয়ার ৫ সেকেন্ড আগে ট্রাই শুরু করবে)
    time.sleep(45)
    
    retry_count = 0
    while retry_count < 10:
        real_period, actual_num = fetch_real_result()
        
        # পিরিয়ড মিলে গেলে রেজাল্ট প্রসেস করবে
        if real_period and real_period[-5:] == period_to_check[-5:]:
            actual_size = "BIG" if actual_num >= 5 else "SMALL"
            is_win = (pred_signal == actual_size)
            
            if is_win:
                total_wins += 1
                current_win_streak += 1
                current_loss_streak = 0  # Loss রিসেট
                status_str = f"🟢 WIN {current_win_streak}!"
            else:
                total_losses += 1
                current_loss_streak += 1
                current_win_streak = 0  # Win রিসেট
                status_str = f"🔴 LOSS {current_loss_streak}!"
            
            total_games = total_wins + total_losses
            win_rate = (total_wins / total_games) * 100 if total_games > 0 else 0
            
            res_msg = (
                f"🎯 *RESULT UPDATE*\n"
                f"🆔 *Period:* `{period_to_check[-5:]}`\n"
                f"🎰 *Actual Number:* `{actual_num}` ({actual_size})\n"
                f"📌 *Result:* *{status_str}*\n"
                f"📊 *Win Rate:* `{win_rate:.1f}%` ({total_wins}W / {total_losses}L)"
            )
            send_telegram(res_msg)
            break
            
        time.sleep(3)
        retry_count += 1

# ─── MAIN BOT LOOP ───
current_period = None

send_telegram("🚀 *ANSH BOSS VIP PREDICTOR ACTIVATED!*")

while True:
    try:
        period_id, pred_signal, pred_num = get_vip_prediction()
        
        # নতুন পিরিয়ড আসার ১-২ সেকেন্ডের মধ্যেই মেসেজ পাঠাবে
        if period_id != current_period:
            current_period = period_id
            
            msg = (
                f"⚡ *ANSH BOSS VIP PREDICTION*\n"
                f"⏱️ *Mode:* 1 Minute Wingo\n"
                f"🆔 *Period:* `{current_period[-5:]}`\n"
                f"🔮 *Prediction:* `{pred_signal}` (Num: {pred_num})\n"
                f"⏳ *Status:* Result Awaiting..."
            )
            send_telegram(msg)

            # রেজাল্ট চেক করার কাজ ব্যাকগ্রাউন্ডে পাঠিয়ে দেওয়া হলো
            threading.Thread(
                target=check_result_in_background, 
                args=(current_period, pred_signal), 
                daemon=True
            ).start()

    except Exception as e:
        print("Loop error:", e)

    time.sleep(2)
