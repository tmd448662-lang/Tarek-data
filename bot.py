# ============================================================
# 🔥 FURIOUS AI BOT v2 — COMPLETE FIXED VERSION
# 📡 শুধু 1 MIN WINGO
# 🧠 সম্পূর্ণ HTML এর মতো ১০-ইঞ্জিন সিস্টেম
# 📊 হাওয়ারলি রিপোর্ট
# ✅ প্রথমে রেজাল্ট → তারপর প্রেডিকশন
# 🎯 Jackpot = WIN হিসাবে কাউন্ট
# ============================================================

import asyncio
import time
import requests
import os
import random
import json
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
        self.wfile.write(b"FURIOUS AI BOT is running!")

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
total_wins = 0
total_losses = 0
total_rounds = 0
current_streak = 0
best_streak = 0
loss_streak = 0
current_level = 1

# LTS State (HTML থেকে নেওয়া)
lts_state = {
    'trend_side': None,
    'wrong_breaks': 0,
    'ride_mode': False,
    'post_trans_ride_for': 0,
    'phase': None
}

history_data = []
last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
last_predicted_conf = 0
prediction_sent_for_period = {}

# ==================== হাওয়ারলি স্ট্যাটস ====================
hourly_stats = {
    'total_rounds': 0,
    'total_wins': 0,
    'total_losses': 0,
    'max_win_streak': 0,
    'max_loss_streak': 0,
    'current_streak': 0,
    'streak_type': 'WIN',
    'jackpots': 0
}
last_hour_report_time = time.time()

# ============================================================
# 🧠 COMPLETE 10-ENGINE FURIOUS SYSTEM (HTML থেকে নেওয়া)
# ============================================================

