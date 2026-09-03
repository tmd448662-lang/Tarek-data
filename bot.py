import asyncio
import time
import requests
import os
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Bot

# ==================== RENDER WEB SERVICE PORT BINDING ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"SUPER HYBRID V5 BOT is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ==================== KEEP-ALIVE ====================
def keep_alive():
    while True:
        try:
            time.sleep(600)
            port = int(os.environ.get("PORT", 8080))
            requests.get(f"http://localhost:{port}/", timeout=5)
        except:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

# ==================== BOT CONFIG ====================
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"
RAW_API = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

bot = Bot(token=BOT_TOKEN)

# ==================== STATS ====================
total_wins = 0
total_losses = 0
jackpots = 0
loss_streak = 0
current_level = 1
consecutive_losses = 0
total_rounds = 0
history_data = []

# ==================== BIG/SMALL STATS ====================
bs_stats = {
    'wins': 0,
    'losses': 0,
    'total': 0,
    'streak': 0,
    'max_win_streak': 0,
    'max_loss_streak': 0,
    'current_streak': 0,
    'streak_type': 'WIN',
    'win_rate': 0
}

# ==================== COLOR STATS ====================
color_stats = {
    'wins': 0,
    'losses': 0,
    'total': 0,
    'streak': 0,
    'max_win_streak': 0,
    'max_loss_streak': 0,
    'current_streak': 0,
    'streak_type': 'WIN',
    'win_rate': 0
}

# ==================== HOURLY STATS ====================
hourly_bs_stats = {
    'wins': 0,
    'losses': 0,
    'total': 0,
    'max_win_streak': 0,
    'max_loss_streak': 0,
    'current_streak': 0,
    'streak_type': 'WIN'
}

hourly_color_stats = {
    'wins': 0,
    'losses': 0,
    'total': 0,
    'max_win_streak': 0,
    'max_loss_streak': 0,
    'current_streak': 0,
    'streak_type': 'WIN'
}

# ==================== STAKE SYSTEM ====================
BASE_STAKE = 10

def get_stake(bs_streak, color_streak):
    if bs_streak <= -3:
        bs_stake = BASE_STAKE * 4
    elif bs_streak <= -2:
        bs_stake = BASE_STAKE * 2
    elif bs_streak <= -1:
        bs_stake = BASE_STAKE * 1.5
    else:
        bs_stake = BASE_STAKE
    
    if color_streak <= -3:
        color_stake = BASE_STAKE * 4
    elif color_streak <= -2:
        color_stake = BASE_STAKE * 2
    else:
        color_stake = BASE_STAKE
    
    return int(bs_stake), int(color_stake)

# ==================== COLOR SYSTEM ====================
def get_color(number):
    if number in [0, 5]:
        return "VIOLET", "🔮"
    elif number in [1, 3, 7, 9]:
        return "GREEN", "🟢"
    else:
        return "RED", "🔴"

# ==================== HYBRID V5 ENGINES (7টি) ====================

def core_engine(data):
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 76}
    weights = [9, 7, 5, 3, 2, 1, 1, 1]
    score = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score += weights[i]
        else:
            score -= weights[i]
    pred = "BIG" if score >= 0 else "SMALL"
    conf = 87 if abs(score) >= 3 else 76
    return {"prediction": pred, "confidence": conf}

def smart_engine(data):
    if len(data) < 4:
        return {"prediction": "SMALL", "confidence": 75}
    sides = [d['side'] for d in data[:4]]
    if sides[0] == sides[3] and sides[1] == sides[2]:
        pred = "SMALL" if sides[0] == "BIG" else "BIG"
        return {"prediction": pred, "confidence": 92}
    return {"prediction": "SMALL", "confidence": 75}

def hybrid_engine(data):
    if len(data) < 5:
        return {"prediction": "BIG", "confidence": 73}
    math_num = (data[0]['number'] + data[1]['number']) % 10
    pred = "BIG" if math_num >= 5 else "SMALL"
    return {"prediction": pred, "confidence": 82}

