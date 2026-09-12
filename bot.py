#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 REAL VIP V3 · NEURAL ANALYZER - 3M WINGO
🧠 Anti-Dragon + Mirror + Twin + Majority + Smart Number
🤖 @rakiiibahmed
"""

import asyncio
import time
import requests
import os
import random
import logging
from datetime import datetime
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
        self.wfile.write(b"REAL VIP V3 BOT is running!")

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
last_predicted_nums = []
prediction_sent_for_period = {}
last_result_sent = False

# ============================================================
#  🧠 REAL VIP V3 NEURAL LOGIC
# ============================================================
def get_neural_analysis(data):
    """
    REAL VIP V3 · NEURAL ANALYZER
    - Anti-Dragon
    - 1-1 Mirror
    - 2-2 Twin
    - Majority
    """
    if len(data) < 10:
        return {"pred": "BIG", "conf": "STABILIZING", "nums": [5, 7], "reason": "INSUFFICIENT DATA"}
    
    # শেষ ১০টি রেজাল্ট
    results = []
    for d in data[:10]:
        num = d['number']
        results.append({
            "num": num,
            "size": "BIG" if num >= 5 else "SMALL"
        })
    
    sizes = [r["size"] for r in results]
    
    # ── ১. Dragon Count (টানা একই দিক) ──
    dragon = 1
    for i in range(len(sizes) - 1):
        if sizes[i] == sizes[i+1]:
            dragon += 1
        else:
            break
    
    pred = ""
    conf = ""
    reason = ""
    
    # ── ২. Anti-Dragon Logic (dragon >= 4) ──
    if dragon >= 4:
        pred = "SMALL" if sizes[0] == "BIG" else "BIG"
        conf = "ULTRA 🔥 (BREAK)"
        reason = f"ANTI-DRAGON ({dragon}টি টানা {sizes[0]})"
    
    # ── ৩. 1-1 Mirror Logic ──
    elif sizes[0] != sizes[1] and sizes[1] != sizes[2]:
        pred = "SMALL" if sizes[0] == "BIG" else "BIG"
        conf = "EXTREME 🚀 (MIRROR)"
        reason = f"1-1 MIRROR ({sizes[0]}-{sizes[1]}-{sizes[2]})"
    
    # ── ৪. 2-2 Twin Logic ──
    elif sizes[0] == sizes[1] and sizes[2] == sizes[3]:
        pred = "SMALL" if sizes[0] == "BIG" else "BIG"
        conf = "HIGH ⚡ (TWIN)"
        reason = f"2-2 TWIN ({sizes[0]}{sizes[1]}-{sizes[2]}{sizes[3]})"
    
    # ── ৫. Majority Logic (Fallback) ──
    else:
        bigs = sizes[:6].count("BIG")
        pred = "BIG" if bigs >= 3 else "SMALL"
        conf = "NORMAL ⚡"
        reason = f"MAJORITY (শেষ ৬টিতে {bigs}B-{6-bigs}S)"
    
    # ── ৬. Smart Number Selection ──
    # সাম্প্রতিক ৮টি নম্বর বাদ দিয়ে বাকি পুল থেকে নম্বর নেয়
    recent_nums = set(r["num"] for r in results[:8])
    pool = [5, 6, 7, 8, 9] if pred == "BIG" else [0, 1, 2, 3, 4]
    smart_nums = [n for n in pool if n not in recent_nums]
    
    if len(smart_nums) < 2:
        smart_nums = random.sample(pool, 2)
    else:
        smart_nums = random.sample(smart_nums, 2)
    
    smart_nums = sorted(smart_nums)
    
    return {
        "pred": pred,
        "conf": conf,
        "nums": smart_nums,
        "reason": reason,
        "dragon": dragon
    }

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
        f"📊 *আওয়ারলি রিপোর্ট - REAL VIP V3*\n"
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
    global last_predicted_nums, prediction_sent_for_period
    global last_result_sent

    logger.info("🔥 REAL VIP V3 NEURAL ANALYZER বট স্টার্ট...")

    await send_message(
        "🔥 *REAL VIP V3 · NEURAL ANALYZER* 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🧠 *Neural Logic:*\n"
        "1️⃣ Anti-Dragon (টানা ৪+)\n"
        "2️⃣ 1-1 Mirror\n"
        "3️⃣ 2-2 Twin\n"
        "4️⃣ Majority\n"
        "🎯 *Smart Number:* Hot number বাদ\n"
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
                logger.warning("⚠️ ডেটা নেই, রিট্রাই...")
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
                is_jackpot = actual_num in last_predicted_nums
                
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
                    jackpot_text = " 🎰 JACKPOT!" if is_jackpot else ""
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
                    jackpot_text = ""

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
                    f"🔮 প্রেডিকশন: `{last_predicted_signal}`\n"
                    f"🎯 টার্গেট: `{', '.join(map(str, last_predicted_nums))}`\n"
                    f"🎰 একচুয়াল: `{actual_num}` → `{actual_type}`\n"
                    f"📌 রেজাল্ট: `{status}{jackpot_text}`\n"
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
                
                # 🔥 REAL VIP V3 NEURAL ANALYSIS
                analysis = get_neural_analysis(history_data)
                
                pred = analysis['pred']
                nums = analysis['nums']
                conf = analysis['conf']
                reason = analysis['reason']
                
                multiplier = f"{current_level}x"
                streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"
                
                prediction_msg = (
                    f"🔥 *REAL VIP V3 · NEURAL ANALYZER* 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 পিরিয়ড: `#{next_period[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 প্রেডিকশন: `{pred}`\n"
                    f"🔢 টার্গেট নম্বর: `{', '.join(map(str, nums))}`\n"
                    f"⚡ কনফিডেন্স: `{conf}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 ইঞ্জিন: {reason}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎰 JACKPOT: `{', '.join(map(str, nums))}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👑 লেভেল: `{current_level}` ({multiplier})\n"
                    f"{streak_emoji} স্ট্রিক: `{current_streak:+d}`\n"
                    f"❌ টানা লস: `{consecutive_losses}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ রেজাল্টের জন্য অপেক্ষা...\n"
                    f"🤖 @rakiiibahmed"
                )

                last_predicted_period = next_period
                last_predicted_signal = pred
                last_predicted_nums = nums
                prediction_sent_for_period[next_period] = True
                last_result_sent = False

                await send_message(prediction_msg)
                logger.info(f"✅ প্রেডিকশন: {next_period} → {pred} ({reason})")

                if len(prediction_sent_for_period) > 5:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            logger.error(f"❌ Loop Error: {e}")
            await asyncio.sleep(5)

# ==================== 🚀 স্টার্ট ====================
if __name__ == '__main__':
    print("🔥 REAL VIP V3 · NEURAL ANALYZER")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 Neural Logic:")
    print("  1. Anti-Dragon (4+ streak)")
    print("  2. 1-1 Mirror")
    print("  3. 2-2 Twin")
    print("  4. Majority")
    print("🎯 Smart Number Selection")
    print("📡 MODE: 3M WINGO")
    print("🤖 BOT: @rakiiibahmed")
    print("━━━━━━━━━━━━━━━━━━━━")
    
    try:
        asyncio.run(prediction_bot())
    except KeyboardInterrupt:
        print("\n👋 বট বন্ধ করা হয়েছে")
    except Exception as e:
        print(f"❌ ফাটাল এরর: {e}")