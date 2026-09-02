import asyncio
import time
import random
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
RAW_API = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json?ts="

bot = Bot(token=BOT_TOKEN)

# ট্র্যাকিং ভ্যারিয়েবল
total_wins = 0
total_losses = 0
total_jackpots = 0
loss_streak = 0

last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None

# ==================== HYBRID HACKED PRO ALGORITHM ====================

def compute_rifu(data):
    if not data:
        return {"side": "BIG", "conf": 70}
    sides = [x['side'] for x in data]
    last = sides[0]
    
    streak = 0
    for s in sides:
        if s == last:
            streak += 1
        else:
            break
            
    if streak >= 5:
        return {"side": last, "conf": 90}
    
    big_count = sum(1 for s in sides[:5] if s == "BIG")
    if big_count >= 4:
        return {"side": "SMALL", "conf": 76}
    elif big_count <= 1:
        return {"side": "BIG", "conf": 76}
        
    return {"side": "SMALL" if last == "BIG" else "BIG", "conf": 72}

def compute_smart(data):
    if len(data) < 4:
        return {"side": "BIG", "conf": 50}
    sides = [x['side'] for x in data[:4]]
    if sides[0] == sides[3] and sides[1] == sides[2]:
        return {"side": "SMALL" if sides[0] == "BIG" else "BIG", "conf": 92}
    if all(s == sides[0] for s in sides):
        return {"side": sides[0], "conf": 85}
    return {"side": "BIG", "conf": 60}

def compute_ultimate(data):
    if len(data) < 5:
        return {"side": "BIG", "conf": 60}
    score = 0
    weights = [8, 5, 3, 2, 1]
    for i in range(min(len(data), 5)):
        score += (1 if data[i]['number'] >= 5 else -1) * weights[i]
    
    side = "BIG" if score > 0 else "SMALL"
    conf = 85 if abs(score) >= 5 else 75
    return {"side": side, "conf": conf}

def predict_hybrid_engine(history_list):
    if not history_list:
        return "BIG", 7, 75, "ULTIMATE"

    mapped = []
    for item in history_list[:12]:
        num = int(item['number'])
        mapped.append({
            'number': num,
            'side': "BIG" if num >= 5 else "SMALL"
        })

    rifu = compute_rifu(mapped)
    smart = compute_smart(mapped)
    ultimate = compute_ultimate(mapped)

    engines = {
        "CORE": rifu,
        "SMART": smart,
        "ULTIMATE": ultimate
    }

    # Best engine নির্বাচন
    best_engine = max(engines, key=lambda k: engines[k]['conf'])
    final_side = engines[best_engine]['side']
    confidence = engines[best_engine]['conf']

    # নাম্বার নির্বাচন (BIG হলে 5-9, SMALL হলে 0-4)
    freq = [0] * 10
    for m in mapped:
        freq[m['number']] += 1

    if final_side == "BIG":
        pool = [5, 6, 7, 8, 9]
    else:
        pool = [0, 1, 2, 3, 4]
    
    pool.sort(key=lambda x: freq[x])
    suggested_num = pool[0]

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
    global total_wins, total_losses, total_jackpots, loss_streak

    print("🔥 HYBRID HACKED PRO (30S WINGO) STARTED...")

    while True:
        try:
            current_sec = int(time.time()) % 30
            sleep_time = 30 - current_sec + 2  
            await asyncio.sleep(sleep_time)

            history = fetch_api_data()
            if not history:
                continue

            latest_issue = str(history[0]['issueNumber'])
            actual_num = int(history[0]['number'])
            actual_bs = "BIG" if actual_num >= 5 else "SMALL"

            # ১. আগের সিগন্যালের রেজাল্ট চেক ও আপডেট
            if last_predicted_period == latest_issue and last_predicted_signal:
                is_jackpot = (actual_num == last_predicted_num)
                is_win = (last_predicted_signal == actual_bs)

                if is_jackpot:
                    total_jackpots += 1
                    total_wins += 1
                    loss_streak = 0
                    status_str = "⭐ JACKPOT WIN!"
                elif is_win:
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
                    f"📊 *Win Rate:* `{win_rate:.1f}%` ({total_wins}W / {total_losses}L / {total_jackpots}J)"
                )
                await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                await asyncio.sleep(1)

            # ২. অ্যালগরিদম ব্যবহার করে নতুন প্রেডিকশন তৈরি
            signal, pred_num, conf, engine_used = predict_hybrid_engine(history)
            next_period = str(int(latest_issue) + 1)

            prediction_msg = (
                f"🔥 *HYBRID HACKED PRO 30S*\n"
                f"⏱️ *Mode:* 30 Sec Wingo\n"
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
