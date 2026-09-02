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

RAW_API = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts="

bot = Bot(token=BOT_TOKEN)

total_wins = 0
total_losses = 0
loss_streak = 0

last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None

# ==================== EXACT WEB ADVANCED ENGINE ====================

def compute_advanced_exact(data):
    """
    ওয়েবসাইটের JS-এর EXACT ADVANCED ইঞ্জিন অ্যালগরিদম
    """
    if len(data) < 8:
        return "BIG", 87
    
    # ওয়েবসাইটের অরিজিনাল ওয়েটেড স্কেলিং
    weights = [9, 7, 5, 3, 2, 1, 1, 1]
    score = 0
    
    for i in range(8):
        if data[i]['number'] >= 5:
            score += weights[i]
        else:
            score -= weights[i]
    
    # Positive = BIG, Negative = SMALL
    pred = "BIG" if score >= 0 else "SMALL"
    
    # ওয়েবসাইটের মতো ৮৭% ফিক্সড
    conf = 87
    
    return pred, conf

# ==================== CORE ENGINE (MATCHES WEB) ====================

def compute_core_exact(data):
    if not data:
        return "BIG", 76
    
    sides = [x['side'] for x in data]
    last = sides[0]
    streak = 0
    for s in sides:
        if s == last:
            streak += 1
        else:
            break
    
    if streak >= 5:
        return last, 90
    
    # Reversal: if last is BIG → predict SMALL, else BIG
    pred = "SMALL" if last == "BIG" else "BIG"
    return pred, 76

# ==================== SMART ENGINE ====================

def compute_smart_exact(data):
    if len(data) < 4:
        return "SMALL", 75
    
    sides = [x['side'] for x in data[:4]]
    
    # Mirror Pattern (ABBA)
    if sides[0] == sides[3] and sides[1] == sides[2]:
        pred = "SMALL" if sides[0] == "BIG" else "BIG"
        return pred, 85
    
    return "SMALL", 75

# ==================== HYBRID ENGINE ====================

def compute_hybrid_exact(data):
    if len(data) < 5:
        return "BIG", 73
    
    math_num = (data[0]['number'] + data[1]['number']) % 10
    pred = "BIG" if math_num >= 5 else "SMALL"
    return pred, 73

# ==================== MASTER ENGINE ====================

def compute_master_exact(data):
    if len(data) < 8:
        return "BIG", 73
    
    # ওয়েবসাইটের মতো সিম্পল স্কোর
    score = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score += 1
        else:
            score -= 1
    
    pred = "BIG" if score >= 0 else "SMALL"
    conf = 73
    return pred, conf

# ==================== ULTIMATE ENGINE ====================

def compute_ultimate_exact(data):
    if len(data) < 8:
        return "BIG", 70
    
    # সিম্পল ট্রেন্ড ফলো
    big_count = sum(1 for x in data[:8] if x['number'] >= 5)
    pred = "BIG" if big_count >= 4 else "SMALL"
    conf = 70
    return pred, conf

# ==================== PREDICTION SYSTEM (EXACT WEB MATCH) ====================

def generate_numbers(side, data):
    freq = [0] * 10
    for x in data:
        freq[x['number']] += 1
    
    if side == "BIG":
        pool = [5, 6, 7, 8, 9]
        pool.sort(key=lambda x: freq[x])
        return pool[0] if pool else 7
    else:
        pool = [0, 1, 2, 3, 4]
        pool.sort(key=lambda x: freq[x])
        return pool[0] if pool else 2

def predict_hybrid_engine(history_list):
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

    # ===== ওয়েবসাইটের EXACT অ্যালগরিদম =====
    core_pred, core_conf = compute_core_exact(mapped)
    smart_pred, smart_conf = compute_smart_exact(mapped)
    hybrid_pred, hybrid_conf = compute_hybrid_exact(mapped)
    master_pred, master_conf = compute_master_exact(mapped)
    advanced_pred, advanced_conf = compute_advanced_exact(mapped)
    ultimate_pred, ultimate_conf = compute_ultimate_exact(mapped)

    # ===== ইঞ্জিন কনফিডেন্স ম্যাপ =====
    engines = {
        "CORE": {"side": core_pred, "conf": core_conf},
        "SMART": {"side": smart_pred, "conf": smart_conf},
        "HYBRID": {"side": hybrid_pred, "conf": hybrid_conf},
        "MASTER": {"side": master_pred, "conf": master_conf},
        "ADVANCED": {"side": advanced_pred, "conf": advanced_conf},
        "ULTIMATE": {"side": ultimate_pred, "conf": ultimate_conf},
    }

    # ===== ওয়েবসাইটের মতো ADVANCED কে প্রায়োরিটি =====
    # ওয়েবসাইটে ADVANCED ইঞ্জিন ৮৭% দিয়ে সিলেক্ট হয়
    selected_engine = "ADVANCED"
    selected = engines[selected_engine]
    
    final_side = selected['side']
    confidence = selected['conf']
    suggested_num = generate_numbers(final_side, mapped)

    return final_side, suggested_num, confidence, selected_engine

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

    print("🔥 HYBRID HACKED PRO 1M (EXACT WEB MATCH) BOT STARTED...")

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
