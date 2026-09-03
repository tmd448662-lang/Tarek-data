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
        self.wfile.write(b"SUPER HYBRID VIP BOT is running!")

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

# ==================== HOURLY REPORT STATS ====================
hourly_stats = {
    'start_time': time.time(),
    'wins': 0,
    'losses': 0,
    'total': 0,
    'max_win_streak': 0,
    'max_loss_streak': 0,
    'current_streak': 0,
    'streak_type': 'WIN',  # WIN or LOSS
    'hourly_wins': [],
    'hourly_losses': []
}

last_hour_report_time = time.time()
hourly_report_sent = False

last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
prediction_sent_for_period = {}
last_best_engine = "DARK X"

# ==================== ৬টি AI ইঞ্জিন ====================

def core_engine(data):
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 76}
    
    weights = [9, 7, 5, 3, 2, 1, 1, 1]
    score = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score += weights[i]
        else:
            score -= weights[i]
    
    pred = "BIG" if score >= 0 else "SMALL"
    conf = 87 if abs(score) >= 3 else 76
    return {"prediction": pred, "confidence": conf}

def smart_engine(data):
    if len(data) < 4:
        return {"prediction": "SMALL", "confidence": 75}
    
    sides = [d['side'] for d in data[:4]]
    if sides[0] == sides[3] and sides[1] == sides[2]:
        pred = "SMALL" if sides[0] == "BIG" else "BIG"
        return {"prediction": pred, "confidence": 92}
    return {"prediction": "SMALL", "confidence": 75}

def hybrid_engine(data):
    if len(data) < 5:
        return {"prediction": "BIG", "confidence": 73}
    
    math_num = (data[0]['number'] + data[1]['number']) % 10
    pred = "BIG" if math_num >= 5 else "SMALL"
    return {"prediction": pred, "confidence": 82}

def master_engine(data):
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 73}
    
    score = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score += (8 - i)
        else:
            score -= (8 - i)
    
    pred = "BIG" if score >= 0 else "SMALL"
    return {"prediction": pred, "confidence": 95}

def advanced_engine(data):
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 87}
    
    weights = [9, 7, 5, 3, 2, 1, 1, 1]
    score = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score += weights[i]
        else:
            score -= weights[i]
    
    global loss_streak
    if loss_streak >= 3:
        score = -score
    
    pred = "BIG" if score >= 0 else "SMALL"
    conf = 87 if abs(score) >= 3 else 76
    return {"prediction": pred, "confidence": conf + (5 if loss_streak >= 3 else 0)}

def ultimate_engine(data):
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 70}
    
    sides = [d['side'] for d in data[:8]]
    streak = 1
    for i in range(1, len(sides)):
        if sides[i] == sides[i-1]:
            streak += 1
        else:
            break
    
    if streak >= 5:
        pred = "SMALL" if sides[0] == "BIG" else "BIG"
        return {"prediction": pred, "confidence": 95}
    
    big_count = sides.count("BIG")
    pred = "BIG" if big_count >= 4 else "SMALL"
    conf = 70 + (abs(big_count - 4) * 5)
    return {"prediction": pred, "confidence": min(95, conf)}

def dark_x_engine(data):
    if len(data) < 3:
        return {"prediction": "BIG", "confidence": 50}
    
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
        latest = int(data[0]['number'])
        pred = "SMALL" if latest >= 5 else "BIG"
        conf = 99
    
    return {"prediction": pred, "confidence": conf}

# ==================== হাইব্রিড প্রেডিকশন ====================

def hybrid_prediction(data):
    engines = {
        'DARK X': dark_x_engine(data),
        'CORE': core_engine(data),
        'SMART': smart_engine(data),
        'HYBRID': hybrid_engine(data),
        'MASTER': master_engine(data),
        'ADVANCED': advanced_engine(data),
        'ULTIMATE': ultimate_engine(data)
    }
    
    votes = {'BIG': 0, 'SMALL': 0}
    confidences = []
    
    for name, result in engines.items():
        votes[result['prediction']] += 1
        confidences.append(result['confidence'])
    
    final_pred = max(votes, key=votes.get)
    avg_conf = sum(confidences) / len(confidences)
    best = max(engines, key=lambda x: engines[x]['confidence'])
    
    if final_pred == "BIG":
        dna_value = random.randint(5, 9)
    else:
        dna_value = random.randint(0, 4)
    
    return {
        'prediction': final_pred,
        'confidence': avg_conf,
        'dna_value': dna_value,
        'best_engine': best,
        'all_engines': engines
    }

# ==================== API FETCH ====================

