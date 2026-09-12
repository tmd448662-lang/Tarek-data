#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 DARK X HYBRID V3 - BEST WIN RATE
🎯 Priority: Alternating → Trend → Markov → Loss Breaker
🤖 @rakiiibahmed
"""

import asyncio
import time
import requests
import os
import random
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
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"

API_URLS = [
    "https://draw.ar-lottery01.com/WinGo/WinGo_3M/GetHistoryIssuePage.json",
    "https://api.ar-lottery01.com/WinGo/WinGo_3M/GetHistoryIssuePage.json",
]

# ==================== 🌐 ওয়েব সার্ভার ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"DARK X HYBRID V3 BOT is running!")

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

# ==================== 📊 বট ইনিশিয়ালাইজ ====================
try:
    bot = Bot(token=BOT_TOKEN)
    logger.info("✅ বট ইনিশিয়ালাইজেশন সফল!")
    logger.info(f"🤖 বট: @rakiiibahmed")
except Exception as e:
    logger.error(f"❌ বট ইনিশিয়ালাইজেশন ব্যর্থ: {e}")
    exit(1)

# ==================== গ্লোবাল ভেরিয়েবল ====================
total_wins = 0
total_losses = 0
total_rounds = 0
current_streak = 0
best_win_streak = 0
worst_loss_streak = 0
current_level = 1
consecutive_losses = 0

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

# ═══════════════════════════════════════════════════
#  🧠 ENGINE 1: ALTERNATING PATTERN
# ═══════════════════════════════════════════════════
def alternating_engine(types):
    if len(types) < 4:
        return None
    
    last4 = types[:4]
    
    if last4 == ["BIG", "SMALL", "BIG", "SMALL"]:
        return {"prediction": "BIG", "confidence": 88, "reason": "ALTERNATING (B-S-B-S)"}
    elif last4 == ["SMALL", "BIG", "SMALL", "BIG"]:
        return {"prediction": "SMALL", "confidence": 88, "reason": "ALTERNATING (S-B-S-B)"}
    
    return None

# ═══════════════════════════════════════════════════
#  🧠 ENGINE 2: TREND FOLLOW
# ═══════════════════════════════════════════════════
def trend_engine(types):
    if len(types) < 5:
        return None
    
    recent5 = types[:5]
    big_count = recent5.count("BIG")
    small_count = recent5.count("SMALL")
    
    if big_count >= 4:
        return {
            "prediction": "BIG",
            "confidence": 85 if big_count == 5 else 80,
            "reason": f"TREND FOLLOW ({big_count}B-{small_count}S)"
        }
    elif small_count >= 4:
        return {
            "prediction": "SMALL",
            "confidence": 85 if small_count == 5 else 80,
            "reason": f"TREND FOLLOW ({big_count}B-{small_count}S)"
        }
    
    return None

# ═══════════════════════════════════════════════════
#  🧠 ENGINE 3: MARKOV CHAIN
# ═══════════════════════════════════════════════════
def markov_engine(data, level):
    if len(data) < 3:
        return {"prediction": "BIG", "confidence": 50, "reason": "MARKOV (Fallback)"}
    
    types = [d['side'] for d in data[:10]]
    last1 = types[0] if len(types) > 0 else "BIG"
    last2 = types[1] if len(types) > 1 else "BIG"
    
    if last1 == "SMALL":
        pred = "BIG"
        conf = 75
    else:
        pred = "SMALL"
        conf = 60
    
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
    
    if level >= 3 and len(data) > 0:
        latest_num = data[0]['number']
        pred = "SMALL" if latest_num >= 5 else "BIG"
        conf = 99
    
    return {"prediction": pred, "confidence": conf, "reason": "MARKOV CHAIN"}

# ═══════════════════════════════════════════════════
#  🧠 ENGINE 4: LOSS BREAKER
# ═══════════════════════════════════════════════════
def loss_breaker_engine(data, level, consec_losses):
    if consec_losses < 3:
        return None
    
    markov = markov_engine(data, level)
    
    if consec_losses % 2 == 1:
        pred = "SMALL" if markov['prediction'] == "BIG" else "BIG"
        reason = f"LOSS BREAKER (উল্টো, {consec_losses}টি টানা লস)"
    else:
        pred = markov['prediction']
        reason = f"LOSS BREAKER (একই দিক, {consec_losses}টি টানা লস)"
    
    return {
        "prediction": pred,
        "confidence": min(99, markov['confidence'] + 5),
        "reason": reason
    }

# ═══════════════════════════════════════════════════
#  🔥 MASTER HYBRID V3 ENGINE
# ═══════════════════════════════════════════════════
def hybrid_v3_engine(data, level, consec_losses):
    if len(data) < 3:
        return {"prediction": "BIG", "confidence": 50, "number": 7, "reason": "INSUFFICIENT DATA"}
    
    types = [d['side'] for d in data]
    
    # ধাপ ১: Alternating Pattern
    alt_result = alternating_engine(types)
    if alt_result:
        pred = alt_result['prediction']
        num = random.randint(5, 9) if pred == "BIG" else random.randint(0, 4)
        return {
            "prediction": pred,
            "confidence": alt_result['confidence'],
            "number": num,
            "reason": alt_result['reason']
        }
    
    # ধাপ ২: Trend Follow
    trend_result = trend_engine(types)
    if trend_result:
        pred = trend_result['prediction']
        num = random.randint(5, 9) if pred == "BIG" else random.randint(0, 4)
        return {
            "prediction": pred,
            "confidence": trend_result['confidence'],
            "number": num,
            "reason": trend_result['reason']
        }
    
    # ধাপ ৩: Loss Breaker (৩+ লস হলে)
    if consec_losses >= 3:
        lb_result = loss_breaker_engine(data, level, consec_losses)
        if lb_result:
            pred = lb_result['prediction']
            num = random.randint(5, 9) if pred == "BIG" else random.randint(0, 4)
            return {
                "prediction": pred,
                "confidence": lb_result['confidence'],
                "number": num,
                "reason": lb_result['reason']
            }
    
    # ধাপ ৪: Markov Chain (Fallback)
    markov = markov_engine(data, level)
    pred = markov['prediction']
    num = random.randint(5, 9) if pred == "BIG" else random.randint(0, 4)
    return {
        "prediction": pred,
        "confidence": markov['confidence'],
        "number": num,
        "reason": markov['reason']
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
            res = requests.get(url, headers=headers, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                list_data = data.get("data", {}).get("list", [])
                if list_data and len(list_data) > 0:
                    return list_data
            else:
                logger.warning(f"⚠️ {api_url} → HTTP {res.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ {api_url} → এরর: {e}")
    
    return []

# ==================== 📤 মেসেজ সেন্ড ====================
async def send_message(text, parse_mode="Markdown", retry_count=3):
    for attempt in range(retry_count):
        try:
            await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=parse_mode)
            return True
        except (TimedOut, NetworkError):
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"❌ টেলিগ্রাম এরর: {e}")
            break
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
        f"📊 *আওয়ারলি রিপোর্ট - HYBRID V3*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 *সময়:* {datetime.now().strftime('%I:%M %p')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔄 *এই ঘন্টায় রাউন্ড:* `{hourly_rounds}`\n"
        f"✅ *এই ঘন্টায় জয়:* `{hourly_wins}`\n"
        f"❌ *এই ঘন্টায় হার:* `{hourly_losses}`\n"
        f"📈 *এই ঘন্টায় হার:* `{hourly_win_rate:.1f}%`\n"
        f"🔥 *সেরা জয় স্ট্রিক:* `{hourly_best_win_streak}x`\n"
        f"📉 *সেরা হার স্ট্রিক:* `{hourly_worst_loss_streak}x`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *মোট রাউন্ড:* `{total_rounds}`\n"
        f"✅ *মোট জয়:* `{total_wins}`\n"
        f"❌ *মোট হার:* `{total_losses}`\n"
        f"📈 *মোট জয়ের হার:* `{total_win_rate:.1f}%`\n"
        f"🔥 *সেরা জয় স্ট্রিক:* `{best_win_streak}x`\n"
        f"📉 *সেরা হার স্ট্রিক:* `{worst_loss_streak}x`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 @rakiiibahmed"
    )
    
    await send_message(report_msg)
    
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
    global current_level, consecutive_losses, history_data
    global last_predicted_period, last_predicted_signal
    global last_predicted_num, prediction_sent_for_period
    global last_result_sent

    logger.info("🔥 DARK X HYBRID V3 বট স্টার্ট...")

    await send_message(
        "🔥 *DARK X HYBRID V3 - BEST WIN RATE* 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🧠 *Priority Order:*\n"
        "1️⃣ Alternating Pattern (B-S-B-S)\n"
        "2️⃣ Trend Follow (4+/5)\n"
        "3️⃣ Markov Chain (DARK X)\n"
        "4️⃣ Loss Breaker (3+ losses)\n"
        "📡 *মোড:* 3M WINGO\n"
        "🤖 *বট:* @rakiiibahmed\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⏳ প্রথম সিগন্যালের জন্য অপেক্ষা..."
    )

    last_hour_time = time.time()

    while True:
        try:
            current_sec = int(time.time()) % 180
            sleep_time = 180 - current_sec + 5
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

            logger.info(f"📡 পিরিয়ড: {latest_issue}, নাম্বার: {actual_num} ({actual_type})")

            # ===== রেজাল্ট চেক =====
            if last_predicted_period == latest_issue and last_predicted_signal is not None and not last_result_sent:
                is_win = (last_predicted_signal == actual_type)
                
                if is_win:
                    total_wins += 1
                    hourly_wins += 1
                    consecutive_losses = 0
                    
                    if current_streak >= 0:
                        current_streak += 1
                    else:
                        current_streak = 1
                    
                    if current_streak > best_win_streak:
                        best_win_streak = current_streak
                    if current_streak > hourly_best_win_streak:
                        hourly_best_win_streak = current_streak
                    
                    current_level = 1
                    status = "✅ জয় 🎉"
                else:
                    total_losses += 1
                    hourly_losses += 1
                    consecutive_losses += 1
                    
                    if current_streak <= 0:
                        current_streak -= 1
                    else:
                        current_streak = -1
                    
                    if abs(current_streak) > worst_loss_streak:
                        worst_loss_streak = abs(current_streak)
                    if abs(current_streak) > hourly_worst_loss_streak:
                        hourly_worst_loss_streak = abs(current_streak)
                    
                    current_level = min(3, current_level + 1)
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
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🤖 @rakiiibahmed"
                )

                await send_message(result_msg)
                last_result_sent = True
                logger.info(f"✅ রেজাল্ট পাঠানো হয়েছে: {latest_issue}")

                if time.time() - last_hour_time >= 3600:
                    await send_hourly_report()
                    last_hour_time = time.time()

            # ===== নতুন প্রেডিকশন =====
            next_period = str(int(latest_issue) + 1)
            
            if not prediction_sent_for_period.get(next_period, False):
                
                pred = hybrid_v3_engine(history_data, current_level, consecutive_losses)
                
                multiplier = f"{current_level}x"
                streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"
                
                if pred['confidence'] >= 85:
                    rec = "🔥 হাই কনফিডেন্স - নরমাল বেট"
                elif pred['confidence'] >= 70:
                    rec = "⚡ মিডিয়াম কনফিডেন্স - সেফ বেট"
                else:
                    rec = "⚠️ লো কনফিডেন্স - ছোট বেট বা ওয়েট"

                prediction_msg = (
                    f"🔥 *DARK X HYBRID V3 - 3M WINGO* 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 পিরিয়ড: `#{next_period[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 প্রেডিকশন: `{pred['prediction']}`\n"
                    f"🔢 টার্গেট নম্বর: `{pred['number']}`\n"
                    f"⚡ কনফিডেন্স: `{pred['confidence']}%`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 ইঞ্জিন: {pred['reason']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💡 রেকমেন্ডেশন:\n"
                    f"• {rec}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👑 লেভেল: `{current_level}` ({multiplier})\n"
                    f"{streak_emoji} স্ট্রিক: `{current_streak:+d}`\n"
                    f"❌ টানা লস: `{consecutive_losses}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ রেজাল্টের জন্য অপেক্ষা...\n"
                    f"🤖 @rakiiibahmed"
                )

                last_predicted_period = next_period
                last_predicted_signal = pred['prediction']
                last_predicted_num = pred['number']
                prediction_sent_for_period[next_period] = True
                last_result_sent = False

                await send_message(prediction_msg)
                logger.info(f"✅ প্রেডিকশন: {next_period} → {pred['prediction']} ({pred['reason']})")

                if len(prediction_sent_for_period) > 5:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            logger.error(f"❌ Loop Error: {e}")
            await asyncio.sleep(5)

# ==================== 🚀 স্টার্ট ====================
if __name__ == '__main__':
    print("🔥 DARK X HYBRID V3 - BEST WIN RATE")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🎯 1. Alternating Pattern")
    print("🎯 2. Trend Follow (4+/5)")
    print("🎯 3. Markov Chain (DARK X)")
    print("🎯 4. Loss Breaker (3+ losses)")
    print("📡 MODE: 3M WINGO")
    print("🤖 BOT: @rakiiibahmed")
    print("━━━━━━━━━━━━━━━━━━━━")
    
    try:
        asyncio.run(prediction_bot())
    except KeyboardInterrupt:
        print("\n👋 বট বন্ধ করা হয়েছে")
    except Exception as e:
        print(f"❌ ফাটাল এরর: {e}")