#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 PATTERN MATCHER V2 - 1 MIN WINGO
📊 PDF 1 (Pattern) + PDF 2 (Trap + Level)
🤖 @rakiiibahmed
"""

import asyncio
import time
import requests
import os
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

# ✅ 1 MIN WINGO API
API_URLS = [
    "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json",
    "https://api.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json",
]

# ==================== 🌐 ওয়েব সার্ভার ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"PATTERN MATCHER V2 - 1M is running!")

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

hourly_wins = 0
hourly_losses = 0
hourly_rounds = 0
hourly_best_win_streak = 0
hourly_worst_loss_streak = 0

# Level System (PDF 2)
current_level = 1
consecutive_losses = 0
break_until_period = None

last_predicted_period = None
last_predicted_signal = None
last_trap_detected = None
prediction_sent_for_period = {}
last_result_sent = False

# ============================================================
#  📚 PATTERN DATABASE (PDF 1)
# ============================================================
PATTERNS_5 = {
    "SSBSS": "S", "BBSBS": "S", "SBBBS": "B", "BSBBB": "S",
    "BBBBS": "B", "BBBSB": "B", "SSBSB": "B",
    "SBSBS": "B", "SBSBB": "B", "SSSBB": "B", "BSSBS": "S",
    "SBBSB": "S", "BSBSB": "S", "SBSSB": "S",
    "BSSSB": "S", "BBSBB": "B", "SBBBB": "B",
    "SBSSBB": "B", "BBSSSB": "B", "BSSBSB": "S",
}

PATTERNS_6 = {
    "BSBBSS": "S", "BSBSSS": "S", "SSSBBB": "B", "SSSBBS": "B",
    "SSBBBS": "B", "BSBSSB": "S", "BSSSBS": "B", "SSSSSS": "B",
    "SSSSSB": "B", "BBSBSB": "S", "BBBBSB": "S", "SBBBBB": "S",
    "SBBBBS": "S", "BBSBBB": "S", "BSBSBB": "S", "SSSSBS": "B",
    "SSBBSB": "B", "SBSSSB": "B", "BSBBBS": "S", "SSSBSB": "B",
}

PATTERNS_7 = {
    "SSBBBS": "B", "BSSSSB": "S", "BSSSBB": "S", "SBBBBS": "S",
    "SSSBBB": "B", "BSSBBB": "S", "SSSSBB": "B", "SSSSSSB": "B",
    "SSSSSB": "B", "BSBSBSB": "S", "BSSBSBS": "S",
    "SBSBSB": "B", "BSBSBSS": "B", "SSSBSB": "B", "BBSBSB": "S",
    "BBSBSBS": "B", "SBSBSBS": "S", "BSSBSBS": "B", "SSSSSSS": "B",
    "BBBBBBS": "S", "SBBBBBB": "S", "BSBBBSB": "S",
    "SSSBBSB": "B", "BBSBBBS": "S",
}

# ============================================================
#  🎯 PDF 2: TRAP DATABASE
# ============================================================
TRAP_PATTERNS = {
    "BBBB": "S", "SSSS": "B",
    "BSBS": "S", "SBSB": "B",
    "BBSS": "S", "SSBB": "B",
    "BSSB": "S", "SBBS": "B",
    "BSBB": "S", "SBSS": "B",
    "BBSB": "S", "SSBS": "B",
    "BBBS": "S", "SSSB": "B",
    "BSSS": "B", "SBBB": "S",
}

# ============================================================
#  🧠 PATTERN MATCHER (PDF 1)
# ============================================================
def pattern_matcher(sides):
    if len(sides) < 5:
        return {"prediction": "BIG", "confidence": 50, "reason": "INSUFFICIENT DATA", "pattern": None}
    
    # 7-digit
    if len(sides) >= 7:
        p7 = ''.join(sides[:7])
        if p7 in PATTERNS_7:
            pred = "BIG" if PATTERNS_7[p7] == "B" else "SMALL"
            return {"prediction": pred, "confidence": 80, "reason": f"7-DIGIT ({p7})", "pattern": p7}
    
    # 6-digit
    if len(sides) >= 6:
        p6 = ''.join(sides[:6])
        if p6 in PATTERNS_6:
            pred = "BIG" if PATTERNS_6[p6] == "B" else "SMALL"
            return {"prediction": pred, "confidence": 75, "reason": f"6-DIGIT ({p6})", "pattern": p6}
    
    # 5-digit
    if len(sides) >= 5:
        p5 = ''.join(sides[:5])
        if p5 in PATTERNS_5:
            pred = "BIG" if PATTERNS_5[p5] == "B" else "SMALL"
            return {"prediction": pred, "confidence": 70, "reason": f"5-DIGIT ({p5})", "pattern": p5}
    
    # Fallback
    recent5 = sides[:5]
    b = recent5.count("B")
    s = recent5.count("S")
    pred = "BIG" if b >= s else "SMALL"
    return {"prediction": pred, "confidence": 55, "reason": f"MAJORITY ({b}B-{s}S)", "pattern": None}

# ============================================================
#  🧠 TRAP DETECTION (PDF 2)
# ============================================================
def detect_trap(sides):
    if len(sides) < 3:
        return None
    
    if len(sides) >= 4:
        p4 = ''.join(sides[:4])
        if p4 in TRAP_PATTERNS:
            trap_pred = TRAP_PATTERNS[p4]
            return {
                "trap_pattern": p4,
                "trap_prediction": "BIG" if trap_pred == "B" else "SMALL",
                "human_thinks": "BIG" if trap_pred == "S" else "SMALL"
            }
    
    p3 = ''.join(sides[:3])
    if p3 == "BBB":
        return {"trap_pattern": p3, "trap_prediction": "SMALL", "human_thinks": "BIG"}
    elif p3 == "SSS":
        return {"trap_pattern": p3, "trap_prediction": "BIG", "human_thinks": "SMALL"}
    
    return None

# ============================================================
#  🧠 LEVEL SYSTEM (PDF 2)
# ============================================================
def apply_level(prediction, level):
    if level == 1:
        return prediction, "Level 1"
    elif level == 2:
        flipped = "SMALL" if prediction == "BIG" else "BIG"
        return flipped, "Level 2 (Flipped)"
    else:
        return prediction, "Level 3"

# ============================================================
#  🔥 MASTER ENGINE (PDF 1 + PDF 2)
# ============================================================
def master_engine(sides, level):
    pattern_result = pattern_matcher(sides)
    base_pred = pattern_result['prediction']
    
    trap = detect_trap(sides)
    
    if trap:
        final_pred = trap['trap_prediction']
        engine_type = f"TRAP ({trap['trap_pattern']})"
        confidence = 78
    else:
        final_pred = base_pred
        engine_type = pattern_result['reason']
        confidence = pattern_result['confidence']
    
    leveled_pred, level_name = apply_level(final_pred, level)
    
    return {
        "prediction": leveled_pred,
        "base_prediction": final_pred,
        "confidence": confidence,
        "engine": engine_type,
        "pattern": pattern_result['pattern'],
        "trap": trap,
        "level": level,
        "level_name": level_name
    }

# ==================== 📡 API ফেচ ====================
def fetch_api_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.google.com/',
        'Cache-Control': 'no-cache',
    }
    
    for api_url in API_URLS:
        try:
            url = api_url + "?t=" + str(int(time.time() * 1000))
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                list_data = data.get("data", {}).get("list", [])
                if list_data:
                    return list_data
        except:
            continue
    return []

# ==================== 📤 মেসেজ সেন্ড ====================
async def send_message(text, parse_mode="Markdown"):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=parse_mode)
        return True
    except Exception as e:
        logger.error(f"❌ টেলিগ্রাম এরর: {e}")
        return False

# ==================== 📊 হাওয়ারলি রিপোর্ট ====================
async def send_hourly_report():
    global hourly_wins, hourly_losses, hourly_rounds
    global hourly_best_win_streak, hourly_worst_loss_streak
    global total_wins, total_losses, total_rounds
    global best_win_streak, worst_loss_streak
    
    if hourly_rounds == 0:
        return
    
    h_rate = (hourly_wins / hourly_rounds * 100) if hourly_rounds > 0 else 0
    t_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
    
    report = (
        f"📊 *আওয়ারলি রিপোর্ট - 1M WINGO*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 *সময়:* {datetime.now().strftime('%I:%M %p')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔄 *এই ঘন্টায় রাউন্ড:* `{hourly_rounds}`\n"
        f"✅ *জয়:* `{hourly_wins}` | ❌ *হার:* `{hourly_losses}`\n"
        f"📈 *জয়ের হার:* `{h_rate:.1f}%`\n"
        f"🔥 *সেরা জয় স্ট্রিক:* `{hourly_best_win_streak}x`\n"
        f"📉 *সেরা হার স্ট্রিক:* `{hourly_worst_loss_streak}x`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *মোট রাউন্ড:* `{total_rounds}`\n"
        f"✅ *মোট জয়:* `{total_wins}` | ❌ *মোট হার:* `{total_losses}`\n"
        f"📈 *মোট জয়ের হার:* `{t_rate:.1f}%`\n"
        f"🔥 *সেরা জয় স্ট্রিক:* `{best_win_streak}x`\n"
        f"📉 *সেরা হার স্ট্রিক:* `{worst_loss_streak}x`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 @rakiiibahmed"
    )
    
    await send_message(report)
    
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
    global current_level, consecutive_losses, break_until_period
    global last_predicted_period, last_predicted_signal
    global last_trap_detected, prediction_sent_for_period
    global last_result_sent

    logger.info("🔥 PATTERN MATCHER V2 - 1M WINGO স্টার্ট...")

    await send_message(
        "🔥 *PATTERN MATCHER V2 - 1M* 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📚 *PDF 1:* Pattern Matching\n"
        "🎯 *PDF 2:* Trap + Level System\n"
        "📡 *মোড:* 1 MIN WINGO\n"
        "🤖 *বট:* @rakiiibahmed\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⏳ প্রথম সিগন্যালের জন্য অপেক্ষা..."
    )

    last_hour_time = time.time()

    while True:
        try:
            # ✅ 1 মিনিট (60 সেকেন্ড) অপেক্ষা
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

            logger.info(f"📡 পিরিয়ড: {latest_issue}, নাম্বার: {actual_num} ({actual_type})")

            # ===== রেজাল্ট চেক =====
            if last_predicted_period == latest_issue and last_predicted_signal and not last_result_sent:
                is_win = (last_predicted_signal == actual_type)
                
                if is_win:
                    total_wins += 1
                    hourly_wins += 1
                    consecutive_losses = 0
                    current_level = 1
                    
                    if current_streak >= 0:
                        current_streak += 1
                    else:
                        current_streak = 1
                    
                    if current_streak > best_win_streak:
                        best_win_streak = current_streak
                    if current_streak > hourly_best_win_streak:
                        hourly_best_win_streak = current_streak
                    
                    status = "✅ জয় 🎉"
                    level_text = "→ Level 1 (Reset)"
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
                    
                    if current_level == 1:
                        current_level = 2
                        level_text = "→ Level 2"
                    elif current_level == 2:
                        current_level = 3
                        level_text = "→ Level 3"
                    else:
                        current_level = 1
                        consecutive_losses = 0
                        break_until_period = str(int(latest_issue) + 2)
                        level_text = "⚠️ Break (২ রাউন্ড)"
                    
                    status = "❌ হার"

                total_rounds += 1
                hourly_rounds += 1
                
                t_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
                streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"
                
                trap_info = ""
                if last_trap_detected:
                    trap_info = f"\n🎭 Trap: `{last_trap_detected['trap_pattern']}`"

                result_msg = (
                    f"🎯 *রেজাল্ট আপডেট*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 পিরিয়ড: `#{latest_issue[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔮 প্রেডিকশন: `{last_predicted_signal}`\n"
                    f"🎰 একচুয়াল: `{actual_num}` → `{actual_type}`\n"
                    f"📌 রেজাল্ট: `{status}`\n"
                    f"{trap_info}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 জয়ের হার: `{t_rate:.1f}%` ({total_wins}W/{total_losses}L)\n"
                    f"{streak_emoji} স্ট্রিক: `{current_streak:+d}`\n"
                    f"👑 লেভেল: `{current_level}` {level_text}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🤖 @rakiiibahmed"
                )

                await send_message(result_msg)
                last_result_sent = True

                if time.time() - last_hour_time >= 3600:
                    await send_hourly_report()
                    last_hour_time = time.time()

            # ===== নতুন প্রেডিকশন =====
            next_period = str(int(latest_issue) + 1)
            
            if break_until_period and next_period < break_until_period:
                logger.info(f"⏸️ Break: {next_period}")
                continue
            
            if not prediction_sent_for_period.get(next_period, False):
                
                sides = [d['side'][0] for d in history_data]
                result = master_engine(sides, current_level)
                
                last_trap_detected = result.get('trap')
                
                streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"
                
                if result['confidence'] >= 80:
                    rec = "🔥 হাই কনফিডেন্স"
                elif result['confidence'] >= 70:
                    rec = "⚡ মিডিয়াম কনফিডেন্স"
                else:
                    rec = "⚠️ লো কনফিডেন্স"

                trap_msg = ""
                if result.get('trap'):
                    trap_msg = (
                        f"\n🎭 *Trap Detected:*\n"
                        f"• প্যাটার্ন: `{result['trap']['trap_pattern']}`\n"
                        f"• মানুষ ভাবে: `{result['trap']['human_thinks']}`\n"
                        f"• আমরা দিচ্ছি: `{result['trap']['trap_prediction']}`\n"
                    )

                prediction_msg = (
                    f"🔥 *PATTERN MATCHER V2 - 1M* 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 পিরিয়ড: `#{next_period[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 প্রেডিকশন: `{result['prediction']}`\n"
                    f"⚡ কনফিডেন্স: `{result['confidence']}%`\n"
                    f"👑 লেভেল: `{current_level}` ({result['level_name']})\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 ইঞ্জিন: {result['engine']}\n"
                    f"📊 PDF 1 Pattern: `{result['pattern'] or 'None'}`\n"
                    f"{trap_msg}"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💡 রেকমেন্ডেশন:\n"
                    f"• {rec}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{streak_emoji} স্ট্রিক: `{current_streak:+d}`\n"
                    f"❌ টানা লস: `{consecutive_losses}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ রেজাল্টের জন্য অপেক্ষা...\n"
                    f"🤖 @rakiiibahmed"
                )

                last_predicted_period = next_period
                last_predicted_signal = result['prediction']
                prediction_sent_for_period[next_period] = True
                last_result_sent = False

                await send_message(prediction_msg)
                logger.info(f"✅ প্রেডিকশন: {next_period} → {result['prediction']} ({result['engine']})")

                if len(prediction_sent_for_period) > 10:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            logger.error(f"❌ Loop Error: {e}")
            await asyncio.sleep(5)

# ==================== 🚀 স্টার্ট ====================
if __name__ == '__main__':
    print("🔥 PATTERN MATCHER V2 - 1 MIN WINGO")
    print("━━━━━━━━━━━━━━━━━━━━")
    print(f"📚 PDF 1 Pattern: {len(PATTERNS_5)}+{len(PATTERNS_6)}+{len(PATTERNS_7)}")
    print(f"🎯 PDF 2 Trap: {len(TRAP_PATTERNS)}")
    print("📡 MODE: 1 MIN WINGO")
    print("🤖 BOT: @rakiiibahmed")
    print("━━━━━━━━━━━━━━━━━━━━")
    
    try:
        asyncio.run(prediction_bot())
    except KeyboardInterrupt:
        print("\n👋 বট বন্ধ করা হয়েছে")
    except Exception as e:
        print(f"❌ ফাটাল এরর: {e}")