def master_engine(data):
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 73}
    score = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score += (8 - i)
        else:
            score -= (8 - i)
    pred = "BIG" if score >= 0 else "SMALL"
    return {"prediction": pred, "confidence": 95}

def advanced_engine(data):
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 87}
    weights = [9, 7, 5, 3, 2, 1, 1, 1]
    score = 0
    for i in range(min(8, len(data))):
        if data[i]['number'] >= 5:
            score += weights[i]
        else:
            score -= weights[i]
    global loss_streak
    if loss_streak >= 3:
        score = -score
    pred = "BIG" if score >= 0 else "SMALL"
    conf = 87 if abs(score) >= 3 else 76
    return {"prediction": pred, "confidence": conf + (5 if loss_streak >= 3 else 0)}

def ultimate_engine(data):
    if len(data) < 8:
        return {"prediction": "BIG", "confidence": 70}
    sides = [d['side'] for d in data[:8]]
    streak = 1
    for i in range(1, len(sides)):
        if sides[i] == sides[i-1]:
            streak += 1
        else:
            break
    if streak >= 5:
        pred = "SMALL" if sides[0] == "BIG" else "BIG"
        return {"prediction": pred, "confidence": 95}
    big_count = sides.count("BIG")
    pred = "BIG" if big_count >= 4 else "SMALL"
    conf = 70 + (abs(big_count - 4) * 5)
    return {"prediction": pred, "confidence": min(95, conf)}

def dark_x_engine(data):
    if len(data) < 3:
        return {"prediction": "BIG", "confidence": 50}
    sides = [d['side'] for d in data[:10]]
    last1 = sides[0] if len(sides) > 0 else "BIG"
    last2 = sides[1] if len(sides) > 1 else "BIG"
    if last1 == "SMALL":
        pred = "BIG"
        conf = 75
    elif last1 == "BIG":
        pred = "SMALL"
        conf = 60
    else:
        pred = "BIG"
        conf = 50
    if last1 == "BIG" and last2 == "BIG":
        pred = "SMALL"
        conf = 90
    elif last1 == "SMALL" and last2 == "SMALL":
        pred = "BIG"
        conf = 95
    global current_level
    if current_level == 3:
        latest = int(data[0]['number'])
        pred = "SMALL" if latest >= 5 else "BIG"
        conf = 99
    return {"prediction": pred, "confidence": conf}

# ==================== ORAIN AI ENGINE (12 Experts) ====================

