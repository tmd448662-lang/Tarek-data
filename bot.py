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
        self.wfile.write(b"SUPER HYBRID BOT is running!")

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
jackpots = 0
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
    'wins': 0, 'losses': 0, 'total': 0,
    'max_win_streak': 0, 'max_loss_streak': 0,
    'current_streak': 0, 'streak_type': 'WIN'
}
last_hour_report_time = time.time()

# ============================================================
#  ENGINE 1: DARK X (FIXED - 7 ENGINES থেকে)
# ============================================================

def dark_x_engine(data):
    if len(data) < 5:
        return {"prediction": "BIG", "confidence": 50, "number": 7}
    
    sides = [d['side'] for d in data[:10]]
    last1 = sides[0] if len(sides) > 0 else "BIG"
    last2 = sides[1] if len(sides) > 1 else "BIG"
    last3 = sides[2] if len(sides) > 2 else "BIG"
    
    big_count = sum(1 for s in sides[:8] if s == "BIG")
    small_count = sum(1 for s in sides[:8] if s == "SMALL")
    trend = "BIG" if big_count > small_count else "SMALL"
    
    if last1 == last2 and last2 == last3:
        pred = "SMALL" if last1 == "BIG" else "BIG"
        conf = 92
    elif big_count >= 6:
        pred = "BIG"
        conf = 85
    elif small_count >= 6:
        pred = "SMALL"
        conf = 85
    else:
        if last1 == "SMALL" and last2 == "SMALL":
            pred = "BIG"
            conf = 75
        elif last1 == "BIG" and last2 == "BIG":
            pred = "SMALL"
            conf = 75
        else:
            pred = trend
            conf = 70
    
    global loss_streak
    if loss_streak <= -2:
        pred = "SMALL" if pred == "BIG" else "BIG"
        conf = min(98, conf + 15)
    
    global current_level
    if current_level == 3:
        pred = "SMALL" if pred == "BIG" else "BIG"
        conf = min(99, conf + 10)
    
    num = pred == "BIG" and 7 or 2
    
    return {"prediction": pred, "confidence": conf, "number": num, "engine": "DARK X"}

# ============================================================
#  ENGINE 2: ANSH BOSS (12-STEP RGB PATTERN)
# ============================================================

def ansh_boss_engine(data):
    """ANSH BOSS - 12 Step RGB Pattern"""
    if len(data) < 12:
        return {"prediction": "BIG", "confidence": 60, "number": 5, "engine": "ANSH BOSS"}
    
    PATTERN = [
        {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 2}, {"s": "SMALL", "n": 4},
        {"s": "BIG", "n": 9}, {"s": "BIG", "n": 6}, {"s": "SMALL", "n": 0},
        {"s": "BIG", "n": 8}, {"s": "SMALL", "n": 3}, {"s": "SMALL", "n": 1},
        {"s": "BIG", "n": 5}, {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 4}
    ]
    
    period = data[0]['issueNumber']
    idx = int(str(period)[-3:]) % 12
    pred = PATTERN[idx]
    
    return {"prediction": pred["s"], "confidence": 78, "number": pred["n"], "engine": "ANSH BOSS"}

# ============================================================
#  ENGINE 3: TITAN ULTRA (MARKOV CHAIN + LEVEL 3)
# ============================================================

def titan_engine(data):
    """TITAN ULTRA - Markov Chain with Level 3"""
    if len(data) < 5:
        return {"prediction": "BIG", "confidence": 60, "number": 7, "engine": "TITAN ULTRA"}
    
    sides = [d['side'] for d in data[:10]]
    last1 = sides[0] if len(sides) > 0 else "BIG"
    last2 = sides[1] if len(sides) > 1 else "BIG"
    
    if last1 == "SMALL":
        pred = "BIG"
        conf = 75
    elif last1 == "BIG":
        pred = "SMALL"
        conf = 60
    else:
        pred = "BIG"
        conf = 50
    
    if last1 == "BIG" and last2 == "BIG":
        pred = "SMALL"
        conf = 90
    elif last1 == "SMALL" and last2 == "SMALL":
        pred = "BIG"
        conf = 95
    
    global current_level
    if current_level == 3:
        latest = data[0]['number']
        pred = "SMALL" if latest >= 5 else "BIG"
        conf = 99
    
    num = pred == "BIG" and 9 or 1
    
    return {"prediction": pred, "confidence": conf, "number": num, "engine": "TITAN ULTRA"}