def fetch_api_data():
    try:
        res = requests.get(RAW_API + "?t=" + str(int(time.time() * 1000)), timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", {}).get("list", [])
    except:
        pass
    return []

# ==================== HOURLY REPORT FUNCTION ====================

async def send_hourly_report():
    """প্রতি ঘন্টায় রিপোর্ট পাঠায়"""
    global hourly_stats, last_hour_report_time, hourly_report_sent
    
    now = time.time()
    
    # প্রতি ঘন্টায় (৩৬০০ সেকেন্ড)
    if now - last_hour_report_time >= 3600 and not hourly_report_sent:
        
        hourly_report_sent = True
        
        total = hourly_stats['total']
        wins = hourly_stats['wins']
        losses = hourly_stats['losses']
        max_win_streak = hourly_stats['max_win_streak']
        max_loss_streak = hourly_stats['max_loss_streak']
        
        win_rate = (wins / total * 100) if total > 0 else 0
        
        # স্ট্রিক এমোজি
        if max_win_streak > max_loss_streak:
            streak_emoji = "🔥"
            streak_text = f"MAX WIN STREAK: {max_win_streak}"
        elif max_loss_streak > max_win_streak:
            streak_emoji = "📉"
            streak_text = f"MAX LOSS STREAK: {max_loss_streak}"
        else:
            streak_emoji = "⏸️"
            streak_text = "BALANCED"
        
        # রিপোর্ট মেসেজ
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
            f"🔥 *BEST WIN STREAK:* `{max_win_streak}x`\n"
            f"📉 *WORST LOSS STREAK:* `{max_loss_streak}x`\n"
            f"{streak_emoji} *CURRENT STREAK:* `{hourly_stats['current_streak']}x {hourly_stats['streak_type']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 *SUPER HYBRID VIP V5*"
        )
        
        try:
            await bot.send_message(chat_id=CHAT_ID, text=report_msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Report error: {e}")
        
        # রিসেট হাওয়ারলি স্ট্যাটস
        hourly_stats = {
            'start_time': time.time(),
            'wins': 0,
            'losses': 0,
            'total': 0,
            'max_win_streak': 0,
            'max_loss_streak': 0,
            'current_streak': 0,
            'streak_type': 'WIN',
            'hourly_wins': [],
            'hourly_losses': []
        }
        
        last_hour_report_time = time.time()
        hourly_report_sent = False

# ==================== MAIN LOOP ====================

async def prediction_bot():
    global total_wins, total_losses, loss_streak, current_level, total_rounds
    global last_predicted_period, last_predicted_signal, last_predicted_num
    global history_data, prediction_sent_for_period, last_best_engine
    global hourly_stats, last_hour_report_time, hourly_report_sent

    print("🔥 SUPER HYBRID VIP BOT STARTED...")
    print("🧠 7 ENGINES ACTIVE")
    print("📊 HOURLY REPORT ACTIVE")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🔥 SUPER HYBRID VIP BOT 🔥\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "🧠 7 AI ENGINES ACTIVE\n"
                 "⚡ MODE: 1 MIN WINGO\n"
                 "📊 HOURLY REPORT: ACTIVE\n"
                 "🛡️ STATUS: ONLINE & SYNCED\n"
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
                
                if is_win:
                    total_wins += 1
                    hourly_stats['wins'] += 1
                    status = "WIN"
                    status_icon = "🟢"
                    loss_streak = 0 if loss_streak < 0 else loss_streak + 1
                    current_level = 1
                    
                    # স্ট্রিক ট্র্যাক
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
                    
                    # স্ট্রিক ট্র্যাক
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
                
                is_jackpot = (actual_num == 0 or actual_num == 5)
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
                    f"🧠 BEST ENGINE: {last_best_engine}\n"
                    f"💎 SUPER HYBRID VIP V5"
                )
                
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=result_msg)
                    await asyncio.sleep(1)
                except:
                    pass
                
                # প্রতি রেজাল্টের পর হাওয়ারলি রিপোর্ট চেক
                await send_hourly_report()
                
                last_predicted_period = None
                last_predicted_signal = None
                last_predicted_num = None

            # ===== NEW PREDICTION =====
            next_period = str(int(latest_issue) + 1)
            
            if not prediction_sent_for_period.get(next_period, False):
                
                pred = hybrid_prediction(history_data)
                last_best_engine = pred['best_engine']
                
                multiplier = "1x" if current_level == 1 else "3x" if current_level == 2 else "9x"
                confidence_pct = int(pred['confidence'])
                
                prediction_msg = (
                    f"🔥 SUPER HYBRID VIP 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: #{next_period[-5:]}\n"
                    f"🎯 PREDICTION: {pred['prediction']}\n"
                    f"🔢 TARGET NUMBER: {pred['dna_value']}\n"
                    f"⚡ CONFIDENCE: {confidence_pct}%\n"
                    f"🧠 BEST ENGINE: {pred['best_engine']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👑 LEVEL: {current_level} ({multiplier})\n"
                    f"🔥 STREAK: {loss_streak:+d}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ RESULT AWAITING...\n"
                    f"💎 SUPER HYBRID VIP V5"
                )
                
                last_predicted_period = next_period
                last_predicted_signal = pred['prediction']
                last_predicted_num = pred['dna_value']
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
    print("🔥 SUPER HYBRID VIP BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 7 ENGINES ACTIVE")
    print("📊 HOURLY REPORT ACTIVE")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
