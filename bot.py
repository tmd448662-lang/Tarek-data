import asyncio
import time
import requests
import os
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Bot

# ==================== RENDER WEB SERVICE PORT BINDING ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"DARK X BHAI VIP BOT is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ==================== KEEP-ALIVE FUNCTION ====================
def keep_alive():
    """প্রতি ১০ মিনিটে নিজেকে পিং করে যাতে বট স্লিপ না হয়"""
    while True:
        try:
            time.sleep(600)  # ১০ মিনিট
            port = int(os.environ.get("PORT", 8080))
            url = f"http://localhost:{port}/"
            requests.get(url, timeout=5)
            print("🔄 Keep-alive ping sent")
        except Exception as e:
            print(f"Keep-alive error: {e}")

threading.Thread(target=keep_alive, daemon=True).start()

# ==================== BOT CONFIGURATION ====================
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"  
CHAT_ID = "5012028880"  
SCRAPER_API_KEY = "809f9c620ed6b5fe5a72bc368e8eabee"

RAW_API = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

bot = Bot(token=BOT_TOKEN)

# ==================== STATS ====================
total_wins = 0
total_losses = 0
loss_streak = 0
current_level = 1
consecutive_losses = 0
total_rounds = 0

last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
prediction_sent_for_period = {}

# ==================== EXACT ALGORITHM ====================

def run_algorithm(history_list):
    if not history_list or len(history_list) < 3:
        return "BIG", 0.50
    
    types = []
    for h in history_list[:10]:
        num = int(h['number'])
        types.append("BIG" if num >= 5 else "SMALL")
    
    last1 = types[0] if len(types) > 0 else "BIG"
    last2 = types[1] if len(types) > 1 else "BIG"
    
    if last1 == "SMALL":
        pred_type = "BIG"
        confidence = 0.75
    elif last1 == "BIG":
        pred_type = "SMALL"
        confidence = 0.60
    else:
        pred_type = "BIG"
        confidence = 0.50
    
    if last1 == "BIG" and last2 == "BIG":
        pred_type = "SMALL"
        confidence = 0.90
    elif last1 == "SMALL" and last2 == "SMALL":
        pred_type = "BIG"
        confidence = 0.95
    elif last1 == "SMALL" and last2 == "BIG":
        pred_type = "BIG"
        confidence = 0.70
    elif last1 == "BIG" and last2 == "SMALL":
        pred_type = "BIG"
        confidence = 0.85
    
    if current_level == 3:
        latest_num = int(history_list[0]['number'])
        pred_type = "SMALL" if latest_num >= 5 else "BIG"
        confidence = 0.99
    
    return pred_type, confidence

def generate_dna_value(pred_type):
    if pred_type == "BIG":
        return random.randint(5, 9)
    else:
        return random.randint(0, 4)

def update_stats_on_result(actual_num, predicted_type):
    global total_wins, total_losses, loss_streak
    global current_level, consecutive_losses, total_rounds
    
    actual_type = "BIG" if actual_num >= 5 else "SMALL"
    
    if predicted_type == actual_type:
        total_wins += 1
        status = "WIN"
        status_icon = "🟢"
        
        loss_streak = 0 if loss_streak < 0 else loss_streak + 1
        consecutive_losses = 0
        current_level = 1
    else:
        total_losses += 1
        status = "LOSS"
        status_icon = "🔴"
        
        loss_streak = -1 if loss_streak > 0 else loss_streak - 1
        consecutive_losses += 1
        current_level = 3 if current_level >= 3 else current_level + 1
    
    total_rounds += 1
    return status, status_icon

def get_martingale_info(level):
    if level == 1:
        return "1x"
    elif level == 2:
        return "3x"
    else:
        return "9x"

def get_streak_emoji(streak):
    if streak > 0:
        return "🔥"
    elif streak < 0:
        return "📉"
    else:
        return "⏸️"

# ==================== API FETCHING ====================