# ---- CPU PATTERN DB (সম্পূর্ণ HTML থেকে) ----
CPU_PATTERN_DB = {
    'BBB': {'next': 'SMALL', 'conf': 82},
    'SSS': {'next': 'BIG', 'conf': 82},
    'BBS': {'next': 'SMALL', 'conf': 70},
    'SSB': {'next': 'BIG', 'conf': 70},
    'BSS': {'next': 'BIG', 'conf': 68},
    'SBB': {'next': 'SMALL', 'conf': 68},
    'BSB': {'next': 'SMALL', 'conf': 63},
    'SBS': {'next': 'BIG', 'conf': 63},
    'BBBB': {'next': 'SMALL', 'conf': 88},
    'SSSS': {'next': 'BIG', 'conf': 88},
    'BBBS': {'next': 'SMALL', 'conf': 84},
    'SSSB': {'next': 'BIG', 'conf': 84},
    'BBSS': {'next': 'SMALL', 'conf': 76},
    'SSBB': {'next': 'BIG', 'conf': 76},
    'BSBS': {'next': 'BIG', 'conf': 62},
    'SBSB': {'next': 'SMALL', 'conf': 62},
    'BSSB': {'next': 'BIG', 'conf': 68},
    'SBBS': {'next': 'SMALL', 'conf': 68},
    'BSBB': {'next': 'SMALL', 'conf': 68},
    'SBSS': {'next': 'BIG', 'conf': 68},
    'BBSB': {'next': 'SMALL', 'conf': 72},
    'SSBS': {'next': 'BIG', 'conf': 72},
    'BSSS': {'next': 'BIG', 'conf': 80},
    'SBBB': {'next': 'SMALL', 'conf': 80},
    'BBBBB': {'next': 'SMALL', 'conf': 90},
    'SSSSS': {'next': 'BIG', 'conf': 90},
    'BBBBBS': {'next': 'SMALL', 'conf': 86},
    'SSSSSB': {'next': 'BIG', 'conf': 86},
    'BBBSS': {'next': 'SMALL', 'conf': 76},
    'SSSBB': {'next': 'BIG', 'conf': 76},
    'BSBSB': {'next': 'BIG', 'conf': 62},
    'SBSBS': {'next': 'SMALL', 'conf': 62},
    'BBSSB': {'next': 'SMALL', 'conf': 70},
    'SSBBS': {'next': 'BIG', 'conf': 70},
    'BSSBB': {'next': 'SMALL', 'conf': 70},
    'SBBSS': {'next': 'BIG', 'conf': 70},
    'BSSSS': {'next': 'BIG', 'conf': 84},
    'SBBBB': {'next': 'SMALL', 'conf': 84},
    'BBBSB': {'next': 'SMALL', 'conf': 78},
    'SSSBS': {'next': 'BIG', 'conf': 78},
    'BSBBS': {'next': 'BIG', 'conf': 66},
    'SBSSB': {'next': 'SMALL', 'conf': 66},
    'BBBBBB': {'next': 'SMALL', 'conf': 92},
    'SSSSSS': {'next': 'BIG', 'conf': 92},
    'BBBSSS': {'next': 'SMALL', 'conf': 85},
    'SSSBBB': {'next': 'BIG', 'conf': 85},
    'BBSSBB': {'next': 'SMALL', 'conf': 83},
    'SSBBSS': {'next': 'BIG', 'conf': 83},
    'BSBSBS': {'next': 'BIG', 'conf': 74},
    'SBSBSB': {'next': 'SMALL', 'conf': 74},
    'BBBBSS': {'next': 'SMALL', 'conf': 86},
    'SSSSBB': {'next': 'BIG', 'conf': 86},
    'BBBBBS': {'next': 'SMALL', 'conf': 90},
    'SSSSSB': {'next': 'BIG', 'conf': 90},
    'BBBBBBB': {'next': 'SMALL', 'conf': 93},
    'SSSSSSS': {'next': 'BIG', 'conf': 93},
    'BSBSBSB': {'next': 'BIG', 'conf': 76},
    'SBSBSBS': {'next': 'SMALL', 'conf': 76},
    'BBBSSSS': {'next': 'SMALL', 'conf': 76},
    'SSSBBBB': {'next': 'BIG', 'conf': 76},
    'BBBSSBB': {'next': 'SMALL', 'conf': 78},
    'SSSBBSS': {'next': 'BIG', 'conf': 78},
    'BBBBSSS': {'next': 'SMALL', 'conf': 86},
    'SSSSBBB': {'next': 'BIG', 'conf': 86},
    'BBBBBBBB': {'next': 'SMALL', 'conf': 96},
    'SSSSSSSS': {'next': 'BIG', 'conf': 96},
    'BSBSBSBS': {'next': 'BIG', 'conf': 78},
    'SBSBSBSB': {'next': 'SMALL', 'conf': 78},
    'BBBBSSSS': {'next': 'SMALL', 'conf': 86},
    'SSSSBBBB': {'next': 'BIG', 'conf': 86},
    'BBSSBBSS': {'next': 'SMALL', 'conf': 85},
    'SSBBSSBB': {'next': 'BIG', 'conf': 85},
    'BBBSSSBB': {'next': 'SMALL', 'conf': 86},
    'SSSBBBSS': {'next': 'BIG', 'conf': 86},
    'BBBBBBSS': {'next': 'SMALL', 'conf': 90},
    'SSSSSSBB': {'next': 'BIG', 'conf': 90},
    'SSSBBSSS': {'next': 'BIG', 'conf': 86},
    'BBBSSBBB': {'next': 'SMALL', 'conf': 86},
    'BBSBB': {'next': 'SMALL', 'conf': 68},
    'SSBSS': {'next': 'BIG', 'conf': 68},
    'BBBSBB': {'next': 'SMALL', 'conf': 76},
    'SSSBSS': {'next': 'BIG', 'conf': 76},
    'BBBSBBB': {'next': 'SMALL', 'conf': 80},
    'SSSBSSS': {'next': 'BIG', 'conf': 80},
    'BBSBS': {'next': 'SMALL', 'conf': 67},
    'SSBSB': {'next': 'BIG', 'conf': 67},
    'BBSBSB': {'next': 'SMALL', 'conf': 64},
    'SSBSBS': {'next': 'BIG', 'conf': 64},
    'BBSBB': {'next': 'SMALL', 'conf': 68},
    'BBBSB': {'next': 'SMALL', 'conf': 78},
    # Dragon streaks (6x-12x)
    'BBBBBB': {'next': 'SMALL', 'conf': 94},
    'SSSSSS': {'next': 'BIG', 'conf': 94},
    'BBBBBBB': {'next': 'SMALL', 'conf': 96},
    'SSSSSSS': {'next': 'BIG', 'conf': 96},
    'BBBBBBBB': {'next': 'SMALL', 'conf': 98},
    'SSSSSSSS': {'next': 'BIG', 'conf': 98},
}

