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

# ─── BASE PATTERN ───
BASE_PATTERN = [
    {"s": "BIG", "n": 9}, {"s": "SMALL", "n": 2}, {"s": "SMALL", "n": 4},
    {"s": "BIG", "n": 6}, {"s": "BIG", "n": 8}, {"s": "SMALL", "n": 0},
    {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 3}, {"s": "SMALL", "n": 1},
    {"s": "BIG", "n": 5}, {"s": "BIG", "n": 9}, {"s": "SMALL", "n": 4}
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

def fetch_latest_history():
    """লাইভ এপিআই থেকে সর্বশেষ রেজাল্ট নিয়ে আসা"""
    global history_data
    timestamp = str(int(time.time() * 1000))
    url = RAW_API + timestamp
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            list_data = res.json().get("data", {}).get("list", [])
            if list_data:
                temp_list = []
                for item in list_data[:20]:
                    num = int(item.get("number"))
                    temp_list.append({
                        'period': str(item.get("issueNumber")),
                        'number': num,
                        'side': "BIG" if num >= 5 else "SMALL"
                    })
                history_data = temp_list
                print(f"Updated History: Latest Period #{history_data[0]['period']}")
                return history_data[0]['period'], history_data[0]['number']
    except Exception as e:
        print("History Fetch Error:", e)
    return None, None

# ============================================================
#  ENGINE 1: DARK X VIP (TITAN ULTRA CORE)
# ============================================================
def dark_x_engine():
    if not history_data:
        return "BIG", 9, 85

    # লস রিকভারি মোড (Martingale Logic)
    if current_loss_streak >= 1:
        last_side = history_data[0]['side']
        pred_side = "BIG" if last_side == "BIG" else "BIG"
        return pred_side, 9, 99

    # প্যাটার্ন অ্যানালাইসিস
    last_3 = [d['side'] for d in history_data[:3]]
    if last_3.count("BIG") >= 2:
        return "BIG", 9, 90
    else:
        return "SMALL", 3, 80

# ============================================================
#  ENGINE 2: RGB VIP HACK (ANSH BOSS)
# ============================================================
def rgb_vip_hack_engine(current_period_id):
    if not history_data:
        return "BIG", 6, 85

    last_num = history_data[0]['number']
    period_digit = int(current_period_id[-1]) if current_period_id else 0

    # ANSH BOSS ম্যাথমেটিকাল ফর্মুলা
    calc = (last_num + period_digit) % 10
    
    if current_loss_streak >= 1:
        # লস হলে ট্রেন্ড রিভার্সাল
        pred_side = "BIG" if calc >= 4 else "SMALL"
    else:
        pred_side = "BIG" if calc >= 5 else "SMALL"

    target_num = calc if pred_side == ("BIG" if calc >= 5 else "SMALL") else (6 if pred_side == "BIG" else 2)
    return pred_side, target_num, 85

# ============================================================
#  ENGINE 3: FUKD BY SAAD (6-Engine Sub-Voting)
# ============================================================
def fukd_6sub_engines(current_period_id):
    if not history_data:
        return "BIG", 7, 88

    sub_votes = {'BIG': 0, 'SMALL': 0}
    last_num = history_data[0]['number']

    # 1. CORE POWER
    sub_votes["BIG" if last_num in [0, 2, 6, 7, 8, 9] else "SMALL"] += 1

    # 2. SMART
    sub_votes["BIG" if last_num in [3, 4, 7, 8, 9] else "SMALL"] += 1

    # 3. HYBRID
    avg = sum([d['number'] for d in history_data[:3]]) / 3.0
    sub_votes["BIG" if avg >= 4.5 else "SMALL"] += 1

    # 4. MASTER
    sub_votes["BIG" if history_data[0]['side'] == "BIG" else "SMALL"] += 1

    # 5. DELTA VIP
    p_digit = int(current_period_id[-1]) if current_period_id else 0
    sub_votes["BIG" if p_digit % 2 == 0 else "SMALL"] += 1

    # 6. QUANTUM
    sub_votes["BIG" if (last_num * 2 + 1) % 10 >= 5 else "SMALL"] += 1

    fukd_pred = max(sub_votes, key=sub_votes.get)
    fukd_num = 7 if fukd_pred == "BIG" else 3

    return fukd_pred, fukd_num, 88

# ============================================================
#  MAIN MASTER VOTING SYSTEM
# ============================================================
def master_voting_system(current_period_id):
    dark_pred, dark_num, dark_conf = dark_x_engine()
    rgb_pred, rgb_num, rgb_conf = rgb_vip_hack_engine(current_period_id)
    fukd_pred, fukd_num, fukd_conf = fukd_6sub_engines(current_period_id)

    votes = {'BIG': 0, 'SMALL': 0}
    engines_detail = {
        'DARK X VIP': {'prediction': dark_pred, 'number': dark_num, 'confidence': dark_conf},
        'FUKD BY SAAD (6-Engine)': {'prediction': fukd_pred, 'number': fukd_num, 'confidence': fukd_conf},
        'RGB VIP HACK': {'prediction': rgb_pred, 'number': rgb_num, 'confidence': rgb_conf}
    }

    votes[dark_pred] += 1
    votes[fukd_pred] += 1
    votes[rgb_pred] += 1

    final_pred = max(votes, key=votes.get)

    matching_nums = [data['number'] for data in engines_detail.values() if data['prediction'] == final_pred]
    final_num = matching_nums[0] if matching_nums else (7 if final_pred == "BIG" else 3)

    total_conf = sum([data['confidence'] for data in engines_detail.values()])
    final_conf = int(total_conf / 3)

    return {
        'prediction': final_pred,
        'number': final_num,
        'confidence': final_conf,
        'votes': votes,
        'engines': engines_detail
    }

# ============================================================
#  TELEGRAM & API FUNCTIONS
# ============================================================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Telegram Send Error:", e)

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
fetch_latest_history()
send_telegram("🚀 *3-ENGINE HYBRID VIP BOT ACTIVATED!*")

while True:
    try:
        current_period, idx = get_period_info()

        if current_period != last_processed_period:

            if last_processed_period is not None:
                # রেজাল্ট আপডেট হওয়ার জন্য ৪ সেকেন্ড অপেক্ষা
                time.sleep(4)

                real_period, actual_num = fetch_latest_history()

                if real_period and real_period[-5:] == last_processed_period[-5:]:
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

            # নতুন পিরিয়ডের প্রেডিকশন
            fetch_latest_history()
            pred_result = master_voting_system(current_period)
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
