#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 GURU 30s WINGO BIG/SMALL বট - ফুল ফিক্সড
🤖 @rakiiibahmed
"""

import asyncio
import time
import requests
import os
import json
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Logging সেটআপ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from telegram import Bot
    from telegram.error import TelegramError, TimedOut, NetworkError
except ImportError:
    print("❌ python-telegram-bot ইনস্টল নেই! রান করুন: pip install python-telegram-bot")
    exit(1)

# ==================== 📌 কনফিগারেশন ====================
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30s/GetHistoryIssuePage.json"

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
try:
    bot = Bot(token=BOT_TOKEN)
    logger.info("✅ বট ইনিশিয়ালাইজেশন সফল!")
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
last_sent_period = None

# ==================== 🧠 অ্যালগরিদম ====================
def guru_algorithm(period_number):
    """ডিজিটের যোগফল % 10 → BIG (>=5) বা SMALL (<5)"""
    try:
        str_period = str(period_number)
        digit_sum = 0
        for ch in str_period:
            if ch.isdigit():
                digit_sum += int(ch)
        
        remainder = digit_sum % 10
        is_big = remainder >= 5
        prediction = "BIG" if is_big else "SMALL"
        
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
    except Exception as e:
        logger.error(f"অ্যালগরিদম এরর: {e}")
        return {'prediction': 'BIG', 'number': 5, 'digit_sum': 0, 'confidence': 50}

# ==================== 📡 API ফেচ ====================
def fetch_api_data():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        res = requests.get(API_URL + "?t=" + str(int(time.time() * 1000)), headers=headers, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            if data.get('code') == 0 or data.get('success') == True:
                list_data = data.get("data", {}).get("list", [])
                if list_data and len(list_data) > 0:
                    return list_data
                else:
                    logger.warning("API থেকে কোনো ডেটা পাওয়া যায়নি")
            else:
                logger.warning(f"API এরর রেসপন্স: {data}")
        else:
            logger.warning(f"HTTP এরর: {res.status_code}")
    except requests.exceptions.Timeout:
        logger.warning("API টাইমআউট")
    except requests.exceptions.ConnectionError:
        logger.warning("API কানেকশন এরর")
    except Exception as e:
        logger.error(f"API ফেচ এরর: {e}")
    
    return []

# ==================== 📤 মেসেজ সেন্ড ফাংশন ====================
async def send_message(text, parse_mode="Markdown", retry_count=3):
    """মেসেজ পাঠানোর ফাংশন - রিট্রাই সহ"""
    for attempt in range(retry_count):
        try:
            await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=parse_mode)
            logger.info("✅ মেসেজ সফলভাবে পাঠানো হয়েছে")
            return True
        except TimedOut:
            logger.warning(f"⏱️ টাইমআউট, রিট্রাই {attempt+1}/{retry_count}")
            await asyncio.sleep(2)
        except NetworkError:
            logger.warning(f"🌐 নেটওয়ার্ক এরর, রিট্রাই {attempt+1}/{retry_count}")
            await asyncio.sleep(2)
        except TelegramError as e:
            logger.error(f"❌ টেলিগ্রাম এরর: {e}")
            break
        except Exception as e:
            logger.error(f"❌ অজানা এরর: {e}")
            break
    
    logger.error("❌ মেসেজ পাঠাতে ব্যর্থ হয়েছে")
    return False

# ==================== 📊 রিপোর্ট ====================
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
    
    await send_message(report_msg)

# ==================== 🚀 মেইন লুপ ====================
async def prediction_bot():
    global total_wins, total_losses, total_rounds
    global current_streak, best_streak
    global last_predicted_period, last_predicted_signal
    global last_predicted_num, prediction_sent_for_period
    global last_result_sent, last_result_period, last_sent_period

    logger.info("🔥 GURU 30s WINGO BIG/SMALL বট স্টার্ট...")
    logger.info(f"🤖 বট: @rakiiibahmed")
    logger.info(f"📡 চ্যাট আইডি: {CHAT_ID}")
    logger.info("📡 মোড: 30s Wingo BIG/SMALL")
    logger.info("📊 অর্ডার: রেজাল্ট → প্রেডিকশন")
    logger.info("━━━━━━━━━━━━━━━━━━━━")

    # স্টার্টআপ মেসেজ
    startup_msg = (
        "🔥 *GURU 30s WINGO BIG/SMALL বট* 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 *বট:* @rakiiibahmed\n"
        "📡 *মোড:* 30s Wingo BIG/SMALL\n"
        "📊 *অর্ডার:* রেজাল্ট → প্রেডিকশন\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⏳ প্রথম সিগন্যালের জন্য অপেক্ষা..."
    )
    
    await send_message(startup_msg)

    last_hour_time = time.time()
    no_data_count = 0
    consecutive_fails = 0

    while True:
        try:
            current_sec = int(time.time()) % 30
            sleep_time = 30 - current_sec + 2
            await asyncio.sleep(sleep_time)

            logger.info("📡 API থেকে ডেটা নেওয়া হচ্ছে...")
            raw_list = fetch_api_data()
            
            if not raw_list:
                no_data_count += 1
                consecutive_fails += 1
                if consecutive_fails >= 5:
                    logger.error("❌ পরপর ৫ বার API ফেইল, ১০ সেকেন্ড অপেক্ষা...")
                    await asyncio.sleep(10)
                    consecutive_fails = 0
                continue
            else:
                no_data_count = 0
                consecutive_fails = 0

            latest = raw_list[0]
            latest_issue = str(latest.get('issueNumber', ''))
            
            if not latest_issue or not latest_issue.isdigit():
                logger.warning(f"⚠️ ইনভ্যালিড ইস্যু: {latest_issue}")
                continue
                
            actual_num = int(latest.get('number', 0))
            actual_type = "BIG" if actual_num >= 5 else "SMALL"

            logger.info(f"📡 পিরিয়ড: {latest_issue}, নাম্বার: {actual_num} ({actual_type})")

            # ============================================================
            # 🔥 রেজাল্ট চেক (প্রথমে রেজাল্ট)
            # ============================================================
            if last_predicted_period and last_predicted_period == latest_issue and not last_result_sent:
                is_win = (last_predicted_signal == actual_type)
                
                if is_win:
                    total_wins += 1
                    current_streak += 1
                    if current_streak > best_streak:
                        best_streak = current_streak
                    status = "✅ জয় 🎉"
                else:
                    total_losses += 1
                    current_streak = -1 if current_streak < 0 else 0
                    status = "❌ হার"

                total_rounds += 1
                win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0

                level = min(10, max(1, current_streak + 1)) if current_streak >= 0 else 1
                multiplier = f"{level}x"

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
                    f"📈 *লেভেল:* `{level}` ({multiplier})\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚡ *GURU 30s WINGO BOT*"
                )

                await send_message(result_msg)
                last_result_sent = True
                last_result_period = latest_issue
                logger.info(f"✅ রেজাল্ট পাঠানো হয়েছে: {latest_issue} → {'জয়' if is_win else 'হার'}")

                # প্রতি ঘন্টায় রিপোর্ট
                if time.time() - last_hour_time >= 3600:
                    await send_hourly_report()
                    total_wins = 0
                    total_losses = 0
                    total_rounds = 0
                    current_streak = 0
                    best_streak = 0
                    last_hour_time = time.time()

            # ============================================================
            # 🔥 নতুন প্রেডিকশন
            # ============================================================
            next_period = str(int(latest_issue) + 1)
            
            if next_period not in prediction_sent_for_period or not prediction_sent_for_period[next_period]:
                pred = guru_algorithm(next_period)

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
                last_result_sent = False

                await send_message(prediction_msg)
                logger.info(f"✅ প্রেডিকশন: {next_period} → {pred['prediction']} ({pred['number']})")

                if len(prediction_sent_for_period) > 5:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            logger.error(f"❌ লুপ এরর: {e}")
            await asyncio.sleep(5)

# ==================== 🚀 স্টার্ট ====================
if __name__ == '__main__':
    print("🔥 GURU 30s WINGO BIG/SMALL বট")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🤖 @rakiiibahmed")
    print(f"📡 চ্যাট আইডি: {CHAT_ID}")
    print("📡 মোড: 30s Wingo BIG/SMALL")
    print("📊 অর্ডার: রেজাল্ট → প্রেডিকশন")
    print("━━━━━━━━━━━━━━━━━━━━")
    
    try:
        asyncio.run(prediction_bot())
    except KeyboardInterrupt:
        print("\n👋 বট বন্ধ করা হয়েছে")
    except Exception as e:
        print(f"❌ ফাটাল এরর: {e}")