# ---- LTS v10 (HTML থেকে নেওয়া) ----
def lts_analyze(types):
    if len(types) < 3:
        return None
    
    streak = 1
    for i in range(1, len(types)):
        if types[i] == types[0]:
            streak += 1
        else:
            break
    
    cur_side = 'BIG' if types[0] == 'B' else 'SMALL'
    opp_side = 'SMALL' if cur_side == 'BIG' else 'BIG'
    
    # POST-TRANSITION RIDE
    if lts_state['post_trans_ride_for'] > 0 and streak < 4:
        lts_state['post_trans_ride_for'] -= 1
        return {
            'is_active': True,
            'phase': 'POST_TRANS',
            'streak': streak,
            'cur_side': cur_side,
            'opp_side': opp_side,
            'decision': 'POST_TRANS_RIDE',
            'predicted_size': cur_side,
            'conf': 78,
            'note': f'🌊 PostTrans RIDE → {cur_side}'
        }
    
    # BLOCK PATTERN DETECT
    if streak < 4:
        block = detect_block_pattern(types)
        if block:
            return {
                'is_active': True,
                'phase': 'BLOCK',
                'streak': streak,
                'cur_side': cur_side,
                'opp_side': opp_side,
                'decision': 'BLOCK_RIDE',
                'predicted_size': block['ride_predict'],
                'conf': 82,
                'note': block['note']
            }
        return None
    
    # TREND SIDE RESET
    if lts_state['trend_side'] != cur_side:
        lts_state['trend_side'] = cur_side
        lts_state['wrong_breaks'] = 0
        lts_state['ride_mode'] = False
        lts_state['post_trans_ride_for'] = 0
    
    phase = 'DRAGON' if streak >= 7 else 'EXTREME' if streak >= 6 else 'STRONG' if streak >= 5 else 'ACTIVE'
    lts_state['phase'] = phase
    
    # 4x: BREAK (86%)
    if streak == 4:
        return {
            'is_active': True,
            'phase': phase,
            'streak': streak,
            'cur_side': cur_side,
            'opp_side': opp_side,
            'decision': 'BLEND_BREAK',
            'predicted_size': opp_side,
            'conf': 86,
            'note': f'🔶 4x {cur_side} → BREAK 86%'
        }
    
    # 5x+: RIDE_FORCED if ride_mode
    if lts_state['ride_mode']:
        return {
            'is_active': True,
            'phase': phase,
            'streak': streak,
            'cur_side': cur_side,
            'opp_side': opp_side,
            'decision': 'RIDE_FORCED',
            'predicted_size': cur_side,
            'conf': 74,
            'note': f'🛡️ RIDE_FORCED {streak}x [{cur_side}]'
        }
    
    # 5x+: ANALYZE_BLEND
    return {
        'is_active': True,
        'phase': phase,
        'streak': streak,
        'cur_side': cur_side,
        'opp_side': opp_side,
        'decision': 'ANALYZE_BLEND',
        'predicted_size': cur_side,
        'conf': 68,
        'note': f'📊 {streak}x {cur_side} RIDE 52%'
    }

def detect_block_pattern(types):
    if len(types) < 6:
        return None
    
    streak = 1
    while streak < len(types) and types[streak] == types[0]:
        streak += 1
    
    prev_start = streak
    prev_block = 0
    while prev_start + prev_block < len(types) and types[prev_start + prev_block] == types[prev_start]:
        prev_block += 1
    
    if prev_block < 2:
        return None
    
    pp_start = prev_start + prev_block
    pp_block = 0
    while pp_start + pp_block < len(types) and types[pp_start + pp_block] == types[pp_start]:
        pp_block += 1
    
    if pp_block < 2:
        return None
    
    block_size = prev_block
    confirm_size = pp_block
    
    if abs(block_size - confirm_size) <= 1 and streak < block_size:
        side = 'BIG' if types[0] == 'B' else 'SMALL'
        return {
            'block_size': block_size,
            'streak': streak,
            'ride_predict': side,
            'note': f'🔲 BLOCK_{block_size} mid({streak}/{block_size}) → RIDE {side}'
        }
    return None

