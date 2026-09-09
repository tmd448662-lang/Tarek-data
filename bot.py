#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import time
import requests
import os
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Bot

# ==================== কনফিগ ───
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

# ==================== ওয়েব সার্ভার ───
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"SHANTO+RGB VIP BOT is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

def keep_alive():
    while True:
        try:
            time.sleep(600)
            port = int(os.environ.get("PORT", 8080))
            requests.get(f"http://localhost:{port}/", timeout=5)
        except:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

# ==================== বট ───
bot = Bot(token=BOT_TOKEN)

# ==================== ডেটা ───
match_wins = 0
match_losses = 0
match_total = 0
loss_streak = 0
current_level = 1

history_data = []
last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
last_match_status = None
prediction_sent_for_period = {}

# ==================== আওয়ারলি ───
hourly_stats = {
    'total_rounds': 0,
    'total_wins': 0,
    'total_losses': 0,
    'max_win_streak': 0,
    'max_loss_streak': 0,
    'current_streak': 0,
    'streak_type': 'WIN'
}
last_hour_report_time = time.time()

# ============================================================
# 🧠 ১. SHANTO (মার্কভ চেইন)
# ============================================================

def shanto_algorithm(last_results):
    if len(last_results) < 2:
        return {"s": "BIG", "n": 7}
    
    last1 = last_results[-1]
    last2 = last_results[-2]
    
    if last1 == "SMALL" and last2 == "SMALL":
        return {"s": "BIG", "n": 8}
    elif last1 == "BIG" and last2 == "BIG":
        return {"s": "SMALL", "n": 3}
    elif last1 == "SMALL" and last2 == "BIG":
        return {"s": "BIG", "n": 7}
    elif last1 == "BIG" and last2 == "SMALL":
        return {"s": "SMALL", "n": 4}
    return {"s": "BIG", "n": 7}

# ============================================================
# 🧠 ২. RGB (ANSH BOSS)
# ============================================================

RGB_PATTERN = [
    {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 2},
    {"s": "SMALL", "n": 4}, {"s": "BIG", "n": 9},
    {"s": "BIG", "n": 6}, {"s": "SMALL", "n": 0},
    {"s": "BIG", "n": 8}, {"s": "SMALL", "n": 3},
    {"s": "SMALL", "n": 1}, {"s": "BIG", "n": 5},
    {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 4}
]

