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
        self.wfile.write(b"RGB MATCHING 1MIN VIP BOT is running!")

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

API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

bot = Bot(token=BOT_TOKEN)

# ==================== GLOBAL STATS ====================
total_wins = 0
total_losses = 0
loss_streak = 0          # positive = win streak, negative = loss streak
current_level = 1        # 1, 2, or 3 (cycles on losses)
total_rounds = 0
history_data = []        # list of dicts {issueNumber, number, side}

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
#  ENGINE 1: DARK X (from first HTML)
# ============================================================
def dark_x_engine(data, level):
    """
    Implements the Markov-chain logic from DARK X BHAI VIP V1.3.
    data: list of recent results (each with 'number' and 'side')
    level: current martingale level (1,2,3)
    Returns: {'prediction': 'BIG'/'SMALL', 'confidence': int, 'number': int}
    """
    if len(data) < 3:
        return {"prediction": "BIG", "confidence": 50, "number": 7}

    types = [d['side'] for d in data[:10]]
    last1 = types[0] if len(types) > 0 else "BIG"
    last2 = types[1] if len(types) > 1 else "BIG"

    # Default transition logic (as per HTML)
    if last1 == "SMALL":
        pred = "BIG"
        conf = 75
    else:
        pred = "SMALL"
        conf = 60

    # Sequence overrides
    if last1 == "BIG" and last2 == "BIG":
        pred = "SMALL"
        conf = 90
    elif last1 == "SMALL" and last2 == "SMALL":
        pred = "BIG"
        conf = 95
    elif last1 == "SMALL" and last2 == "BIG":
        pred = "BIG"
        conf = 70
    elif last1 == "BIG" and last2 == "SMALL":
        pred = "BIG"
        conf = 85

    # Level 3 safety net: reverse based on latest actual number
    if level == 3 and len(data) > 0:
        latest_num = data[0]['number']
        pred = "SMALL" if latest_num >= 5 else "BIG"
        conf = 99

    # Generate a number for display (BIG: 5-9, SMALL: 0-4)
    if pred == "BIG":
        num = random.randint(5, 9)
    else:
        num = random.randint(0, 4)

    return {"prediction": pred, "confidence": conf, "number": num}

# ============================================================
#  ENGINE 2: RGB HACK (corrected 12-step pattern)
# ============================================================
def rgb_hack_engine(period_str):
    """
    Uses the fixed 12-step pattern from VIP NUMBER_decoded.html.
    period_str: e.g., "20260904100011082"
    We extract the last 5 digits as the period index (starting from 1).
    For 1-minute mode, offset = 5, so pattern_index = (index + 5) % 12.
    """
    PATTERN = [
        {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 2}, {"s": "SMALL", "n": 4},
        {"s": "BIG", "n": 9}, {"s": "BIG", "n": 6}, {"s": "SMALL", "n": 0},
        {"s": "BIG", "n": 8}, {"s": "SMALL", "n": 3}, {"s": "SMALL", "n": 1},
        {"s": "BIG", "n": 5}, {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 4}
    ]
    # Extract the last 5 characters (period index)
    try:
        idx = int(period_str[-5:])
    except:
        idx = 0
    # 1-minute offset = 5
    pattern_index = (idx + 5) % 12
    pred = PATTERN[pattern_index]
    return {"prediction": pred["s"], "confidence": 78, "number": pred["n"]}

# ============================================================
#  MASTER MATCHING SYSTEM
# ============================================================
def master_matching_system(data, period_str, level):
    dark = dark_x_engine(data, level)
    rgb = rgb_hack_engine(period_str)

    if dark['prediction'] == rgb['prediction']:
        final_pred = dark['prediction']
        final_num = rgb['number'] if rgb['number'] is not None else dark['number']
        final_conf = int((dark['confidence'] + rgb['confidence']) / 2)
        matched = True
        status = "✅ MATCH FOUND"
        icon = "🟢"
    else:
        final_pred = "WAIT"
        final_num = "--"
        final_conf = 0
        matched = False
        status = "⏳ WAITING - NO MATCH"
        icon = "🟡"

    return {
        'matched': matched,
        'prediction': final_pred,
        'number': final_num,
        'confidence': final_conf,
        'dark': dark,
        'rgb': rgb,
        'status': status,
        'status_icon': icon
    }