# ---- LTS Track Result (HTML থেকে) ----
def lts_track_result(lts, predicted, actual):
    if not lts or not lts.get('is_active'):
        return
    
    won = predicted == actual
    
    if lts['decision'] == 'POST_TRANS_RIDE':
        if won:
            lts_state['post_trans_ride_for'] = max(0, lts_state['post_trans_ride_for'] - 1)
        else:
            lts_state['post_trans_ride_for'] = 0
    
    elif lts['decision'] == 'BLEND_BREAK' or lts['decision'] == 'ANALYZE_BLEND':
        if won:
            lts_state['wrong_breaks'] = max(0, lts_state['wrong_breaks'] - 1)
            if lts_state['wrong_breaks'] == 0:
                lts_state['ride_mode'] = False
        else:
            lts_state['wrong_breaks'] += 1
            lts_state['ride_mode'] = True
    
    elif lts['decision'] == 'RIDE_FORCED':
        if not won:
            lts_state['ride_mode'] = False
            lts_state['wrong_breaks'] = 0
            lts_state['post_trans_ride_for'] = 3

# ---- LB Shield (HTML থেকে) ----
def lb_shield(last_actual_side, consecutive_losses):
    if consecutive_losses >= 2:
        return 'SMALL' if last_actual_side == 'BIG' else 'BIG'
    return None

# ---- Zigzag Detection ----
def detect_zigzag(types):
    if len(types) < 3:
        return None
    
    alt_count = 0
    for i in range(min(10, len(types) - 1)):
        if types[i] != types[i + 1]:
            alt_count += 1
        else:
            break
    
    if alt_count >= 2:
        if alt_count >= 6:
            return {
                'is_zigzag': True,
                'alt_depth': alt_count,
                'next': 'BIG' if types[0] == 'S' else 'SMALL',
                'conf': min(92, 52 + alt_count * 6),
                'phase': 'EXHAUSTING'
            }
        else:
            return {
                'is_zigzag': True,
                'alt_depth': alt_count,
                'next': 'SMALL' if types[0] == 'B' else 'BIG',
                'conf': min(85, 62 + alt_count * 4),
                'phase': 'ACTIVE'
            }
    return None

# ---- Markov Chain ----
def markov_chain(types):
    if len(types) < 6:
        return None
    
    bb = bs = sb = ss = 0
    for i in range(len(types) - 1):
        if types[i] == 'B' and types[i+1] == 'B':
            bb += 1
        elif types[i] == 'B' and types[i+1] == 'S':
            bs += 1
        elif types[i] == 'S' and types[i+1] == 'B':
            sb += 1
        elif types[i] == 'S' and types[i+1] == 'S':
            ss += 1
    
    cur = types[0]
    if cur == 'B':
        total = bb + bs
        if total > 0:
            return {'next': 'BIG' if bb/total >= bs/total else 'SMALL', 'conf': 60 + max(bb, bs)/total * 30}
    else:
        total = sb + ss
        if total > 0:
            return {'next': 'BIG' if sb/total >= ss/total else 'SMALL', 'conf': 60 + max(sb, ss)/total * 30}
    return None

# ---- CPU Analyze ----
def cpu_analyze(types):
    if len(types) < 3:
        return None
    
    for length in range(8, 2, -1):
        if len(types) >= length:
            pat = ''.join(types[:length])
            if pat in CPU_PATTERN_DB:
                return CPU_PATTERN_DB[pat]
    
    # Streak detection
    streak = 1
    for i in range(1, len(types)):
        if types[i] == types[0]:
            streak += 1
        else:
            break
    
    # LTS-aware streak handling
    if streak >= 4:
        # Check if ride_mode active
        if lts_state['ride_mode']:
            return {'next': 'BIG' if types[0] == 'B' else 'SMALL', 'conf': 72}
        return {'next': 'SMALL' if types[0] == 'B' else 'BIG', 'conf': min(86, 70 + streak * 3)}
    elif streak >= 3:
        return {'next': 'SMALL' if types[0] == 'B' else 'BIG', 'conf': 72}
    
    return None