def orain_engine(data):
    """ORAIN AI - 12 Expert Ensemble"""
    if not data or len(data) < 8:
        return {"prediction": "BIG", "confidence": 60}
    
    # ডাটা প্রস্তুত
    numbers = [d['number'] for d in data[:30]]
    sides = [1 if n >= 5 else -1 for n in numbers]
    L = len(sides)
    last = sides[-1] if sides else 1
    
    # স্ট্রিক
    streak = 1
    for i in range(L-2, -1, -1):
        if sides[i] == last:
            streak += 1
        else:
            break
    
    # ফ্লিপ রেট
    flips = 0
    for i in range(1, min(14, L)):
        if sides[i] != sides[i-1]:
            flips += 1
    flip_rate = flips / min(13, L-1) if L > 1 else 0.5
    
    # বিগ রেশিও
    big10 = sum(1 for s in sides[-10:] if s > 0) / min(10, L) if L >= 10 else 0.5
    big20 = sum(1 for s in sides[-20:] if s > 0) / min(20, L) if L >= 20 else 0.5
    
    # EMA
    ema = 0
    alpha = 0.30
    for i, n in enumerate(numbers[-20:]):
        v = (n - 4.5) / 4.5
        ema = alpha * v + (1 - alpha) * ema if i > 0 else v
    
    # ১২টি এক্সপার্টের ভোট
    votes = {}
    
    # 1. Streak Expert
    votes['streak'] = -last * min(streak / 5, 1.0) if streak >= 4 else last * 0.58
    
    # 2. Alternation
    votes['alternation'] = (flip_rate - 0.5) * 2.4 * (-last)
    
    # 3. Momentum
    votes['momentum'] = max(-1, min(1, ema * 1.75))
    
    # 4. Reversion
    votes['reversion'] = max(-1, min(1, (0.5 - big20) * 2.8 + (0.5 - big10) * 1.2))
    
    # 5. Markov2
    if L >= 8:
        tbl = {}
        for i in range(2, L):
            key = f"{sides[i-2]}|{sides[i-1]}"
            if key not in tbl:
                tbl[key] = {'b': 0, 'sm': 0}
            if sides[i] > 0:
                tbl[key]['b'] += 1
            else:
                tbl[key]['sm'] += 1
        cur = f"{sides[L-2]}|{sides[L-1]}"
        c = tbl.get(cur)
        if c and (c['b'] + c['sm']) >= 3:
            votes['markov2'] = max(-1, min(1, ((c['b'] + 0.5) / (c['b'] + c['sm'] + 1) - 0.5) * 2.6))
        else:
            votes['markov2'] = 0
    else:
        votes['markov2'] = 0
    
    # 6. Cluster/Gap
    gap_big = 0
    for i in range(L-1, -1, -1):
        if numbers[i] >= 5:
            gap_big += 1
        else:
            break
    gap_small = 0
    for i in range(L-1, -1, -1):
        if numbers[i] < 5:
            gap_small += 1
        else:
            break
    votes['cluster'] = max(-1, min(1, (min(gap_big, 7) * 0.13) - (min(gap_small, 7) * 0.13)))
    
    # 7. Cycle
    d = int(str(data[0]['issueNumber'])[-1]) if data else 0
    if L >= 12 and d >= 0:
        b = 0
        t = 0
        for i in range(L):
            if ((d - (L-1-i)) % 10 + 10) % 10 == d % 10:
                t += 1
                if sides[i] > 0:
                    b += 1
        votes['cycle'] = max(-1, min(1, ((b + 0.5) / (t + 1) - 0.5) * 2.4)) if t >= 3 else 0
    else:
        votes['cycle'] = 0
    
    # 8. Markov3
    if L >= 10:
        tbl = {}
        for i in range(3, L):
            key = f"{sides[i-3]}|{sides[i-2]}|{sides[i-1]}"
            if key not in tbl:
                tbl[key] = {'b': 0, 'sm': 0}
            if sides[i] > 0:
                tbl[key]['b'] += 1
            else:
                tbl[key]['sm'] += 1
        cur = f"{sides[L-3]}|{sides[L-2]}|{sides[L-1]}"
        c = tbl.get(cur)
        if c and (c['b'] + c['sm']) >= 2:
            votes['markov3'] = max(-1, min(1, ((c['b'] + 0.5) / (c['b'] + c['sm'] + 1) - 0.5) * 3.0))
        else:
            votes['markov3'] = 0
    else:
        votes['markov3'] = 0
    
    # 9. Volatility
    diffs = []
    for i in range(1, min(10, L)):
        diffs.append(abs(numbers[i] - numbers[i-1]))
    avg_diff = sum(diffs) / len(diffs) if diffs else 4.5
    votes['volatility'] = max(-1, min(1, ((avg_diff - 4.5) / 4.5) * (0.5 - big10) * 2.5))
    
    # 10. Volume Bias
    b5 = sum(1 for s in sides[-5:] if s > 0) / min(5, L) if L >= 5 else 0.5
    votes['volumeBias'] = max(-1, min(1, -(b5 - big20) * 3.5 + (0.5 - big20) * 1.8))
    
    # 11. Entropy
    ent = -(big20 * (big20 and 1) * 0.0001 + (1-big20) * (1-big20 and 1) * 0.0001)
    # সহজ এনট্রপি
    b = sum(1 for s in sides[-20:] if s > 0)
    s_cnt = len(sides[-20:]) - b
    ph = b / (len(sides[-20:]) or 1)
    pl = s_cnt / (len(sides[-20:]) or 1)
    entropy = -(ph * (ph and 1) * 0.0001 + pl * (pl and 1) * 0.0001)
    if entropy > 0.90:
        votes['entropy'] = -last * 0.70
    elif entropy > 0.75:
        votes['entropy'] = -last * 0.35
    elif entropy < 0.45:
        votes['entropy'] = last * 0.65
    else:
        votes['entropy'] = 0
    
    # 12. Session Drift
    if L >= 15:
        h1 = sum(1 for s in sides[-30:-15] if s > 0) / 15
        h2 = sum(1 for s in sides[-15:] if s > 0) / 15
        drift = h2 - h1
        votes['sessionDrift'] = max(-1, min(1, drift * 2.8)) if abs(drift) > 0.20 else max(-1, min(1, -drift * 1.2))
    else:
        votes['sessionDrift'] = 0
    
    # ওয়েটিং
    weights = {
        'streak': 1.2, 'alternation': 1.0, 'momentum': 1.3,
        'reversion': 1.1, 'markov2': 1.0, 'cluster': 0.9,
        'cycle': 0.8, 'markov3': 1.1, 'volatility': 0.9,
        'volumeBias': 1.0, 'entropy': 1.2, 'sessionDrift': 1.0
    }
    
    # SureShot Level
    global loss_streak
    ss_level = 3 if loss_streak >= 2 else (2 if loss_streak == 1 else 1)
    
    # L2/L3 বুস্ট
    if ss_level == 2:
        for k in weights:
            weights[k] = weights[k] ** 1.55
    elif ss_level == 3:
        for k in weights:
            weights[k] = weights[k] ** 2.2
    
    # স্কোর
    score = 0
    wsum = 0
    for k, v in votes.items():
        w = weights.get(k, 1.0)
        score += w * v
        wsum += w
    
    norm = score / wsum if wsum > 0 else 0
    
    # মেজরিটি অ্যাগ্রিমেন্ট
    agree_big = sum(1 for v in votes.values() if v > 0.05)
    agree_small = sum(1 for v in votes.values() if v < -0.05)
    total_experts = len(votes)
    
    if abs(norm) < 0.08:
        if agree_big > agree_small and agree_big / total_experts >= 0.5:
            norm = 0.10
        elif agree_small > agree_big and agree_small / total_experts >= 0.5:
            norm = -0.10
    
    if ss_level == 3 and abs(norm) < 0.18:
        norm = 0.18 if norm >= 0 else -0.18
    
    pred = "BIG" if norm >= 0 else "SMALL"
    conf = min(98, max(54, 50 + abs(norm) * 68 + (12 if ss_level == 3 else 6 if ss_level == 2 else 0)))
    
    # কালার প্রেডিক্ট
    color_counts = {"RED": 0, "GREEN": 0, "VIOLET": 0}
    for n in numbers[:15]:
        color, _ = get_color(n)
        color_counts[color] += 1
    pred_color = max(color_counts, key=color_counts.get)
    color_conf = int((color_counts[pred_color] / 15) * 100) if len(numbers) >= 15 else 60
    
    return {
        "prediction": pred,
        "confidence": conf,
        "color": pred_color,
        "color_conf": color_conf,
        "ss_level": ss_level,
        "engine": "ORAIN AI (12 Experts)",
        "experts": len(votes)
    }

