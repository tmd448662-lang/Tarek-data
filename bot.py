import asyncio
import time
import requests
import os
from datetime import datetime, timezone
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

# 1 MINUTE WINGO API ONLY
RAW_API = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts="

bot = Bot(token=BOT_TOKEN)

# ট্র্যাকিং ভ্যারিয়েবল (জ্যাকপট আলাদা না রেখে শুধু Win ও Loss রাখা হয়েছে)
total_wins = 0
total_losses = 0
loss_streak = 0

last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None

# ==================== EXACT HTML / JS ENGINES IN PYTHON ====================

def generate_numbers(side, history_list):
    freq = [0] * 10
    for x in history_list:
        freq[x['number']] += 1
    
    big_pool = [5, 6, 7, 8, 9]
    small_pool = [0, 1, 2, 3, 4]

    big_pool.sort(key=lambda x: freq[x])
    small_pool.sort(key=lambda x: freq[x])

    numB = big_pool[0]
    numS = small_pool[0]

    return numB, numS

# 1. CORE (Rifu Pattern)
def compute_rifu(data):
    if not data:
        return {"side": "BIG", "confidence": 70, "logic": "INIT"}
    sides = [x['side'] for x in data]
    last = sides[0]

    streak = 0
    for s in sides:
        if s == last: streak += 1
        else: break
    
    if streak >= 5:
        return {"side": last, "confidence": 90, "logic": "5+ STREAK"}

    if len(sides) >= 3:
        if sides[2] == "BIG" and sides[1] == "SMALL" and sides[0] == "BIG":
            return {"side": "BIG", "confidence": 84, "logic": "3P-PATTERN"}
        elif sides[2] == "SMALL" and sides[1] == "BIG" and sides[0] == "SMALL":
            return {"side": "SMALL", "confidence": 84, "logic": "3P-PATTERN"}

    big_count = sum(1 for s in sides[:5] if s == "BIG")
    if big_count >= 4:
        return {"side": "SMALL", "confidence": 76, "logic": "REVERSAL"}
    elif big_count <= 1:
        return {"side": "BIG", "confidence": 76, "logic": "REVERSAL"}

    return {"side": "SMALL" if last == "BIG" else "BIG", "confidence": 72, "logic": "TREND"}

# 2. SMART (Symmetry + Gap)
def compute_smart(data):
    if len(data) < 4:
        return {"side": "BIG", "confidence": 45, "reason": "CALIBRATING"}
    sides = [x['side'] for x in data[:4]]
    if sides[0] == sides[3] and sides[1] == sides[2]:
        p = "SMALL" if sides[0] == "BIG" else "BIG"
        return {"side": p, "confidence": 92, "reason": "SYMMETRY"}
    if all(x == sides[0] for x in sides):
        return {"side": sides[0], "confidence": 85, "reason": "BOUNCE-TRAP"}

    nums = [x['number'] for x in data[:15]]
    missing = next((n for n in range(10) if n not in nums), None)
    if missing is not None:
        return {"side": "BIG" if missing >= 5 else "SMALL", "confidence": 75, "reason": "GAP"}

    return {"side": "BIG", "confidence": 60, "reason": "FREQUENCY"}

# 3. HYBRID
def compute_hybrid(data):
    if len(data) < 5:
        return {"side": "BIG", "confidence": 50, "reason": "CALIBRATING"}
    math_num = (data[0]['number'] + data[1]['number']) % 10
    period_mod = int(data[0]['issueNumber'] or "0") % 3
    
    if period_mod == 1:
        pred = "BIG" if math_num >= 5 else "SMALL"
        reason = "MATH-SEQ"
    else:
        pred = "SMALL" if data[0]['side'] == "BIG" else "BIG"
        reason = "TREND-REV"

    return {"side": pred, "confidence": 75, "reason": reason}

# 4. MASTER
def compute_master(data):
    if len(data) < 10:
        return {"side": "BIG", "confidence": 50, "reason": "INIT"}
    votes = {"BIG": 0, "SMALL": 0}
    sides = [x['side'] for x in data[:4]]
    if sides[0] == sides[3] and sides[1] == sides[2]:
        votes["SMALL" if sides[0] == "BIG" else "BIG"] += 3

    trend_score = sum((1 if x['number'] >= 5 else -1) * (8 - i) for i, x in enumerate(data[:8]))
    votes["BIG" if trend_score > 0 else "SMALL"] += 2

    pred = "BIG" if votes["BIG"] >= votes["SMALL"] else "SMALL"
    conf = min(95, int((max(votes.values()) / max(sum(votes.values()), 1)) * 80 + 20))
    return {"side": pred, "confidence": conf, "reason": "MULTI-VOTE"}

