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
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

# ==================== ওয়েব সার্ভার ====================
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
# মোট স্ট্যাটস
total_wins = 0
total_losses = 0
loss_streak = 0
current_level = 1
total_rounds = 0

# DARK X আলাদা স্ট্যাটস
dark_x_wins = 0
dark_x_losses = 0
dark_x_total = 0

# RGB HACK আলাদা স্ট্যাটস
rgb_wins = 0
rgb_losses = 0
rgb_total = 0

# NO MATCH স্ট্যাটস
no_match_count = 0
no_match_wins = 0
no_match_losses = 0

history_data = []

last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
last_match_status = None  # 'match' or 'no_match'
prediction_sent_for_period = {}

# ==================== আওয়ারলি স্ট্যাটস ====================
hourly_stats = {
    'total_rounds': 0,
    'total_wins': 0,
    'total_losses': 0,
    'dark_x_wins': 0,
    'dark_x_losses': 0,
    'rgb_wins': 0,
    'rgb_losses': 0,
    'no_match_count': 0,
    'no_match_wins': 0,
    'no_match_losses': 0,
    'max_win_streak': 0,
    'max_loss_streak': 0,
    'current_streak': 0,
    'streak_type': 'WIN'
}
last_hour_report_time = time.time()

# ============================================================
#  DARK X ENGINE
# ============================================================
def dark_x_engine(data, level):
    if len(data) < 3:
        return {"prediction": "BIG", "confidence": 50, "number": 7}
    
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
    
    if level == 3 and len(data) > 0:
        latest_num = data[0]['number']
        pred = "SMALL" if latest_num >= 5 else "BIG"
        conf = 99
    
    if pred == "BIG":
        num = random.randint(5, 9)
    else:
        num = random.randint(0, 4)
    
    return {"prediction": pred, "confidence": conf, "number": num}

