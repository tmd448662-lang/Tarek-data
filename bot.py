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
last_10_results = []

# ─── GLOBAL STATS ───
total_wins = 0
total_losses = 0
current_win_streak = 0
current_loss_streak = 0
last_processed_period = None
last_pred_signal = None
last_pred_num = None

# ============================================================
#  ENGINE 1: DARK X VIP (ঠিক করা)
# ============================================================
def dark_x_engine():
    """DARK X VIP - ঠিক করা"""
    if len(history_data) < 5:
        return "BIG", 7, 50
    
    sides = [d['side'] for d in history_data[:10]]
    numbers = [d['number'] for d in history_data[:10]]
    
    # ===== ৫টি ফ্যাক্টর =====
    votes = {'BIG': 0, 'SMALL': 0}
    
    # ---- 1. LAST 3 PATTERN ----
    if len(sides) >= 3:
        last3 = sides[:3]
        if last3[0] == last3[1] == last3[2]:
            # ৩টি একই হলে রিভার্সাল
            pred = "SMALL" if last3[0] == "BIG" else "BIG"
            votes[pred] += 2
        elif last3[0] == last3[1]:
            # ২টি একই হলে উল্টোটা
            pred = "SMALL" if last3[0] == "BIG" else "BIG"
            votes[pred] += 1
    
    # ---- 2. TREND ANALYSIS ----
    big_count = sides[:8].count("BIG")
    small_count = sides[:8].count("SMALL")
    
    if big_count >= 6:
        votes["SMALL"] += 2  # বেশি BIG আসলে SMALL
    elif small_count >= 6:
        votes["BIG"] += 2    # বেশি SMALL আসলে BIG
    elif big_count >= small_count:
        votes["BIG"] += 1
    else:
        votes["SMALL"] += 1
    
    # ---- 3. GAP ANALYSIS ----
    missing_nums = [n for n in range(10) if n not in numbers[:10]]
    if missing_nums:
        gap_num = missing_nums[0]
        votes["BIG" if gap_num >= 5 else "SMALL"] += 1
    
    # ---- 4. LOSS RECOVERY ----
    if current_loss_streak >= 2:
        # লস স্ট্রিকে রিভার্সাল
        opposite = "SMALL" if max(votes, key=votes.get) == "BIG" else "BIG"
        votes[opposite] += 2
    
    # ---- ফাইনাল ডিসিশন ----
    final_pred = max(votes, key=votes.get)
    
    # ---- ডায়নামিক নাম্বার ----
    if final_pred == "BIG":
        all_bigs = [5, 6, 7, 8, 9]
        recent_bigs = [n for n in numbers[:5] if n >= 5]
        available = [n for n in all_bigs if n not in recent_bigs]
        final_num = random.choice(available) if available else random.choice(all_bigs)
    else:
        all_smalls = [0, 1, 2, 3, 4]
        recent_smalls = [n for n in numbers[:5] if n < 5]
        available = [n for n in all_smalls if n not in recent_smalls]
        final_num = random.choice(available) if available else random.choice(all_smalls)
    
    # ---- কনফিডেন্স ----
    total_votes = sum(votes.values())
    if total_votes > 0:
        conf = 70 + (max(votes.values()) / total_votes * 20)
    else:
        conf = 65
    
    return final_pred, final_num, int(conf)

