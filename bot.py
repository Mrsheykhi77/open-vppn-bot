import os
from telegram import InlineKeyboardButton as B,InlineKeyboardMarkup as M
from telegram.ext import Application,CommandHandler,CallbackQueryHandler,MessageHandler,filters

TOKEN=os.environ["BOT_TOKEN"];CARD=os.environ["CARD_NUMBER"];ADMIN=704985066
P={
"ov20":("OPEN VPN VIP","20GB","1","30 روز","199,000"),"ov30":("OPEN VPN VIP","30GB","1","30 روز","249,000"),
"ov50":("OPEN VPN VIP","50GB","1","30 روز","299,000"),"ov100":("OPEN VPN VIP","100GB","1","30 روز","499,000"),
"ov200":("OPEN VPN VIP","200GB","1","30 روز","990,000"),"ov330":("OPEN VPN VIP","30GB","3","بدون محدودیت","299,000"),
"ov350":("OPEN VPN VIP","50GB","3","بدون محدودیت","499,000"),"ov3100":("OPEN VPN VIP","100GB","3","بدون محدودیت","990,000"),
"ov3200":("OPEN VPN VIP","200GB","3","بدون محدودیت","1,900,000"),
"npv25":("NPV Tunnel","25GB","نامحدود","30 روز","145,000"),"npv50":("NPV Tunnel","50GB","نامحدود","30 روز","220,000"),
"npv80":("NPV Tunnel","80GB","نامحدود","30 روز","300,000")}

async def menu(q,t,bs):
    await q.edit_message_text(t,reply_markup=M([[B(x,callback_data=y)] for x,y in bs]))

async def start(u,c):
    await u.message.reply_text("🛒 فروشگاه OpenVppn ❤️\n\nسرویس را انتخاب کنید:",
    reply_markup=M([[B("🟢 OPEN VPN | VIP",callback_data="ov")],
    [B("🔵 NPV Tunnel | اقتصادی",callback_data="npv")],
    [B("📞 پشتیبانی",callback_data="sup")]]))

async def btn(u,c):
    q=u.callback_query;await q.answer();d=q.data
    if d=="home": await start(type("X",(),{"message":q.message})(),c)
    elif d=="ov": await menu(q,"🟢 OPEN VPN VIP\n\nتک‌کاربره — 30 روزه",
    [("20GB — 199,000","ov20"),("30GB — 249,000","ov30"),("50GB — 299,000","ov50"),
    ("100GB — 499,000","ov100"),("200GB — 990,000","ov200"),("👥 سه کاربره","3"),("🔙 برگشت","home")])
    elif d=="3": await menu(q,"👥 OPEN VPN | سه کاربره\n\n⏳ بدون محدودیت",
    [("30GB — 299,000","ov330"),("50GB — 499,000","ov350"),("100GB — 990,000","ov3100"),
    ("200GB — 1,900,000","ov3200"),("🔙 برگشت","ov")])
    elif d=="npv": await menu(q,"🔵 NPV Tunnel | اقتصادی\n\n👥 کاربر نامحدود\n⏳ 30 روز",
    [("25GB — 145,000","npv25"),("50GB — 220,000","npv50"),("80GB — 300,000","npv80"),("🔙 برگشت","home")])
    elif d=="sup": await menu(q,"📞 پشتیبانی OpenVppn\n\n@mammadhossein1",[("🔙 برگشت","home")])
    elif d in P:
        p=P[d];await menu(q,f"📦 {p[0]}\n\n📊 {p[1]}\n👤 کاربران: {p[2]}\n⏳ {p[3]}\n💰 {p[4]} تومان",
        [("💳 اطلاعات پرداخت","pay"+d),("🔙 برگشت","home")])
    elif d.startswith("pay"):
        k=d[3:];p=P[k]
        await menu(q,f"💳 اطلاعات پرداخت\n\n📦 {p[0]} | {p[1]}\n💰 {p[4]} تومان\n\n💳 کارت:\n{CARD}\n\n👤 محمدحسین شیخی\n\nپس از واریز رسید را بفرستید.",
        [("📤 ارسال رسید","rec"+k),("🔙 برگشت",k)])
    elif d.startswith("rec"):
        c.user_data["order"]=d[3:];await q.message.reply_text("📸 لطفاً عکس رسید پرداخت را همینجا ارسال کنید.")

