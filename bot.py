import asyncio
import time
import requests
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Bot

# ==================== RENDER FREE WEB SERVICE PORT BINDING ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ==================== BOT CONFIGURATION ====================
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"  
CHAT_ID = "5012028880"  
SCRAPER_API_KEY = "809f9c620ed6b5fe5a72bc368e8eabee"

# 1 MINUTE WINGO API
RAW_API = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts="

bot = Bot(token=BOT_TOKEN)

total_wins = 0
total_losses = 0
total_jackpots = 0
loss_streak = 0

last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None

# ==================== WEB ENGINES ====================

def generate_numbers(side, history_list):
    freq = [0] * 10
    for x in history_list:
        freq[x['number']] += 1
    
    big_pool = [5, 6, 7, 8, 9]
    small_pool = [0, 1, 2, 3, 4]

    big_pool.sort(key=lambda x: freq[x])
    small_pool.sort(key=lambda x: freq[x])

    return big_pool[0] if side == "BIG" else small_pool[0]

def compute_rifu(data):
    if not data: return {"side": "BIG", "confidence": 76}
    sides = [x['side'] for x in data]
    last = sides[0]
    streak = sum(1 for s in sides if s == last)
    if streak >= 5: return {"side": last, "confidence": 90}
    return {"side": "BIG" if last == "SMALL" else "SMALL", "confidence": 76}

def compute_smart(data):
    if len(data) < 4: return {"side": "SMALL", "confidence": 75}
    sides = [x['side'] for x in data[:4]]
    if sides[0] == sides[3] and sides[1] == sides[2]:
        return {"side": "SMALL" if sides[0] == "BIG" else "BIG", "confidence": 85}
    return {"side": "SMALL", "confidence": 75}

def compute_hybrid(data):
    if len(data) < 5: return {"side": "BIG", "confidence": 73}
    math_num = (data[0]['number'] + data[1]['number']) % 10
    return {"side": "BIG" if math_num >= 5 else "SMALL", "confidence": 73}

def compute_master(data):
    if len(data) < 8: return {"side": "SMALL", "confidence": 68}
    score = sum((1 if x['number'] >= 5 else -1) for x in data[:5])
    pred = "BIG" if score >= 0 else "SMALL"
    return {"side": pred, "confidence": 68}

def compute_advanced(data):
    if len(data) < 8: return {"side": "SMALL", "confidence": 85}
    weights = [9, 7, 5, 3, 2, 1, 1, 1]
    score = sum((1 if data[i]['side'] == "BIG" else -1) * weights[i] for i in range(min(len(data), 8)))
    pred = "BIG" if score >= 0 else "SMALL"
    return {"side": pred, "confidence": 85}

def compute_ultimate(data):
    if len(data) < 8: return {"side": "BIG", "confidence": 78}
    recent_bigs = sum(1 for x in data[:5] if x['side'] == "BIG")
    pred = "BIG" if recent_bigs >= 3 else "SMALL"
    return {"side": pred, "confidence": 78}

# ─── PREDICTION SYSTEM (MAJORITY VOTE + % TIE-BREAKER) ───
def predict_hybrid_engine(history_list):
    if not history_list:
        return "BIG", 9, 75, "MAJORITY VOTE"

    mapped = []
    for item in history_list[:12]:
        num = int(item['number'])
        mapped.append({
            'issueNumber': str(item['issueNumber']),
            'number': num,
            'side': "BIG" if num >= 5 else "SMALL"
        })

    # ৬টি ইঞ্জিনের আউটপুট গণনা
    engines = [
        compute_rifu(mapped),
        compute_smart(mapped),
        compute_hybrid(mapped),
        compute_master(mapped),
        compute_advanced(mapped),
        compute_ultimate(mapped)
    ]

    big_votes = 0
    small_votes = 0
    big_conf_sum = 0
    small_conf_sum = 0

    for eng in engines:
        if eng['side'] == "BIG":
            big_votes += 1
            big_conf_sum += eng['confidence']
        else:
            small_votes += 1
            small_conf_sum += eng['confidence']

    # ১. মেজোরিটি ভোট ফিল্টার
    if big_votes > small_votes:
        final_side = "BIG"
        avg_confidence = round(big_conf_sum / big_votes)
    elif small_votes > big_votes:
        final_side = "SMALL"
        avg_confidence = round(small_conf_sum / small_votes)
    else:
        # ২. টাই-ব্রেকার (৩টি BIG এবং ৩টি SMALL হলে মোট % হিসাব)
        if big_conf_sum >= small_conf_sum:
            final_side = "BIG"
            avg_confidence = round(big_conf_sum / 3)
        else:
            final_side = "SMALL"
            avg_confidence = round(small_conf_sum / 3)

    suggested_num = generate_numbers(final_side, mapped)

    return final_side, suggested_num, avg_confidence, "MAJORITY VOTE"

