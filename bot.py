import os
import random

from telegram import InlineKeyboardButton as B
from telegram import InlineKeyboardMarkup as M
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]
CARD = os.environ["CARD_NUMBER"]

ADMIN = 704985066


P = {
    "ov20": ("OPEN VPN VIP", "20GB", "1", "30 روز", "199,000"),
    "ov30": ("OPEN VPN VIP", "30GB", "1", "30 روز", "249,000"),
    "ov50": ("OPEN VPN VIP", "50GB", "1", "30 روز", "299,000"),
    "ov100": ("OPEN VPN VIP", "100GB", "1", "30 روز", "499,000"),
    "ov200": ("OPEN VPN VIP", "200GB", "1", "30 روز", "990,000"),

    "ov330": ("OPEN VPN VIP", "30GB", "3", "بدون محدودیت", "299,000"),
    "ov350": ("OPEN VPN VIP", "50GB", "3", "بدون محدودیت", "499,000"),
    "ov3100": ("OPEN VPN VIP", "100GB", "3", "بدون محدودیت", "990,000"),
    "ov3200": ("OPEN VPN VIP", "200GB", "3", "بدون محدودیت", "1,900,000"),

    "npv25": ("NPV Tunnel", "25GB", "نامحدود", "30 روز", "145,000"),
    "npv50": ("NPV Tunnel", "50GB", "نامحدود", "30 روز", "220,000"),
    "npv80": ("NPV Tunnel", "80GB", "نامحدود", "30 روز", "300,000"),
}


def oid():
    return f"OV-{random.randint(1000, 9999)}"


async def menu(q, text, buttons):
    await q.edit_message_text(
        text,
        reply_markup=M(
            [[B(x, callback_data=y)] for x, y in buttons]
        ),
    )


# =========================
# START
# =========================

async def start(u, c):
    await u.message.reply_text(
        "🛒 فروشگاه OpenVppn ❤️\n\n"
        "سرویس را انتخاب کنید:",
        reply_markup=M([
            [B("🟢 OPEN VPN | VIP", callback_data="ov")],
            [B("🔵 NPV Tunnel | اقتصادی", callback_data="npv")],
            [B("📞 پشتیبانی", callback_data="sup")],
        ]),
    )


# =========================
# ADMIN PANEL
# =========================

async def admin_panel(u, c):

    if u.effective_user.id != ADMIN:
        return await u.message.reply_text(
            "⛔ دسترسی ندارید."
        )

    await u.message.reply_text(
        "🛠️ پنل مدیریت OpenVppn\n\n"
        "مدیریت سفارش‌ها و فروشگاه:",
        reply_markup=M([
            [B("📦 سفارش‌های جدید", callback_data="adm_new")],
            [B("⏳ سفارش‌های در حال انجام", callback_data="adm_work")],
            [B("✅ سفارش‌های تکمیل‌شده", callback_data="adm_done")],
            [B("❌ سفارش‌های ردشده", callback_data="adm_no")],
            [B("📊 آمار فروش", callback_data="adm_stats")],
        ]),
    )


async def admin_menu(u, c):

    q = u.callback_query
    await q.answer()

    if u.effective_user.id != ADMIN:
        return

    d = q.data
    orders = c.bot_data.get("orders", {})

    # برگشت به پنل اصلی
    if d == "adm_home":

        return await q.edit_message_text(
            "🛠️ پنل مدیریت OpenVppn\n\n"
            "مدیریت سفارش‌ها و فروشگاه:",
            reply_markup=M([
                [B("📦 سفارش‌های جدید", callback_data="adm_new")],
                [B("⏳ سفارش‌های در حال انجام", callback_data="adm_work")],
                [B("✅ سفارش‌های تکمیل‌شده", callback_data="adm_done")],
                [B("❌ سفارش‌های ردشده", callback_data="adm_no")],
                [B("📊 آمار فروش", callback_data="adm_stats")],
            ]),
        )

    # لیست سفارش‌ها
    if d in ["adm_new", "adm_work", "adm_done", "adm_no"]:

        status = {
            "adm_new": "review",
            "adm_work": "delivery",
            "adm_done": "completed",
            "adm_no": "rejected",
        }[d]

        title = {
            "review": "📦 سفارش‌های جدید",
            "delivery": "⏳ سفارش‌های در حال انجام",
            "completed": "✅ سفارش‌های تکمیل‌شده",
            "rejected": "❌ سفارش‌های ردشده",
        }[status]

        found = []

        for number, order in orders.items():

            if order.get("status") == status:

                p = P.get(order["key"])

                if p:
                    found.append(
                        f"🔖 #{number}\n"
                        f"📦 {p[0]} | {p[1]}\n"
                        f"👤 ID: {order['uid']}"
                    )

        text = title + "\n\n"

        if found:
            text += "\n\n".join(found)
        else:
            text += "هیچ سفارشی وجود ندارد."

        return await q.edit_message_text(
            text,
            reply_markup=M([
                [
                    B(
                        "🔄 بروزرسانی",
                        callback_data=d
                    )
                ],
                [
                    B(
                        "🔙 پنل مدیریت",
                        callback_data="adm_home"
                    )
                ],
            ]),
        )

    # آمار
    if d == "adm_stats":

        total = len(orders)

        review = sum(
            1
            for o in orders.values()
            if o.get("status") == "review"
        )

        work = sum(
            1
            for o in orders.values()
            if o.get("status") == "delivery"
        )

        done = sum(
            1
            for o in orders.values()
            if o.get("status") == "completed"
        )

        rejected = sum(
            1
            for o in orders.values()
            if o.get("status") == "rejected"
        )

        return await q.edit_message_text(
            "📊 آمار فروشگاه\n\n"
            f"📦 کل سفارش‌ها: {total}\n"
            f"📦 در انتظار بررسی: {review}\n"
            f"⏳ در حال انجام: {work}\n"
            f"✅ تکمیل‌شده: {done}\n"
            f"❌ ردشده: {rejected}",
            reply_markup=M([
                [
                    B(
                        "🔙 پنل مدیریت",
                        callback_data="adm_home"
                    )
                ]
            ]),
        )