# ============================================================
#  RGB HACK ENGINE
# ============================================================
def get_correct_period_index():
    now = datetime.now(timezone.utc)
    midnight = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
    diff_seconds = (now - midnight).total_seconds()
    period_index = int(diff_seconds // 60) + 1
    return period_index

def rgb_hack_engine():
    PATTERN = [
        {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 2}, {"s": "SMALL", "n": 4},
        {"s": "BIG", "n": 9}, {"s": "BIG", "n": 6}, {"s": "SMALL", "n": 0},
        {"s": "BIG", "n": 8}, {"s": "SMALL", "n": 3}, {"s": "SMALL", "n": 1},
        {"s": "BIG", "n": 5}, {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 4}
    ]
    
    period_index = get_correct_period_index()
    pattern_index = (period_index + 5) % 12
    
    pred = PATTERN[pattern_index]
    return {"prediction": pred["s"], "confidence": 78, "number": pred["n"]}

# ============================================================
#  MASTER MATCHING SYSTEM
# ============================================================
def master_matching_system(data, period_str, level):
    dark = dark_x_engine(data, level)
    rgb = rgb_hack_engine()
    
    if dark['prediction'] == rgb['prediction']:
        final_pred = dark['prediction']
        final_num = dark['number']
        final_conf = int((dark['confidence'] + rgb['confidence']) / 2)
        matched = True
        status = "✅ MATCH FOUND"
        icon = "🟢"
    else:
        # NO MATCH হলেও DARK X-এর প্রেডিকশন পাঠাবে
        final_pred = dark['prediction']
        final_num = dark['number']
        final_conf = dark['confidence']
        matched = False
        status = "❌ NO MATCH"
        icon = "🔴"
    
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

# ==================== API ফেচ ====================
def fetch_api_data():
    try:
        res = requests.get(API_URL + "?t=" + str(int(time.time() * 1000)), timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", {}).get("list", [])
    except:
        pass
    return []

# ==================== আওয়ারলি রিপোর্ট ====================
async def send_hourly_report():
    global hourly_stats, last_hour_report_time

    if time.time() - last_hour_report_time >= 3600:
        total = hourly_stats['total_rounds']
        wins = hourly_stats['total_wins']
        losses = hourly_stats['total_losses']
        win_rate = (wins / total * 100) if total > 0 else 0
        
        dark_win_rate = (hourly_stats['dark_x_wins'] / (hourly_stats['dark_x_wins'] + hourly_stats['dark_x_losses']) * 100) if (hourly_stats['dark_x_wins'] + hourly_stats['dark_x_losses']) > 0 else 0
        rgb_win_rate = (hourly_stats['rgb_wins'] / (hourly_stats['rgb_wins'] + hourly_stats['rgb_losses']) * 100) if (hourly_stats['rgb_wins'] + hourly_stats['rgb_losses']) > 0 else 0
        no_match_win_rate = (hourly_stats['no_match_wins'] / (hourly_stats['no_match_wins'] + hourly_stats['no_match_losses']) * 100) if (hourly_stats['no_match_wins'] + hourly_stats['no_match_losses']) > 0 else 0

        report_msg = (
            f"📊 *HOURLY PERFORMANCE REPORT*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🕐 *TIME:* {datetime.now().strftime('%I:%M %p')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔄 *TOTAL ROUNDS:* `{total}`\n"
            f"✅ *TOTAL WINS:* `{wins}`\n"
            f"❌ *TOTAL LOSSES:* `{losses}`\n"
            f"📈 *TOTAL WIN RATE:* `{win_rate:.1f}%`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🧠 *DARK X:* {hourly_stats['dark_x_wins']}W/{hourly_stats['dark_x_losses']}L ({dark_win_rate:.1f}%)\n"
            f"🧠 *RGB HACK:* {hourly_stats['rgb_wins']}W/{hourly_stats['rgb_losses']}L ({rgb_win_rate:.1f}%)\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ *NO MATCH:* {hourly_stats['no_match_count']} rounds\n"
            f"   → {hourly_stats['no_match_wins']}W/{hourly_stats['no_match_losses']}L ({no_match_win_rate:.1f}%)\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 *BEST WIN STREAK:* `{hourly_stats['max_win_streak']}x`\n"
            f"📉 *WORST LOSS STREAK:* `{hourly_stats['max_loss_streak']}x`\n"
            f"🔥 *CURRENT STREAK:* `{hourly_stats['current_streak']}x {hourly_stats['streak_type']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 RGB MATCHING 1MIN VIP"
        )
        try:
            await bot.send_message(chat_id=CHAT_ID, text=report_msg, parse_mode="Markdown")
        except:
            pass

        hourly_stats = {
            'total_rounds': 0,
            'total_wins': 0,
            'total_losses': 0,
            'dark_x_wins': 0,
            'dark_x_losses': 0,
            'rgb_wins': 0,
            'rgb_losses': 0,
            'no_match_count': 0,
            'no_match_wins': 0,
            'no_match_losses': 0,
            'max_win_streak': 0,
            'max_loss_streak': 0,
            'current_streak': 0,
            'streak_type': 'WIN'
        }
        last_hour_report_time = time.time()

# ==================== মেইন লুপ ====================
async def prediction_bot():
    global total_wins, total_losses, loss_streak, current_level
    global total_rounds, history_data, last_predicted_period
    global last_predicted_signal, last_predicted_num, last_match_status
    global dark_x_wins, dark_x_losses, dark_x_total
    global rgb_wins, rgb_losses, rgb_total
    global no_match_count, no_match_wins, no_match_losses
    global prediction_sent_for_period

    print("🔥 RGB MATCHING 1MIN VIP BOT STARTED...")
    print("📡 MODE: 1 MIN WINGO")
    print("🧠 ENGINES: DARK X + RGB HACK")
    print("✅ MATCH FOUND = SEND | ❌ NO MATCH = ALSO SEND")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                "🔥 RGB MATCHING 1MIN VIP 🔥\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🧠 ENGINES: DARK X + RGB HACK\n"
                "✅ MATCH FOUND = SEND PREDICTION\n"
                "❌ NO MATCH = ALSO SEND PREDICTION\n"
                "📡 MODE: 1 MIN WINGO\n"
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

            print(f"📡 LATEST PERIOD: {latest_issue}, NUMBER: {actual_num}")

            # ===== RESULT CHECK =====
            if last_predicted_period == latest_issue and last_predicted_signal is not None:
                is_win = (last_predicted_signal == actual_type)
                is_jackpot = (actual_num == 0 or actual_num == 5)
                
                # DARK X result
                dark_win = (dark_x_engine(history_data, current_level)['prediction'] == actual_type)
                # RGB result
                rgb_win = (rgb_hack_engine()['prediction'] == actual_type)

                if is_win or is_jackpot:
                    total_wins += 1
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
                    total_losses += 1
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

                total_rounds += 1
                hourly_stats['total_rounds'] += 1
                
                # DARK X আলাদা স্ট্যাটস
                if dark_win:
                    dark_x_wins += 1
                    hourly_stats['dark_x_wins'] += 1
                else:
                    dark_x_losses += 1
                    hourly_stats['dark_x_losses'] += 1
                dark_x_total += 1
                
                # RGB HACK আলাদা স্ট্যাটস
                if rgb_win:
                    rgb_wins += 1
                    hourly_stats['rgb_wins'] += 1
                else:
                    rgb_losses += 1
                    hourly_stats['rgb_losses'] += 1
                rgb_total += 1
                
                # NO MATCH স্ট্যাটস
                if last_match_status == 'no_match':
                    no_match_count += 1
                    hourly_stats['no_match_count'] += 1
                    if is_win or is_jackpot:
                        no_match_wins += 1
                        hourly_stats['no_match_wins'] += 1
                    else:
                        no_match_losses += 1
                        hourly_stats['no_match_losses'] += 1

                total_games = total_wins + total_losses
                win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0
                multiplier = f"{current_level}x"
                streak_emoji = "🔥" if loss_streak > 0 else "📉" if loss_streak < 0 else "⏸️"
                
                match_status_text = "✅ MATCH" if last_match_status == 'match' else "❌ NO MATCH"

                result_msg = (
                    f"🎯 RESULT UPDATE\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: #{latest_issue[-5:]}\n"
                    f"📌 MATCH STATUS: {match_status_text}\n"
                    f"🎯 PREDICTED: {last_predicted_signal} → {last_predicted_num}\n"
                    f"🎰 ACTUAL: {actual_num} ({actual_type})\n"
                    f"📌 RESULT: {status}{jackpot_text}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 DARK X: {'✅' if dark_win else '❌'} → {dark_x_wins}W/{dark_x_losses}L\n"
                    f"🧠 RGB HACK: {'✅' if rgb_win else '❌'} → {rgb_wins}W/{rgb_losses}L\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 WIN RATE: {win_rate:.1f}% ({total_wins}W/{total_losses}L)\n"
                    f"{streak_emoji} STREAK: {loss_streak:+d}\n"
                    f"👑 LEVEL: {current_level} ({multiplier})\n"
                    f"❌ NO MATCH: {no_match_count} rounds\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
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
                last_match_status = None

            # ===== NEW PREDICTION =====
            next_period = str(int(latest_issue) + 1)
            print(f"🎯 NEXT PERIOD: {next_period}")

            if not prediction_sent_for_period.get(next_period, False):
                pred = master_matching_system(history_data, next_period, current_level)
                
                # ম্যাচ স্ট্যাটাস সেভ করুন
                last_match_status = 'match' if pred['matched'] else 'no_match'
                
                multiplier = f"{current_level}x"
                streak_emoji = "🔥" if loss_streak > 0 else "📉" if loss_streak < 0 else "⏸️"
                
                match_text = "✅ MATCH FOUND!" if pred['matched'] else "❌ NO MATCH (DARK X PRIORITY)"
                
                prediction_msg = (
                    f"🔥 RGB MATCHING 1MIN VIP 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: #{next_period[-5:]}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{match_text}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 PREDICTION: {pred['prediction']}\n"
                    f"🔢 TARGET NUMBER: {pred['number']}\n"
                    f"⚡ CONFIDENCE: {pred['confidence']}%\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 DARK X: {pred['dark']['prediction']} ({pred['dark']['number']}) {pred['dark']['confidence']}%\n"
                    f"🧠 RGB HACK: {pred['rgb']['prediction']} ({pred['rgb']['number']}) {pred['rgb']['confidence']}%\n"
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
                    print(f"✅ PREDICTION SENT: {next_period} → {pred['prediction']} ({'MATCH' if pred['matched'] else 'NO MATCH'})")
                except Exception as e:
                    print(f"❌ SEND FAILED: {e}")

                if len(prediction_sent_for_period) > 5:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            print(f"❌ Loop Error: {e}")
            await asyncio.sleep(5)

# ==================== স্টার্ট ====================
if __name__ == '__main__':
    print("🔥 RGB MATCHING 1MIN VIP BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 ENGINES: DARK X + RGB HACK")
    print("✅ MATCH FOUND = SEND PREDICTION")
    print("❌ NO MATCH = ALSO SEND PREDICTION")
    print("📡 MODE: 1 MIN WINGO")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
