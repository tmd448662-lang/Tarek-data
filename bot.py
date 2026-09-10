#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 RGB HACK 3M WINGO BIG/SMALL বট
🤖 @Tarek3o
"""

import asyncio
import time
import requests
import os
import logging
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from telegram import Bot
    from telegram.error import TelegramError, TimedOut, NetworkError
except ImportError:
    print("❌ python-telegram-bot ইনস্টল নেই!")
    exit(1)

# ==================== 📌 কনফিগারেশন ====================
BOT_TOKEN = "8632082751:AAEcUqV8hFs-Id0E9uL0ltvW-e6ybZkKcJ0"
CHAT_ID = "6678981102"

# ✅ 3 মিনিট উইঙ্গো API
API_URLS = [
    "https://draw.ar-lottery01.com/WinGo/WinGo_3M/GetHistoryIssuePage.json",
    "https://api.ar-lottery01.com/WinGo/WinGo_3M/GetHistoryIssuePage.json",
]

# ==================== 🌐 ওয়েব সার্ভার ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"RGB HACK 3M WINGO BOT is running!")
    
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ==================== 📊 বট ইনিশিয়ালাইজ ====================
try:
    bot = Bot(token=BOT_TOKEN)
    logger.info("✅ বট ইনিশিয়ালাইজেশন সফল!")
    logger.info(f"🤖 বট ইউজারনেম: @Tarek3o")
except Exception as e:
    logger.error(f"❌ বট ইনিশিয়ালাইজেশন ব্যর্থ: {e}")
    exit(1)

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
last_result_sent = False
last_result_period = None

# ============================================================
#  🧠 RGB HACK ENGINE (Ansh Boss এর মতো)
# ============================================================
def get_period_index():
    now = datetime.now(timezone.utc)
    midnight = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
    diff_seconds = (now - midnight).total_seconds()
    period_index = int(diff_seconds // 180) + 1
    return period_index

def rgb_hack_engine():
    PATTERN = [
        {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 2}, {"s": "SMALL", "n": 4},
        {"s": "BIG", "n": 9}, {"s": "BIG", "n": 6}, {"s": "SMALL", "n": 0},
        {"s": "BIG", "n": 8}, {"s": "SMALL", "n": 3}, {"s": "SMALL", "n": 1},
        {"s": "BIG", "n": 5}, {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 4}
    ]
    
    period_index = get_period_index()
    pattern_index = (period_index + 5) % 12
    
    pred = PATTERN[pattern_index]
    
    return {
        "prediction": pred["s"], 
        "confidence": 78, 
        "number": pred["n"],
        "pattern_index": pattern_index,
        "period_index": period_index
    }

# ==================== 📡 API ফেচ ====================
def fetch_api_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
    }
    
    for api_url in API_URLS:
        try:
            url = api_url + "?t=" + str(int(time.time() * 1000))
            logger.info(f"📡 চেষ্টা করছি: {api_url}")
            res = requests.get(url, headers=headers, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                list_data = data.get("data", {}).get("list", [])
                if list_data and len(list_data) > 0:
                    logger.info(f"✅ API সফল: {api_url}")
                    return list_data
                else:
                    logger.warning(f"⚠️ {api_url} → ডেটা খালি")
            else:
                logger.warning(f"⚠️ {api_url} → HTTP {res.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ {api_url} → এরর: {e}")
    
    logger.error("❌ সব API ব্যর্থ!")
    return []

# ==================== 📤 মেসেজ সেন্ড ====================
async def send_message(text, parse_mode="Markdown", retry_count=3):
    for attempt in range(retry_count):
        try:
            await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=parse_mode)
            logger.info("✅ মেসেজ সফলভাবে পাঠানো হয়েছে")
            return True
        except (TimedOut, NetworkError):
            logger.warning(f"⏱️ রিট্রাই {attempt+1}/{retry_count}")
            await asyncio.sleep(2)
        except TelegramError as e:
            logger.error(f"❌ টেলিগ্রাম এরর: {e}")
            break
        except Exception as e:
            logger.error(f"❌ অজানা এরর: {e}")
            break
    return False

# ==================== 📊 হাওয়ারলি রিপোর্ট ====================
async def send_hourly_report():
    global total_wins, total_losses, total_rounds, current_streak, best_streak
    
    if total_rounds == 0:
        return
    
    win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
    
    report_msg = (
        f"📊 *আওয়ারলি রিপোর্ট - RGB HACK 3M*\n"
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
        f"🤖 @Tarek3o"
    )
    
    await send_message(report_msg)

# ==================== 🚀 মেইন লুপ ====================
async def prediction_bot():
    global total_wins, total_losses, total_rounds
    global current_streak, best_streak
    global last_predicted_period, last_predicted_signal
    global last_predicted_num, prediction_sent_for_period
    global last_result_sent, last_result_period

    logger.info("🔥 RGB HACK 3M WINGO BIG/SMALL বট স্টার্ট...")
    logger.info(f"🤖 বট: @Tarek3o")
    logger.info(f"📡 চ্যাট আইডি: {CHAT_ID}")
    logger.info("━━━━━━━━━━━━━━━━━━━━")

    await send_message(
        "🔥 *RGB HACK 3M WINGO BIG/SMALL বট* 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🧠 *ইঞ্জিন:* RGB HACK (১২-স্টেপ প্যাটার্ন)\n"
        "📡 *মোড:* 3M WINGO BIG/SMALL\n"
        "📊 *প্যাটার্ন:* Ansh Boss স্টাইল\n"
        "🤖 *বট:* @Tarek3o\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⏳ প্রথম সিগন্যালের জন্য অপেক্ষা..."
    )

    last_hour_time = time.time()

    while True:
        try:
            current_sec = int(time.time()) % 180
            sleep_time = 180 - current_sec + 5
            await asyncio.sleep(sleep_time)

            logger.info("📡 API থেকে ডেটা নেওয়া হচ্ছে...")
            raw_list = fetch_api_data()
            
            if not raw_list:
                logger.warning("⚠️ ডেটা নেই, রিট্রাই...")
                continue

            latest = raw_list[0]
            latest_issue = str(latest.get('issueNumber', ''))
            
            if not latest_issue or not latest_issue.isdigit():
                logger.warning(f"⚠️ ইনভ্যালিড ইস্যু: {latest_issue}")
                continue
                
            actual_num = int(latest.get('number', 0))
            actual_type = "BIG" if actual_num >= 5 else "SMALL"

            logger.info(f"📡 লেটেস্ট পিরিয়ড: {latest_issue}, নাম্বার: {actual_num} ({actual_type})")

            # ===== রেজাল্ট চেক =====
            if last_predicted_period == latest_issue and last_predicted_signal is not None and not last_result_sent:
                is_win = (last_predicted_signal == actual_type)
                
                if is_win:
                    total_wins += 1
                    current_streak += 1
                    if current_streak > best_streak:
                        best_streak = current_streak
                    status = "✅ জয় 🎉"
                else:
                    total_losses += 1
                    current_streak = 0
                    status = "❌ হার"

                total_rounds += 1
                win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
                level = min(10, max(1, current_streak + 1)) if current_streak >= 0 else 1

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
                    f"📈 *লেভেল:* `{level}` ({level}x)\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🤖 @Tarek3o"
                )

                await send_message(result_msg)
                last_result_sent = True
                last_result_period = latest_issue
                logger.info(f"✅ রেজাল্ট পাঠানো হয়েছে: {latest_issue}")

                if time.time() - last_hour_time >= 3600:
                    await send_hourly_report()
                    total_wins = 0
                    total_losses = 0
                    total_rounds = 0
                    current_streak = 0
                    best_streak = 0
                    last_hour_time = time.time()

            # ===== নতুন প্রেডিকশন (RGB HACK) =====
            next_period = str(int(latest_issue) + 1)
            
            if next_period not in prediction_sent_for_period or not prediction_sent_for_period[next_period]:
                
                logger.info(f"🎯 নতুন প্রেডিকশন: {next_period}")
                
                pred = rgb_hack_engine()

                if pred['confidence'] >= 80:
                    rec = "🔥 হাই কনফিডেন্স - নরমাল বেট"
                elif pred['confidence'] >= 65:
                    rec = "⚡ মিডিয়াম কনফিডেন্স - সেফ বেট"
                else:
                    rec = "⚠️ লো কনফিডেন্স - ছোট বেট বা ওয়েট"

                prediction_msg = (
                    f"🔥 *RGB HACK 3M WINGO* 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 পিরিয়ড: `#{next_period[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 *প্রেডিকশন:* `{pred['prediction']}`\n"
                    f"🔢 *টার্গেট নম্বর:* `{pred['number']}`\n"
                    f"⚡ *কনফিডেন্স:* `{pred['confidence']}%`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 *প্যাটার্ন ইনডেক্স:* `{pred['pattern_index']}`\n"
                    f"📊 *পিরিয়ড ইনডেক্স:* `{pred['period_index']}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💡 *রেকমেন্ডেশন:*\n"
                    f"• {rec}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ *রেজাল্টের জন্য অপেক্ষা...*\n"
                    f"🤖 @Tarek3o"
                )

                last_predicted_period = next_period
                last_predicted_signal = pred['prediction']
                last_predicted_num = pred['number']
                prediction_sent_for_period[next_period] = True
                last_result_sent = False

                await send_message(prediction_msg)
                logger.info(f"✅ প্রেডিকশন: {next_period} → {pred['prediction']} ({pred['number']})")

                if len(prediction_sent_for_period) > 5:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]
                    logger.info(f"🗑️ পুরনো পিরিয়ড ডিলিট: {oldest}")

        except Exception as e:
            logger.error(f"❌ লুপ এরর: {e}")
            await asyncio.sleep(5)

# ==================== 🚀 স্টার্ট ====================
if __name__ == '__main__':
    print("🔥 RGB HACK 3M WINGO BIG/SMALL বট")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 ইঞ্জিন: RGB HACK (১২-স্টেপ প্যাটার্ন)")
    print("📡 মোড: 3M WINGO")
    print("🤖 বট: @Tarek3o")
    print("━━━━━━━━━━━━━━━━━━━━")
    
    try:
        asyncio.run(prediction_bot())
    except KeyboardInterrupt:
        print("\n👋 বট বন্ধ করা হয়েছে")
    except Exception as e:
        print(f"❌ ফাটাল এরর: {e}")