# 5. ADVANCED
def compute_advanced(data, current_loss_streak):
    if len(data) < 10:
        return {"side": "BIG", "confidence": 50, "reason": "CALIBRATING"}
    votes = {"BIG": 0, "SMALL": 0}
    sides = [x['side'] for x in data[:4]]
    if sides[0] == sides[3] and sides[1] == sides[2]:
        votes["SMALL" if sides[0] == "BIG" else "BIG"] += 3

    trend_score = sum((1 if x['number'] >= 5 else -1) * (8 - i) for i, x in enumerate(data[:8]))
    votes["BIG" if trend_score > 0 else "SMALL"] += 2

    if current_loss_streak >= 2:
        counter = "SMALL" if votes["BIG"] >= votes["SMALL"] else "BIG"
        votes[counter] += 2

    pred = "BIG" if votes["BIG"] >= votes["SMALL"] else "SMALL"
    conf = min(95, int(70 + (max(votes.values()) / max(sum(votes.values()), 1)) * 25 + current_loss_streak * 3))
    return {"side": pred, "confidence": conf, "reason": "ADVANCED-VOTE"}

# 6. ULTIMATE
def compute_ultimate(data):
    if len(data) < 8:
        return {"side": "BIG", "confidence": 60, "reason": "INIT"}
    votes = {"BIG": 0, "SMALL": 0}
    sides = [x['side'] for x in data[:5]]

    if len(sides) == 5 and sides[0] == sides[4] and sides[1] == sides[3]:
        votes["SMALL" if sides[0] == "BIG" else "BIG"] += 3

    score = 0
    weights = [8, 5, 3, 2, 1]
    for i in range(min(len(data), 5)):
        score += (1 if data[i]['number'] >= 5 else -1) * weights[i]
    
    votes["BIG" if score > 0 else "SMALL"] += 2
    pred = "BIG" if votes["BIG"] >= votes["SMALL"] else "SMALL"
    diff = abs(votes["BIG"] - votes["SMALL"])
    
    conf = 95 if diff >= 5 else (90 if diff >= 4 else (85 if diff >= 3 else 75))
    return {"side": pred, "confidence": conf, "reason": "ULTIMATE-ADAPTIVE"}

# ─── PREDICTION SYSTEM ───
def predict_hybrid_engine(history_list, streak):
    if not history_list:
        return "BIG", 7, 75, "ULTIMATE"

    mapped = []
    for item in history_list[:12]:
        num = int(item['number'])
        mapped.append({
            'issueNumber': str(item['issueNumber']),
            'number': num,
            'side': "BIG" if num >= 5 else "SMALL"
        })

    rifu = compute_rifu(mapped)
    smart = compute_smart(mapped)
    hybrid = compute_hybrid(mapped)
    master = compute_master(mapped)
    advanced = compute_advanced(mapped, streak)
    ultimate = compute_ultimate(mapped)

    engines = {
        "CORE": rifu,
        "SMART": smart,
        "HYBRID": hybrid,
        "MASTER": master,
        "ADV": advanced,
        "ULTIMATE": ultimate
    }

    best_engine = max(engines, key=lambda k: engines[k]['confidence'])
    final_side = engines[best_engine]['side']
    confidence = engines[best_engine]['confidence']

    numB, numS = generate_numbers(final_side, mapped)
    suggested_num = numB if final_side == "BIG" else numS

    return final_side, suggested_num, confidence, best_engine

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
    global total_wins, total_losses, loss_streak

    print("🔥 HYBRID HACKED PRO (1 MINUTE WINGO) BOT STARTED...")

    while True:
        try:
            # 1 MINUTE LOOP TIMER (৬ও সেকেন্ডের টাইমার সমন্বয়)
            current_sec = int(time.time()) % 60
            sleep_time = 60 - current_sec + 2  
            await asyncio.sleep(sleep_time)

            history = fetch_api_data()
            if not history:
                continue

            latest_issue = str(history[0]['issueNumber'])
            actual_num = int(history[0]['number'])
            actual_bs = "BIG" if actual_num >= 5 else "SMALL"

            # ১. রেজাল্ট চেক ও আপডেট (Jackpot এবং সাধারণ Win উভয়ই একটি Win হিসেবে গণ্য হবে)
            if last_predicted_period == latest_issue and last_predicted_signal:
                is_win = (last_predicted_signal == actual_bs)

                if is_win:
                    total_wins += 1
                    loss_streak = 0
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
                    f"📊 *Win Rate:* `{win_rate:.1f}%` ({total_wins}W / {total_losses}L)"
                )
                await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                await asyncio.sleep(1)

            # ২. নতুন প্রেডিকশন
            signal, pred_num, conf, engine_used = predict_hybrid_engine(history, loss_streak)
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
