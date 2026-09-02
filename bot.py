import asyncio
import time
import random
import requests
from telegram import Bot

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"  
CHAT_ID = "5012028880"  

# HTML কোড থেকে নেওয়া মূল প্যাটার্ন লজিক
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

# নতুন করে ট্র্যাকিং শুরু (0 থেকে কাউন্ট)
last_predicted_period = None
last_predicted_signal = None
total_wins = 0
total_losses = 0

def get_sifat_signal(history_list):
    if not history_list or len(history_list) < 2:
        return "BIG"
    last_num1 = str(history_list[0]['number'])
    last_num2 = str(history_list[1]['number'])
    search_key = f"{last_num2}+{last_num1}"
    return PATTERN_LOGIC.get(search_key, 'SMALL')

def fetch_api_data():
    try:
        url = f"https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json?ts={int(time.time() * 1000)}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get('data', {}).get('list', [])
    except Exception as e:
        print(f"API Fetch Error: {e}")
    return []

async def prediction_bot():
    global last_predicted_period, last_predicted_signal, total_wins, total_losses
    print("30S Wingo Predictor Bot Started...")

    while True:
        try:
            # ৩০ সেকেন্ডের সাইকেল হিসাব (ড্র শেষ হওয়ার ২ সেকেন্ড পর রিফ্রেশ)
            current_sec = int(time.time()) % 30
            sleep_time = 30 - current_sec + 2  
            await asyncio.sleep(sleep_time)

            history = fetch_api_data()
            if not history:
                continue

            latest_issue = str(history[0]['issueNumber'])
                actual_num = int(history[0]['number'])
            actual_bs = "BIG" if actual_num >= 5 else "SMALL"

            # ১. আগের প্রেডিকশনের রেজাল্ট পাঠানো (Result Update First)
            if last_predicted_period == latest_issue and last_predicted_signal:
                is_win = (last_predicted_signal == actual_bs)
                if is_win:
                    total_wins += 1
                    status_str = "🟢 WIN 1!"
                else:
                    total_losses += 1
                    status_str = "🔴 LOSS"
                
                total_games = total_wins + total_losses
                win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0
                
                result_msg = (
                    f"🎯 RESULT UPDATE\n"
                    f"🆔 Period: {latest_issue[-5:]}\n"
                    f"🎰 Actual Number: {actual_num} ({actual_bs})\n"
                    f"📌 Result: {status_str}\n"
                    f"📊 Win Rate: {win_rate:.1f}% ({total_wins}W / {total_losses}L)"
                )
                await bot.send_message(chat_id=CHAT_ID, text=result_msg)
                await asyncio.sleep(1) # ১ সেকেন্ড বিরতি

            # ২. নতুন পোঁডের জন্য নতুন প্রেডিকশন দেওয়া (New Prediction)
            next_period = str(int(latest_issue) + 1)
            new_signal = get_sifat_signal(history)

            if new_signal == "BIG":
                suggested_num = random.choice([5, 6, 7, 8, 9])
            else:
                suggested_num = random.choice([0, 1, 2, 3, 4])

            last_predicted_period = next_period
            last_predicted_signal = new_signal

            prediction_msg = (
                f"⚡ PREDICTION\n"
                f"⏱️ Mode: 30S Wingo\n"
                f"🆔 Period: {next_period[-5:]}\n"
                f"🔮 Prediction: {new_signal} (Num: {suggested_num})\n"
                f"⏳ Status: Result Awaiting..."
            )
            await bot.send_message(chat_id=CHAT_ID, text=prediction_msg)

        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(2)

if __name__ == '__main__':
    asyncio.run(prediction_bot())