# ==================== MASTER HYBRID ENGINE ====================

def master_prediction(data):
    """সব ইঞ্জিনের সমন্বয়"""
    if not data:
        return "BIG", 60, 7, "GREEN", 60, "HYBRID V5"
    
    # ৭টি HYBRID V5 ইঞ্জিন
    hybrid_v5_engines = {
        'CORE': core_engine(data),
        'SMART': smart_engine(data),
        'HYBRID': hybrid_engine(data),
        'MASTER': master_engine(data),
        'ADVANCED': advanced_engine(data),
        'ULTIMATE': ultimate_engine(data),
        'DARK X': dark_x_engine(data)
    }
    
    # ORAIN AI ইঞ্জিন
    orain_result = orain_engine(data)
    
    # সব ইঞ্জিনের ভোট
    votes = {'BIG': 0, 'SMALL': 0}
    confidences = []
    best_engine = None
    best_conf = 0
    
    for name, result in hybrid_v5_engines.items():
        votes[result['prediction']] += 1
        confidences.append(result['confidence'])
        if result['confidence'] > best_conf:
            best_conf = result['confidence']
            best_engine = name
    
    # ORAIN যোগ
    votes[orain_result['prediction']] += 2  # ORAIN কে ডাবল ভোট
    confidences.append(orain_result['confidence'])
    if orain_result['confidence'] > best_conf:
        best_conf = orain_result['confidence']
        best_engine = orain_result['engine']
    
    # ফাইনাল প্রেডিকশন
    final_pred = max(votes, key=votes.get)
    avg_conf = int(sum(confidences) / len(confidences))
    
    # নম্বর জেনারেট
    if final_pred == "BIG":
        dna_value = random.randint(5, 9)
    else:
        dna_value = random.randint(0, 4)
    
    # কালার
    color = orain_result['color']
    color_conf = orain_result['color_conf']
    
    return final_pred, avg_conf, dna_value, color, color_conf, best_engine