# ============================================================
#  ENGINE 4: CORE POWER (7 Engines থেকে)
# ============================================================

def core_engine(data):
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 76, "number": 6, "engine": "CORE POWER"}
    
    weights = [9, 7, 5, 3, 2, 1, 1, 1]
    score = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score += weights[i]
        else:
            score -= weights[i]
    
    pred = "BIG" if score >= 0 else "SMALL"
    conf = 87 if abs(score) >= 3 else 76
    num = pred == "BIG" and 6 or 0
    
    return {"prediction": pred, "confidence": conf, "number": num, "engine": "CORE POWER"}

# ============================================================
#  ENGINE 5: MASTER (7 Engines থেকে)
# ============================================================

def master_engine(data):
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 73, "number": 6, "engine": "MASTER"}
    
    score = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score += (8 - i)
        else:
            score -= (8 - i)
    
    pred = "BIG" if score >= 0 else "SMALL"
    conf = 95
    num = pred == "BIG" and 8 or 3
    
    return {"prediction": pred, "confidence": conf, "number": num, "engine": "MASTER"}

# ============================================================
#  ENGINE 6: ULTIMATE (7 Engines থেকে)
# ============================================================

def ultimate_engine(data):
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 70, "number": 6, "engine": "ULTIMATE"}
    
    sides = [d['side'] for d in data[:8]]
    streak = 1
    for i in range(1, len(sides)):
        if sides[i] == sides[i-1]:
            streak += 1
        else:
            break
    
    if streak >= 5:
        pred = "SMALL" if sides[0] == "BIG" else "BIG"
        conf = 95
    else:
        big_count = sides.count("BIG")
        pred = "BIG" if big_count >= 4 else "SMALL"
        conf = 70 + (abs(big_count - 4) * 5)
        conf = min(95, conf)
    
    num = pred == "BIG" and 7 or 4
    
    return {"prediction": pred, "confidence": conf, "number": num, "engine": "ULTIMATE"}

# ============================================================
#  ENGINE 7: SMART (7 Engines থেকে)
# ============================================================

def smart_engine(data):
    if len(data) < 4:
        return {"prediction": "SMALL", "confidence": 75, "number": 2, "engine": "SMART"}
    
    sides = [d['side'] for d in data[:4]]
    if sides[0] == sides[3] and sides[1] == sides[2]:
        pred = "SMALL" if sides[0] == "BIG" else "BIG"
        conf = 92
    else:
        pred = "SMALL"
        conf = 75
    
    num = pred == "BIG" and 8 or 1
    
    return {"prediction": pred, "confidence": conf, "number": num, "engine": "SMART"}

# ============================================================
#  MASTER VOTING SYSTEM (7 ENGINES)
# ============================================================

