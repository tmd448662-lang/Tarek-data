import os
import requests
import json
import time
import random
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ─── DUMMY WEB SERVER FOR RENDER ───
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ─── CONFIGURATION ───
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"
SCRAPER_API_KEY = "809f9c620ed6b5fe5a72bc368e8eabee"

RAW_API = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?t="

# ─── BASE PATTERN (12-STEP) ───
BASE_PATTERN = [
    {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 2}, {"s": "SMALL", "n": 4},
    {"s": "BIG", "n": 9}, {"s": "BIG", "n": 6}, {"s": "SMALL", "n": 0},
    {"s": "BIG", "n": 8}, {"s": "SMALL", "n": 3}, {"s": "SMALL", "n": 1},
    {"s": "BIG", "n": 5}, {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 4}
]

# ─── HISTORY DATA STORE ───
history_data = []

# ─── GLOBAL STATS ───
total_wins = 0
total_losses = 0
current_win_streak = 0
current_loss_streak = 0
last_processed_period = None
last_pred_signal = None
last_pred_num = None

# ============================================================
#  API HISTORY POPULATOR (হিস্ট্রি লোড করার জন্য)
# ============================================================
def init_history_data():
    """বোট চালু হওয়ার সাথে সাথে ২০টি রেজাল্ট ফেচ করে হিস্ট্রি ফিল করে"""
    global history_data
    timestamp = str(int(time.time() * 1000))
    url = RAW_API + timestamp
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            list_data = res.json().get("data", {}).get("list", [])
            history_data = []
            for item in list_data[:20]:
                num = int(item.get("number"))
                history_data.append({
                    'period': str(item.get("issueNumber")),
                    'number': num,
                    'side': "BIG" if num >= 5 else "SMALL"
                })
            print(f"Successfully loaded {len(history_data)} past history items.")
    except Exception as e:
        print("History Init Fetch Error:", e)

# ============================================================
#  ENGINE 1: DARK X VIP (TITAN ULTRA FIXED)
# ============================================================
def dark_x_engine():
    """TITAN ULTRA Core Matching Logic"""
    if not history_data:
        # ফলব্যাক যদি কোনো হিস্ট্রি না থাকে
        return "SMALL", 3, 90
    
    latest_num = history_data[0]['number']
    latest_side = history_data[0]['side']
    
    # লাস্ট রেজাল্ট থেকে রিভার্সাল ও গ্যাপ ট্র্যাকিং
    if len(history_data) >= 3:
        last3 = [d['side'] for d in history_data[:3]]
        if last3[0] == last3[1] == "BIG":
            return "SMALL", 3, 90
        elif last3[0] == last3[1] == "SMALL":
            return "BIG", 7, 90

    # গ্যাপ ও সিকোয়েন্স কাউন্টার
    pred_side = "SMALL" if latest_side == "BIG" else "BIG"
    pred_num = 3 if pred_side == "SMALL" else 7
    return pred_side, pred_num, 90

# ============================================================
#  ENGINE 2: FUKD BY SAAD (PRO AI FIXED)
# ============================================================
def fukd_saad_engine():
    """Ultimate Pro AI Matching Logic"""
    if not history_data:
        return "BIG", 6, 76
    
    # ম্যাথ-সিকোয়েন্স মেথড
    num_sum = sum([d['number'] for d in history_data[:3]])
    math_val = num_sum % 10
    
    final_pred = "BIG" if math_val >= 5 else "SMALL"
    final_num = math_val if (math_val >= 5 and final_pred == "BIG") or (math_val < 5 and final_pred == "SMALL") else (6 if final_pred == "BIG" else 3)
    
    return final_pred, final_num, 78