# ============================================================
#  ENGINE 2: FUKD BY SAAD (ঠিক করা)
# ============================================================
def fukd_saad_engine():
    """FUKD BY SAAD - ঠিক করা"""
    if len(history_data) < 8:
        return "BIG", 5, 50
    
    sides = [d['side'] for d in history_data[:10]]
    numbers = [d['number'] for d in history_data[:10]]
    
    votes = {'BIG': 0, 'SMALL': 0}
    
    # ---- 1. CORE (Weighted Score) ----
    weights = [9, 7, 5, 3, 2, 1, 1, 1]
    score = 0
    for i in range(min(8, len(history_data))):
        if history_data[i]['number'] >= 5:
            score += weights[i]
        else:
            score -= weights[i]
    
    if score >= 5:
        votes["BIG"] += 2
    elif score <= -5:
        votes["SMALL"] += 2
    elif score >= 0:
        votes["BIG"] += 1
    else:
        votes["SMALL"] += 1
    
    # ---- 2. SMART (Symmetry/Mirror) ----
    if len(sides) >= 4:
        if sides[0] == sides[3] and sides[1] == sides[2]:
            # মিরর প্যাটার্ন
            mirror_pred = "SMALL" if sides[0] == "BIG" else "BIG"
            votes[mirror_pred] += 1
        elif sides[0] == sides[1] == sides[2]:
            votes["SMALL" if sides[0] == "BIG" else "BIG"] += 1
        else:
            # ট্রেন্ড অনুযায়ী
            big_count = sides[:4].count("BIG")
            small_count = sides[:4].count("SMALL")
            votes["BIG" if big_count >= small_count else "SMALL"] += 1
    
    # ---- 3. HYBRID (Math Offset) ----
    if len(numbers) >= 2:
        math_num = (numbers[0] + numbers[1]) % 10
        votes["BIG" if math_num >= 5 else "SMALL"] += 1
    
    # ---- 4. MASTER (Weighted Score 2) ----
    score2 = 0
    for i in range(min(8, len(history_data))):
        if history_data[i]['number'] >= 5:
            score2 += (8 - i)
        else:
            score2 -= (8 - i)
    
    if score2 >= 5:
        votes["BIG"] += 2
    elif score2 <= -5:
        votes["SMALL"] += 2
    elif score2 >= 0:
        votes["BIG"] += 1
    else:
        votes["SMALL"] += 1
    
    # ---- 5. ADVANCED (Memory Based) ----
    if current_loss_streak >= 2:
        # লস স্ট্রিকে রিভার্সাল
        opposite = "SMALL" if max(votes, key=votes.get) == "BIG" else "BIG"
        votes[opposite] += 2
    else:
        # নরমাল ট্রেন্ড
        big_count = sides[:8].count("BIG")
        votes["BIG" if big_count >= 4 else "SMALL"] += 1
    
    # ---- 6. ULTIMATE (Streak Analysis) ----
    streak = 1
    for i in range(1, len(sides[:8])):
        if sides[i] == sides[i-1]:
            streak += 1
        else:
            break
    
    if streak >= 4:
        votes["SMALL" if sides[0] == "BIG" else "BIG"] += 2
    elif streak >= 2:
        votes["SMALL" if sides[0] == "BIG" else "BIG"] += 1
    
    # ---- ফাইনাল ডিসিশন ----
    final_pred = max(votes, key=votes.get)
    
    # ---- ডায়নামিক নাম্বার ----
    if final_pred == "BIG":
        all_bigs = [5, 6, 7, 8, 9]
        recent_bigs = [n for n in numbers[:5] if n >= 5]
        available = [n for n in all_bigs if n not in recent_bigs]
        final_num = random.choice(available) if available else random.choice(all_bigs)
    else:
        all_smalls = [0, 1, 2, 3, 4]
        recent_smalls = [n for n in numbers[:5] if n < 5]
        available = [n for n in all_smalls if n not in recent_smalls]
        final_num = random.choice(available) if available else random.choice(all_smalls)
    
    # ---- কনফিডেন্স ----
    total_votes = sum(votes.values())
    if total_votes > 0:
        conf = 70 + (max(votes.values()) / total_votes * 20)
    else:
        conf = 65
    
    return final_pred, final_num, int(conf)

