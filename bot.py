import requests
import json
import time
from datetime import datetime, timezone

# ─── ১. TELEGRAM BOT INFO ───
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"

# ─── ২. DIRECT API (NO PROXY NEEDED ON RENDER) ───
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
        else:
            print("Status Code Error:", res.status_code)
    except Exception as e:
        print("Fetch Error:", e)
    return None, None

# ─── MAIN BOT LOOP ───
wins = 0
losses = 0
current_period = None
current_pred_signal = None
current_pred_num = None
pending_check = False

send_telegram("🚀 *ANSH BOSS VIP PREDICTOR ACTIVATED (RENDER)!*")

while True:
    try:
        period_id, pred_signal, pred_num = get_vip_prediction()
        
        if period_id != current_period:
            current_period = period_id
            current_pred_signal = pred_signal
            current_pred_num = pred_num
            pending_check = True
            
            msg = (
                f"⚡ *ANSH BOSS VIP PREDICTION*\n"
                f"⏱️ *Mode:* 1 Minute Wingo\n"
                f"🆔 *Period:* `{current_period[-5:]}`\n"
                f"🔮 *Prediction:* `{current_pred_signal}` (Num: {current_pred_num})\n"
                f"⏳ *Status:* Result Awaiting..."
            )
            send_telegram(msg)

        if pending_check:
            real_period, actual_num = fetch_real_result()
            
            if real_period and actual_num is not None:
                if real_period[-5:] == current_period[-5:] or int(real_period) >= int(current_period) - 1:
                    actual_size = "BIG" if actual_num >= 5 else "SMALL"
                    is_win = (current_pred_signal == actual_size)
                    
                    if is_win:
                        wins += 1
                        status_str = "🟢 WIN!"
                    else:
                        losses += 1
                        status_str = "🔴 LOSS!"
                    
                    total = wins + losses
                    win_rate = (wins / total) * 100 if total > 0 else 0
                    
                    res_msg = (
                        f"🎯 *RESULT UPDATE*\n"
                        f"🆔 *Period:* `{current_period[-5:]}`\n"
                        f"🎰 *Actual Number:* `{actual_num}` ({actual_size})\n"
                        f"📌 *Result:* *{status_str}*\n"
                        f"📊 *Win Rate:* `{win_rate:.1f}%` ({wins}W / {losses}L)"
                    )
                    send_telegram(res_msg)
                    pending_check = False

    except Exception as e:
        print("Loop error:", e)

    time.sleep(3)