# =========================
# USER BUTTONS
# =========================

async def btn(u, c):

    q = u.callback_query
    await q.answer()

    d = q.data

    # دکمه‌های پنل ادمین
    if d.startswith("adm_"):
        return await admin_menu(u, c)

    # خانه
    if d == "home":

        return await start(
            type("X", (), {"message": q.message})(),
            c
        )

    # OPEN VPN
    if d == "ov":

        return await menu(
            q,
            "🟢 OPEN VPN VIP\n\n"
            "تک‌کاربره — 30 روزه",
            [
                ("20GB — 199,000", "ov20"),
                ("30GB — 249,000", "ov30"),
                ("50GB — 299,000", "ov50"),
                ("100GB — 499,000", "ov100"),
                ("200GB — 990,000", "ov200"),
                ("👥 سه کاربره", "3"),
                ("🔙 برگشت", "home"),
            ],
        )

    # سه کاربره
    if d == "3":

        return await menu(
            q,
            "👥 OPEN VPN | سه کاربره\n\n"
            "⏳ بدون محدودیت",
            [
                ("30GB — 299,000", "ov330"),
                ("50GB — 499,000", "ov350"),
                ("100GB — 990,000", "ov3100"),
                ("200GB — 1,900,000", "ov3200"),
                ("🔙 برگشت", "ov"),
            ],
        )

    # NPV
    if d == "npv":

        return await menu(
            q,
            "🔵 NPV Tunnel | اقتصادی\n\n"
            "👥 کاربر نامحدود\n"
            "⏳ 30 روز",
            [
                ("25GB — 145,000", "npv25"),
                ("50GB — 220,000", "npv50"),
                ("80GB — 300,000", "npv80"),
                ("🔙 برگشت", "home"),
            ],
        )

    # پشتیبانی
    if d == "sup":

        return await menu(
            q,
            "📞 پشتیبانی OpenVppn\n\n"
            "@mammadhossein1",
            [
                ("🔙 برگشت", "home")
            ],
        )

    # انتخاب پلن
    if d in P:

        p = P[d]

        return await menu(
            q,
            f"📦 {p[0]}\n\n"
            f"📊 {p[1]}\n"
            f"👤 کاربران: {p[2]}\n"
            f"⏳ {p[3]}\n"
            f"💰 {p[4]} تومان",
            [
                ("💳 اطلاعات پرداخت", "pay" + d),
                ("🔙 برگشت", "home"),
            ],
        )

    # اطلاعات پرداخت
    if d.startswith("pay"):

        k = d[3:]
        p = P[k]

        return await menu(
            q,
            f"💳 اطلاعات پرداخت\n\n"
            f"📦 {p[0]} | {p[1]}\n"
            f"💰 {p[4]} تومان\n\n"
            f"💳 کارت:\n"
            f"{CARD}\n\n"
            f"👤 محمدحسین شیخی\n\n"
            f"پس از واریز رسید را بفرستید.",
            [
                ("📤 ارسال رسید", "rec" + k),
                ("🔙 برگشت", k),
            ],
        )

    # ارسال رسید
    if d.startswith("rec"):

        c.user_data["order"] = d[3:]

        return await q.message.reply_text(
            "📸 لطفاً عکس رسید پرداخت را همینجا ارسال کنید."
        )


# =========================
# RECEIPT
# =========================

