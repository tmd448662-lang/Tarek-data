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
#  ENGINE 1: DARK X
# ============================================================

def dark_x_engine(data):
    """DARK X - Single Prediction Engine"""
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
    if current_level >= 3:
        pred = "SMALL" if pred == "BIG" else "BIG"
        conf = min(99, conf + 10)
    
    num = pred == "BIG" and 7 or 2
    
    return {"prediction": pred, "confidence": conf, "number": num}

# ============================================================
#  ENGINE 2: FUKD BY SAAD (6 Engines Voting)
# ============================================================

def fukd_saad_prediction(data):
    """FUKD BY SAAD - 6 Engine Voting System"""
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 60, "number": 5}
    
    sides = [d['side'] for d in data[:10]]
    numbers = [d['number'] for d in data[:10]]
    
    votes = {'BIG': 0, 'SMALL': 0}
    confidences = []
    
    # 1. CORE ENGINE
    weights = [9, 7, 5, 3, 2, 1, 1, 1]
    score = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score += weights[i]
        else:
            score -= weights[i]
    core_pred = "BIG" if score >= 0 else "SMALL"
    core_conf = 87 if abs(score) >= 3 else 76
    votes[core_pred] += 1
    confidences.append(core_conf)
    
    # 2. SMART ENGINE
    if len(sides) >= 4 and sides[0] == sides[3] and sides[1] == sides[2]:
        smart_pred = "SMALL" if sides[0] == "BIG" else "BIG"
        smart_conf = 92
    else:
        smart_pred = "SMALL"
        smart_conf = 75
    votes[smart_pred] += 1
    confidences.append(smart_conf)
    
    # 3. HYBRID ENGINE
    math_num = (numbers[0] + numbers[1]) % 10
    hybrid_pred = "BIG" if math_num >= 5 else "SMALL"
    hybrid_conf = 82
    votes[hybrid_pred] += 1
    confidences.append(hybrid_conf)
    
    # 4. MASTER ENGINE
    score = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score += (8 - i)
        else:
            score -= (8 - i)
    master_pred = "BIG" if score >= 0 else "SMALL"
    master_conf = 95
    votes[master_pred] += 1
    confidences.append(master_conf)
    
    # 5. ADVANCED ENGINE
    global loss_streak
    if loss_streak >= 3:
        score = -score
    advanced_pred = "BIG" if score >= 0 else "SMALL"
    advanced_conf = 87 if abs(score) >= 3 else 76
    advanced_conf = advanced_conf + (5 if loss_streak >= 3 else 0)
    votes[advanced_pred] += 1
    confidences.append(advanced_conf)
    
    # 6. ULTIMATE ENGINE
    streak = 1
    for i in range(1, len(sides[:8])):
        if sides[i] == sides[i-1]:
            streak += 1
        else:
            break
    if streak >= 5:
        ultimate_pred = "SMALL" if sides[0] == "BIG" else "BIG"
        ultimate_conf = 95
    else:
        big_count = sides[:8].count("BIG")
        ultimate_pred = "BIG" if big_count >= 4 else "SMALL"
        ultimate_conf = 70 + (abs(big_count - 4) * 5)
        ultimate_conf = min(95, ultimate_conf)
    votes[ultimate_pred] += 1
    confidences.append(ultimate_conf)
    
    final_pred = max(votes, key=votes.get)
    final_conf = int(sum(confidences) / len(confidences))
    
    if final_pred == "BIG":
        final_num = random.randint(5, 9)
    else:
        final_num = random.randint(0, 4)
    
    return {"prediction": final_pred, "confidence": final_conf, "number": final_num}

# ============================================================
#  ENGINE 3: ULTIMATE PRO AI (বিশেষ)
# ============================================================