# ==================== UPDATE STATS ====================

def update_bs_stats(is_win):
    global bs_stats, hourly_bs_stats
    if is_win:
        bs_stats['wins'] += 1
        hourly_bs_stats['wins'] += 1
        if bs_stats['streak_type'] == 'WIN':
            bs_stats['current_streak'] += 1
        else:
            bs_stats['current_streak'] = 1
            bs_stats['streak_type'] = 'WIN'
        if bs_stats['current_streak'] > bs_stats['max_win_streak']:
            bs_stats['max_win_streak'] = bs_stats['current_streak']
    else:
        bs_stats['losses'] += 1
        hourly_bs_stats['losses'] += 1
        if bs_stats['streak_type'] == 'LOSS':
            bs_stats['current_streak'] += 1
        else:
            bs_stats['current_streak'] = 1
            bs_stats['streak_type'] = 'LOSS'
        if bs_stats['current_streak'] > bs_stats['max_loss_streak']:
            bs_stats['max_loss_streak'] = bs_stats['current_streak']
    bs_stats['total'] += 1
    hourly_bs_stats['total'] += 1
    bs_stats['win_rate'] = (bs_stats['wins'] / bs_stats['total'] * 100) if bs_stats['total'] > 0 else 0

def update_color_stats(is_win):
    global color_stats, hourly_color_stats
    if is_win:
        color_stats['wins'] += 1
        hourly_color_stats['wins'] += 1
        if color_stats['streak_type'] == 'WIN':
            color_stats['current_streak'] += 1
        else:
            color_stats['current_streak'] = 1
            color_stats['streak_type'] = 'WIN'
        if color_stats['current_streak'] > color_stats['max_win_streak']:
            color_stats['max_win_streak'] = color_stats['current_streak']
    else:
        color_stats['losses'] += 1
        hourly_color_stats['losses'] += 1
        if color_stats['streak_type'] == 'LOSS':
            color_stats['current_streak'] += 1
        else:
            color_stats['current_streak'] = 1
            color_stats['streak_type'] = 'LOSS'
        if color_stats['current_streak'] > color_stats['max_loss_streak']:
            color_stats['max_loss_streak'] = color_stats['current_streak']
    color_stats['total'] += 1
    hourly_color_stats['total'] += 1
    color_stats['win_rate'] = (color_stats['wins'] / color_stats['total'] * 100) if color_stats['total'] > 0 else 0

# ==================== API FETCH ====================