# ==================== API FETCHING ====================

def fetch_api_data():
    timestamp = str(int(time.time() * 1000))
    raw_url = RAW_API + timestamp
    try:
        res = requests.get(raw_url, timeout=4)
        if res.status_code == 200:
            data = res.json()
            list_data = data.get("data", {}).get("list", [])
            if list_data:
                return list_data
    except Exception:
        pass

    try:
        proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={requests.utils.quote(raw_url)}"
        res = requests.get(proxy_url, timeout=8)
        if res.status_code == 200:
            data = res.json()
            list_data = data.get("data", {}).get("list", [])
            if list_data:
                return list_data
    except Exception as e:
        print("API Fetch Error:", e)

    return []

# ==================== MAIN BOT LOOP ====================

async def prediction_bot():
    global last_predicted_period, last_predicted_signal, last_predicted_num
    global total_wins, total_losses, total_jackpots, loss_streak

    print("🔥 HYBRID HACKED PRO 1M (MAJORITY VOTE) BOT STARTED...")

    while True:
        try:
            current_sec = int(time.time()) % 60
            sleep_time = 60 - current_sec + 2  
            await asyncio.sleep(sleep_time)

            history = fetch_api_data()
            if not history:
                continue

            latest_issue = str(history[0]['issueNumber'])
            actual_num = int(history[0]['number'])
            actual_bs = "BIG" if actual_num >= 5 else "SMALL"

            # ১. রেজাল্ট এবং জ্যাকপট ট্র্যাকিং
            if last_predicted_period == latest_issue and last_predicted_signal:
                is_side_win = (last_predicted_signal == actual_bs)
                is_exact_num = (last_predicted_num == actual_num)

                if is_side_win:
                    total_wins += 1
                    loss_streak = 0
                    if is_exact_num:
                        total_jackpots += 1
                        status_str = "⭐ JACKPOT!"
                    else:
                        status_str = "🟢 WIN!"
                else:
                    total_losses += 1
                    loss_streak += 1
                    status_str = "🔴 LOSS!"

                total_games = total_wins + total_losses
                win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0

                result_msg = (
                    f"🎯 *RESULT UPDATE*\n"
                    f"🆔 *Period:* `{latest_issue[-5:]}`\n"
                    f"🎰 *Actual Number:* `{actual_num}` ({actual_bs})\n"
                    f"📌 *Result:* *{status_str}*\n"
                    f"📊 *Win Rate:* `{win_rate:.1f}%` ({total_wins}W / {total_losses}L)\n"
                    f"⭐ *Jackpots:* `{total_jackpots}`"
                )
                await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                await asyncio.sleep(1)

            # ২. মেজোরিটি ভোট প্রেডিকশন
            signal, pred_num, conf, engine_used = predict_hybrid_engine(history)
            next_period = str(int(latest_issue) + 1)

            prediction_msg = (
                f"🔥 *HYBRID HACKED PRO 1M*\n"
                f"⏱️ *Mode:* 1 Min Wingo\n"
                f"🆔 *Period:* `{next_period[-5:]}`\n"
                f"🔮 *Prediction:* `{signal}` (Num: `{pred_num}`)\n"
                f"⚡ *Confidence:* `{conf}%`\n"
                f"🧠 *Engine:* `{engine_used}`\n"
                f"⏳ *Status:* Result Awaiting..."
            )

            last_predicted_period = next_period
            last_predicted_signal = signal
            last_predicted_num = pred_num

            await bot.send_message(chat_id=CHAT_ID, text=prediction_msg, parse_mode="Markdown")

        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(2)

if __name__ == '__main__':
    asyncio.run(prediction_bot())
