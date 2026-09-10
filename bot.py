#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 DARK X 3M WINGO BIG/SMALL বট
📡 শুধু 3 MIN WINGO
🧠 শুধু DARK X অ্যালগরিদম
"""

import asyncio
import time
import requests
import os
import random
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Bot

# ==================== কনফিগারেশন ====================
BOT_TOKEN = "8632082751:AAEcUqV8hFs-Id0E9uL0ltvW-e6ybZkKcJ0"
CHAT_ID = "6678981102"

# ✅ 3 মিনিট উইঙ্গো API
API_URLS = [
    "https://draw.ar-lottery01.com/WinGo/WinGo_3M/GetHistoryIssuePage.json",
    "https://api.ar-lottery01.com/WinGo/WinGo_3M/GetHistoryIssuePage.json",
]

# ==================== ওয়েব সার্ভার ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"DARK X 3M WINGO BOT is running!")

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

# ==================== বট ইনিশিয়ালাইজ ====================
bot = Bot(token=BOT_TOKEN)

# ==================== গ্লোবাল ভেরিয়েবল ====================
# ✅ মোট স্ট্যাটস (কখনো রিসেট হবে না)
total_wins = 0
total_losses = 0
total_rounds = 0
current_streak = 0
best_win_streak = 0
worst_loss_streak = 0
current_level = 1

# ✅ hourly স্ট্যাটস (প্রতি ঘন্টায় রিসেট হবে)
hourly_wins = 0
hourly_losses = 0
hourly_rounds = 0
hourly_best_win_streak = 0
hourly_worst_loss_streak = 0

history_data = []

last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
prediction_sent_for_period = {}
last_result_sent = False

# ============================================================
#  🧠 DARK X ENGINE (Titan HTML থেকে)
# ============================================================
def dark_x_engine(data, level):
    if len(data) < 3:
        return {"prediction": "BIG", "confidence": 50, "number": 7}
    
    types = [d['side'] for d in data[:10]]
    last1 = types[0] if len(types) > 0 else "BIG"
    last2 = types[1] if len(types) > 1 else "BIG"
    
    # ডিফল্ট ট্রানজিশন
    if last1 == "SMALL":
        pred = "BIG"
        conf = 75
    else:
        pred = "SMALL"
        conf = 60
    
    # সিকোয়েন্স ওভাররাইড
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
    
    # লেভেল ৩ সেফটি নেট
    if level == 3 and len(data) > 0:
        latest_num = data[0]['number']
        pred = "SMALL" if latest_num >= 5 else "BIG"
        conf = 99
    
    # নম্বর জেনারেট
    if pred == "BIG":
        num = random.randint(5, 9)
    else:
        num = random.randint(0, 4)
    
    return {"prediction": pred, "confidence": conf, "number": num}

# ==================== 📡 API ফেচ ====================
def fetch_api_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'Origin': 'https://www.google.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
    }
    
    for api_url in API_URLS:
        try:
            url = api_url + "?t=" + str(int(time.time() * 1000))
            res = requests.get(url, headers=headers, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                list_data = data.get("data", {}).get("list", [])
                if list_data and len(list_data) > 0:
                    return list_data
            else:
                print(f"⚠️ {api_url} → HTTP {res.status_code}")
        except Exception as e:
            print(f"⚠️ {api_url} → এরর: {e}")
    
    return []

# ==================== 📤 মেসেজ সেন্ড ====================
async def send_message(text, parse_mode="Markdown"):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=parse_mode)
        return True
    except Exception as e:
        print(f"❌ টেলিগ্রাম এরর: {e}")
        return False

# ==================== 📊 হাওয়ারলি রিপোর্ট ====================
async def send_hourly_report():
    global hourly_wins, hourly_losses, hourly_rounds
    global hourly_best_win_streak, hourly_worst_loss_streak
    global total_wins, total_losses, total_rounds
    global best_win_streak, worst_loss_streak
    
    if hourly_rounds == 0:
        return
    
    hourly_win_rate = (hourly_wins / hourly_rounds * 100) if hourly_rounds > 0 else 0
    total_win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
    
    report_msg = (
        f"📊 *আওয়ারলি রিপোর্ট - DARK X 3M*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 *সময়:* {datetime.now().strftime('%I:%M %p')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔄 *এই ঘন্টায় রাউন্ড:* `{hourly_rounds}`\n"
        f"✅ *এই ঘন্টায় জয়:* `{hourly_wins}`\n"
        f"❌ *এই ঘন্টায় হার:* `{hourly_losses}`\n"
        f"📈 *এই ঘন্টায় হার:* `{hourly_win_rate:.1f}%`\n"
        f"🔥 *এই ঘন্টায় সেরা জয় স্ট্রিক:* `{hourly_best_win_streak}x`\n"
        f"📉 *এই ঘন্টায় সেরা হার স্ট্রিক:* `{hourly_worst_loss_streak}x`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *মোট রাউন্ড:* `{total_rounds}`\n"
        f"✅ *মোট জয়:* `{total_wins}`\n"
        f"❌ *মোট হার:* `{total_losses}`\n"
        f"📈 *মোট জয়ের হার:* `{total_win_rate:.1f}%`\n"
        f"🔥 *সেরা জয় স্ট্রিক:* `{best_win_streak}x`\n"
        f"📉 *সেরা হার স্ট্রিক:* `{worst_loss_streak}x`\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    await send_message(report_msg)
    
    # ✅ শুধু hourly স্ট্যাটস রিসেট হবে
    hourly_wins = 0
    hourly_losses = 0
    hourly_rounds = 0
    hourly_best_win_streak = 0
    hourly_worst_loss_streak = 0

# ==================== 🚀 মেইন লুপ ====================
async def prediction_bot():
    global total_wins, total_losses, total_rounds
    global hourly_wins, hourly_losses, hourly_rounds
    global hourly_best_win_streak, hourly_worst_loss_streak
    global current_streak, best_win_streak, worst_loss_streak
    global current_level, history_data
    global last_predicted_period, last_predicted_signal
    global last_predicted_num, prediction_sent_for_period
    global last_result_sent

    print("🔥 DARK X 3M WINGO BOT STARTED...")
    print("📡 MODE: 3 MIN WINGO")
    print("🧠 ENGINE: DARK X ONLY")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                "🔥 *DARK X 3M WINGO* 🔥\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🧠 ইঞ্জিন: DARK X (মার্কভ চেইন)\n"
                "📡 মোড: 3 MIN WINGO\n"
                "📊 স্ট্র্যাটেজি: মার্টিঙ্গেল লেভেল\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "⏳ প্রথম সিগন্যালের জন্য অপেক্ষা..."
            )
        )
    except Exception as e:
        print(f"Startup error: {e}")

    last_hour_time = time.time()

    while True:
        try:
            # ✅ 3 মিনিট (180 সেকেন্ড) অপেক্ষা
            current_sec = int(time.time()) % 180
            sleep_time = 180 - current_sec + 5
            await asyncio.sleep(sleep_time)

            raw_list = fetch_api_data()
            if not raw_list:
                print("⚠️ API থেকে ডেটা পাওয়া যায়নি")
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

            print(f"📡 LATEST PERIOD: {latest_issue}, NUMBER: {actual_num} ({actual_type})")

            # ============================================================
            # 🔥 RESULT CHECK (শুধু DARK X)
            # ============================================================
            if last_predicted_period == latest_issue and last_predicted_signal is not None and not last_result_sent:
                is_win = (last_predicted_signal == actual_type)
                
                if is_win:
                    total_wins += 1
                    hourly_wins += 1
                    
                    if current_streak >= 0:
                        current_streak += 1
                    else:
                        current_streak = 1
                    
                    # best win streak আপডেট
                    if current_streak > best_win_streak:
                        best_win_streak = current_streak
                    if current_streak > hourly_best_win_streak:
                        hourly_best_win_streak = current_streak
                    
                    # লেভেল রিসেট
                    current_level = 1
                    
                    status = "✅ জয় 🎉"
                else:
                    total_losses += 1
                    hourly_losses += 1
                    
                    if current_streak <= 0:
                        current_streak -= 1
                    else:
                        current_streak = -1
                    
                    # worst loss streak আপডেট
                    if abs(current_streak) > worst_loss_streak:
                        worst_loss_streak = abs(current_streak)
                    if abs(current_streak) > hourly_worst_loss_streak:
                        hourly_worst_loss_streak = abs(current_streak)
                    
                    # লেভেল আপডেট (1 → 2 → 3 → 1)
                    current_level = (current_level % 3) + 1
                    
                    status = "❌ হার"

                total_rounds += 1
                hourly_rounds += 1
                
                total_win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
                multiplier = f"{current_level}x"
                streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"

                result_msg = (
                    f"🎯 *রেজাল্ট আপডেট*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 পিরিয়ড: `#{latest_issue[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔮 প্রেডিকশন: `{last_predicted_signal}` → `{last_predicted_num}`\n"
                    f"🎰 একচুয়াল: `{actual_num}` → `{actual_type}`\n"
                    f"📌 রেজাল্ট: `{status}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 জয়ের হার: `{total_win_rate:.1f}%` ({total_wins}W/{total_losses}L)\n"
                    f"{streak_emoji} স্ট্রিক: `{current_streak:+d}`\n"
                    f"👑 লেভেল: `{current_level}` ({multiplier})\n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )

                await send_message(result_msg)
                last_result_sent = True
                print(f"✅ রেজাল্ট পাঠানো হয়েছে: {latest_issue}")

                # প্রতি ঘন্টায় রিপোর্ট
                if time.time() - last_hour_time >= 3600:
                    await send_hourly_report()
                    last_hour_time = time.time()

            # ============================================================
            # 🔥 NEW PREDICTION (শুধু DARK X)
            # ============================================================
            next_period = str(int(latest_issue) + 1)
            print(f"🎯 NEXT PERIOD: {next_period}")

            if not prediction_sent_for_period.get(next_period, False):
                # DARK X ইঞ্জিন
                pred = dark_x_engine(history_data, current_level)
                
                multiplier = f"{current_level}x"
                streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"
                
                # রেকমেন্ডেশন
                if pred['confidence'] >= 85:
                    rec = "🔥 হাই কনফিডেন্স - নরমাল বেট"
                elif pred['confidence'] >= 70:
                    rec = "⚡ মিডিয়াম কনফিডেন্স - সেফ বেট"
                else:
                    rec = "⚠️ লো কনফিডেন্স - ছোট বেট বা ওয়েট"

                prediction_msg = (
                    f"🔥 *DARK X 3M WINGO* 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 পিরিয়ড: `#{next_period[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 প্রেডিকশন: `{pred['prediction']}`\n"
                    f"🔢 টার্গেট নম্বর: `{pred['number']}`\n"
                    f"⚡ কনফিডেন্স: `{pred['confidence']}%`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💡 রেকমেন্ডেশন:\n"
                    f"• {rec}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👑 লেভেল: `{current_level}` ({multiplier})\n"
                    f"{streak_emoji} স্ট্রিক: `{current_streak:+d}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ রেজাল্টের জন্য অপেক্ষা..."
                )

                last_predicted_period = next_period
                last_predicted_signal = pred['prediction']
                last_predicted_num = pred['number']
                prediction_sent_for_period[next_period] = True
                last_result_sent = False

                await send_message(prediction_msg)
                print(f"✅ প্রেডিকশন: {next_period} → {pred['prediction']} ({pred['number']})")

                if len(prediction_sent_for_period) > 5:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            print(f"❌ Loop Error: {e}")
            await asyncio.sleep(5)

# ==================== 🚀 স্টার্ট ====================
if __name__ == '__main__':
    print("🔥 DARK X 3M WINGO BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 ENGINE: DARK X (Titan)")
    print("📡 MODE: 3 MIN WINGO")
    print("━━━━━━━━━━━━━━━━━━━━")
    
    try:
        asyncio.run(prediction_bot())
    except KeyboardInterrupt:
        print("\n👋 বট বন্ধ করা হয়েছে")
    except Exception as e:
        print(f"❌ ফাটাল এরর: {e}")
