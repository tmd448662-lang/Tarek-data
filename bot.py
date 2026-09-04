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
        self.wfile.write(b"RGB MATCHING HYBRID VIP BOT is running!")

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
#  ENGINE 2: RGB HACK (12-STEP PATTERN)
# ============================================================

def rgb_hack_engine(data):
    """RGB HACK - 12 Step Fixed Pattern"""
    if len(data) < 1:
        return {"prediction": "BIG", "confidence": 60, "number": 7}
    
    # RGB 12-STEP PATTERN
    PATTERN = [
        {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 2}, {"s": "SMALL", "n": 4},
        {"s": "BIG", "n": 9}, {"s": "BIG", "n": 6}, {"s": "SMALL", "n": 0},
        {"s": "BIG", "n": 8}, {"s": "SMALL", "n": 3}, {"s": "SMALL", "n": 1},
        {"s": "BIG", "n": 5}, {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 4}
    ]
    
    # পিরিয়ড থেকে শেষ ৩ ডিজিট বের করা
    period = data[0]['issueNumber']
    last_three = int(str(period)[-3:])
    index = last_three % 12
    
    pred = PATTERN[index]
    
    return {"prediction": pred["s"], "confidence": 78, "number": pred["n"]}

# ============================================================
#  MASTER MATCHING SYSTEM (DARK X + RGB)
# ============================================================

def master_matching_system(data):
    """DARK X + RGB HACK - Matching System"""
    
    dark_x = dark_x_engine(data)
    rgb = rgb_hack_engine(data)
    
    if dark_x['prediction'] == rgb['prediction']:
        matched = True
        final_pred = dark_x['prediction']
        final_num = dark_x['number']
        final_conf = int((dark_x['confidence'] + rgb['confidence']) / 2)
        status_text = "✅ MATCH FOUND"
        status_icon = "🟢"
    else:
        matched = False
        final_pred = "WAIT"
        final_num = "--"
        final_conf = 0
        status_text = "⏳ WAITING - NO MATCH"
        status_icon = "🟡"
    
    return {
        'matched': matched,
        'prediction': final_pred,
        'number': final_num,
        'confidence': final_conf,
        'dark_x': dark_x,
        'rgb': rgb,
        'status': status_text,
        'status_icon': status_icon
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
            f"🧠 *MATCHING SYSTEM: DARK X + RGB HACK*\n"
            f"💎 RGB MATCHING HYBRID VIP"
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

    print("🔥 RGB MATCHING HYBRID VIP BOT STARTED...")
    print("🧠 DARK X + RGB HACK (12-Step Pattern)")
    print("✅ MATCH = SEND | ❌ NO MATCH = WAIT")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🔥 RGB MATCHING HYBRID VIP 🔥\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "🧠 DARK X + RGB HACK (12-Step Pattern)\n"
                 "✅ MATCH FOUND = SEND PREDICTION\n"
                 "❌ NO MATCH = WAIT FOR NEXT ROUND\n"
                 "⭐ JACKPOT → WIN COUNT\n"
                 "📊 LOSS = STREAK -1, LEVEL UP\n"
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
                    f"🧠 MATCHING SYSTEM: DARK X + RGB HACK\n"
                    f"💎 RGB MATCHING HYBRID VIP"
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
                
                pred = master_matching_system(history_data)
                multiplier = f"{current_level}x"
                streak_emoji = "🔥" if loss_streak > 0 else "📉" if loss_streak < 0 else "⏸️"
                
                if pred['matched']:
                    prediction_msg = (
                        f"🔥 RGB MATCHING HYBRID VIP 🔥\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: #{next_period[-5:]}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ *MATCH FOUND!*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📈 *FINAL PREDICTION*\n"
                        f"🎯 PREDICTION: {pred['prediction']}\n"
                        f"🔢 TARGET NUMBER: {pred['number']}\n"
                        f"⚡ CONFIDENCE: {pred['confidence']}%\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 *DARK X:* {pred['dark_x']['prediction']} ({pred['dark_x']['number']}) {pred['dark_x']['confidence']}%\n"
                        f"🧠 *RGB HACK:* {pred['rgb']['prediction']} ({pred['rgb']['number']}) {pred['rgb']['confidence']}%\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"👑 LEVEL: {current_level} ({multiplier})\n"
                        f"{streak_emoji} STREAK: {loss_streak:+d}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⏳ RESULT AWAITING...\n"
                        f"💎 RGB MATCHING HYBRID VIP"
                    )
                    
                    last_predicted_period = next_period
                    last_predicted_signal = pred['prediction']
                    last_predicted_num = pred['number']
                    prediction_sent_for_period[next_period] = True
                    
                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=prediction_msg)
                    except:
                        pass
                else:
                    wait_msg = (
                        f"⏳ *WAITING - NO MATCH*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: #{next_period[-5:]}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 *DARK X:* {pred['dark_x']['prediction']} ({pred['dark_x']['number']}) {pred['dark_x']['confidence']}%\n"
                        f"🧠 *RGB HACK:* {pred['rgb']['prediction']} ({pred['rgb']['number']}) {pred['rgb']['confidence']}%\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"❌ *NO MATCH FOUND*\n"
                        f"⏳ *WAITING FOR NEXT ROUND...*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💎 RGB MATCHING HYBRID VIP"
                    )
                    
                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=wait_msg)
                    except:
                        pass

            if len(prediction_sent_for_period) > 5:
                oldest = min(prediction_sent_for_period.keys())
                del prediction_sent_for_period[oldest]

        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(5)

if __name__ == '__main__':
    print("🔥 RGB MATCHING HYBRID VIP BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 DARK X + RGB HACK (12-Step Pattern)")
    print("✅ MATCH = SEND | ❌ NO MATCH = WAIT")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