# ============================================================
#  API FETCH
# ============================================================
def fetch_api_data():
    try:
        res = requests.get(API_URL + "?t=" + str(int(time.time() * 1000)), timeout=5)
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
            f"🧠 *ENGINES: DARK X + RGB HACK (1 Min)*\n"
            f"💎 RGB MATCHING 1MIN VIP"
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

    print("🔥 RGB MATCHING 1MIN VIP BOT STARTED...")
    print("🧠 DARK X + RGB HACK (12-Step Pattern)")
    print("📡 MODE: 1 MIN WINGO")
    print("✅ MATCH = SEND | ❌ NO MATCH = WAIT")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                "🔥 RGB MATCHING 1MIN VIP 🔥\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🧠 DARK X + RGB HACK (12-Step)\n"
                "✅ MATCH FOUND = SEND PREDICTION\n"
                "❌ NO MATCH = WAIT FOR NEXT ROUND\n"
                "⭐ JACKPOT → WIN COUNT\n"
                "📊 LOSS = STREAK -1, LEVEL UP\n"
                "⚡ MODE: 1 MIN WINGO\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "⏳ WAITING FOR FIRST SIGNAL..."
            )
        )
    except Exception as e:
        print(f"Startup error: {e}")

    while True:
        try:
            current_sec = int(time.time()) % 60
            sleep_time = 60 - current_sec + 3
            await asyncio.sleep(sleep_time)

            raw_list = fetch_api_data()
            if not raw_list:
                continue

            history_data = []
            for h in raw_list[:20]:
                num = int(h['number'])
                history_data.append({
                    'issueNumber': str(h['issueNumber']),
                    'number': num,
                    'side': "BIG" if num >= 5 else "SMALL"
                })

            latest = history_data[0]
            latest_issue = latest['issueNumber']
            actual_num = latest['number']
            actual_type = "BIG" if actual_num >= 5 else "SMALL"

            # ===== RESULT CHECK =====
            if last_predicted_period == latest_issue and last_predicted_signal is not None:
                is_win = (last_predicted_signal == actual_type)
                is_jackpot = (actual_num == 0 or actual_num == 5)

                if is_win or is_jackpot:
                    total_wins += 1
                    hourly_stats['wins'] += 1
                    status = "WIN"
                    status_icon = "🟢"

                    if loss_streak >= 0:
                        loss_streak += 1
                    else:
                        loss_streak = 1
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

                    if loss_streak <= 0:
                        loss_streak -= 1
                    else:
                        loss_streak = -1
                    current_level = (current_level % 3) + 1

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
                    f"🧠 ENGINES: DARK X + RGB HACK (1 Min)\n"
                    f"💎 RGB MATCHING 1MIN VIP"
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
                pred = master_matching_system(history_data, next_period, current_level)
                multiplier = f"{current_level}x"
                streak_emoji = "🔥" if loss_streak > 0 else "📉" if loss_streak < 0 else "⏸️"

                if pred['matched']:
                    prediction_msg = (
                        f"🔥 RGB MATCHING 1MIN VIP 🔥\n"
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
                        f"🧠 *DARK X:* {pred['dark']['prediction']} ({pred['dark']['number']}) {pred['dark']['confidence']}%\n"
                        f"🧠 *RGB HACK:* {pred['rgb']['prediction']} ({pred['rgb']['number']}) {pred['rgb']['confidence']}%\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"👑 LEVEL: {current_level} ({multiplier})\n"
                        f"{streak_emoji} STREAK: {loss_streak:+d}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⏳ RESULT AWAITING...\n"
                        f"💎 RGB MATCHING 1MIN VIP"
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
                        f"🧠 *DARK X:* {pred['dark']['prediction']} ({pred['dark']['number']}) {pred['dark']['confidence']}%\n"
                        f"🧠 *RGB HACK:* {pred['rgb']['prediction']} ({pred['rgb']['number']}) {pred['rgb']['confidence']}%\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"❌ *NO MATCH FOUND*\n"
                        f"⏳ *WAITING FOR NEXT ROUND...*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💎 RGB MATCHING 1MIN VIP"
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

# ============================================================
#  START
# ============================================================
if __name__ == '__main__':
    print("🔥 RGB MATCHING 1MIN VIP BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 DARK X + RGB HACK (12-Step Pattern)")
    print("📡 MODE: 1 MIN WINGO")
    print("✅ MATCH = SEND | ❌ NO MATCH = WAIT")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
