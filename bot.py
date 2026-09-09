#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 GURU SERVER BOT — Wingo 30s BIG/SMALL প্রেডিকশন
🧠 অ্যালগরিদম: ডিজিটের যোগফল % 10 → BIG (>=5) বা SMALL (<5)
📡 অর্ডার: রেজাল্ট → প্রেডিকশন
🤖 বট: @rakiiibahmed
"""

import asyncio
import time
import requests
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

try:
    from telegram import Bot
except ImportError:
    print("❌ python-telegram-bot ইনস্টল নেই! রান করুন: pip install python-telegram-bot")
    exit(1)

# ==================== 📌 কনফিগারেশন ====================
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30s/GetHistoryIssuePage.json"  # 30s Wingo

# ==================== 🌐 ওয়েব সার্ভার ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"GURU 30s WINGO BOT is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ==================== 📊 বট ইনিশিয়ালাইজ ====================
bot = Bot(token=BOT_TOKEN)

# ==================== গ্লোবাল ভেরিয়েবল ====================
total_wins = 0
total_losses = 0
total_rounds = 0
current_streak = 0
best_streak = 0
last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
prediction_sent_for_period = {}

# ==================== 🧠 গুরু অ্যালগরিদম (শুধু BIG/SMALL) ====================
def guru_algorithm(period_number):
    """ডিজিটের যোগফল % 10 → BIG (>=5) বা SMALL (<5)"""
    str_period = str(period_number)
    digit_sum = sum(int(ch) for ch in str_period if ch.isdigit())
    remainder = digit_sum % 10
    
    is_big = remainder >= 5
    prediction = "BIG" if is_big else "SMALL"
    
    # কনফিডেন্স লেভেল
    if is_big:
        confidence = min(95, 70 + remainder * 5)
    else:
        confidence = min(95, 70 + (9 - remainder) * 5)
    
    return {
        'prediction': prediction,
        'number': remainder,
        'digit_sum': digit_sum,
        'confidence': confidence
    }

# ==================== 📡 API ফেচ ====================
def fetch_api_data():
    try:
        res = requests.get(API_URL + "?t=" + str(int(time.time() * 1000)), timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", {}).get("list", [])
    except:
        pass
    return []

# ==================== 📊 হাওয়ারলি রিপোর্ট ====================
async def send_hourly_report():
    global total_wins, total_losses, total_rounds, current_streak, best_streak
    
    if total_rounds == 0:
        return
    
    win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
    
    report_msg = (
        f"📊 *আওয়ারলি রিপোর্ট - 30s Wingo*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 *সময়:* {datetime.now().strftime('%I:%M %p')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔄 *মোট রাউন্ড:* `{total_rounds}`\n"
        f"✅ *জয়:* `{total_wins}`\n"
        f"❌ *হার:* `{total_losses}`\n"
        f"📈 *জয়ের হার:* `{win_rate:.1f}%`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 *সেরা স্ট্রিক:* `{best_streak}x`\n"
        f"📉 *বর্তমান স্ট্রিক:* `{current_streak:+d}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ *GURU 30s WINGO BOT*"
    )
    
    try:
        await bot.send_message(chat_id=CHAT_ID, text=report_msg, parse_mode="Markdown")
    except:
        pass

# ==================== 🚀 মেইন লুপ ====================
async def prediction_bot():
    global total_wins, total_losses, total_rounds
    global current_streak, best_streak
    global last_predicted_period, last_predicted_signal
    global last_predicted_num
    global prediction_sent_for_period

    print("🔥 GURU 30s WINGO BIG/SMALL বট স্টার্ট...")
    print("🤖 @rakiiibahmed")
    print("📡 মোড: 30s Wingo BIG/SMALL")
    print("📊 অর্ডার: রেজাল্ট → প্রেডিকশন")
    print("━━━━━━━━━━━━━━━━━━━━")

    # স্টার্টআপ মেসেজ
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                "🔥 *GURU 30s WINGO BIG/SMALL বট* 🔥\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🤖 *বট:* @rakiiibahmed\n"
                "📡 *মোড:* 30s Wingo BIG/SMALL\n"
                "📊 *অর্ডার:* রেজাল্ট → প্রেডিকশন\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "⏳ প্রথম সিগন্যালের জন্য অপেক্ষা..."
            ),
            parse_mode="Markdown"
        )
    except:
        pass

    last_hour_time = time.time()

    while True:
        try:
            # 30 সেকেন্ডের সিঙ্ক
            current_sec = int(time.time()) % 30
            sleep_time = 30 - current_sec + 1
            await asyncio.sleep(sleep_time)

            raw_list = fetch_api_data()
            if not raw_list:
                print("⚠️ API থেকে ডেটা পাওয়া যায়নি")
                continue

            latest = raw_list[0]
            latest_issue = str(latest['issueNumber'])
            actual_num = int(latest['number'])
            actual_type = "BIG" if actual_num >= 5 else "SMALL"

            print(f"📡 লেটেস্ট পিরিয়ড: {latest_issue}, নাম্বার: {actual_num} ({actual_type})")

            # ============================================================
            # 🔥 রেজাল্ট চেক (প্রথমে রেজাল্ট)
            # ============================================================
            if last_predicted_period == latest_issue and last_predicted_signal is not None:
                is_win = (last_predicted_signal == actual_type)
                
                if is_win:
                    total_wins += 1
                    current_streak += 1
                    if current_streak > best_streak:
                        best_streak = current_streak
                    status = "✅ জয় 🎉"
                else:
                    total_losses += 1
                    current_streak = 0 if current_streak < 0 else -1
                    status = "❌ হার"

                total_rounds += 1
                win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0

                # রেজাল্ট মেসেজ
                result_msg = (
                    f"🎯 *রেজাল্ট আপডেট*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 পিরিয়ড: `#{latest_issue[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔮 *প্রেডিকশন:* `{last_predicted_signal}` → `{last_predicted_num}`\n"
                    f"🎰 *একচুয়াল:* `{actual_num}` → `{actual_type}`\n"
                    f"📌 *রেজাল্ট:* `{status}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 *জয়ের হার:* `{win_rate:.1f}%` ({total_wins}W/{total_losses}L)\n"
                    f"🔥 *স্ট্রিক:* `{current_streak:+d}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚡ *GURU 30s WINGO BOT*"
                )

                try:
                    await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                except:
                    pass

                # প্রতি ঘন্টায় রিপোর্ট
                if time.time() - last_hour_time >= 3600:
                    await send_hourly_report()
                    # রিসেট
                    total_wins = 0
                    total_losses = 0
                    total_rounds = 0
                    current_streak = 0
                    best_streak = 0
                    last_hour_time = time.time()

                last_predicted_period = None
                last_predicted_signal = None

            # ============================================================
            # 🔥 নতুন প্রেডিকশন (রেজাল্টের পর)
            # ============================================================
            next_period = str(int(latest_issue) + 1)
            print(f"🎯 পরবর্তী পিরিয়ড: {next_period}")

            if not prediction_sent_for_period.get(next_period, False):
                pred = guru_algorithm(next_period)

                # রেকমেন্ডেশন
                if pred['confidence'] >= 80:
                    rec = "🔥 হাই কনফিডেন্স - নরমাল বেট"
                elif pred['confidence'] >= 65:
                    rec = "⚡ মিডিয়াম কনফিডেন্স - সেফ বেট"
                else:
                    rec = "⚠️ লো কনফিডেন্স - ছোট বেট বা ওয়েট"

                prediction_msg = (
                    f"🔥 *GURU 30s WINGO BIG/SMALL* 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 পিরিয়ড: `#{next_period[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 *প্রেডিকশন:* `{pred['prediction']}`\n"
                    f"🔢 *নাম্বার:* `{pred['number']}`\n"
                    f"⚡ *কনফিডেন্স:* `{pred['confidence']}%`\n"
                    f"📊 *ডিজিট সাম:* `{pred['digit_sum']}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💡 *রেকমেন্ডেশন:*\n"
                    f"• {rec}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ *রেজাল্টের জন্য অপেক্ষা...*\n"
                    f"⚡ *GURU 30s WINGO BOT*"
                )

                last_predicted_period = next_period
                last_predicted_signal = pred['prediction']
                last_predicted_num = pred['number']
                prediction_sent_for_period[next_period] = True

                try:
                    await bot.send_message(chat_id=CHAT_ID, text=prediction_msg, parse_mode="Markdown")
                    print(f"✅ প্রেডিকশন: {next_period} → {pred['prediction']} ({pred['number']})")
                except Exception as e:
                    print(f"❌ প্রেরণ ব্যর্থ: {e}")

                # পুরনো পিরিয়ড ক্লিয়ার
                if len(prediction_sent_for_period) > 5:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            print(f"❌ লুপ এরর: {e}")
            await asyncio.sleep(3)

# ==================== 🚀 স্টার্ট ====================
if __name__ == '__main__':
    print("🔥 GURU 30s WINGO BIG/SMALL বট")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🤖 @rakiiibahmed")
    print("📡 মোড: 30s Wingo BIG/SMALL")
    print("📊 অর্ডার: রেজাল্ট → প্রেডিকশন")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
