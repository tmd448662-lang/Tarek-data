import asyncio
import time
import requests
import os
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Bot

# ==================== RENDER WEB SERVICE PORT BINDING ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"3-SYSTEM HYBRID VIP BOT is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ==================== KEEP-ALIVE ====================
def keep_alive():
    while True:
        try:
            time.sleep(600)
            port = int(os.environ.get("PORT", 8080))
            requests.get(f"http://localhost:{port}/", timeout=5)
        except:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

# ==================== BOT CONFIG ====================
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"
RAW_API = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

bot = Bot(token=BOT_TOKEN)

# ==================== STATS ====================
total_wins = 0
total_losses = 0
loss_streak = 0
current_level = 1
total_rounds = 0
history_data = []

last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
prediction_sent_for_period = {}

# ==================== HOURLY STATS ====================
hourly_stats = {
    'wins': 0,
    'losses': 0,
    'total': 0,
    'max_win_streak': 0,
    'max_loss_streak': 0,
    'current_streak': 0,
    'streak_type': 'WIN'
}
last_hour_report_time = time.time()

# ============================================================
#  ENGINE 1: DARK X VIP (ঠিক করা)
# ============================================================

def dark_x_engine(data):
    """DARK X VIP - ঠিক করা (স্ক্রিনশট অনুযায়ী)"""
    if len(data) < 5:
        return {"prediction": "BIG", "confidence": 50, "number": 7}
    
    sides = [d['side'] for d in data[:10]]
    numbers = [d['number'] for d in data[:10]]
    
    # ===== ডায়নামিক ভোটিং =====
    votes = {'BIG': 0, 'SMALL': 0}
    
    # ---- 1. লাস্ট ৩ প্যাটার্ন ----
    if len(sides) >= 3:
        last3 = sides[:3]
        if last3[0] == last3[1] == last3[2]:
            # ৩টি একই হলে রিভার্সাল
            votes["SMALL" if last3[0] == "BIG" else "BIG"] += 3
        elif last3[0] == last3[1]:
            votes["SMALL" if last3[0] == "BIG" else "BIG"] += 2
        elif last3[1] == last3[2]:
            votes["SMALL" if last3[1] == "BIG" else "BIG"] += 2
        else:
            votes[last3[0]] += 1
    
    # ---- 2. ট্রেন্ড অ্যানালাইসিস ----
    big_count = sum(1 for s in sides[:8] if s == "BIG")
    small_count = sum(1 for s in sides[:8] if s == "SMALL")
    
    if big_count >= 6:
        votes["SMALL"] += 2  # বেশি BIG আসলে SMALL
    elif small_count >= 6:
        votes["BIG"] += 2    # বেশি SMALL আসলে BIG
    elif big_count >= small_count:
        votes["BIG"] += 1
    else:
        votes["SMALL"] += 1
    
    # ---- 3. গ্যাপ অ্যানালাইসিস ----
    missing = [n for n in range(10) if n not in numbers[:10]]
    if missing:
        gap = missing[0]
        votes["BIG" if gap >= 5 else "SMALL"] += 1
    
    # ---- 4. লস রিকভারি ----
    global loss_streak
    if loss_streak <= -2:
        opposite = "SMALL" if max(votes, key=votes.get) == "BIG" else "BIG"
        votes[opposite] += 3
    
    # ---- 5. লেভেল ৩ বুস্ট ----
    global current_level
    if current_level >= 3:
        opposite = "SMALL" if max(votes, key=votes.get) == "BIG" else "BIG"
        votes[opposite] += 2
    
    # ---- ফাইনাল ----
    final_pred = max(votes, key=votes.get)
    total_votes = sum(votes.values())
    conf = 70 + (max(votes.values()) / total_votes * 25) if total_votes > 0 else 70
    conf = int(min(99, conf))
    
    # ---- নাম্বার ----
    if final_pred == "BIG":
        recent_bigs = [n for n in numbers[:5] if n >= 5]
        available = [n for n in [5, 6, 7, 8, 9] if n not in recent_bigs]
        num = random.choice(available) if available else random.randint(5, 9)
    else:
        recent_smalls = [n for n in numbers[:5] if n < 5]
        available = [n for n in [0, 1, 2, 3, 4] if n not in recent_smalls]
        num = random.choice(available) if available else random.randint(0, 4)
    
    return {"prediction": final_pred, "confidence": conf, "number": num}

# ============================================================
#  ENGINE 2: FUKD BY SAAD (ঠিক করা - 6 Engines Voting)
# ============================================================