def get_correct_period_index():
    now = datetime.now(timezone.utc)
    midnight = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
    diff_seconds = (now - midnight).total_seconds()
    period_index = int(diff_seconds // 60) + 1
    return period_index

def rgb_algorithm():
    period_index = get_correct_period_index()
    pattern_index = (period_index + 5) % 12
    pred = RGB_PATTERN[pattern_index]
    return {"s": pred["s"], "n": pred["n"]}

# ============================================================
# 🎯 MASTER MATCHING (SHANTO + RGB)
# ============================================================

def master_system(last_results):
    shanto = shanto_algorithm(last_results)
    rgb = rgb_algorithm()
    
    if shanto["s"] == rgb["s"]:
        return {
            'matched': True,
            'prediction': shanto["s"],
            'number': shanto["n"],
            'shanto': shanto,
            'rgb': rgb,
            'confidence': 90
        }
    else:
        return {
            'matched': False,
            'prediction': None,
            'number': None,
            'shanto': shanto,
            'rgb': rgb,
            'confidence': 0
        }

# ==================== API ───
def fetch_api_data():
    try:
        res = requests.get(API_URL + "?t=" + str(int(time.time() * 1000)), timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", {}).get("list", [])
    except:
        pass
    return []

# ==================== আওয়ারলি ───
async def send_hourly_report():
    global hourly_stats, last_hour_report_time

    if time.time() - last_hour_report_time >= 3600:
        total = hourly_stats['total_rounds']
        wins = hourly_stats['total_wins']
        losses = hourly_stats['total_losses']
        win_rate = (wins / total * 100) if total > 0 else 0

        report_msg = (
            f"📊 *HOURLY REPORT*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🕐 {datetime.now().strftime('%I:%M %p')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔄 TOTAL: `{total}`\n"
            f"✅ WINS: `{wins}`\n"
            f"❌ LOSSES: `{losses}`\n"
            f"📈 WIN RATE: `{win_rate:.1f}%`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 BEST WIN: `{hourly_stats['max_win_streak']}x`\n"
            f"📉 WORST LOSS: `{hourly_stats['max_loss_streak']}x`\n"
            f"🔥 CURRENT: `{hourly_stats['current_streak']}x {hourly_stats['streak_type']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 SHANTO+RGB VIP"
        )
        try:
            await bot.send_message(chat_id=CHAT_ID, text=report_msg, parse_mode="Markdown")
        except:
            pass

        hourly_stats = {
            'total_rounds': 0,
            'total_wins': 0,
            'total_losses': 0,
            'max_win_streak': 0,
            'max_loss_streak': 0,
            'current_streak': 0,
            'streak_type': 'WIN'
        }
        last_hour_report_time = time.time()

# ==================== মেইন ───
async def prediction_bot():
    global match_wins, match_losses, match_total
    global loss_streak, current_level
    global history_data, last_predicted_period
    global last_predicted_signal, last_predicted_num, last_match_status
    global prediction_sent_for_period

    print("🔥 SHANTO+RGB VIP BOT STARTED...")
    print("🧠 SHANTO + RGB (ANSH BOSS)")
    print("✅ MATCH = SEND | ❌ NO MATCH = SKIP")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                "🔥 *SHANTO+RGB VIP* 🔥\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🧠 SHANTO + RGB (ANSH BOSS)\n"
                "✅ MATCH = SEND PREDICTION\n"
                "❌ NO MATCH = SKIP\n"
                "📡 MODE: 1 MIN WINGO\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "⏳ WAITING..."
            ),
            parse_mode="Markdown"
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
                print("⚠️ API ডেটা নেই")
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

            print(f"📡 PERIOD: {latest_issue}, NUMBER: {actual_num}")

            # ==================== RESULT CHECK ====================
            if last_predicted_period == latest_issue:

                if last_match_status == 'match' and last_predicted_signal is not None:
                    is_win = (last_predicted_signal == actual_type)
                    is_jackpot = (actual_num == 0 or actual_num == 5)

                    if is_win or is_jackpot:
                        match_wins += 1
                        hourly_stats['total_wins'] += 1
                        status = "WIN 🟢"
                        
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
                        match_losses += 1
                        hourly_stats['total_losses'] += 1
                        status = "LOSS 🔴"
                        
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

                    match_total += 1
                    hourly_stats['total_rounds'] += 1

                    total_games = match_wins + match_losses
                    win_rate = (match_wins / total_games * 100) if total_games > 0 else 0.0
                    multiplier = f"{current_level}x"
                    streak_emoji = "🔥" if loss_streak > 0 else "📉" if loss_streak < 0 else "⏸️"

                    result_msg = (
                        f"🎯 *RESULT UPDATE*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{latest_issue[-5:]}`\n"
                        f"🎯 PREDICTED: `{last_predicted_signal}` → `{last_predicted_num}`\n"
                        f"🎰 ACTUAL: `{actual_num}` (`{actual_type}`)\n"
                        f"📌 RESULT: `{status}`{jackpot_text}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 WIN RATE: `{win_rate:.1f}%` ({match_wins}W/{match_losses}L)\n"
                        f"{streak_emoji} STREAK: `{loss_streak:+d}`\n"
                        f"👑 LEVEL: `{current_level}` ({multiplier})\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💎 SHANTO+RGB VIP"
                    )

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                        await asyncio.sleep(1)
                    except:
                        pass

                    await send_hourly_report()

                else:
                    # NO MATCH
                    result_msg = (
                        f"🎯 *RESULT (NO MATCH)*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{latest_issue[-5:]}`\n"
                        f"🎰 ACTUAL: `{actual_num}` (`{actual_type}`)\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💎 SHANTO+RGB VIP"
                    )

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                        await asyncio.sleep(1)
                    except:
                        pass

                last_predicted_period = None
                last_predicted_signal = None
                last_predicted_num = None
                last_match_status = None

            # ==================== NEW PREDICTION ====================
            next_period = str(int(latest_issue) + 1)
            print(f"🎯 NEXT PERIOD: {next_period}")

            if not prediction_sent_for_period.get(next_period, False):
                last_results = [d['side'] for d in history_data[:10]]
                pred = master_system(last_results)

                if pred['matched']:
                    last_match_status = 'match'
                    
                    prediction_msg = (
                        f"🔮 *PREDICTION* 🟢\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{next_period[-5:]}`\n"
                        f"🎯 PREDICTION: `{pred['prediction']}` → `{pred['number']}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 SHANTO: `{pred['shanto']['s']}` → `{pred['shanto']['n']}`\n"
                        f"🧠 RGB: `{pred['rgb']['s']}` → `{pred['rgb']['n']}`\n"
                        f"📊 STATUS: `✅ MATCH FOUND`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💎 SHANTO+RGB VIP"
                    )

                    last_predicted_period = next_period
                    last_predicted_signal = pred['prediction']
                    last_predicted_num = pred['number']
                    prediction_sent_for_period[next_period] = True

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=prediction_msg, parse_mode="Markdown")
                        print(f"✅ MATCH: {next_period} → {pred['prediction']}")
                    except Exception as e:
                        print(f"❌ SEND FAILED: {e}")

                else:
                    last_match_status = 'no_match'
                    
                    no_match_msg = (
                        f"⏭️ *NO MATCH* 🔴\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{next_period[-5:]}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 SHANTO: `{pred['shanto']['s']}` → `{pred['shanto']['n']}`\n"
                        f"🧠 RGB: `{pred['rgb']['s']}` → `{pred['rgb']['n']}`\n"
                        f"📊 STATUS: `❌ NO MATCH (SKIP)`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💎 SHANTO+RGB VIP"
                    )

                    last_predicted_period = next_period
                    last_predicted_signal = None
                    last_predicted_num = None
                    prediction_sent_for_period[next_period] = True

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=no_match_msg, parse_mode="Markdown")
                        print(f"❌ NO MATCH: {next_period}")
                    except Exception as e:
                        print(f"❌ SEND FAILED: {e}")

                if len(prediction_sent_for_period) > 5:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            print(f"❌ Loop Error: {e}")
            await asyncio.sleep(5)

# ==================== স্টার্ট ───
if __name__ == '__main__':
    print("🔥 SHANTO+RGB VIP BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 SHANTO + RGB (ANSH BOSS)")
    print("✅ MATCH = SEND PREDICTION + RESULT")
    print("❌ NO MATCH = SHOW RESULT ONLY")
    print("📡 MODE: 1 MIN WINGO")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