def ultimate_pro_engine(data):
    """ULTIMATE PRO AI - Advanced Prediction Engine"""
    if len(data) < 10:
        return {"prediction": "BIG", "confidence": 70, "number": 7}
    
    sides = [d['side'] for d in data[:15]]
    numbers = [d['number'] for d in data[:15]]
    
    # ===== ১. স্ট্রিক ডিটেকশন =====
    streak = 1
    for i in range(1, len(sides)):
        if sides[i] == sides[i-1]:
            streak += 1
        else:
            break
    
    last1 = sides[0] if len(sides) > 0 else "BIG"
    last2 = sides[1] if len(sides) > 1 else "BIG"
    last3 = sides[2] if len(sides) > 2 else "BIG"
    last4 = sides[3] if len(sides) > 3 else "BIG"
    last5 = sides[4] if len(sides) > 4 else "BIG"
    
    # ===== ২. ট্রেন্ড অ্যানালাইসিস =====
    big_count = sum(1 for s in sides[:10] if s == "BIG")
    small_count = sum(1 for s in sides[:10] if s == "SMALL")
    big_ratio = big_count / (big_count + small_count) if (big_count + small_count) > 0 else 0.5
    
    # ===== ৩. ফ্রিকোয়েন্সি অ্যানালাইসিস =====
    freq = [0] * 10
    for n in numbers[:15]:
        freq[n] += 1
    
    # সবচেয়ে কম আসা নম্বর (কোল্ড)
    min_freq = min(freq)
    cold_numbers = [i for i, f in enumerate(freq) if f == min_freq]
    
    # ===== ৪. ড্রাগন সিরিজ (৫+ একই) =====
    if streak >= 5:
        pred = "SMALL" if last1 == "BIG" else "BIG"
        conf = 95
        reason = "DRAGON_REVERSAL"
    
    # ===== ৫. ৪-স্টেপ প্যাটার্ন (ABAB) =====
    elif len(sides) >= 4 and last1 == last3 and last2 == last4 and last1 != last2:
        pred = last1
        conf = 90
        reason = "PATTERN_ABAB"
    
    # ===== ৬. ৩-স্টেপ প্যাটার্ন (ABA) =====
    elif len(sides) >= 3 and last1 == last3 and last1 != last2:
        pred = last1
        conf = 85
        reason = "PATTERN_ABA"
    
    # ===== ৭. অল্টারনেটিং প্যাটার্ন =====
    elif len(sides) >= 5 and all(sides[i] != sides[i+1] for i in range(4)):
        pred = sides[0]
        conf = 80
        reason = "ALTERNATING"
    
    # ===== ৮. ট্রেন্ড ফলো =====
    elif big_ratio >= 0.60:
        pred = "BIG"
        conf = 75 + (big_ratio - 0.5) * 30
        reason = "TREND_BIG"
    elif big_ratio <= 0.40:
        pred = "SMALL"
        conf = 75 + (0.5 - big_ratio) * 30
        reason = "TREND_SMALL"
    
    # ===== ৯. ম্যাথমেটিক্যাল অফসেট =====
    else:
        last_five_sum = sum(numbers[:5])
        if last_five_sum % 2 == 0:
            pred = "BIG"
            conf = 70
            reason = "MATH_EVEN"
        else:
            pred = "SMALL"
            conf = 70
            reason = "MATH_ODD"
    
    # ===== ১০. লস স্ট্রেক প্রোটেকশন =====
    global loss_streak
    if loss_streak <= -2:
        pred = "SMALL" if pred == "BIG" else "BIG"
        conf = min(98, conf + 15)
        reason = "LOSS_REVERSAL"
    
    # ===== ১১. লেভেল 3 বুস্ট =====
    global current_level
    if current_level >= 3:
        pred = "SMALL" if pred == "BIG" else "BIG"
        conf = min(99, conf + 10)
        reason = "LEVEL3_BOOST"
    
    # ===== ১২. নম্বর জেনারেট (কোল্ড নম্বর) =====
    if pred == "BIG":
        cold_big = [n for n in cold_numbers if n >= 5]
        num = cold_big[0] if cold_big else random.randint(5, 9)
    else:
        cold_small = [n for n in cold_numbers if n < 5]
        num = cold_small[0] if cold_small else random.randint(0, 4)
    
    return {"prediction": pred, "confidence": int(conf), "number": num}

# ============================================================
#  3-SYSTEM VOTING (DARK X + FUKD + ULTIMATE PRO)
# ============================================================

