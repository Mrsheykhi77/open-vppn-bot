
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8971885825:AAHkOBmcCEhuEatgT0WD2gtsuHsPQBJbMRA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\n"
        "به فروشگاه OpenVppn خوش اومدی ❤️"
    )

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