def fukd_saad_engine(data):
    """FUKD BY SAAD - ঠিক করা (6 Engines Voting)"""
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 60, "number": 5}
    
    sides = [d['side'] for d in data[:10]]
    numbers = [d['number'] for d in data[:10]]
    
    votes = {'BIG': 0, 'SMALL': 0}
    confidences = []
    
    # ---- 1. CORE ENGINE ----
    weights = [9, 7, 5, 3, 2, 1, 1, 1]
    score = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score += weights[i]
        else:
            score -= weights[i]
    votes["BIG" if score >= 0 else "SMALL"] += 1
    confidences.append(85 if abs(score) >= 5 else 75)
    
    # ---- 2. SMART ENGINE (সিমেট্রি) ----
    if len(sides) >= 4:
        if sides[0] == sides[3] and sides[1] == sides[2]:
            votes["SMALL" if sides[0] == "BIG" else "BIG"] += 1
            confidences.append(92)
        elif sides[0] == sides[1] and sides[1] == sides[2]:
            votes["SMALL" if sides[0] == "BIG" else "BIG"] += 1
            confidences.append(90)
        else:
            b_count = sides[:4].count("BIG")
            votes["BIG" if b_count >= 2 else "SMALL"] += 1
            confidences.append(75)
    
    # ---- 3. HYBRID ENGINE ----
    if len(numbers) >= 2:
        math_num = (numbers[0] + numbers[1]) % 10
        votes["BIG" if math_num >= 5 else "SMALL"] += 1
        confidences.append(82)
    
    # ---- 4. MASTER ENGINE ----
    score2 = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score2 += (8 - i)
        else:
            score2 -= (8 - i)
    votes["BIG" if score2 >= 0 else "SMALL"] += 1
    confidences.append(90 if abs(score2) >= 5 else 80)
    
    # ---- 5. ADVANCED ENGINE (মেমরি) ----
    global loss_streak
    if loss_streak <= -2:
        votes["SMALL" if max(votes, key=votes.get) == "BIG" else "BIG"] += 2
        confidences.append(95)
    else:
        b_count = sides[:8].count("BIG")
        votes["BIG" if b_count >= 4 else "SMALL"] += 1
        confidences.append(80)
    
    # ---- 6. ULTIMATE ENGINE ----
    streak = 1
    for i in range(1, len(sides[:8])):
        if sides[i] == sides[i-1]:
            streak += 1
        else:
            break
    
    if streak >= 4:
        votes["SMALL" if sides[0] == "BIG" else "BIG"] += 2
        confidences.append(95)
    elif streak >= 2:
        votes["SMALL" if sides[0] == "BIG" else "BIG"] += 1
        confidences.append(88)
    else:
        b_count = sides[:8].count("BIG")
        votes["BIG" if b_count >= 4 else "SMALL"] += 1
        confidences.append(75)
    
    # ---- ফাইনাল ----
    final_pred = max(votes, key=votes.get)
    final_conf = int(sum(confidences) / len(confidences)) if confidences else 70
    
    if final_pred == "BIG":
        recent_bigs = [n for n in numbers[:5] if n >= 5]
        available = [n for n in [5, 6, 7, 8, 9] if n not in recent_bigs]
        num = random.choice(available) if available else random.randint(5, 9)
    else:
        recent_smalls = [n for n in numbers[:5] if n < 5]
        available = [n for n in [0, 1, 2, 3, 4] if n not in recent_smalls]
        num = random.choice(available) if available else random.randint(0, 4)
    
    return {"prediction": final_pred, "confidence": final_conf, "number": num}

# ============================================================
#  ENGINE 3: ULTIMATE PRO AI (ঠিক করা)
# ============================================================

