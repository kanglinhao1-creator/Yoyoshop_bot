import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# =========================
# SETTINGS — CHANGE THESE
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Edit your products here
PRODUCTS = {
    "d86": ("💎 86 Diamonds", 5600),
    "d172": ("💎 172 Diamonds", 10600),
    "d257": ("💎 257 Diamonds", 15500),
    "d343": ("💎 343 Diamonds", 20500),
    "uc60": ("🎮 PUBG UC 60", 4300),
    "uc120": ("🎮 PUBG UC 120", 8200),
}

PAYMENT_INFO = """
💳 ငွေပေးချေမှု

KPay — YOUR_KPAY_NUMBER
WavePay — YOUR_WAVEPAY_NUMBER

ငွေလွှဲပြီး Screenshot ကို ဒီ Bot ထဲပို့ပေးပါ။
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💎 Diamonds", callback_data="diamonds")],
        [InlineKeyboardButton("🎮 PUBG UC", callback_data="uc")],
        [InlineKeyboardButton("📦 Order စစ်ရန်", callback_data="status")],
        [InlineKeyboardButton("💳 ငွေပေးချေမှု", callback_data="payment")],
    ]
    await update.message.reply_text(
        "🛒 Welcome to My Shop!\n\n"
        "ဝယ်ချင်တဲ့အမျိုးအစားကို ရွေးပါ 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def product_buttons(prefix):
    rows = []
    for key, (name, price) in PRODUCTS.items():
        if key.startswith(prefix):
            rows.append([InlineKeyboardButton(
                f"{name} — {price:,} Ks",
                callback_data=f"buy:{key}"
            )])
    return InlineKeyboardMarkup(rows)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "diamonds":
        await query.edit_message_text(
            "💎 Diamonds ရွေးပါ:",
            reply_markup=product_buttons("d")
        )

    elif data == "uc":
        await query.edit_message_text(
            "🎮 UC ရွေးပါ:",
            reply_markup=product_buttons("uc")
        )

    elif data == "payment":
        await query.edit_message_text(PAYMENT_INFO)

    elif data == "status":
        await query.edit_message_text(
            "📦 Order စစ်ရန်\n"
            "Admin ကို သင့် Order ID ပို့ပြီး စစ်ဆေးနိုင်ပါတယ်။"
        )

    elif data.startswith("buy:"):
        key = data.split(":", 1)[1]
        name, price = PRODUCTS[key]
        context.user_data["product"] = name
        context.user_data["price"] = price

        await query.message.reply_text(
            f"✅ ရွေးထားသောပစ္စည်း\n"
            f"{name}\n"
            f"💰 {price:,} Ks\n\n"
            "အခု Game ID / Player ID ကို ပို့ပါ။"
        )
        context.user_data["step"] = "game_id"

async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")

    if step == "game_id":
        context.user_data["game_id"] = update.message.text
        context.user_data["step"] = "payment"

        await update.message.reply_text(
            "💳 ငွေလွှဲပြီး Screenshot ကို ဒီနေရာမှာ ပို့ပါ။\n\n"
            + PAYMENT_INFO
        )

async def photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product = context.user_data.get("product")
    price = context.user_data.get("price")
    game_id = context.user_data.get("game_id")

    if not product:
        await update.message.reply_text("အရင်ဆုံး ပစ္စည်းတစ်ခုရွေးပါ။ /start")
        return

    order = (
        f"🆕 NEW ORDER\n\n"
        f"👤 User: @{update.effective_user.username or 'No username'}\n"
        f"🆔 Telegram ID: {update.effective_user.id}\n"
        f"📦 Product: {product}\n"
        f"💰 Price: {price:,} Ks\n"
        f"🎮 Game ID: {game_id}"
    )

    if ADMIN_ID:
        await context.bot.send_message(ADMIN_ID, order)
        await context.bot.send_photo(
            ADMIN_ID,
            update.message.photo[-1].file_id,
            caption="💳 Payment Screenshot"
        )

    await update.message.reply_text(
        "✅ Order လက်ခံပြီးပါပြီ။\n"
        "Admin က ငွေပေးချေမှုစစ်ပြီး ဆက်လက်ဆောင်ရွက်ပေးပါမယ်။"
    )
    context.user_data.clear()

def main():
    if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        raise ValueError("BOT_TOKEN ကို ထည့်ပါ။")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.PHOTO, photo_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