# ---- Motherboard Decision (10-Engine) ----
def motherboard_decision(types):
    if len(types) < 3:
        return {'size': 'BIG', 'confidence': 70, 'method': 'DEFAULT'}
    
    scores = {'BIG': 0, 'SMALL': 0}
    methods = []
    engine_count = 0
    
    # 1. LTS v10 (Highest priority)
    lts = lts_analyze(types)
    if lts and lts.get('is_active'):
        scores[lts['predicted_size']] += lts['conf'] * 0.5
        methods.append(f"LTS:{lts['predicted_size']}({lts['conf']}%)")
        engine_count += 1
    
    # 2. CPU Pattern
    cpu = cpu_analyze(types)
    if cpu:
        scores[cpu['next']] += cpu['conf'] * 0.4
        methods.append(f"CPU:{cpu['next']}({cpu['conf']}%)")
        engine_count += 1
    
    # 3. Zigzag
    zz = detect_zigzag(types)
    if zz:
        scores[zz['next']] += zz['conf'] * 0.3
        methods.append(f"ZZ:{zz['next']}({zz['conf']}%)")
        engine_count += 1
    
    # 4. Markov
    markov = markov_chain(types)
    if markov:
        scores[markov['next']] += markov['conf'] * 0.25
        methods.append(f"MARKOV:{markov['next']}({markov['conf']}%)")
        engine_count += 1
    
    # 5. Balance
    big_count = sum(1 for t in types[:10] if t == 'B')
    if big_count >= 7:
        scores['SMALL'] += 20
        methods.append("BALANCE:BIG_DOM→SMALL")
        engine_count += 1
    elif big_count <= 3:
        scores['BIG'] += 20
        methods.append("BALANCE:SMALL_DOM→BIG")
        engine_count += 1
    
    # 6. Level adjustment
    if current_level == 2:
        temp = scores['BIG']
        scores['BIG'] = scores['SMALL']
        scores['SMALL'] = temp
        methods.append("LEVEL2_INVERT")
    elif current_level == 3:
        if big_count >= 6:
            scores['SMALL'] += 15
            methods.append("LEVEL3_DEEP→SMALL")
        else:
            scores['BIG'] += 15
            methods.append("LEVEL3_DEEP→BIG")
    
    total = scores['BIG'] + scores['SMALL']
    if total == 0:
        return {'size': 'BIG', 'confidence': 65, 'method': 'FALLBACK'}
    
    final = 'BIG' if scores['BIG'] >= scores['SMALL'] else 'SMALL'
    conf = min(97, max(55, int((max(scores['BIG'], scores['SMALL']) / total) * 100)))
    
    return {
        'size': final,
        'confidence': conf,
        'method': ' | '.join(methods[:4]),
        'engine_count': engine_count
    }

# ---- Select Number ----
def select_number(pred_size, history):
    if pred_size == 'BIG':
        pool = [5, 6, 7, 8, 9]
    else:
        pool = [0, 1, 2, 3, 4]
    
    if not history:
        return pool[0] if pred_size == 'BIG' else 0
    
    # Frequency in last 15
    freq = {n: 0 for n in pool}
    for h in history[:15]:
        if h in freq:
            freq[h] += 1
    
    # Cold numbers get priority
    sorted_nums = sorted(pool, key=lambda n: (freq[n], random.random()))
    return sorted_nums[0]

# ---- LB Shield Apply ----
def apply_lb_shield(pred, last_actual_side, consecutive_losses):
    if consecutive_losses >= 2:
        shield_side = 'SMALL' if last_actual_side == 'BIG' else 'BIG'
        if shield_side != pred['size']:
            pred['size'] = shield_side
            pred['confidence'] = min(97, pred['confidence'] + 5)
            pred['method'] += ' | LB_SHIELD_ACTIVE'
    return pred