def master_voting_system(data):
    """৩টি সিস্টেমের ভোট নিয়ে ফাইনাল সিদ্ধান্ত"""
    
    # ===== ৩টি সিস্টেম চালু =====
    dark_x = dark_x_engine(data)
    fukd = fukd_saad_prediction(data)
    ultimate = ultimate_pro_engine(data)
    
    # ===== ভোট কাউন্ট =====
    votes = {'BIG': 0, 'SMALL': 0}
    numbers = []
    confidences = []
    
    # DARK X
    votes[dark_x['prediction']] += 1
    numbers.append(dark_x['number'])
    confidences.append(dark_x['confidence'])
    
    # FUKD BY SAAD
    votes[fukd['prediction']] += 1
    numbers.append(fukd['number'])
    confidences.append(fukd['confidence'])
    
    # ULTIMATE PRO
    votes[ultimate['prediction']] += 1
    numbers.append(ultimate['number'])
    confidences.append(ultimate['confidence'])
    
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
    
    # সেরা ইঞ্জিন
    best = max([('DARK X', dark_x), ('FUKD BY SAAD', fukd), ('ULTIMATE PRO', ultimate)], 
               key=lambda x: x[1]['confidence'])
    
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
            f"💎 3-SYSTEM HYBRID VIP V8"
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
    print("🧠 DARK X + FUKD BY SAAD (6 Engines) + ULTIMATE PRO")
    print("🗳️ MAJORITY VOTING SYSTEM")
    print("❌ NO MATCH OFF - ALWAYS PREDICT")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🔥 3-SYSTEM HYBRID VIP 🔥\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "🧠 DARK X + FUKD BY SAAD + ULTIMATE PRO\n"
                 "🗳️ MAJORITY VOTING = FINAL\n"
                 "⭐ JACKPOT → WIN\n"
                 "📊 LOSS = STREAK -1, LEVEL UP\n"
                 "❌ NO MATCH OFF - ALWAYS PREDICT\n"
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
                is_jackpot = (actual_num == 0 or actual_num == 5)
                
                if is_win or is_jackpot:
                    total_wins += 1
                    hourly_stats['wins'] += 1
                    status = "WIN"
                    status_icon = "🟢"
                    
                    loss_streak = loss_streak + 1 if loss_streak >= 0 else 1
                    current_level = 1
                    
                    if hourly_stats['streak_type'] == 'WIN':
                        hourly_stats['current_streak'] += 1
                    else:
                        hourly_stats['current_streak'] = 1
                        hourly_stats['streak_type'] = 'WIN'
                    
                    if hourly_stats['current_streak'] > hourly_stats['max_win_streak']:
                        hourly_stats['max_win_streak'] = hourly_stats['current_streak']
                    
                    jackpot_text = " ⭐ JACKPOT!" if is_jackpot else ""
                    
                else:
                    total_losses += 1
                    hourly_stats['losses'] += 1
                    status = "LOSS"
                    status_icon = "🔴"
                    
                    loss_streak = loss_streak - 1 if loss_streak <= 0 else -1
                    current_level = current_level + 1
                    
                    if hourly_stats['streak_type'] == 'LOSS':
                        hourly_stats['current_streak'] += 1
                    else:
                        hourly_stats['current_streak'] = 1
                        hourly_stats['streak_type'] = 'LOSS'
                    
                    if hourly_stats['current_streak'] > hourly_stats['max_loss_streak']:
                        hourly_stats['max_loss_streak'] = hourly_stats['current_streak']
                    
                    jackpot_text = ""
                
                total_rounds += 1
                hourly_stats['total'] += 1
                
                total_games = total_wins + total_losses
                win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0
                multiplier = f"{current_level}x"
                
                streak_emoji = "🔥" if loss_streak > 0 else "📉" if loss_streak < 0 else "⏸️"
                
                result_msg = (
                    f"🎯 RESULT UPDATE {status_icon}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: #{latest_issue[-5:]}\n"
                    f"🎯 PREDICTED: {last_predicted_signal} → {last_predicted_num}\n"
                    f"🎰 ACTUAL: {actual_num} ({actual_type})\n"
                    f"📌 RESULT: {status_icon} {status}{jackpot_text}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 WIN RATE: {win_rate:.1f}% ({total_wins}W/{total_losses}L)\n"
                    f"{streak_emoji} STREAK: {loss_streak:+d}\n"
                    f"👑 LEVEL: {current_level} ({multiplier})\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🗳️ 3-SYSTEM VOTING\n"
                    f"💎 3-SYSTEM HYBRID VIP V8"
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
                multiplier = f"{current_level}x"
                streak_emoji = "🔥" if loss_streak > 0 else "📉" if loss_streak < 0 else "⏸️"
                
                prediction_msg = (
                    f"🔥 3-SYSTEM HYBRID VIP 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: #{next_period[-5:]}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🗳️ *VOTING RESULT*\n"
                    f"📊 BIG: {pred['votes']['BIG']} | SMALL: {pred['votes']['SMALL']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📈 *FINAL PREDICTION*\n"
                    f"🎯 PREDICTION: {pred['prediction']}\n"
                    f"🔢 TARGET NUMBER: {pred['number']}\n"
                    f"⚡ CONFIDENCE: {pred['confidence']}%\n"
                    f"🧠 BEST ENGINE: {pred['best_engine']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 *DARK X:* {pred['dark_x']['prediction']} ({pred['dark_x']['number']}) {pred['dark_x']['confidence']}%\n"
                    f"🧠 *FUKD BY SAAD:* {pred['fukd']['prediction']} ({pred['fukd']['number']}) {pred['fukd']['confidence']}%\n"
                    f"🧠 *ULTIMATE PRO:* {pred['ultimate']['prediction']} ({pred['ultimate']['number']}) {pred['ultimate']['confidence']}%\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👑 LEVEL: {current_level} ({multiplier})\n"
                    f"{streak_emoji} STREAK: {loss_streak:+d}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ RESULT AWAITING...\n"
                    f"💎 3-SYSTEM HYBRID VIP V8"
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
    print("🔥 3-SYSTEM HYBRID VIP BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 DARK X + FUKD BY SAAD + ULTIMATE PRO")
    print("🗳️ MAJORITY VOTING SYSTEM")
    print("❌ NO MATCH OFF - ALWAYS PREDICT")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