def ultimate_pro_engine(data):
    """ULTIMATE PRO AI - ঠিক করা"""
    if len(data) < 10:
        return {"prediction": "BIG", "confidence": 70, "number": 7}
    
    sides = [d['side'] for d in data[:15]]
    numbers = [d['number'] for d in data[:15]]
    
    votes = {'BIG': 0, 'SMALL': 0}
    
    # ---- 1. স্ট্রিক ডিটেকশন ----
    streak = 1
    for i in range(1, len(sides)):
        if sides[i] == sides[i-1]:
            streak += 1
        else:
            break
    
    if streak >= 5:
        votes["SMALL" if sides[0] == "BIG" else "BIG"] += 4
    elif streak >= 3:
        votes["SMALL" if sides[0] == "BIG" else "BIG"] += 2
    
    # ---- 2. অল্টারনেটিং প্যাটার্ন ----
    if len(sides) >= 5:
        alt = True
        for i in range(1, 5):
            if sides[i] == sides[i-1]:
                alt = False
                break
        if alt:
            votes["SMALL" if sides[4] == "BIG" else "BIG"] += 3
    
    # ---- 3. মিরর প্যাটার্ন ----
    if len(sides) >= 5 and sides[0] == sides[4] and sides[1] == sides[3]:
        votes["SMALL" if sides[0] == "BIG" else "BIG"] += 2
    
    # ---- 4. ট্রেন্ড অ্যানালাইসিস ----
    big_count = sum(1 for s in sides[:10] if s == "BIG")
    small_count = sum(1 for s in sides[:10] if s == "SMALL")
    
    if big_count >= 7:
        votes["SMALL"] += 3
    elif small_count >= 7:
        votes["BIG"] += 3
    elif big_count >= small_count:
        votes["BIG"] += 1
    else:
        votes["SMALL"] += 1
    
    # ---- 5. ফ্রিকোয়েন্সি অ্যানালাইসিস ----
    freq = [0] * 10
    for n in numbers[:15]:
        freq[n] += 1
    min_freq = min(freq)
    cold = [i for i, f in enumerate(freq) if f == min_freq]
    if cold:
        votes["BIG" if cold[0] >= 5 else "SMALL"] += 1
    
    # ---- 6. গ্যাপ অ্যানালাইসিস ----
    missing = [n for n in range(10) if n not in numbers[:10]]
    if missing:
        votes["BIG" if missing[0] >= 5 else "SMALL"] += 1
    
    # ---- 7. লস রিকভারি ----
    global loss_streak
    if loss_streak <= -2:
        opposite = "SMALL" if max(votes, key=votes.get) == "BIG" else "BIG"
        votes[opposite] += 3
    
    # ---- 8. লেভেল ৩ বুস্ট ----
    global current_level
    if current_level >= 3:
        opposite = "SMALL" if max(votes, key=votes.get) == "BIG" else "BIG"
        votes[opposite] += 2
    
    # ---- ফাইনাল ----
    final_pred = max(votes, key=votes.get)
    total_votes = sum(votes.values())
    conf = 70 + (max(votes.values()) / total_votes * 25) if total_votes > 0 else 70
    conf = int(min(99, conf))
    
    if final_pred == "BIG":
        cold_big = [n for n in cold if n >= 5] if cold else []
        num = cold_big[0] if cold_big else random.randint(5, 9)
    else:
        cold_small = [n for n in cold if n < 5] if cold else []
        num = cold_small[0] if cold_small else random.randint(0, 4)
    
    return {"prediction": final_pred, "confidence": conf, "number": num}

# ============================================================
#  MASTER VOTING SYSTEM (3 Engines)
# ============================================================

def master_voting_system(data):
    """৩টি সিস্টেমের ভোট - Majority Voting"""
    
    dark_x = dark_x_engine(data)
    fukd = fukd_saad_engine(data)
    ultimate = ultimate_pro_engine(data)
    
    votes = {'BIG': 0, 'SMALL': 0}
    
    # DARK X
    votes[dark_x['prediction']] += 1
    
    # FUKD BY SAAD
    votes[fukd['prediction']] += 1
    
    # ULTIMATE PRO
    votes[ultimate['prediction']] += 1
    
    final_pred = max(votes, key=votes.get)
    
    # Tie Breaker (Confidence Based)
    if votes['BIG'] == votes['SMALL']:
        dark_conf = dark_x['confidence']
        fukd_conf = fukd['confidence']
        ultimate_conf = ultimate['confidence']
        
        big_conf = 0
        small_conf = 0
        
        if dark_x['prediction'] == 'BIG':
            big_conf += dark_conf
        else:
            small_conf += dark_conf
            
        if fukd['prediction'] == 'BIG':
            big_conf += fukd_conf
        else:
            small_conf += fukd_conf
            
        if ultimate['prediction'] == 'BIG':
            big_conf += ultimate_conf
        else:
            small_conf += ultimate_conf
        
        final_pred = "BIG" if big_conf >= small_conf else "SMALL"
    
    # Number Selection
    if final_pred == "BIG":
        numbers = [n for n in [dark_x['number'], fukd['number'], ultimate['number']] if n >= 5]
        final_num = numbers[0] if numbers else 7
    else:
        numbers = [n for n in [dark_x['number'], fukd['number'], ultimate['number']] if n < 5]
        final_num = numbers[0] if numbers else 2
    
    # Best Engine
    best = max([
        ('DARK X', dark_x),
        ('FUKD BY SAAD', fukd),
        ('ULTIMATE PRO', ultimate)
    ], key=lambda x: x[1]['confidence'])
    
    # Final Confidence
    confs = [dark_x['confidence'], fukd['confidence'], ultimate['confidence']]
    final_conf = int(sum(confs) / len(confs))
    
    return {
        'prediction': final_pred,
        'number': final_num,
        'confidence': final_conf,
        'best_engine': best[0],
        'votes': votes,
        'dark_x': dark_x,
        'fukd': fukd,
        'ultimate': ultimate
    }

