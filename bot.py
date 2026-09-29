import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show(update.message, "🛒 فروشگاه OpenVppn ❤️\n\nسرویس مورد نظر را انتخاب کنید:",
        [["🟢 OPEN VPN | VIP", "openvpn"], ["🔵 NPV Tunnel | اقتصادی", "npv"], ["📞 پشتیبانی", "support"]])

async def show(obj, text, buttons):
    kb = [[InlineKeyboardButton(t, callback_data=d)] for t, d in buttons]
    await (obj.edit_message_text if hasattr(obj, "edit_message_text") else obj.reply_text)(
        text, reply_markup=InlineKeyboardMarkup(kb))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    if d == "home":
        await show(q, "🛒 فروشگاه OpenVppn ❤️\n\nسرویس مورد نظر را انتخاب کنید:",
            [["🟢 OPEN VPN | VIP", "openvpn"], ["🔵 NPV Tunnel | اقتصادی", "npv"], ["📞 پشتیبانی", "support"]])

    elif d == "openvpn":
        await show(q, "🟢 OPEN VPN | VIP\n\n🔥 تک‌کاربره VIP — 30 روزه",
            [["20GB — 199,000 تومان", "none"], ["30GB — 249,000 تومان", "none"],
             ["50GB — 299,000 تومان", "none"], ["100GB — 499,000 تومان", "none"],
             ["200GB — 990,000 تومان", "none"], ["👥 پلن‌های 3 کاربره VIP", "ov3"],
             ["🔙 بازگشت", "home"]])

    elif d == "ov3":
        await show(q, "👥 پلن‌های 3 کاربره VIP\n\n⏳ بدون محدودیت زمانی",
            [["30GB — 299,000 تومان", "none"], ["50GB — 499,000 تومان", "none"],
             ["100GB — 990,000 تومان", "none"], ["200GB — 1,900,000 تومان", "none"],
             ["🔙 بازگشت", "openvpn"]])

    elif d == "npv":
        await show(q, "🔵 NPV Tunnel | اقتصادی\n\n👥 تعداد کاربر نامحدود\n⏳ اعتبار: 30 روز",
            [["25GB — 145,000 تومان", "none"], ["50GB — 220,000 تومان", "none"],
             ["80GB — 300,000 تومان", "none"], ["🔙 بازگشت", "home"]])

    elif d == "support":
        await show(q, "📞 پشتیبانی OpenVppn\n\nبرای ارتباط با پشتیبانی:\n\n@mammadhossein1\n\n🕐 پاسخگویی در اسرع وقت",
            [["🔙 بازگشت به فروشگاه", "home"]])

    else:
        await q.answer("این بخش هنوز فعال نشده است.", show_alert=True)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