# ============================================================
#  ENGINE 3: RGB VIP HACK (ঠিক আছে)
# ============================================================
def rgb_vip_hack_engine():
    """RGB VIP HACK - Dynamic Pattern"""
    if len(history_data) < 12:
        return "BIG", 7, 50
    
    sides = [d['side'] for d in history_data[:10]]
    numbers = [d['number'] for d in history_data[:10]]
    
    votes = {'BIG': 0, 'SMALL': 0}
    
    # ---- 1. BASE PATTERN ----
    now = datetime.now(timezone.utc)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    diff = int((now - start_of_day).total_seconds())
    idx = (diff // 60) + 1
    pattern_idx = (idx + 5) % 12
    base_pred = BASE_PATTERN[pattern_idx]
    votes[base_pred["s"]] += 2
    base_num = base_pred["n"]
    
    # ---- 2. STREAK ----
    streak = 1
    for i in range(1, len(sides[:8])):
        if sides[i] == sides[i-1]:
            streak += 1
        else:
            break
    
    if streak >= 4:
        votes["SMALL" if sides[0] == "BIG" else "BIG"] += 2
    elif streak >= 2:
        votes["SMALL" if sides[0] == "BIG" else "BIG"] += 1
    
    # ---- 3. ALTERNATING ----
    if len(sides) >= 5:
        alt_pattern = True
        for i in range(1, 5):
            if sides[i] == sides[i-1]:
                alt_pattern = False
                break
        if alt_pattern:
            alt_pred = "SMALL" if sides[4] == "BIG" else "BIG"
            votes[alt_pred] += 1
    
    # ---- 4. MIRROR ----
    if len(sides) >= 5 and sides[0] == sides[4] and sides[1] == sides[3]:
        mirror_pred = "SMALL" if sides[0] == "BIG" else "BIG"
        votes[mirror_pred] += 1
    
    # ---- 5. GAP ----
    missing_nums = [n for n in range(10) if n not in numbers[:10]]
    if missing_nums:
        gap_num = missing_nums[0]
        votes["BIG" if gap_num >= 5 else "SMALL"] += 1
    
    # ---- ফাইনাল ----
    final_pred = max(votes, key=votes.get)
    
    if final_pred == "BIG":
        all_bigs = [5, 6, 7, 8, 9]
        recent_bigs = [n for n in numbers[:5] if n >= 5]
        available = [n for n in all_bigs if n not in recent_bigs]
        final_num = random.choice(available) if available else random.choice(all_bigs)
    else:
        all_smalls = [0, 1, 2, 3, 4]
        recent_smalls = [n for n in numbers[:5] if n < 5]
        available = [n for n in all_smalls if n not in recent_smalls]
        final_num = random.choice(available) if available else random.choice(all_smalls)
    
    total_votes = sum(votes.values())
    conf = 70 + (max(votes.values()) / total_votes * 20) if total_votes > 0 else 65
    
    return final_pred, final_num, int(conf)

# ============================================================
#  MASTER VOTING SYSTEM (3 Engines)
# ============================================================

def master_voting_system():
    """৩টি ইঞ্জিনের ভোট"""
    
    dark_pred, dark_num, dark_conf = dark_x_engine()
    fukd_pred, fukd_num, fukd_conf = fukd_saad_engine()
    rgb_pred, rgb_num, rgb_conf = rgb_vip_hack_engine()
    
    votes = {'BIG': 0, 'SMALL': 0}
    numbers = []
    confidences = []
    engines_detail = {}
    
    votes[dark_pred] += 1
    numbers.append(dark_num)
    confidences.append(dark_conf)
    engines_detail['DARK X VIP'] = {'prediction': dark_pred, 'number': dark_num, 'confidence': dark_conf}
    
    votes[fukd_pred] += 1
    numbers.append(fukd_num)
    confidences.append(fukd_conf)
    engines_detail['FUKD BY SAAD (6-Engine)'] = {'prediction': fukd_pred, 'number': fukd_num, 'confidence': fukd_conf}
    
    votes[rgb_pred] += 1
    numbers.append(rgb_num)
    confidences.append(rgb_conf)
    engines_detail['RGB VIP HACK'] = {'prediction': rgb_pred, 'number': rgb_num, 'confidence': rgb_conf}
    
    final_pred = max(votes, key=votes.get)
    
    if votes['BIG'] == votes['SMALL']:
        big_conf = sum([d['confidence'] for d in engines_detail.values() if d['prediction'] == 'BIG'])
        small_conf = sum([d['confidence'] for d in engines_detail.values() if d['prediction'] == 'SMALL'])
        final_pred = "BIG" if big_conf >= small_conf else "SMALL"
    
    pred_numbers = [n for n in numbers if (n >= 5 and final_pred == "BIG") or (n < 5 and final_pred == "SMALL")]
    if pred_numbers:
        final_num = pred_numbers[0]
    else:
        final_num = random.choice([7 if final_pred == "BIG" else 2])
    
    final_conf = int(sum(confidences) / len(confidences))
    
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
            data = res.json()
            list_data = data.get("data", {}).get("list", [])
            if list_data:
                return str(list_data[0].get("issueNumber")), int(list_data[0].get("number"))
    except Exception:
        pass

    try:
        proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={requests.utils.quote(raw_url)}"
        res = requests.get(proxy_url, timeout=8)
        if res.status_code == 200:
            data = res.json()
            list_data = data.get("data", {}).get("list", [])
            if list_data:
                return str(list_data[0].get("issueNumber")), int(list_data[0].get("number"))
    except Exception as e:
        print("Fetch Error:", e)

    return None, None

# ============================================================
#  MAIN LOOP
# ============================================================

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

# ─── START ───
send_telegram("🚀 *3-ENGINE HYBRID VIP BOT ACTIVATED!*")
send_telegram(
    "🔥 *3-ENGINE HYBRID VIP* 🔥\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🗳️ *VOTING SYSTEM*\n"
    "├─ DARK X VIP (Dynamic)\n"
    "├─ FUKD BY SAAD (Dynamic)\n"
    "└─ RGB VIP HACK (Dynamic)\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "⚡ MODE: 1 MIN WINGO\n"
    "📊 HOURLY REPORT: ACTIVE\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "⏳ WAITING FOR FIRST SIGNAL..."
)

while True:
    try:
        current_period, idx = get_period_info()
        
        if current_period != last_processed_period:
            
            if last_processed_period is not None:
                time.sleep(4)
                
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