async def receipt(u,c):
    k=c.user_data.get("order")
    if k not in P:return await u.message.reply_text("ابتدا یک پلن انتخاب کنید.")
    p=P[k];x=u.effective_user
    c.bot_data["orders"]={**c.bot_data.get("orders",{}),str(x.id):(x.id,k)}
    text=f"🧾 سفارش جدید\n\n👤 {x.full_name}\n🆔 {x.id}\n\n📦 {p[0]}\n📊 {p[1]}\n👥 {p[2]}\n💰 {p[4]} تومان"
    await u.message.forward(ADMIN)
    await c.bot.send_message(ADMIN,text,reply_markup=M([[B("✅ تأیید پرداخت",callback_data="ok"+str(x.id)),B("❌ رد پرداخت",callback_data="no"+str(x.id))]]))
    await u.message.reply_text("✅ رسید دریافت شد.\n\n🕐 منتظر بررسی پرداخت باشید.")
    c.user_data.pop("order",None)

async def admin(u,c):
    q=u.callback_query;await q.answer()
    if u.effective_user.id!=ADMIN:return
    d=q.data;uid=int(d[2:]);o=c.bot_data.get("orders",{}).get(str(uid))
    if not o:return await q.message.reply_text("❌ سفارش پیدا نشد.")
    k=o[1]
    if d.startswith("no"):
        await c.bot.send_message(uid,"❌ پرداخت شما تأیید نشد.\n\nپشتیبانی: @mammadhossein1")
        return await q.message.reply_text("❌ سفارش رد شد.")
    c.bot_data["delivery"]=(uid,k,"file" if k.startswith("ov") else "npv")
    msg="📎 فایل OpenVPN را بفرستید." if k.startswith("ov") else "📝 ساب‌لینک NPV را بفرستید."
    await q.message.reply_text("✅ پرداخت تأیید شد.\n\n"+msg)

async def delivery(u,c):
    if u.effective_user.id!=ADMIN or "delivery" not in c.bot_data:return
    uid,k,step=c.bot_data["delivery"]
    if step=="file":
        if not u.message.document:return await u.message.reply_text("⚠️ لطفاً فایل OpenVPN را ارسال کنید.")
        await u.message.copy(uid)
        await c.bot.send_message(uid,"✔️پروفایل سرور (برای همه سرویس ها)\n\n✔️ سایت کاربران جهت نمایش میزان\nاعتبار (بدون Vpn)\n🌐 https://promiec.com/users/\n⚠️ لینک بالا را بدون VPN باز کنید.")
        c.bot_data["delivery"]=(uid,k,"login")
        return await u.message.reply_text("✅ فایل ارسال شد.\n\n👤 حالا یوزرنیم و پسورد را بفرستید.")
    if step=="login" and u.message.text:
        await c.bot.send_message(uid,u.message.text)
        await u.message.reply_text("✅ یوزرنیم و پسورد ارسال شد.\n🎉 سفارش OpenVPN تکمیل شد.")
        c.bot_data.pop("delivery",None);return
    if step=="npv" and u.message.text:
        await c.bot.send_message(uid,"تبریک اشتراک شما با موفقیت ساخته شد❤️\n\n🔗 لینک اشتراک شما :\n"+u.message.text)
        await u.message.reply_text("✅ ساب‌لینک ارسال شد.\n🎉 سفارش NPV تکمیل شد.")
        c.bot_data.pop("delivery",None)

app=Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CallbackQueryHandler(admin,pattern="^(ok|no)"))
app.add_handler(CallbackQueryHandler(btn))
app.add_handler(MessageHandler(filters.PHOTO,receipt))
app.add_handler(MessageHandler(filters.Document.ALL|filters.TEXT,delivery))
app.run_polling()