# ============================================================
#  ENGINE 3: RGB VIP HACK (ANSH BOSS FIXED)
# ============================================================
def rgb_vip_hack_engine():
    """ANSH BOSS Real VIP Predictor Sync"""
    now = datetime.now(timezone.utc)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    diff = int((now - start_of_day).total_seconds())
    idx = (diff // 60) + 1
    
    # ANSH BOSS 1 MIN 12-Step Dynamic Math Sync
    pattern_idx = idx % 12
    base_pred = BASE_PATTERN[pattern_idx]
    
    # হিস্ট্রি প্যাটার্ন ওভাররাইড (যদি লস স্ট্রিক থাকে)
    if history_data and len(history_data) >= 2:
        if history_data[0]['side'] == history_data[1]['side']:
            final_pred = "SMALL" if history_data[0]['side'] == "BIG" else "BIG"
            final_num = 3 if final_pred == "SMALL" else 8
            return final_pred, final_num, 85

    return base_pred["s"], base_pred["n"], 85

# ============================================================
#  MASTER VOTING SYSTEM
# ============================================================
def master_voting_system():
    dark_pred, dark_num, dark_conf = dark_x_engine()
    fukd_pred, fukd_num, fukd_conf = fukd_saad_engine()
    rgb_pred, rgb_num, rgb_conf = rgb_vip_hack_engine()
    
    votes = {'BIG': 0, 'SMALL': 0}
    engines_detail = {
        'DARK X VIP': {'prediction': dark_pred, 'number': dark_num, 'confidence': dark_conf},
        'FUKD BY SAAD (6-Engine)': {'prediction': fukd_pred, 'number': fukd_num, 'confidence': fukd_conf},
        'RGB VIP HACK': {'prediction': rgb_pred, 'number': rgb_num, 'confidence': rgb_conf}
    }
    
    votes[dark_pred] += 1
    votes[fukd_pred] += 1
    votes[rgb_pred] += 1
    
    # মেজোরিটি ডিসিশন
    final_pred = max(votes, key=votes.get)
    
    # নাম্বার ও কনফিডেন্স সিলেকশন
    matching_nums = [d['number'] for d in engines_detail.values() if d['prediction'] == final_pred]
    final_num = matching_nums[0] if matching_nums else (7 if final_pred == "BIG" else 3)
    
    total_conf = sum([d['confidence'] for d in engines_detail.values()])
    final_conf = int(total_conf / 3)
    
    return {
        'prediction': final_pred,
        'number': final_num,
        'confidence': final_conf,
        'votes': votes,
        'engines': engines_detail
    }

# ============================================================
#  TELEGRAM FUNCTIONS
# ============================================================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Telegram Send Error:", e)

def fetch_real_result():
    timestamp = str(int(time.time() * 1000))
    raw_url = RAW_API + timestamp
    
    try:
        res = requests.get(raw_url, timeout=4)
        if res.status_code == 200:
            list_data = res.json().get("data", {}).get("list", [])
            if list_data:
                return str(list_data[0].get("issueNumber")), int(list_data[0].get("number"))
    except Exception:
        pass

    try:
        proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={requests.utils.quote(raw_url)}"
        res = requests.get(proxy_url, timeout=8)
        if res.status_code == 200:
            list_data = res.json().get("data", {}).get("list", [])
            if list_data:
                return str(list_data[0].get("issueNumber")), int(list_data[0].get("number"))
    except Exception as e:
        print("Fetch Error:", e)

    return None, None

def get_period_info():
    now = datetime.now(timezone.utc)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    diff = int((now - start_of_day).total_seconds())
    interval = 60
    idx = (diff // interval) + 1
    y = now.strftime("%Y")
    m = now.strftime("%m")
    d = now.strftime("%d")
    period_id = f"{y}{m}{d}{idx:05d}"
    return period_id, idx

# ─── STARTUP ───
init_history_data()  # বোট স্টার্টের সময়ই ২০টি হিস্ট্রি ফিল করবে

send_telegram("🚀 *3-ENGINE HYBRID VIP BOT ACTIVATED!*")

while True:
    try:
        current_period, idx = get_period_info()
        
        if current_period != last_processed_period:
            
            if last_processed_period is not None:
                time.sleep(3)
                
                real_period = None
                actual_num = None
                
                for _ in range(5):
                    real_period, actual_num = fetch_real_result()
                    if real_period and real_period[-5:] == last_processed_period[-5:]:
                        break
                    time.sleep(2)

                if real_period and actual_num is not None:
                    actual_size = "BIG" if actual_num >= 5 else "SMALL"
                    is_win = (last_pred_signal == actual_size)
                    
                    if is_win:
                        total_wins += 1
                        current_win_streak += 1
                        current_loss_streak = 0
                        status_str = f"🟢 WIN {current_win_streak}!"
                    else:
                        total_losses += 1
                        current_loss_streak += 1
                        current_win_streak = 0
                        status_str = f"🔴 LOSS {current_loss_streak}!"
                    
                    total_games = total_wins + total_losses
                    win_rate = (total_wins / total_games) * 100 if total_games > 0 else 0
                    
                    # হিস্ট্রি আপডেট
                    history_data.insert(0, {
                        'period': last_processed_period,
                        'number': actual_num,
                        'side': actual_size
                    })
                    if len(history_data) > 20:
                        history_data.pop()
                    
                    res_msg = (
                        f"🎯 *RESULT UPDATE*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{last_processed_period[-5:]}`\n"
                        f"🎯 PREDICTED: `{last_pred_signal}` → `{last_pred_num}`\n"
                        f"🎰 ACTUAL: `{actual_num}` (`{actual_size}`)\n"
                        f"📌 RESULT: {status_str}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 WIN RATE: `{win_rate:.1f}%` ({total_wins}W/{total_losses}L)\n"
                        f"🔥 STREAK: `{current_win_streak - current_loss_streak:+d}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🗳️ VOTING: 3 ENGINES\n"
                        f"💎 3-ENGINE HYBRID VIP"
                    )
                    send_telegram(res_msg)

            pred_result = master_voting_system()
            final_pred = pred_result['prediction']
            final_num = pred_result['number']
            final_conf = pred_result['confidence']
            votes = pred_result['votes']
            engines = pred_result['engines']
            
            engine_votes = ""
            for name, data in engines.items():
                engine_votes += f"├─ {name}: `{data['prediction']}` ({data['number']}) `{data['confidence']}%`\n"
            
            msg = (
                f"🔥 *3-ENGINE HYBRID VIP* 🔥\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🆔 PERIOD: `#{current_period[-5:]}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🗳️ *VOTING RESULT*\n"
                f"📊 BIG: `{votes['BIG']}` | SMALL: `{votes['SMALL']}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📈 *FINAL PREDICTION*\n"
                f"🎯 PREDICTION: `{final_pred}`\n"
                f"🔢 TARGET NUMBER: `{final_num}`\n"
                f"⚡ CONFIDENCE: `{final_conf}%`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🧠 *ENGINE VOTES*\n"
                f"{engine_votes}"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🔥 STREAK: `{current_win_streak - current_loss_streak:+d}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"⏳ RESULT AWAITING...\n"
                f"💎 3-ENGINE HYBRID VIP"
            )
            send_telegram(msg)
            
            last_processed_period = current_period
            last_pred_signal = final_pred
            last_pred_num = final_num

    except Exception as e:
        print("Loop error:", e)

    time.sleep(2)
