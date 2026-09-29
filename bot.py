import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
CARD_NUMBER = os.environ["CARD_NUMBER"]

plans = {
    "ov20": ("OPEN VPN VIP", "20GB", "1 کاربر", "30 روز", "199,000 تومان"),
    "ov30": ("OPEN VPN VIP", "30GB", "1 کاربر", "30 روز", "249,000 تومان"),
    "ov50": ("OPEN VPN VIP", "50GB", "1 کاربر", "30 روز", "299,000 تومان"),
    "ov100": ("OPEN VPN VIP", "100GB", "1 کاربر", "30 روز", "499,000 تومان"),
    "ov200": ("OPEN VPN VIP", "200GB", "1 کاربر", "30 روز", "990,000 تومان"),
    "ov330": ("OPEN VPN VIP", "30GB", "3 کاربر", "بدون محدودیت", "299,000 تومان"),
    "ov350": ("OPEN VPN VIP", "50GB", "3 کاربر", "بدون محدودیت", "499,000 تومان"),
    "ov3100": ("OPEN VPN VIP", "100GB", "3 کاربر", "بدون محدودیت", "990,000 تومان"),
    "ov3200": ("OPEN VPN VIP", "200GB", "3 کاربر", "بدون محدودیت", "1,900,000 تومان"),
    "npv25": ("NPV Tunnel", "25GB", "نامحدود", "30 روز", "145,000 تومان"),
    "npv50": ("NPV Tunnel", "50GB", "نامحدود", "30 روز", "220,000 تومان"),
    "npv80": ("NPV Tunnel", "80GB", "نامحدود", "30 روز", "300,000 تومان"),
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await home(update.message)

async def show(q, text, buttons):
    keyboard = [[InlineKeyboardButton(t, callback_data=d)] for t, d in buttons]
    func = q.edit_message_text if hasattr(q, "edit_message_text") else q.reply_text
    await func(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def home(q):
    await show(q, "🛒 فروشگاه OpenVppn ❤️\n\nسرویس مورد نظر را انتخاب کنید:",
        [["🟢 OPEN VPN | VIP", "openvpn"],
         ["🔵 NPV Tunnel | اقتصادی", "npv"],
         ["📞 پشتیبانی", "support"]])

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    if d == "home":
        await home(q)

    elif d == "openvpn":
        await show(q, "🟢 OPEN VPN | VIP\n\n🔥 تک‌کاربره — 30 روزه",
            [["20GB — 199,000", "ov20"],
             ["30GB — 249,000", "ov30"],
             ["50GB — 299,000", "ov50"],
             ["100GB — 499,000", "ov100"],
             ["200GB — 990,000", "ov200"],
             ["👥 پلن 3 کاربره", "ov3"],
             ["🔙 برگشت", "home"]])

    elif d == "ov3":
        await show(q, "👥 OPEN VPN | سه کاربره\n\n⏳ بدون محدودیت زمانی",
            [["30GB — 299,000", "ov330"],
             ["50GB — 499,000", "ov350"],
             ["100GB — 990,000", "ov3100"],
             ["200GB — 1,900,000", "ov3200"],
             ["🔙 برگشت", "openvpn"]])

    elif d == "npv":
        await show(q, "🔵 NPV Tunnel | اقتصادی\n\n👥 تعداد کاربر نامحدود\n⏳ اعتبار: 30 روز",
            [["25GB — 145,000", "npv25"],
             ["50GB — 220,000", "npv50"],
             ["80GB — 300,000", "npv80"],
             ["🔙 برگشت", "home"]])

    elif d in plans:
        p = plans[d]
        text = (
            f"📦 {p[0]}\n\n"
            f"📊 حجم: {p[1]}\n"
            f"👤 کاربران: {p[2]}\n"
            f"⏳ اعتبار: {p[3]}\n"
            f"💰 مبلغ: {p[4]}"
        )
        await show(q, text,
            [["💳 اطلاعات پرداخت", "pay_" + d],
             ["🔙 برگشت", "home"]])

    elif d.startswith("pay_"):
        p = plans[d[4:]]
        text = (
            "💳 اطلاعات پرداخت\n\n"
            f"💰 مبلغ: {p[4]}\n\n"
            f"💳 شماره کارت:\n{CARD_NUMBER}\n\n"
            "👤 به نام: محمدحسین شیخی\n\n"
            "بعد از واریز، رسید پرداخت را ارسال کنید."
        )
        await show(q, text,
            [["🔙 برگشت به پلن", d[4:]]])

    elif d == "support":
        await show(q,
            "📞 پشتیبانی OpenVppn\n\n"
            "@mammadhossein1\n\n"
            "🕐 پاسخگویی در اسرع وقت",
            [["🔙 برگشت", "home"]])

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