# ============================================================
#  API FETCH
# ============================================================

def fetch_api_data():
    try:
        res = requests.get(RAW_API + "?t=" + str(int(time.time() * 1000)), timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", {}).get("list", [])
    except:
        pass
    return []

# ============================================================
#  HOURLY REPORT
# ============================================================

async def send_hourly_report():
    global hourly_stats, last_hour_report_time
    
    if time.time() - last_hour_report_time >= 3600:
        total = hourly_stats['total']
        wins = hourly_stats['wins']
        losses = hourly_stats['losses']
        win_rate = (wins / total * 100) if total > 0 else 0
        
        report_msg = (
            f"📊 *HOURLY PERFORMANCE REPORT*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🕐 *TIME:* {datetime.now().strftime('%I:%M %p')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔄 *TOTAL ROUNDS:* `{total}`\n"
            f"✅ *WINS:* `{wins}`\n"
            f"❌ *LOSSES:* `{losses}`\n"
            f"📈 *WIN RATE:* `{win_rate:.1f}%`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 *BEST WIN STREAK:* `{hourly_stats['max_win_streak']}x`\n"
            f"📉 *WORST LOSS STREAK:* `{hourly_stats['max_loss_streak']}x`\n"
            f"🔥 *CURRENT STREAK:* `{hourly_stats['current_streak']}x {hourly_stats['streak_type']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🧠 *3-SYSTEM VOTING: DARK X + FUKD + ULTIMATE PRO*\n"
            f"💎 3-SYSTEM HYBRID VIP V9"
        )
        
        try:
            await bot.send_message(chat_id=CHAT_ID, text=report_msg, parse_mode="Markdown")
        except:
            pass
        
        hourly_stats = {
            'wins': 0, 'losses': 0, 'total': 0,
            'max_win_streak': 0, 'max_loss_streak': 0,
            'current_streak': 0, 'streak_type': 'WIN'
        }
        last_hour_report_time = time.time()

# ============================================================
#  MAIN LOOP
# ============================================================

async def prediction_bot():
    global total_wins, total_losses, loss_streak, current_level
    global total_rounds, history_data, last_predicted_period
    global last_predicted_signal, last_predicted_num, prediction_sent_for_period

    print("🔥 3-SYSTEM HYBRID VIP BOT STARTED...")
    print("🧠 DARK X + FUKD BY SAAD + ULTIMATE PRO")
    print("🗳️ MAJORITY VOTING SYSTEM")
    print("━━━━━━━━━━━━━━━━━━━━")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🔥 3-SYSTEM HYBRID VIP 🔥\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "🧠 DARK X + FUKD BY SAAD + ULTIMATE PRO\n"
                 "🗳️ MAJORITY VOTING = FINAL\n"
                 "⚡ MODE: 1 MIN WINGO\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "⏳ WAITING FOR FIRST SIGNAL...",
        )
    except Exception as e:
        print(f"Startup error: {e}")

    while True:
        try:
            current_sec = int(time.time()) % 60
            sleep_time = 60 - current_sec + 3
            await asyncio.sleep(sleep_time)

            history = fetch_api_data()
            if not history:
                continue

            latest_issue = str(history[0]['issueNumber'])
            actual_num = int(history[0]['number'])
            actual_type = "BIG" if actual_num >= 5 else "SMALL"

            history_data = []
            for h in history[:20]:
                num = int(h['number'])
                history_data.append({
                    'issueNumber': str(h['issueNumber']),
                    'number': num,
                    'side': "BIG" if num >= 5 else "SMALL"
                })

            # ===== RESULT CHECK =====
            if last_predicted_period == latest_issue and last_predicted_signal is not None:
                
                is_win = last_predicted_signal == actual_type
                is_jackpot = (actual_num == last_predicted_num)
                
                if is_jackpot:
                    status = "⭐ JACKPOT"
                    loss_streak = 0 if loss_streak < 0 else loss_streak + 1
                    current_level = 1
                elif is_win:
                    total_wins += 1
                    hourly_stats['wins'] += 1
                    status = "🟢 WIN"
                    loss_streak = 0 if loss_streak < 0 else loss_streak + 1
                    current_level = 1
                    
                    if hourly_stats['streak_type'] == 'WIN':
                        hourly_stats['current_streak'] += 1
                    else:
                        hourly_stats['current_streak'] = 1
                        hourly_stats['streak_type'] = 'WIN'
                    
                    if hourly_stats['current_streak'] > hourly_stats['max_win_streak']:
                        hourly_stats['max_win_streak'] = hourly_stats['current_streak']
                else:
                    total_losses += 1
                    hourly_stats['losses'] += 1
                    status = "🔴 LOSS"
                    loss_streak = -1 if loss_streak > 0 else loss_streak - 1
                    current_level = 3 if current_level >= 3 else current_level + 1
                    
                    if hourly_stats['streak_type'] == 'LOSS':
                        hourly_stats['current_streak'] += 1
                    else:
                        hourly_stats['current_streak'] = 1
                        hourly_stats['streak_type'] = 'LOSS'
                    
                    if hourly_stats['current_streak'] > hourly_stats['max_loss_streak']:
                        hourly_stats['max_loss_streak'] = hourly_stats['current_streak']
                
                total_rounds += 1
                hourly_stats['total'] += 1
                
                total_games = total_wins + total_losses
                win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0
                multiplier = f"{current_level}x"
                
                result_msg = (
                    f"🎯 *RESULT UPDATE*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: `#{latest_issue[-5:]}`\n"
                    f"🎯 PREDICTED: `{last_predicted_signal}` → `{last_predicted_num}`\n"
                    f"🎰 ACTUAL: `{actual_num}` (`{actual_type}`)\n"
                    f"📌 RESULT: {status}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 WIN RATE: `{win_rate:.1f}%` ({total_wins}W/{total_losses}L)\n"
                    f"🔥 STREAK: `{loss_streak:+d}`\n"
                    f"👑 LEVEL: `{current_level}` ({multiplier})\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🗳️ 3-SYSTEM VOTING\n"
                    f"💎 3-SYSTEM HYBRID VIP V9"
                )
                
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                    await asyncio.sleep(1)
                except:
                    pass
                
                await send_hourly_report()
                
                last_predicted_period = None
                last_predicted_signal = None
                last_predicted_num = None

            # ===== NEW PREDICTION =====
            next_period = str(int(latest_issue) + 1)
            
            if not prediction_sent_for_period.get(next_period, False):
                
                pred = master_voting_system(history_data)
                multiplier = f"{current_level}x"
                
                prediction_msg = (
                    f"🔥 *3-SYSTEM HYBRID VIP* 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: `#{next_period[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🗳️ *VOTING RESULT*\n"
                    f"📊 BIG: `{pred['votes']['BIG']}` | SMALL: `{pred['votes']['SMALL']}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📈 *FINAL PREDICTION*\n"
                    f"🎯 PREDICTION: `{pred['prediction']}`\n"
                    f"🔢 TARGET NUMBER: `{pred['number']}`\n"
                    f"⚡ CONFIDENCE: `{pred['confidence']}%`\n"
                    f"🧠 BEST ENGINE: `{pred['best_engine']}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 *DARK X:* `{pred['dark_x']['prediction']}` ({pred['dark_x']['number']}) `{pred['dark_x']['confidence']}%`\n"
                    f"🧠 *FUKD BY SAAD:* `{pred['fukd']['prediction']}` ({pred['fukd']['number']}) `{pred['fukd']['confidence']}%`\n"
                    f"🧠 *ULTIMATE PRO:* `{pred['ultimate']['prediction']}` ({pred['ultimate']['number']}) `{pred['ultimate']['confidence']}%`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👑 LEVEL: `{current_level}` ({multiplier})\n"
                    f"🔥 STREAK: `{loss_streak:+d}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ RESULT AWAITING...\n"
                    f"💎 3-SYSTEM HYBRID VIP V9"
                )
                
                last_predicted_period = next_period
                last_predicted_signal = pred['prediction']
                last_predicted_num = pred['number']
                prediction_sent_for_period[next_period] = True
                
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=prediction_msg, parse_mode="Markdown")
                except:
                    pass

            if len(prediction_sent_for_period) > 5:
                oldest = min(prediction_sent_for_period.keys())
                del prediction_sent_for_period[oldest]

        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(5)

if __name__ == '__main__':
    print("🔥 3-SYSTEM HYBRID VIP BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 DARK X + FUKD BY SAAD + ULTIMATE PRO")
    print("🗳️ MAJORITY VOTING SYSTEM")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
