import logging
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Configuration
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
ADMIN_ID = 5012028880

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# State tracking
user_stats = {
    "wins": 0,
    "losses": 0,
    "total": 0,
    "streak": 0,
    "level": 1
}


def generate_prediction():
    """Simulates the DNA GOD MODE V4 prediction algorithm."""
    period_id = random.randint(202609020000, 202609029999)
    pred_type = random.choice(["BIG", "SMALL"])
    confidence = round(random.uniform(85.0, 99.4), 1)
    
    if pred_type == "BIG":
        core_num = random.choice([5, 6, 7, 8, 9])
        color = "🔴 RED / 🟣 VIOLET" if core_num == 5 else "🔴 RED"
    else:
        core_num = random.choice([0, 1, 2, 3, 4])
        color = "🟢 GREEN / 🟣 VIOLET" if core_num == 0 else "🟢 GREEN"
        
    return {
        "period": period_id,
        "type": pred_type,
        "number": core_num,
        "color": color,
        "confidence": confidence,
        "level": user_stats["level"]
    }


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command."""
    user = update.effective_user
    
    welcome_text = (
        f"🧬 **TITAN ULTRA PREDICTION CORE** 🧬\n"
        f"__DNA GOD MODE V4 PROTOCOL__\n\n"
        f"👤 **User Identity:** {user.first_name}\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"🔰 **Clearance:** `VIP GOD MODE`\n"
        f"⚡ **System Status:** `ONLINE / 4ms LATENCY`\n\n"
        f"Select an operation below to generate signals or inspect system metrics:"
    )
    
    keyboard = [
        [InlineKeyboardButton("⚡ GENERATE SIGNAL", callback_data="get_signal")],
        [
            InlineKeyboardButton("📊 ENGINE STATS", callback_data="get_stats"),
            InlineKeyboardButton("⚙️ ALGO LOGIC", callback_data="get_algo")
        ],
        [InlineKeyboardButton("🔄 RESET HISTORY CACHE", callback_data="reset_cache")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles inline button interactions."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "get_signal":
        pred = generate_prediction()
        
        signal_text = (
            f"🧬 **TITAN VIP DNA V4 SIGNAL** 🧬\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **TARGET PERIOD:** `{pred['period']}`\n"
            f"🔥 **PREDICTION:** `{pred['type']}`\n"
            f"💎 **EMISSION VALUE:** `{pred['number']}`\n"
            f"🎨 **COLOR MATRIX:** {pred['color']}\n"
            f"📊 **CONFIDENCE:** `{pred['confidence']}%`\n"
            f"⚠️ **SAFETY LEVEL:** `LEVEL {pred['level']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🚀 **STATUS:** `ENGINE LINK CONFIRMED`"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ WIN", callback_data="res_win"),
                InlineKeyboardButton("❌ LOSS", callback_data="res_loss")
            ],
            [InlineKeyboardButton("⚡ NEXT SIGNAL", callback_data="get_signal")],
            [InlineKeyboardButton("🔙 MAIN MENU", callback_data="main_menu")]
        ]
        await query.edit_message_text(signal_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data == "res_win":
        user_stats["wins"] += 1
        user_stats["total"] += 1
        user_stats["streak"] = user_stats["streak"] + 1 if user_stats["streak"] >= 0 else 1
        user_stats["level"] = 1
        
        await query.edit_message_text(
            f"🎉 **MATCH TARGET WIN REGISTERED!**\n\n"
            f"Wins: `{user_stats['wins']}` | Total: `{user_stats['total']}`\n"
            f"Current Strategy Level reset to: `LEVEL 1`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚡ NEXT SIGNAL", callback_data="get_signal")]])
        )

    elif data == "res_loss":
        user_stats["losses"] += 1
        user_stats["total"] += 1
        user_stats["streak"] = user_stats["streak"] - 1 if user_stats["streak"] <= 0 else -1
        user_stats["level"] = 3 if user_stats["level"] >= 3 else user_stats["level"] + 1
        
        await query.edit_message_text(
            f"❌ **LOSS REGISTERED - BYPASS ENGAGED**\n\n"
            f"Losses: `{user_stats['losses']}` | Total: `{user_stats['total']}`\n"
            f"Martingale Level elevated to: `LEVEL {user_stats['level']}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚡ RECOVERY SIGNAL", callback_data="get_signal")]])
        )

    elif data == "get_stats":
        accuracy = round((user_stats["wins"] / user_stats["total"] * 100), 1) if user_stats["total"] > 0 else 100.0
        
        stats_text = (
            f"📊 **SERVER DATABASE AUDIT LOG**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 **WIN DECODE:** `{user_stats['wins']}`\n"
            f"🔴 **LOSS BYPASS:** `{user_stats['losses']}`\n"
            f"🔄 **CYCLES RUN:** `{user_stats['total']}`\n"
            f"⚡ **STREAK LOG:** `{user_stats['streak']}`\n"
            f"🎯 **DYNAMIC ACCURACY:** `{accuracy}%`\n"
            f"🛡️ **ACTIVE MARTINGALE:** `LEVEL {user_stats['level']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = [[InlineKeyboardButton("🔙 MAIN MENU", callback_data="main_menu")]]
        await query.edit_message_text(stats_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "get_algo":
        algo_text = (
            f"⚙️ **STRUCTURAL EQUATION METRICS**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📐 **ALGORITHM CORE:**\n"
            f"`Value = [(∑ PeriodDigits × 8) + (Last4Digits mod 7) + (PrevRound × 3)] mod 10`\n\n"
            f"🪞 **COUNTER BALANCER MIRROR:**\n"
            f"If `Round_n ≡ Round_n-1`, multi-stage inversion triggers for 5 operational rounds.\n\n"
            f"🎯 **CLASSIFICATION MATRIX:**\n"
            f"• `{0, 5}` ➔ VIOLET CORES (JACKPOT)\n"
            f"• `{6, 8}` ➔ RED / BIG\n"
            f"• `{1, 3, 7, 9}` ➔ GREEN / SMALL\n"
            f"• `{2, 4}` ➔ RED / SMALL"
        )
        keyboard = [[InlineKeyboardButton("🔙 MAIN MENU", callback_data="main_menu")]]
        await query.edit_message_text(algo_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "reset_cache":
        global user_stats
        user_stats = {"wins": 0, "losses": 0, "total": 0, "streak": 0, "level": 1}
        await query.edit_message_text(
            "⚠️ **TRANSMISSION ERASED DONE**\nHistory cache cleared successfully.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 MAIN MENU", callback_data="main_menu")]])
        )

    elif data == "main_menu":
        await start_command(update, context)


def main():
    """Starts the Telegram bot."""
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Titan DNA God Mode V4 Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