# ---- Main Prediction ----
def furious_predict(data):
    if not data:
        return {'size': 'BIG', 'number': 7, 'confidence': 70, 'method': 'DEFAULT', 'streak': 0}
    
    numbers = [d['number'] for d in data[:20]]
    types = ['B' if n >= 5 else 'S' for n in numbers]
    
    # Get prediction from motherboard
    result = motherboard_decision(types)
    
    # Apply LB Shield if needed
    if len(history_data) > 0:
        last_actual = history_data[0]['side']
        result = apply_lb_shield(result, last_actual, loss_streak)
    
    number = select_number(result['size'], numbers)
    
    return {
        'size': result['size'],
        'number': number,
        'confidence': result['confidence'],
        'method': result['method'],
        'streak': len(types[:10])
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

# ==================== হাওয়ারলি রিপোর্ট ====================
async def send_hourly_report():
    global hourly_stats, last_hour_report_time

    if time.time() - last_hour_report_time >= 3600:
        total = hourly_stats['total_rounds']
        wins = hourly_stats['total_wins']
        losses = hourly_stats['total_losses']
        win_rate = (wins / total * 100) if total > 0 else 0

        report_msg = (
            f"📊 *HOURLY PERFORMANCE REPORT*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🕐 *TIME:* {datetime.now().strftime('%I:%M %p')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔄 *TOTAL ROUNDS:* `{total}`\n"
            f"✅ *TOTAL WINS:* `{wins}`\n"
            f"❌ *TOTAL LOSSES:* `{losses}`\n"
            f"⭐ *JACKPOTS:* `{hourly_stats['jackpots']}`\n"
            f"📈 *WIN RATE:* `{win_rate:.1f}%`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 *BEST WIN STREAK:* `{hourly_stats['max_win_streak']}x`\n"
            f"📉 *WORST LOSS STREAK:* `{hourly_stats['max_loss_streak']}x`\n"
            f"🔥 *CURRENT STREAK:* `{hourly_stats['current_streak']}x {hourly_stats['streak_type']}`\n"
            f"👑 *CURRENT LEVEL:* `{current_level}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ @FURIOUS_AI_BOT"
        )
        try:
            await bot.send_message(chat_id=CHAT_ID, text=report_msg, parse_mode="Markdown")
        except:
            pass

        hourly_stats = {
            'total_rounds': 0,
            'total_wins': 0,
            'total_losses': 0,
            'max_win_streak': 0,
            'max_loss_streak': 0,
            'current_streak': 0,
            'streak_type': 'WIN',
            'jackpots': 0
        }
        last_hour_report_time = time.time()

# ==================== মেইন লুপ ====================
async def prediction_bot():
    global total_wins, total_losses, total_rounds
    global current_streak, best_streak, loss_streak
    global current_level, history_data
    global last_predicted_period, last_predicted_signal
    global last_predicted_num, last_predicted_conf
    global prediction_sent_for_period, hourly_stats

    print("🔥 FURIOUS AI BOT v2 STARTED...")
    print("📡 MODE: 1 MIN WINGO")
    print("🧠 ENGINE: 10-ENGINE FURIOUS SYSTEM (HTML Clone)")
    print("✅ LTS v10 + LB Shield + Jackpot Tracking")
    print("📊 ORDER: RESULT → PREDICTION")
    print("━━━━━━━━━━━━━━━━━━━━")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                "🔥 *FURIOUS AI BOT v2* 🔥\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🧠 *ENGINE:* 10-ENGINE FURIOUS SYSTEM\n"
                "📡 *MODE:* 1 MIN WINGO\n"
                "✅ *LTS v10 + LB Shield*\n"
                "⭐ *Jackpot = WIN*\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "⏳ WAITING FOR FIRST SIGNAL..."
            ),
            parse_mode="Markdown"
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

            # ============================================================
            # 🔥 STEP 1: RESULT CHECK (প্রথমে রেজাল্ট)
            # ============================================================
            if last_predicted_period == latest_issue and last_predicted_signal is not None:
                is_win = (last_predicted_signal == actual_type)
                is_jackpot = (actual_num == last_predicted_num)
                
                # LTS Track Result
                lts = lts_analyze(['B' if n >= 5 else 'S' for n in [d['number'] for d in history_data[:10]]])
                if lts and lts.get('is_active'):
                    lts_track_result(lts, last_predicted_signal, actual_type)

                if is_win:
                    total_wins += 1
                    hourly_stats['total_wins'] += 1
                    current_streak += 1
                    if current_streak > best_streak:
                        best_streak = current_streak
                    loss_streak = 0
                    current_level = 1
                    status = "✅ WIN"

                    if hourly_stats['streak_type'] == 'WIN':
                        hourly_stats['current_streak'] += 1
                    else:
                        hourly_stats['current_streak'] = 1
                        hourly_stats['streak_type'] = 'WIN'
                    if hourly_stats['current_streak'] > hourly_stats['max_win_streak']:
                        hourly_stats['max_win_streak'] = hourly_stats['current_streak']

                    # ⭐ Jackpot = WIN হিসাবে কাউন্ট
                    if is_jackpot:
                        hourly_stats['jackpots'] += 1
                        status = "✅ WIN ⭐ JACKPOT!"

                else:
                    total_losses += 1
                    hourly_stats['total_losses'] += 1
                    current_streak = 0
                    loss_streak += 1
                    current_level = min(loss_streak + 1, 3)
                    status = "❌ LOSS"

                    if hourly_stats['streak_type'] == 'LOSS':
                        hourly_stats['current_streak'] += 1
                    else:
                        hourly_stats['current_streak'] = 1
                        hourly_stats['streak_type'] = 'LOSS'
                    if hourly_stats['current_streak'] > hourly_stats['max_loss_streak']:
                        hourly_stats['max_loss_streak'] = hourly_stats['current_streak']

                total_rounds += 1
                hourly_stats['total_rounds'] += 1

                total_games = total_wins + total_losses
                win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0

                result_msg = (
                    f"🎯 *RESULT UPDATE*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: `#{latest_issue[-5:]}`\n"
                    f"🎯 PREDICTED: `{last_predicted_signal}` → `{last_predicted_num}`\n"
                    f"🎰 ACTUAL: `{actual_num}` (`{actual_type}`)\n"
                    f"📌 RESULT: `{status}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 WIN RATE: `{win_rate:.1f}%` ({total_wins}W/{total_losses}L)\n"
                    f"🔥 STREAK: `{current_streak:+d}`\n"
                    f"👑 LEVEL: `{current_level}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚡ @FURIOUS_AI_BOT"
                )

                try:
                    await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                    await asyncio.sleep(1)
                except:
                    pass

                await send_hourly_report()

                last_predicted_period = None
                last_predicted_signal = None
                last_predicted_num = None
                last_predicted_conf = 0

            # ============================================================
            # 🔥 STEP 2: NEW PREDICTION (রেজাল্টের পর)
            # ============================================================
            next_period = str(int(latest_issue) + 1)
            print(f"🎯 NEXT PERIOD: {next_period}")

            if not prediction_sent_for_period.get(next_period, False):
                pred = furious_predict(history_data)

                prediction_msg = (
                    f"🔥 *FURIOUS AI PREDICTION* 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: `#{next_period[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 *PREDICTION:* `{pred['size']}`\n"
                    f"🔢 *TARGET NUMBER:* `{pred['number']}`\n"
                    f"⚡ *CONFIDENCE:* `{pred['confidence']}%`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 *ENGINE:* `{pred['method']}`\n"
                    f"📈 *STREAK:* `{pred['streak']}x`\n"
                    f"👑 *LEVEL:* `{current_level}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ *RESULT AWAITING...*\n"
                    f"⚡ @FURIOUS_AI_BOT"
                )

                last_predicted_period = next_period
                last_predicted_signal = pred['size']
                last_predicted_num = pred['number']
                last_predicted_conf = pred['confidence']
                prediction_sent_for_period[next_period] = True

                try:
                    await bot.send_message(chat_id=CHAT_ID, text=prediction_msg, parse_mode="Markdown")
                    print(f"✅ PREDICTION: {next_period} → {pred['size']} ({pred['number']})")
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
    print("🔥 FURIOUS AI BOT v2")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 10-ENGINE FURIOUS SYSTEM (HTML Clone)")
    print("✅ LTS v10 + LB Shield")
    print("⭐ Jackpot = WIN হিসাবে কাউন্ট")
    print("📊 ORDER: RESULT → PREDICTION")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
