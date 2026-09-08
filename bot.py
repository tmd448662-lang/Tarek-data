#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 ULTIMATE PRO AI BOT — Wingo 1M Predictor
🧠 ENGINE: ULTIMATE PRO ENGINE (100% HTML)
📡 MODE: 1 MINUTE
✅ FIRST RESULT → THEN PREDICTION
📊 HOURLY REPORT INCLUDED
"""

import asyncio
import time
import requests
import os
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

try:
    from telegram import Bot
except ImportError:
    print("❌ python-telegram-bot not installed! Run: pip install python-telegram-bot")
    exit(1)

# ============================================================
# 🔥 কনফিগারেশন
# ============================================================
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

# ============================================================
# ওয়েব সার্ভার (পোর্ট 8080)
# ============================================================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ULTIMATE PRO AI BOT is running!")

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

# ============================================================
# বট ইনিশিয়ালাইজ
# ============================================================
bot = Bot(token=BOT_TOKEN)

# ============================================================
# 🧠 ULTIMATE PRO ENGINE (HTML এর 100% সঠিক)
# ============================================================
class UltimateProEngine:
    def __init__(self):
        # HTML থেকে নেওয়া মেমরি
        self.loss_streak = 0
        self.total_predictions = 0
        self.correct_predictions = 0
        self.last_10_accuracy = []
        self.last_prediction = "BIG"
        self.adaptive_weights = {'mirror': 3, 'ema': 2, 'gap': 1, 'cluster': 2, 'trend': 2}
        self.period_counter = 0
        
    def update(self, is_win, prediction):
        self.total_predictions += 1
        if is_win:
            self.correct_predictions += 1
            self.loss_streak = 0
            self.last_10_accuracy.append(True)
        else:
            self.loss_streak += 1
            self.last_10_accuracy.append(False)
            
        if len(self.last_10_accuracy) > 20:
            self.last_10_accuracy.pop(0)
            
        if len(self.last_10_accuracy) >= 5:
            last_5 = self.last_10_accuracy[-5:]
            accuracy = sum(1 for x in last_5 if x) / 5
            if accuracy < 0.4 and self.total_predictions > 10:
                self.adaptive_weights['gap'] = self.adaptive_weights.get('gap', 1) + 0.5
                self.adaptive_weights['mirror'] = max(0.5, self.adaptive_weights.get('mirror', 3) - 0.5)
            elif accuracy > 0.7:
                self.adaptive_weights['mirror'] = self.adaptive_weights.get('mirror', 3) + 0.3
                
        for key in self.adaptive_weights:
            self.adaptive_weights[key] = max(0.5, min(5, self.adaptive_weights[key]))
            
        self.last_prediction = prediction
        
    def get_accuracy(self):
        if self.total_predictions == 0:
            return 0
        return (self.correct_predictions / self.total_predictions) * 100
        
    def predict(self, data):
        """
        ULTIMATE PRO ENGINE - HTML থেকে 100% সঠিক
        HTML Ultimate Pro Engine Algorithm
        """
        if len(data) < 8:
            return {
                'prediction': 'BIG',
                'number': 5,
                'confidence': 60,
                'reason': 'INITIALIZING...',
                'accuracy': 0
            }
        
        # ============================================================
        # ULTIMATE PRO ENGINE VOTING SYSTEM
        # ============================================================
        votes = {'BIG': 0, 'SMALL': 0}
        weights = self.adaptive_weights
        
        types = [d['side'] for d in data[:5]]
        numbers = [d['number'] for d in data[:15]]
        
        # 1. MIRROR PATTERN
        if len(types) >= 5 and types[0] == types[4] and types[1] == types[3]:
            pred = 'SMALL' if types[0] == 'BIG' else 'BIG'
            votes[pred] += weights.get('mirror', 3) * 1.5
        
        # 2. STREAK ANALYSIS
        streak = 1
        for i in range(1, len(types)):
            if types[i] == types[i-1]:
                streak += 1
            else:
                break
                
        if streak >= 4:
            pred = 'SMALL' if types[0] == 'BIG' else 'BIG'
            votes[pred] += 4 if streak >= 6 else 2
        
        # 3. ALTERNATING PATTERN
        if len(data) >= 5:
            last_5 = [d['side'] for d in data[:5]]
            is_alt = all(last_5[i] != last_5[i-1] for i in range(1, 5))
            if is_alt:
                pred = 'SMALL' if last_5[-1] == 'BIG' else 'BIG'
                votes[pred] += 3
            if last_5[0] == last_5[1] and last_5[3] == last_5[4] and last_5[0] == last_5[4]:
                votes[last_5[0]] += 3
        
        # 4. TREND SCORE
        score = 0
        for i in range(min(len(data), 8)):
            weight = [8, 5, 3, 2, 1, 1, 0, 0][i] if i < 8 else 0
            score += (1 if data[i]['number'] >= 5 else -1) * weight
        votes['BIG' if score > 0 else 'SMALL'] += 2
        
        # 5. GAP ANALYSIS (Missing Numbers)
        all_nums = set(range(10))
        present = set(numbers[:15])
        missing = list(all_nums - present)
        if missing:
            num = missing[0]
            votes['BIG' if num >= 5 else 'SMALL'] += 1.5
        
        # 6. ACCURACY ADJUSTMENT
        accuracy = self.correct_predictions / max(self.total_predictions, 1)
        if accuracy < 0.5:
            pred = 'SMALL' if self.last_prediction == 'BIG' else 'BIG'
            votes[pred] += 2
        
        # 7. LOSS STREAK RECOVERY
        if len(self.last_10_accuracy) >= 5:
            last_5_loss = sum(1 for x in self.last_10_accuracy[-5:] if not x)
            if last_5_loss >= 3:
                votes['SMALL' if data[0]['side'] == 'BIG' else 'BIG'] += 3
        
        # ============================================================
        # FINAL DECISION
        # ============================================================
        final_pred = 'BIG' if votes['BIG'] >= votes['SMALL'] else 'SMALL'
        diff = abs(votes['BIG'] - votes['SMALL'])
        
        # CONFIDENCE
        if diff >= 5:
            confidence = 95
        elif diff >= 4:
            confidence = 90
        elif diff >= 3:
            confidence = 85
        elif diff >= 2:
            confidence = 78
        else:
            confidence = 70
            
        if accuracy > 0.6:
            confidence += 5
        if accuracy > 0.75:
            confidence += 5
        confidence = min(95, confidence)
        
        # ============================================================
        # NUMBER SELECTION (HTML এর মতো)
        # ============================================================
        if final_pred == 'BIG':
            freq = {}
            for n in numbers[:15]:
                if n >= 5:
                    freq[n] = freq.get(n, 0) + 1
            if freq:
                num = min(freq, key=freq.get)
            else:
                num = random.choice([5, 6, 7, 8, 9])
        else:
            freq = {}
            for n in numbers[:15]:
                if n < 5:
                    freq[n] = freq.get(n, 0) + 1
            if freq:
                num = min(freq, key=freq.get)
            else:
                num = random.choice([0, 1, 2, 3, 4])
        
        # ============================================================
        # REASON (HTML Ultimate Pro Engine Style)
        # ============================================================
        if diff >= 5:
            reason = "🔥 STRONG SIGNAL"
        elif diff >= 4:
            reason = "📊 HIGH CONFIDENCE"
        elif diff >= 3:
            reason = "📈 MODERATE SIGNAL"
        elif diff >= 2:
            reason = "📉 WEAK SIGNAL"
        else:
            reason = "🔮 NEUTRAL - FOLLOWING TREND"
        
        return {
            'prediction': final_pred,
            'number': num,
            'confidence': confidence,
            'reason': reason,
            'accuracy': round(accuracy * 100, 1)
        }

# ============================================================
# গ্লোবাল ভেরিয়েবল
# ============================================================
history_data = []
last_period = None
prediction_sent = False
result_sent = False
current_prediction = None
engine = UltimateProEngine()
wins = 0
losses = 0

# Hourly Stats
hourly_stats = {
    'total_rounds': 0,
    'total_wins': 0,
    'total_losses': 0,
    'max_win_streak': 0,
    'max_loss_streak': 0,
    'current_streak': 0,
    'streak_type': 'WIN'
}
last_hour_report_time = time.time()
hourly_report_sent = False

# ============================================================
# 📊 HOURLY REPORT
# ============================================================
async def send_hourly_report():
    global hourly_stats, last_hour_report_time, hourly_report_sent
    
    current_time = time.time()
    
    if current_time - last_hour_report_time >= 3600 and not hourly_report_sent:
        total = hourly_stats['total_rounds']
        wins = hourly_stats['total_wins']
        losses = hourly_stats['total_losses']
        win_rate = (wins / total * 100) if total > 0 else 0
        
        current_hour = datetime.now().strftime('%I:%M %p')
        
        msg = (
            f"📊 *HOURLY PERFORMANCE REPORT*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🕐 *TIME:* {current_hour}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔄 *TOTAL ROUNDS:* `{total}`\n"
            f"✅ *TOTAL WINS:* `{wins}`\n"
            f"❌ *TOTAL LOSSES:* `{losses}`\n"
            f"📈 *WIN RATE:* `{win_rate:.1f}%`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 *BEST WIN STREAK:* `{hourly_stats['max_win_streak']}x`\n"
            f"📉 *WORST LOSS STREAK:* `{hourly_stats['max_loss_streak']}x`\n"
            f"🔥 *CURRENT STREAK:* `{hourly_stats['current_streak']}x {hourly_stats['streak_type']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 ULTIMATE PRO AI"
        )
        
        try:
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
            print(f"✅ Hourly Report Sent at {current_hour}")
            hourly_report_sent = True
            last_hour_report_time = current_time
            
            hourly_stats = {
                'total_rounds': 0,
                'total_wins': 0,
                'total_losses': 0,
                'max_win_streak': 0,
                'max_loss_streak': 0,
                'current_streak': 0,
                'streak_type': 'WIN'
            }
        except Exception as e:
            print(f"❌ Failed to send hourly report: {e}")

# ============================================================
# 📡 API ফেচ
# ============================================================
def fetch_api_data():
    try:
        res = requests.get(API_URL + "?t=" + str(int(time.time() * 1000)), timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", {}).get("list", [])
    except:
        pass
    return []

# ============================================================
# 🚀 মেইন লুপ
# ============================================================
async def prediction_bot():
    global history_data, last_period
    global prediction_sent, result_sent, current_prediction
    global wins, losses, hourly_stats, hourly_report_sent

    print("🔥 ULTIMATE PRO ENGINE BOT STARTED...")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 ENGINE: ULTIMATE PRO ENGINE (100% HTML)")
    print("📡 MODE: 1 MINUTE")
    print("✅ RESULT → PREDICTION")
    print("📊 HOURLY REPORT: ENABLED")
    print("━━━━━━━━━━━━━━━━━━━━")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                "🔥 *ULTIMATE PRO ENGINE* 🔥\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🧠 ENGINE: ULTIMATE PRO ENGINE\n"
                "📡 MODE: 1 MINUTE\n"
                "✅ RESULT FIRST → THEN PREDICTION\n"
                "📊 HOURLY REPORT: ENABLED\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "⏳ WAITING FOR FIRST SIGNAL..."
            ),
            parse_mode="Markdown"
        )
    except:
        pass

    while True:
        try:
            current_sec = int(time.time()) % 60
            await asyncio.sleep(60 - current_sec + 2)

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

            print(f"📡 Period: {latest_issue} | Result: {actual_num} ({actual_type})")

            # ============================================================
            # 🔥 RESULT CHECK
            # ============================================================
            if last_period is not None and last_period != latest_issue:
                if current_prediction is not None and not result_sent:
                    is_win = (current_prediction['prediction'] == actual_type)
                    is_jackpot = (actual_num == current_prediction['number'])

                    if is_win or is_jackpot:
                        wins += 1
                        hourly_stats['total_wins'] += 1
                        status = "✅ WIN"
                        if is_jackpot:
                            status = "✅ WIN ⭐ JACKPOT!"
                    else:
                        losses += 1
                        hourly_stats['total_losses'] += 1
                        status = "❌ LOSS"
                    
                    engine.update(is_win, current_prediction['prediction'])
                    accuracy = engine.get_accuracy()
                    total = wins + losses
                    win_rate = (wins / total * 100) if total > 0 else 0

                    hourly_stats['total_rounds'] += 1
                    if is_win:
                        if hourly_stats['streak_type'] == 'WIN':
                            hourly_stats['current_streak'] += 1
                        else:
                            hourly_stats['current_streak'] = 1
                            hourly_stats['streak_type'] = 'WIN'
                        if hourly_stats['current_streak'] > hourly_stats['max_win_streak']:
                            hourly_stats['max_win_streak'] = hourly_stats['current_streak']
                    else:
                        if hourly_stats['streak_type'] == 'LOSS':
                            hourly_stats['current_streak'] += 1
                        else:
                            hourly_stats['current_streak'] = 1
                            hourly_stats['streak_type'] = 'LOSS'
                        if hourly_stats['current_streak'] > hourly_stats['max_loss_streak']:
                            hourly_stats['max_loss_streak'] = hourly_stats['current_streak']

                    result_msg = (
                        f"🎯 *RESULT*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 #{latest_issue[-5:]}\n"
                        f"🎯 PREDICTED: {current_prediction['prediction']} → {current_prediction['number']}\n"
                        f"🎰 ACTUAL: {actual_num} ({actual_type})\n"
                        f"📌 {status}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 WIN RATE: {win_rate:.1f}% ({wins}W/{losses}L)\n"
                        f"🔥 STREAK: {engine.loss_streak:+d}\n"
                        f"📈 ACCURACY: {accuracy:.1f}%\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💎 ULTIMATE PRO ENGINE"
                    )

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                        result_sent = True
                        print(f"✅ Result sent for {latest_issue}")
                        await asyncio.sleep(1)
                    except Exception as e:
                        print(f"❌ Failed to send result: {e}")
                    
                    await send_hourly_report()
                    
                    prediction_sent = False
                    current_prediction = None
                    result_sent = False

            # ============================================================
            # 🔥 NEW PREDICTION
            # ============================================================
            next_period = str(int(latest_issue) + 1)
            
            if last_period is None or (last_period != latest_issue and not prediction_sent):
                pred = engine.predict(history_data)
                current_prediction = pred
                prediction_sent = True
                result_sent = False

                pred_msg = (
                    f"🔥 *ULTIMATE PREDICTION* 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 #{next_period[-5:]}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 *{pred['prediction']}*\n"
                    f"🔢 NUMBER: `{pred['number']}`\n"
                    f"⚡ CONFIDENCE: `{pred['confidence']}%`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 REASON: {pred['reason']}\n"
                    f"📈 AI ACCURACY: `{pred['accuracy']}%`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ RESULT AWAITING...\n"
                    f"💎 ULTIMATE PRO ENGINE"
                )

                try:
                    await bot.send_message(chat_id=CHAT_ID, text=pred_msg, parse_mode="Markdown")
                    print(f"✅ Prediction sent for {next_period}")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"❌ Failed to send prediction: {e}")

            last_period = latest_issue

        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            await asyncio.sleep(5)

if __name__ == '__main__':
    print("🔥 ULTIMATE PRO ENGINE BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print(f"🤖 TOKEN: {BOT_TOKEN[:10]}...")
    print(f"📡 CHAT: {CHAT_ID}")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 ENGINE: ULTIMATE PRO ENGINE (100% HTML)")
    print("📡 MODE: 1 MINUTE")
    print("📊 HOURLY REPORT: ENABLED")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🔄 Starting bot...")
    asyncio.run(prediction_bot())
