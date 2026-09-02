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

# লজিক ১-এর জন্য প্যাটার্ন অ্যারে (১ম কোড থেকে প্রাপ্ত)
PATTERN_ARRAY = [
    {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 2}, {"s": "SMALL", "n": 4}, {"s": "BIG", "n": 9},
    {"s": "BIG", "n": 6}, {"s": "SMALL", "n": 0}, {"s": "BIG", "n": 8}, {"s": "SMALL", "n": 3},
    {"s": "SMALL", "n": 1}, {"s": "BIG", "n": 5}, {"s": "BIG", "n": 7}, {"s": "SMALL", "n": 4}
]

# লজিক ২-এর জন্য হিস্ট্রি ডিকশনারি (২য় কোড থেকে প্রাপ্ত)
PATTERN_LOGIC = {
    "0+0":"BIG","0+1":"BIG","0+2":"BIG","0+3":"BIG","0+4":"BIG","0+5":"BIG","0+6":"BIG","0+7":"BIG","0+8":"BIG","0+9":"BIG",
    "1+0":"SMALL","1+1":"SMALL","1+2":"SMALL","1+3":"SMALL","1+4":"SMALL","1+5":"SMALL","1+6":"SMALL","1+7":"SMALL","1+8":"SMALL","1+9":"SMALL",
    "2+0":"BIG","2+1":"BIG","2+2":"BIG","2+3":"BIG","2+4":"BIG","2+5":"BIG","2+6":"BIG","2+7":"BIG","2+8":"BIG","2+9":"BIG",
    "3+0":"SMALL","3+1":"SMALL","3+2":"SMALL","3+3":"SMALL","3+4":"SMALL","3+5":"SMALL","3+6":"SMALL","3+7":"SMALL","3+8":"SMALL","3+9":"SMALL",
    "4+0":"BIG","4+1":"BIG","4+2":"BIG","4+3":"BIG","4+4":"BIG","4+5":"BIG","4+6":"BIG","4+7":"BIG","4+8":"BIG","4+9":"BIG",
    "5+0":"SMALL","5+1":"SMALL","5+2":"SMALL","5+3":"SMALL","5+4":"SMALL","5+5":"SMALL","5+6":"SMALL","5+7":"SMALL","5+8":"SMALL","5+9":"SMALL",
    "6+0":"BIG","6+1":"BIG","6+2":"BIG","6+3":"BIG","6+4":"BIG","6+5":"BIG","6+6":"BIG","6+7":"BIG","6+8":"BIG","6+9":"BIG",
    "7+0":"SMALL","7+1":"SMALL","7+2":"SMALL","7+3":"SMALL","7+4":"SMALL","7+5":"SMALL","7+6":"SMALL","7+7":"SMALL","7+8":"SMALL","7+9":"SMALL",
    "8+0":"BIG","8+1":"BIG","8+2":"BIG","8+3":"BIG","8+4":"BIG","8+5":"BIG","8+6":"BIG","8+7":"BIG","8+8":"BIG","8+9":"BIG",
    "9+0":"SMALL","9+1":"SMALL","9+2":"SMALL","9+3":"SMALL","9+4":"SMALL","9+5":"SMALL","9+6":"SMALL","9+7":"SMALL","9+8":"SMALL","9+9":"SMALL"
}

bot = Bot(token=BOT_TOKEN)

# ট্র্যাকিং ভ্যারিয়েবল
total_wins = 0
total_losses = 0
last_predicted_period = None
last_predicted_signal = None

# লজিক ১ (টাইম ও অ্যারে বেসড প্রেডিকশন - ৩০ সেকেন্ডের জন্য)
def get_time_based_prediction():
    now = datetime.now(timezone.utc)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    diff = int((now - start_of_day).total_seconds())
    interval = 30  # 30S Wingo
    idx = (diff // interval) + 1
    pattern_index = (idx + 5) % len(PATTERN_ARRAY)
    pred = PATTERN_ARRAY[pattern_index]
    return pred["s"]

# লজিক ২ (হিস্ট্রি এপিআই বেসড প্রেডিকশন)
def get_history_based_prediction(history_list):
    if not history_list or len(history_list) < 2:
        return "BIG"
    last_num1 = str(history_list[0]['number'])
    last_num2 = str(history_list[1]['number'])
    search_key = f"{last_num2}+{last_num1}"
    return PATTERN_LOGIC.get(search_key, 'SMALL')

# এপিআই ডাটা ফেচিং (Direct + ScraperAPI Fallback)
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

async def prediction_bot():
    global last_predicted_period, last_predicted_signal, total_wins, total_losses
    print("30S Dual-Logic Wingo Predictor Bot Started...")

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

            # ১. আগের সিগন্যাল থাকলে রেজাল্ট পাঠানো (স্কিপ করা সিগন্যালে রেজাল্ট পাঠাবে না)
            if last_predicted_period == latest_issue and last_predicted_signal and last_predicted_signal != "WAIT":
                is_win = (last_predicted_signal == actual_bs)
                if is_win:
                    total_wins += 1
                    status_str = f"🟢 WIN {total_wins}!"
                else:
                    total_losses += 1
                    status_str = f"🔴 LOSS {total_losses}!"
                
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

            # ২. দুটি লজিক চেক ও সিদ্ধান্ত নেওয়া
            pred_logic1 = get_time_based_prediction()
            pred_logic2 = get_history_based_prediction(history)

            next_period = str(int(latest_issue) + 1)

            # ২টা লজিক একই হলে প্রেডিকশন পাঠাবে, অমিল হলে WAIT পাঠাবে
            if pred_logic1 == pred_logic2:
                final_signal = pred_logic1
                suggested_num = random.choice([5, 6, 7, 8, 9]) if final_signal == "BIG" else random.choice([0, 1, 2, 3, 4])
                
                prediction_msg = (
                    f"⚡ *ANSH BOSS VIP PREDICTION*\n"
                    f"⏱️ *Mode:* 30S Wingo\n"
                    f"🆔 *Period:* `{next_period[-5:]}`\n"
                    f"🔮 *Prediction:* `{final_signal}` (Num: {suggested_num})\n"
                    f"⏳ *Status:* Result Awaiting..."
                )
            else:
                final_signal = "WAIT"
                prediction_msg = (
                    f"⚡ *ANSH BOSS VIP PREDICTION*\n"
                    f"⏱️ *Mode:* 30S Wingo\n"
                    f"🆔 *Period:* `{next_period[-5:]}`\n"
                    f"🔮 *Prediction:* ⏳ *Wait Next Period...*\n"
                    f"⚠️ *Reason:* Dual Logic Mismatch"
                )

            last_predicted_period = next_period
            last_predicted_signal = final_signal

            await bot.send_message(chat_id=CHAT_ID, text=prediction_msg, parse_mode="Markdown")

        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(2)

if __name__ == '__main__':
    asyncio.run(prediction_bot())
