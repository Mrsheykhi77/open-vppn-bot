import os
from telegram import Update,InlineKeyboardButton as B,InlineKeyboardMarkup as M
from telegram.ext import Application,CommandHandler,CallbackQueryHandler,MessageHandler,ContextTypes,filters

TOKEN=os.environ["BOT_TOKEN"]; CARD=os.environ["CARD_NUMBER"]; ADMIN=704985066
P={
"ov20":("OPEN VPN VIP","20GB","1","30 روز","199,000"),
"ov30":("OPEN VPN VIP","30GB","1","30 روز","249,000"),
"ov50":("OPEN VPN VIP","50GB","1","30 روز","299,000"),
"ov100":("OPEN VPN VIP","100GB","1","30 روز","499,000"),
"ov200":("OPEN VPN VIP","200GB","1","30 روز","990,000"),
"ov330":("OPEN VPN VIP","30GB","3","بدون محدودیت","299,000"),
"ov350":("OPEN VPN VIP","50GB","3","بدون محدودیت","499,000"),
"ov3100":("OPEN VPN VIP","100GB","3","بدون محدودیت","990,000"),
"ov3200":("OPEN VPN VIP","200GB","3","بدون محدودیت","1,900,000"),
"npv25":("NPV Tunnel","25GB","نامحدود","30 روز","145,000"),
"npv50":("NPV Tunnel","50GB","نامحدود","30 روز","220,000"),
"npv80":("NPV Tunnel","80GB","نامحدود","30 روز","300,000")}

async def show(q,t,bs):
    k=[[B(x,y)] for x,y in bs]
    f=q.edit_message_text if hasattr(q,"edit_message_text") else q.reply_text
    await f(t,reply_markup=M(k))

async def start(u,c):
    await show(u.message,"🛒 فروشگاه OpenVppn ❤️\n\nسرویس را انتخاب کنید:",
    [("🟢 OPEN VPN | VIP","ov"),("🔵 NPV Tunnel | اقتصادی","npv"),("📞 پشتیبانی","sup")])

async def btn(u,c):
    q=u.callback_query; await q.answer(); d=q.data
    if d=="home": await start(type("X",(),{"message":q.message})(),c)
    elif d=="ov": await show(q,"🟢 OPEN VPN VIP\n\nتک‌کاربره — 30 روزه",
    [("20GB — 199,000","ov20"),("30GB — 249,000","ov30"),("50GB — 299,000","ov50"),
    ("100GB — 499,000","ov100"),("200GB — 990,000","ov200"),("👥 سه کاربره","3"),("🔙 برگشت","home")])
    elif d=="3": await show(q,"👥 OPEN VPN | سه کاربره\n\n⏳ بدون محدودیت",
    [("30GB — 299,000","ov330"),("50GB — 499,000","ov350"),("100GB — 990,000","ov3100"),("200GB — 1,900,000","ov3200"),("🔙 برگشت","ov")])
    elif d=="npv": await show(q,"🔵 NPV Tunnel | اقتصادی\n\n👥 کاربر نامحدود\n⏳ 30 روز",
    [("25GB — 145,000","npv25"),("50GB — 220,000","npv50"),("80GB — 300,000","npv80"),("🔙 برگشت","home")])
    elif d=="sup": await show(q,"📞 پشتیبانی OpenVppn\n\n@mammadhossein1",[("🔙 برگشت","home")])
    elif d in P:
        p=P[d]; await show(q,f"📦 {p[0]}\n\n📊 {p[1]}\n👤 کاربران: {p[2]}\n⏳ {p[3]}\n💰 {p[4]} تومان",
        [("💳 اطلاعات پرداخت","pay"+d),("🔙 برگشت","home")])
    elif d.startswith("pay"):
        k=d[3:]; p=P[k]
        await show(q,f"💳 اطلاعات پرداخت\n\n📦 {p[0]} | {p[1]}\n💰 {p[4]} تومان\n\n💳 کارت:\n{CARD}\n\n👤 محمدحسین شیخی\n\nپس از واریز رسید را بفرستید.",
        [("📤 ارسال رسید","rec"+k),("🔙 برگشت",k)])
    elif d.startswith("rec"):
        c.user_data["order"]=d[3:]
        await q.message.reply_text("📸 لطفاً عکس رسید پرداخت را همینجا ارسال کنید.")

async def receipt(u,c):
    k=c.user_data.get("order")
    if k not in P:
        await u.message.reply_text("ابتدا یک پلن انتخاب کنید."); return
    p=P[k]; x=u.effective_user; un="@"+x.username if x.username else "ندارد"
    text=f"🧾 سفارش جدید\n\n👤 {x.full_name}\n🔹 {un}\n🆔 {x.id}\n\n📦 {p[0]}\n📊 {p[1]}\n👥 {p[2]}\n⏳ {p[3]}\n💰 {p[4]} تومان\n\n📌 منتظر بررسی پرداخت"
    await u.message.forward(ADMIN)
    await c.bot.send_message(ADMIN,text)
    await u.message.reply_text("✅ رسید دریافت شد.\n\n🕐 پرداخت بررسی می‌شود و سپس سرویس ارسال خواهد شد.")
    c.user_data.pop("order",None)

app=Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CallbackQueryHandler(btn))
app.add_handler(MessageHandler(filters.PHOTO,receipt))
app.run_polling()