async def receipt(u, c):

    k = c.user_data.get("order")

    if k not in P:
        return await u.message.reply_text(
            "ابتدا یک پلن انتخاب کنید."
        )

    p = P[k]
    x = u.effective_user
    number = oid()

    c.bot_data.setdefault("orders", {})[number] = {
        "uid": x.id,
        "key": k,
        "status": "review",
    }

    text = (
        f"🧾 سفارش جدید\n\n"
        f"🔖 شماره سفارش: #{number}\n\n"
        f"👤 {x.full_name}\n"
        f"🆔 {x.id}\n\n"
        f"📦 {p[0]}\n"
        f"📊 {p[1]}\n"
        f"👥 {p[2]}\n"
        f"💰 {p[4]} تومان"
    )

    # ارسال رسید به ادمین
    await u.message.forward(ADMIN)

    # اطلاعات سفارش برای ادمین
    await c.bot.send_message(
        ADMIN,
        text,
        reply_markup=M([
            [
                B(
                    "✅ تأیید پرداخت",
                    callback_data="ok" + number
                ),
                B(
                    "❌ رد پرداخت",
                    callback_data="no" + number
                ),
            ]
        ]),
    )

    await u.message.reply_text(
        f"✅ رسید دریافت شد.\n\n"
        f"🔖 شماره سفارش: #{number}\n"
        f"🕐 وضعیت: در حال بررسی پرداخت"
    )

    c.user_data.pop("order", None)


# =========================
# APPROVE / REJECT
# =========================

async def admin(u, c):

    q = u.callback_query
    await q.answer()

    if u.effective_user.id != ADMIN:
        return

    d = q.data
    number = d[2:]

    order = c.bot_data.get(
        "orders", {}
    ).get(number)

    if not order:

        return await q.message.reply_text(
            "❌ سفارش پیدا نشد."
        )

    uid = order["uid"]
    k = order["key"]

    # رد پرداخت
    if d.startswith("no"):

        order["status"] = "rejected"

        await c.bot.send_message(
            uid,
            f"❌ پرداخت سفارش #{number} تأیید نشد.\n\n"
            f"پشتیبانی: @mammadhossein1"
        )

        return await q.message.reply_text(
            f"❌ سفارش #{number} رد شد."
        )

    # تأیید پرداخت
    order["status"] = "delivery"

    if k.startswith("ov"):

        order["step"] = "file"

        msg = "📎 فایل OpenVPN را بفرستید."

    else:

        order["step"] = "npv"

        msg = "📝 ساب‌لینک NPV را بفرستید."

    await c.bot.send_message(
        uid,
        f"✅ پرداخت سفارش #{number} تأیید شد.\n\n"
        f"🕐 در حال آماده‌سازی سفارش شما..."
    )

    await q.message.reply_text(
        f"✅ سفارش #{number} تأیید شد.\n\n"
        f"{msg}"
    )


# =========================
# DELIVERY
# =========================

async def delivery(u, c):

    if u.effective_user.id != ADMIN:
        return

    for number, order in c.bot_data.get(
        "orders", {}
    ).items():

        if order.get("status") != "delivery":
            continue

        uid = order["uid"]

        # فایل OPEN VPN
        if order.get("step") == "file":

            if not u.message.document:
                continue

            await u.message.copy(uid)

            await c.bot.send_message(
                uid,
                "✔️پروفایل سرور (برای همه سرویس ها)\n\n"
                "✔️ سایت کاربران جهت نمایش میزان\n"
                "اعتبار (بدون Vpn)\n"
                "🌐 https://promiec.com/users/\n"
                "⚠️ لینک بالا را بدون VPN باز کنید."
            )

            order["step"] = "login"

            return await u.message.reply_text(
                f"✅ فایل سفارش #{number} ارسال شد.\n\n"
                f"👤 حالا یوزرنیم و پسورد را بفرستید."
            )

        # یوزرنیم و پسورد OPEN VPN
        if (
            order.get("step") == "login"
            and u.message.text
        ):

            await c.bot.send_message(
                uid,
                u.message.text
            )

            order["status"] = "completed"

            await u.message.reply_text(
                f"✅ سفارش #{number} تکمیل شد. 🎉"
            )

            return await start(
                type("X", (), {"message": u.message})(),
                c
            )

        # ساب لینک NPV
        if (
            order.get("step") == "npv"
            and u.message.text
        ):

            await c.bot.send_message(
                uid,
                "تبریک اشتراک شما با موفقیت ساخته شد❤️\n\n"
                "🔗 لینک اشتراک شما :\n"
                + u.message.text
            )

            order["status"] = "completed"

            await u.message.reply_text(
                f"✅ سفارش #{number} تکمیل شد. 🎉"
            )

            return await start(
                type("X", (), {"message": u.message})(),
                c
            )


# =========================
# HANDLERS
# =========================

app = Application.builder().token(TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CommandHandler("admin", admin_panel)
)

app.add_handler(
    CallbackQueryHandler(
        admin,
        pattern="^(ok|no)"
    )
)

app.add_handler(
    CallbackQueryHandler(btn)
)

app.add_handler(
    MessageHandler(
        filters.PHOTO,
        receipt
    )
)

app.add_handler(
    MessageHandler(
        filters.Document.ALL | filters.TEXT,
        delivery
    )
)


# =========================
# RUN
# =========================

app.run_polling()