def master_voting_system(data):
    """৭টি ইঞ্জিনের ভোট নিয়ে ফাইনাল সিদ্ধান্ত"""
    
    # ===== ৭টি ইঞ্জিন চালু =====
    engines = [
        dark_x_engine(data),
        ansh_boss_engine(data),
        titan_engine(data),
        core_engine(data),
        master_engine(data),
        ultimate_engine(data),
        smart_engine(data)
    ]
    
    # ===== ভোট কাউন্ট =====
    votes = {'BIG': 0, 'SMALL': 0}
    numbers = []
    confidences = []
    engine_details = {}
    
    for eng in engines:
        votes[eng['prediction']] += 1
        numbers.append(eng['number'])
        confidences.append(eng['confidence'])
        engine_details[eng['engine']] = {
            'prediction': eng['prediction'],
            'number': eng['number'],
            'confidence': eng['confidence']
        }
    
    # ===== ফাইনাল ডিসিশন =====
    final_pred = max(votes, key=votes.get)
    
    # সংখ্যা: যে প্রেডিকশন জিতেছে তার সংখ্যা
    if final_pred == "BIG":
        big_nums = [n for n in numbers if n >= 5]
        final_num = big_nums[0] if big_nums else 7
    else:
        small_nums = [n for n in numbers if n < 5]
        final_num = small_nums[0] if small_nums else 2
    
    # কনফিডেন্স
    final_conf = int(sum(confidences) / len(confidences))
    
    return {
        'prediction': final_pred,
        'number': final_num,
        'confidence': final_conf,
        'votes': votes,
        'engines': engine_details
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
            f"🧠 *7 ENGINES VOTING SYSTEM*\n"
            f"💎 SUPER HYBRID VIP V7"
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
    global total_wins, total_losses, jackpots, loss_streak, current_level
    global total_rounds, history_data, last_predicted_period
    global last_predicted_signal, last_predicted_num, prediction_sent_for_period

    print("🔥 SUPER HYBRID VIP V7 BOT STARTED...")
    print("🧠 7 ENGINES: DARK X + ANSH BOSS + TITAN + CORE + MASTER + ULTIMATE + SMART")
    print("🗳️ MAJORITY VOTING SYSTEM ACTIVE")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🔥 SUPER HYBRID VIP V7 🔥\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "🧠 7 ENGINES VOTING SYSTEM\n"
                 "📊 DARK X + ANSH BOSS + TITAN\n"
                 "📊 CORE + MASTER + ULTIMATE + SMART\n"
                 "🗳️ MAJORITY VOTE = FINAL\n"
                 "⚡ MODE: 1 MIN WINGO\n"
                 "📊 HOURLY REPORT: ACTIVE\n"
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
                    jackpots += 1
                    status = "JACKPOT"
                    status_icon = "⭐"
                    loss_streak = 0
                    current_level = 1
                elif is_win:
                    total_wins += 1
                    hourly_stats['wins'] += 1
                    status = "WIN"
                    status_icon = "🟢"
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
                    status = "LOSS"
                    status_icon = "🔴"
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
                multiplier = "1x" if current_level == 1 else "3x" if current_level == 2 else "9x"
                
                jackpot_text = " ⭐ JACKPOT!" if is_jackpot else ""
                
                result_msg = (
                    f"🎯 RESULT UPDATE {status_icon}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: #{latest_issue[-5:]}\n"
                    f"🎯 PREDICTED: {last_predicted_signal} → {last_predicted_num}\n"
                    f"🎰 ACTUAL: {actual_num} ({actual_type})\n"
                    f"📌 RESULT: {status_icon} {status}{jackpot_text}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 WIN RATE: {win_rate:.1f}% ({total_wins}W/{total_losses}L)\n"
                    f"🔥 STREAK: {loss_streak:+d}\n"
                    f"👑 LEVEL: {current_level} ({multiplier})\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🗳️ 7 ENGINES VOTING SYSTEM\n"
                    f"💎 SUPER HYBRID VIP V7"
                )
                
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=result_msg)
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
                multiplier = "1x" if current_level == 1 else "3x" if current_level == 2 else "9x"
                confidence_pct = int(pred['confidence'])
                
                # ইঞ্জিন ভোটের বিবরণ
                engine_votes = ""
                for name, data in pred['engines'].items():
                    engine_votes += f"{name}: {data['prediction']} ({data['number']}) {data['confidence']}%\n"
                
                prediction_msg = (
                    f"🔥 SUPER HYBRID VIP V7 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: #{next_period[-5:]}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🗳️ *VOTING RESULT*\n"
                    f"📊 BIG: {pred['votes']['BIG']} | SMALL: {pred['votes']['SMALL']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📈 *FINAL PREDICTION*\n"
                    f"🎯 PREDICTION: {pred['prediction']}\n"
                    f"🔢 TARGET NUMBER: {pred['number']}\n"
                    f"⚡ CONFIDENCE: {confidence_pct}%\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 *7 ENGINE VOTES*\n"
                    f"{engine_votes}"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👑 LEVEL: {current_level} ({multiplier})\n"
                    f"🔥 STREAK: {loss_streak:+d}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ RESULT AWAITING...\n"
                    f"💎 SUPER HYBRID VIP V7"
                )
                
                last_predicted_period = next_period
                last_predicted_signal = pred['prediction']
                last_predicted_num = pred['number']
                prediction_sent_for_period[next_period] = True
                
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=prediction_msg)
                except:
                    pass

            if len(prediction_sent_for_period) > 5:
                oldest = min(prediction_sent_for_period.keys())
                del prediction_sent_for_period[oldest]

        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(5)

if __name__ == '__main__':
    print("🔥 SUPER HYBRID VIP V7 BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 7 ENGINES: DARK X + ANSH BOSS + TITAN + CORE + MASTER + ULTIMATE + SMART")
    print("🗳️ MAJORITY VOTING SYSTEM")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