def fetch_api_data():
    timestamp = str(int(time.time() * 1000))
    raw_url = RAW_API + "?t=" + timestamp
    try:
        res = requests.get(raw_url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            list_data = data.get("data", {}).get("list", [])
            if list_data:
                return list_data
    except Exception as e:
        print("API Error:", e)
    
    return []

def get_prediction(history_list):
    if not history_list:
        return "BIG", 50, 5, 1
    pred_type, confidence = run_algorithm(history_list)
    dna_value = generate_dna_value(pred_type)
    return pred_type, confidence, dna_value, current_level

# ==================== MAIN BOT LOOP ====================

async def prediction_bot():
    global last_predicted_period, last_predicted_signal, last_predicted_num
    global total_wins, total_losses, loss_streak
    global current_level, total_rounds, prediction_sent_for_period

    print("🔥 DARK X BHAI VIP BOT STARTED...")
    print("📡 Mode: 1 Min Wingo")
    print("🔄 Checking API every 3 seconds")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🔥 DARK X BHAI VIP 🔥\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "💎 TITAN DNA VIP V4\n"
                 "⚡ MODE: 1 MIN WINGO\n"
                 "🛡️ STATUS: ONLINE & SYNCED\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "⏳ WAITING FOR FIRST SIGNAL...",
        )
    except Exception as e:
        print(f"Startup error: {e}")

    while True:
        try:
            current_sec = int(time.time()) % 60
            sleep_time = 60 - current_sec + 3
            await asyncio.sleep(sleep_time)

            history = fetch_api_data()
            if not history:
                print("No data from API, retrying...")
                continue

            latest_issue = str(history[0]['issueNumber'])
            actual_num = int(history[0]['number'])
            actual_type = "BIG" if actual_num >= 5 else "SMALL"

            # ============================================================
            # STEP 1: CHECK RESULT
            # ============================================================
            if last_predicted_period == latest_issue and last_predicted_signal is not None:
                
                status, status_icon = update_stats_on_result(
                    actual_num, 
                    last_predicted_signal
                )
                
                total_games = total_wins + total_losses
                win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0
                multiplier = get_martingale_info(current_level)
                streak_emoji = get_streak_emoji(loss_streak)
                
                is_jackpot = (actual_num == 0 or actual_num == 5)
                jackpot_text = " ⭐ JACKPOT!" if is_jackpot else ""
                
                result_msg = (
                    f"🎯 RESULT UPDATE {status_icon}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: #{latest_issue[-5:]}\n"
                    f"🎯 PREDICTED: {last_predicted_signal} → {last_predicted_num}\n"
                    f"🎰 ACTUAL: {actual_num} ({actual_type})\n"
                    f"📌 RESULT: {status_icon} {status}{jackpot_text}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 WIN RATE: {win_rate:.1f}% ({total_wins}W/{total_losses}L)\n"
                    f"{streak_emoji} STREAK: {loss_streak:+d}\n"
                    f"👑 LEVEL: {current_level} ({multiplier})\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💎 TITAN DNA VIP V4"
                )
                
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=result_msg)
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"Result error: {e}")
                
                last_predicted_period = None
                last_predicted_signal = None
                last_predicted_num = None

            # ============================================================
            # STEP 2: SEND NEW PREDICTION
            # ============================================================
            next_period = str(int(latest_issue) + 1)
            
            if not prediction_sent_for_period.get(next_period, False):
                
                history_mapped = []
                for h in history[:15]:
                    history_mapped.append({
                        'issueNumber': str(h['issueNumber']),
                        'number': int(h['number'])
                    })
                
                pred_type, confidence, dna_value, level = get_prediction(history_mapped)
                multiplier = get_martingale_info(level)
                confidence_pct = int(confidence * 100)
                streak_emoji = get_streak_emoji(loss_streak)
                
                prediction_msg = (
                    f"🔥 DARK X BHAI VIP 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: #{next_period[-5:]}\n"
                    f"🎯 PREDICTION: {pred_type}\n"
                    f"🔢 TARGET NUMBER: {dna_value}\n"
                    f"⚡ CONFIDENCE: {confidence_pct}%\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👑 LEVEL: {level} ({multiplier})\n"
                    f"{streak_emoji} STREAK: {loss_streak:+d}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ RESULT AWAITING...\n"
                    f"💎 TITAN DNA VIP V4"
                )
                
                last_predicted_period = next_period
                last_predicted_signal = pred_type
                last_predicted_num = dna_value
                prediction_sent_for_period[next_period] = True
                
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=prediction_msg)
                except Exception as e:
                    print(f"Prediction error: {e}")

            if len(prediction_sent_for_period) > 5:
                oldest = min(prediction_sent_for_period.keys())
                del prediction_sent_for_period[oldest]

        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(5)

if __name__ == '__main__':
    print("🔥 DARK X BHAI VIP BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("💎 MODE: 1 MIN WINGO")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🔄 STARTING BOT...")
    asyncio.run(prediction_bot())
