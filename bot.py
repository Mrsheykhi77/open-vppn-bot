import os,random
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

def oid():
    return f"OV-{random.randint(1000,9999)}"

async def menu(q,t,bs):
    await q.edit_message_text(t,reply_markup=M([[B(x,callback_data=y)] for x,y in bs]))

async def start(u,c):
    await u.message.reply_text("🛒 فروشگاه OpenVppn ❤️\n\nسرویس را انتخاب کنید:",
    reply_markup=M([[B("🟢 OPEN VPN | VIP",callback_data="ov")],
    [B("🔵 NPV Tunnel | اقتصادی",callback_data="npv")],
    [B("📞 پشتیبانی",callback_data="sup")]]))

async def btn(u,c):
    q=u.callback_query;await q.answer();d=q.data
    if d=="home": return await start(type("X",(),{"message":q.message})(),c)
    if d=="ov": return await menu(q,"🟢 OPEN VPN VIP\n\nتک‌کاربره — 30 روزه",
    [("20GB — 199,000","ov20"),("30GB — 249,000","ov30"),("50GB — 299,000","ov50"),
    ("100GB — 499,000","ov100"),("200GB — 990,000","ov200"),("👥 سه کاربره","3"),("🔙 برگشت","home")])
    if d=="3": return await menu(q,"👥 OPEN VPN | سه کاربره\n\n⏳ بدون محدودیت",
    [("30GB — 299,000","ov330"),("50GB — 499,000","ov350"),("100GB — 990,000","ov3100"),
    ("200GB — 1,900,000","ov3200"),("🔙 برگشت","ov")])
    if d=="npv": return await menu(q,"🔵 NPV Tunnel | اقتصادی\n\n👥 کاربر نامحدود\n⏳ 30 روز",
    [("25GB — 145,000","npv25"),("50GB — 220,000","npv50"),("80GB — 300,000","npv80"),("🔙 برگشت","home")])
    if d=="sup": return await menu(q,"📞 پشتیبانی OpenVppn\n\n@mammadhossein1",[("🔙 برگشت","home")])
    if d in P:
        p=P[d]
        return await menu(q,f"📦 {p[0]}\n\n📊 {p[1]}\n👤 کاربران: {p[2]}\n⏳ {p[3]}\n💰 {p[4]} تومان",
        [("💳 اطلاعات پرداخت","pay"+d),("🔙 برگشت","home")])
    if d.startswith("pay"):
        k=d[3:];p=P[k]
        return await menu(q,f"💳 اطلاعات پرداخت\n\n📦 {p[0]} | {p[1]}\n💰 {p[4]} تومان\n\n💳 کارت:\n{CARD}\n\n👤 محمدحسین شیخی\n\nپس از واریز رسید را بفرستید.",
        [("📤 ارسال رسید","rec"+k),("🔙 برگشت",k)])
    if d.startswith("rec"):
        c.user_data["order"]=d[3:]
        return await q.message.reply_text("📸 لطفاً عکس رسید پرداخت را همینجا ارسال کنید.")

async def receipt(u,c):
    k=c.user_data.get("order")
    if k not in P:return await u.message.reply_text("ابتدا یک پلن انتخاب کنید.")
    p=P[k];x=u.effective_user;number=oid()
    c.bot_data.setdefault("orders",{})[number]={"uid":x.id,"key":k,"status":"review"}
    text=f"🧾 سفارش جدید\n\n🔖 شماره سفارش: #{number}\n\n👤 {x.full_name}\n🆔 {x.id}\n\n📦 {p[0]}\n📊 {p[1]}\n👥 {p[2]}\n💰 {p[4]} تومان"
    await u.message.forward(ADMIN)
    await c.bot.send_message(ADMIN,text,reply_markup=M([[B("✅ تأیید پرداخت",callback_data="ok"+number),B("❌ رد پرداخت",callback_data="no"+number)]]))
    await u.message.reply_text(f"✅ رسید دریافت شد.\n\n🔖 شماره سفارش: #{number}\n🕐 وضعیت: در حال بررسی پرداخت")
    c.user_data.pop("order",None)

async def admin(u,c):
    q=u.callback_query;await q.answer()
    if u.effective_user.id!=ADMIN:return
    d=q.data;number=d[2:];o=c.bot_data.get("orders",{}).get(number)
    if not o:return await q.message.reply_text("❌ سفارش پیدا نشد.")
    uid,k=o["uid"],o["key"]
    if d.startswith("no"):
        o["status"]="rejected"
        await c.bot.send_message(uid,f"❌ پرداخت سفارش #{number} تأیید نشد.\n\nپشتیبانی: @mammadhossein1")
        return await q.message.reply_text(f"❌ سفارش #{number} رد شد.")
    o["status"]="delivery"
    o["step"]="file" if k.startswith("ov") else "npv"
    msg="📎 فایل OpenVPN را بفرستید." if k.startswith("ov") else "📝 ساب‌لینک NPV را بفرستید."
    await c.bot.send_message(uid,f"✅ پرداخت سفارش #{number} تأیید شد.\n\n🕐 در حال آماده‌سازی سفارش شما...")
    await q.message.reply_text(f"✅ سفارش #{number} تأیید شد.\n\n{msg}")

async def delivery(u,c):
    if u.effective_user.id!=ADMIN:return
    orders=c.bot_data.get("orders",{})
    for number,o in orders.items():
        if o.get("status")!="delivery":continue
        uid=o["uid"]
        if o["step"]=="file":
            if not u.message.document:continue
            await u.message.copy(uid)
            await c.bot.send_message(uid,"✔️پروفایل سرور (برای همه سرویس ها)\n\n✔️ سایت کاربران جهت نمایش میزان\nاعتبار (بدون Vpn)\n🌐 https://promiec.com/users/\n⚠️ لینک بالا را بدون VPN باز کنید.")
            o["step"]="login"
            return await u.message.reply_text(f"✅ فایل سفارش #{number} ارسال شد.\n\n👤 حالا یوزرنیم و پسورد را بفرستید.")
        if o["step"]=="login" and u.message.text:
            await c.bot.send_message(uid,u.message.text)
            o["status"]="completed"
            return await u.message.reply_text(f"✅ سفارش #{number} تکمیل شد. 🎉")
        if o["step"]=="npv" and u.message.text:
            await c.bot.send_message(uid,"تبریک اشتراک شما با موفقیت ساخته شد❤️\n\n🔗 لینک اشتراک شما :\n"+u.message.text)
            o["status"]="completed"
            return await u.message.reply_text(f"✅ سفارش #{number} تکمیل شد. 🎉")

app=Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CallbackQueryHandler(admin,pattern="^(ok|no)"))
app.add_handler(CallbackQueryHandler(btn))
app.add_handler(MessageHandler(filters.PHOTO,receipt))
app.add_handler(MessageHandler(filters.Document.ALL|filters.TEXT,delivery))
app.run_polling()
