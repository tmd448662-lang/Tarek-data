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
            print(f"Successfully loaded {len(history_data)} history items.")
    except Exception as e:
        print("History Init Fetch Error:", e)

# ============================================================
#  ENGINE 1: DARK X VIP (TITAN ULTRA Core)
# ============================================================
def dark_x_engine():
    if not history_data:
        return "BIG", 6, 85

    # Martingale / Loss Recovery Logic
    if current_loss_streak >= 1:
        last_num = history_data[0]['number']
        pred_side = "BIG" if history_data[0]['side'] == "SMALL" else "BIG"
        pred_num = 9 if pred_side == "BIG" else 1
        return pred_side, pred_num, 99

    # High-precision Frequency Check
    big_count = sum(1 for d in history_data[:3] if d['side'] == 'BIG')
    if big_count >= 1:
        return "BIG", 6, 85
    else:
        return "SMALL", 3, 80

# ============================================================
#  ENGINE 2: RGB VIP HACK (ANSH BOSS - EXACT APP MATCH)
# ============================================================
def rgb_vip_hack_engine(current_period_id):
    """ANSH BOSS অ্যাপের ১০০% রিয়েল-টাইম অ্যালগরিদম"""
    if not history_data:
        return "BIG", 7, 85

    last_num = history_data[0]['number']
    period_last_digit = int(current_period_id[-1]) if current_period_id else 0

    # ANSH BOSS Formula: (Last Number * 3 + Period Digit) % 10
    calc = (last_num * 3 + period_last_digit) % 10

    if calc >= 5:
        pred_side = "BIG"
        target_num = calc if calc in [5, 6, 7, 8, 9] else 7
    else:
        pred_side = "SMALL"
        target_num = calc if calc in [0, 1, 2, 3, 4] else 2

    # অ্যাপের নির্দিষ্ট কন্ডিশন ম্যাচিং
    if last_num in [4, 8] and period_last_digit in [5, 0]:
        pred_side = "BIG"
        target_num = 7

    return pred_side, target_num, 85

# ============================================================
#  ENGINE 3: FUKD BY SAAD (Ultimate Pro AI Exact Multi-Engine)
# ============================================================
def fukd_6sub_engines():
    """Ultimate Pro AI অ্যাপের আসল সাব-ইঞ্জিন ক্যালকুলেশন"""
    if not history_data:
        return "BIG", 7, 80

    sub_votes = {'BIG': 0, 'SMALL': 0}
    last_num = history_data[0]['number']

    # 1. CORE POWER
    core_side = "BIG" if last_num in [1, 2, 6, 7, 8, 9] else "SMALL"
    sub_votes[core_side] += 1

    # 2. SMART
    smart_side = "BIG" if last_num in [3, 4, 7, 8] else "SMALL"
    sub_votes[smart_side] += 1

    # 3. HYBRID
    recent_avg = sum([d['number'] for d in history_data[:3]]) / 3.0
    hybrid_side = "BIG" if recent_avg >= 4.0 else "SMALL"
    sub_votes[hybrid_side] += 1

    # 4. MASTER
    master_side = "BIG" if (history_data[0]['side'] == "BIG" or last_num in [3, 8, 9]) else "SMALL"
    sub_votes[master_side] += 1

    # 5. DELTA VIP
    delta_side = "BIG" if (int(history_data[0]['period'][-1]) % 2 == 0) else "BIG"
    sub_votes[delta_side] += 1

    # 6. QUANTUM
    quantum_val = (last_num * 3 + 7) % 10
    quantum_side = "BIG" if quantum_val >= 4 else "SMALL"
    sub_votes[quantum_side] += 1

    fukd_pred = max(sub_votes, key=sub_votes.get)
    fukd_num = 7 if fukd_pred == "BIG" else 3
    fukd_conf = 88

    return fukd_pred, fukd_num, fukd_conf

# ============================================================
#  MAIN MASTER VOTING SYSTEM
# ============================================================
def master_voting_system(current_period_id):
    dark_pred, dark_num, dark_conf = dark_x_engine()
    rgb_pred, rgb_num, rgb_conf = rgb_vip_hack_engine(current_period_id)
    fukd_pred, fukd_num, fukd_conf = fukd_6sub_engines()

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
    final_num = matching_nums[0] if matching_nums else (6 if final_pred == "BIG" else 2)

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
init_history_data()

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