def fetch_api_data():
    try:
        res = requests.get(RAW_API + "?t=" + str(int(time.time() * 1000)), timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", {}).get("list", [])
    except:
        pass
    return []

# ==================== MAIN LOOP ====================

async def prediction_bot():
    global total_wins, total_losses, jackpots, loss_streak, current_level
    global total_rounds, history_data, bs_stats, color_stats
    global hourly_bs_stats, hourly_color_stats

    print("🔥 SUPER HYBRID V5 BOT STARTED...")
    print("🧠 19 ENGINES ACTIVE: 7 HYBRID V5 + 12 ORAIN AI")
    print("📊 SEPARATE STATS FOR BIG/SMALL & COLOR")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🔥 SUPER HYBRID V5 🔥\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "🧠 19 AI ENGINES ACTIVE\n"
                 "📈 7 HYBRID V5 + 12 ORAIN AI\n"
                 "🎯 BIG/SMALL + COLOR PREDICTION\n"
                 "📊 SEPARATE STATS FOR BOTH\n"
                 "⚡ MODE: 1 MIN WINGO\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "⏳ WAITING FOR FIRST SIGNAL...",
        )
    except Exception as e:
        print(f"Startup error: {e}")

    last_period = None
    last_bs_pred = None
    last_color_pred = None
    last_bs_num = None
    last_engine = None
    last_hour_report = time.time()

    while True:
        try:
            current_sec = int(time.time()) % 60
            sleep_time = 60 - current_sec + 3
            await asyncio.sleep(sleep_time)

            history = fetch_api_data()
            if not history:
                continue

            latest_issue = str(history[0]['issueNumber'])
            actual_num = int(history[0]['number'])
            actual_color, actual_color_icon = get_color(actual_num)
            actual_bs = "BIG" if actual_num >= 5 else "SMALL"
            
            history_data = []
            for h in history[:30]:
                num = int(h['number'])
                history_data.append({
                    'issueNumber': str(h['issueNumber']),
                    'number': num,
                    'side': "BIG" if num >= 5 else "SMALL"
                })

            # ============================================================
            # CHECK RESULT
            # ============================================================
            if last_period == latest_issue:
                
                # BIG/SMALL RESULT
                if last_bs_pred is not None:
                    bs_win = (last_bs_pred == actual_bs)
                    update_bs_stats(bs_win)
                
                # COLOR RESULT
                if last_color_pred is not None:
                    color_win = (last_color_pred == actual_color)
                    update_color_stats(color_win)
                
                # STAKE
                bs_stake, color_stake = get_stake(bs_stats['streak'], color_stats['streak'])
                
                # RESULT MESSAGE
                result_msg = (
                    f"🎯 *RESULT UPDATE*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: #{latest_issue[-5:]}\n"
                    f"🎰 ACTUAL: {actual_num} ({actual_bs}) {actual_color_icon}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📈 *BIG/SMALL*\n"
                    f"🎯 PREDICTED: {last_bs_pred} → {last_bs_num}\n"
                    f"📌 RESULT: {'✅ WIN' if bs_win else '❌ LOSS'}\n"
                    f"📊 WIN RATE: {bs_stats['win_rate']:.1f}% ({bs_stats['wins']}W/{bs_stats['losses']}L)\n"
                    f"🔥 STREAK: {bs_stats['streak']:+d}\n"
                    f"💰 STAKE: {bs_stake} Taka\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎨 *COLOR*\n"
                    f"🎯 PREDICTED: {last_color_pred} {actual_color_icon}\n"
                    f"📌 RESULT: {'✅ WIN' if color_win else '❌ LOSS'}\n"
                    f"📊 WIN RATE: {color_stats['win_rate']:.1f}% ({color_stats['wins']}W/{color_stats['losses']}L)\n"
                    f"🔥 STREAK: {color_stats['streak']:+d}\n"
                    f"💰 STAKE: {color_stake} Taka\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 ENGINE: {last_engine}\n"
                    f"💎 SUPER HYBRID V5"
                )
                
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                    await asyncio.sleep(1)
                except:
                    pass
                
                last_period = None
                last_bs_pred = None
                last_color_pred = None

            # ============================================================
            # NEW PREDICTION
            # ============================================================
            next_period = str(int(latest_issue) + 1)
            
            if last_period != next_period:
                
                # মাস্টার প্রেডিকশন
                bs_pred, bs_conf, bs_num, color_pred, color_conf, engine = master_prediction(history_data)
                color_icon = "🔮" if color_pred == "VIOLET" else "🟢" if color_pred == "GREEN" else "🔴"
                
                # STAKE
                bs_stake, color_stake = get_stake(bs_stats['streak'], color_stats['streak'])
                
                # PREDICTION MESSAGE
                pred_msg = (
                    f"🔥 *SUPER HYBRID V5* 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: #{next_period[-5:]}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📈 *BIG/SMALL*\n"
                    f"🎯 PREDICTION: {bs_pred}\n"
                    f"🔢 TARGET NUMBER: {bs_num}\n"
                    f"⚡ CONFIDENCE: {bs_conf}%\n"
                    f"💰 STAKE: {bs_stake} Taka\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎨 *COLOR*\n"
                    f"🎯 PREDICTION: {color_pred} {color_icon}\n"
                    f"⚡ CONFIDENCE: {color_conf}%\n"
                    f"💰 STAKE: {color_stake} Taka\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 ENGINE: {engine}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ RESULT AWAITING...\n"
                    f"💎 SUPER HYBRID V5"
                )
                
                last_period = next_period
                last_bs_pred = bs_pred
                last_color_pred = color_pred
                last_bs_num = bs_num
                last_engine = engine
                
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=pred_msg, parse_mode="Markdown")
                except:
                    pass
            
            # ============================================================
            # HOURLY REPORT
            # ============================================================
            if time.time() - last_hour_report >= 3600:
                bs_total = hourly_bs_stats['total']
                bs_wins = hourly_bs_stats['wins']
                bs_losses = hourly_bs_stats['losses']
                bs_win_rate = (bs_wins / bs_total * 100) if bs_total > 0 else 0
                
                color_total = hourly_color_stats['total']
                color_wins = hourly_color_stats['wins']
                color_losses = hourly_color_stats['losses']
                color_win_rate = (color_wins / color_total * 100) if color_total > 0 else 0
                
                report_msg = (
                    f"📊 *HOURLY PERFORMANCE REPORT*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🕐 TIME: {datetime.now().strftime('%I:%M %p')}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📈 *BIG/SMALL STATS*\n"
                    f"🔄 TOTAL: {bs_total}\n"
                    f"✅ WINS: {bs_wins}\n"
                    f"❌ LOSSES: {bs_losses}\n"
                    f"📊 WIN RATE: {bs_win_rate:.1f}%\n"
                    f"🔥 BEST WIN STREAK: {hourly_bs_stats['max_win_streak']}x\n"
                    f"📉 WORST LOSS STREAK: {hourly_bs_stats['max_loss_streak']}x\n"
                    f"🔥 CURRENT STREAK: {hourly_bs_stats['current_streak']}x {hourly_bs_stats['streak_type']}\n\n"
                    f"🎨 *COLOR STATS*\n"
                    f"🔄 TOTAL: {color_total}\n"
                    f"✅ WINS: {color_wins}\n"
                    f"❌ LOSSES: {color_losses}\n"
                    f"📊 WIN RATE: {color_win_rate:.1f}%\n"
                    f"🔥 BEST WIN STREAK: {hourly_color_stats['max_win_streak']}x\n"
                    f"📉 WORST LOSS STREAK: {hourly_color_stats['max_loss_streak']}x\n"
                    f"🔥 CURRENT STREAK: {hourly_color_stats['current_streak']}x {hourly_color_stats['streak_type']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 19 ENGINES ACTIVE\n"
                    f"💎 SUPER HYBRID V5"
                )
                
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=report_msg, parse_mode="Markdown")
                except:
                    pass
                
                # রিসেট হাওয়ারলি স্ট্যাটস
                hourly_bs_stats = {
                    'wins': 0, 'losses': 0, 'total': 0,
                    'max_win_streak': 0, 'max_loss_streak': 0,
                    'current_streak': 0, 'streak_type': 'WIN'
                }
                hourly_color_stats = {
                    'wins': 0, 'losses': 0, 'total': 0,
                    'max_win_streak': 0, 'max_loss_streak': 0,
                    'current_streak': 0, 'streak_type': 'WIN'
                }
                last_hour_report = time.time()

        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(5)

if __name__ == '__main__':
    print("🔥 SUPER HYBRID V5 BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 19 ENGINES ACTIVE")
    print("📈 7 HYBRID V5 + 12 ORAIN AI")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
