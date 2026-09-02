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
loss_streak = 0

last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None

# ==================== EXACT HTML/JS ENGINE LOGIC ====================

def generate_numbers(side, history_list):
    freq = [0] * 10
    for x in history_list:
        freq[x['number']] += 1
    
    big_pool = [5, 6, 7, 8, 9]
    small_pool = [0, 1, 2, 3, 4]

    big_pool.sort(key=lambda x: freq[x])
    small_pool.sort(key=lambda x: freq[x])

    return big_pool[0] if side == "BIG" else small_pool[0]

# 1. CORE ENGINE
def compute_rifu(data):
    if not data: return {"side": "BIG", "confidence": 76}
    sides = [x['side'] for x in data]
    last = sides[0]
    streak = 0
    for s in sides:
        if s == last: streak += 1
        else: break
    if streak >= 5: return {"side": last, "confidence": 90}
    return {"side": "BIG" if last == "SMALL" else "SMALL", "confidence": 76}

# 2. SMART ENGINE
def compute_smart(data):
    if len(data) < 4: return {"side": "SMALL", "confidence": 75}
    sides = [x['side'] for x in data[:4]]
    if sides[0] == sides[3] and sides[1] == sides[2]:
        return {"side": "SMALL" if sides[0] == "BIG" else "BIG", "confidence": 85}
    return {"side": "SMALL", "confidence": 75}

# 3. HYBRID ENGINE
def compute_hybrid(data):
    if len(data) < 5: return {"side": "BIG", "confidence": 73}
    math_num = (data[0]['number'] + data[1]['number']) % 10
    return {"side": "BIG" if math_num >= 5 else "SMALL", "confidence": 73}

# 4. MASTER ENGINE
def compute_master(data):
    if len(data) < 8: return {"side": "BIG", "confidence": 73}
    score = sum((1 if x['number'] >= 5 else -1) for x in data[:5])
    pred = "BIG" if score >= 0 else "SMALL"
    return {"side": pred, "confidence": 73}

# 5. ADVANCED ENGINE (EXACT WEIGHTED FORMULA FROM WEB)
def compute_advanced(data, streak):
    if len(data) < 8: 
        return {"side": "BIG", "confidence": 87}
    
    # ওয়েবসাইটের অরিজিনাল ওয়েটেড স্কেলিং অ্যালগরিদম
    weights = [9, 7, 5, 3, 2, 1, 1, 1]
    score = 0
    for i in range(min(len(data), 8)):
        val = 1 if data[i]['side'] == "BIG" else -1
        score += val * weights[i]
    
    # Positive score = BIG, Negative = SMALL
    pred = "BIG" if score >= 0 else "SMALL"
    
    # কনফিডেন্স ৮৭% ওয়েবসাইটের সাথে ফিক্সড
    conf = 87 if abs(score) >= 3 else 76
    return {"side": pred, "confidence": conf}

# 6. ULTIMATE ENGINE
def compute_ultimate(data):
    if len(data) < 8: return {"side": "BIG", "confidence": 70}
    return {"side": "BIG", "confidence": 70}

# ─── PREDICTION SYSTEM (WEB MATCHED PRIORITY) ───
def predict_hybrid_engine(history_list, streak):
    if not history_list:
        return "BIG", 9, 87, "ADVANCED"

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
        "ADVANCED": advanced,
        "CORE": rifu,
        "SMART": smart,
        "HYBRID": hybrid,
        "MASTER": master,
        "ULTIMATE": ultimate
    }

    # ওয়েবসাইটে ADVANCED ইঞ্জিনকে সর্বোচ্চ অগ্রাধিকার দেওয়া হয়
    selected_engine_name = "ADVANCED"
    selected = engines[selected_engine_name]

    final_side = selected['side']
    confidence = selected['confidence']
    suggested_num = generate_numbers(final_side, mapped)

    return final_side, suggested_num, confidence, selected_engine_name

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

    print("🔥 HYBRID HACKED PRO 1M (FIXED MATCH) BOT STARTED...")

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

            # ১. রেজাল্ট চেক
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
