import os
import random

from telegram import InlineKeyboardButton as B
from telegram import InlineKeyboardMarkup as M
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# تنظیمات
# =========================

TOKEN = os.environ["BOT_TOKEN"]
CARD = os.environ["CARD_NUMBER"]

ADMIN = 704985066


# =========================
# قیمت‌ها
# =========================

P = {
    # OPEN VPN - یک کاربر - 30 روز
    "ov20": ("OPEN VPN VIP", "20GB", "1", "30 روز", "199,000"),
    "ov30": ("OPEN VPN VIP", "30GB", "1", "30 روز", "249,000"),
    "ov50": ("OPEN VPN VIP", "50GB", "1", "30 روز", "299,000"),
    "ov100": ("OPEN VPN VIP", "100GB", "1", "30 روز", "499,000"),
    "ov200": ("OPEN VPN VIP", "200GB", "1", "30 روز", "990,000"),

    # OPEN VPN - سه کاربر - بدون محدودیت زمانی
    "ov330": ("OPEN VPN VIP", "30GB", "3", "بدون محدودیت", "299,000"),
    "ov350": ("OPEN VPN VIP", "50GB", "3", "بدون محدودیت", "499,000"),
    "ov3100": ("OPEN VPN VIP", "100GB", "3", "بدون محدودیت", "990,000"),
    "ov3200": ("OPEN VPN VIP", "200GB", "3", "بدون محدودیت", "1,900,000"),

    # NPV
    "npv25": ("NPV Tunnel", "25GB", "نامحدود", "30 روز", "145,000"),
    "npv50": ("NPV Tunnel", "50GB", "نامحدود", "30 روز", "220,000"),
    "npv80": ("NPV Tunnel", "80GB", "نامحدود", "30 روز", "300,000"),
}


# =========================
# منوی اصلی
# =========================

def home_markup():
    return M([
        [B("🟢 OPEN VPN | VIP", callback_data="ov")],
        [B("🔵 NPV Tunnel | اقتصادی", callback_data="npv")],
        [B("📞 پشتیبانی", callback_data="sup")],
    ])


# =========================
# ابزارها
# =========================

def oid():
    return random.randint(100000, 999999)


def status_fa(status):
    return {
        "pending": "⏳ در انتظار بررسی",
        "approved": "🟢 تأیید شده",
        "rejected": "🔴 رد شده",
        "delivery": "📦 در حال تحویل",
        "completed": "✅ تکمیل شده",
    }.get(status, status)


def order_text(order):
    return (
        f"🧾 سفارش #{order['number']}\n\n"
        f"👤 نام: {order['name']}\n"
        f"🆔 آیدی عددی: {order['user_id']}\n"
        f"🔗 یوزرنیم: @{order['username']}\n\n"
        f"📦 سرویس: {order['service']}\n"
        f"💾 حجم: {order['volume']}\n"
        f"👥 کاربران: {order['users']}\n"
        f"⏱ مدت: {order['duration']}\n"
        f"💰 مبلغ: {order['price']} تومان\n\n"
        f"📌 وضعیت: {status_fa(order['status'])}"
    )


def admin_home_markup():
    return M([
        [B("🆕 سفارش‌های جدید", callback_data="adm_new")],
        [B("🟢 تأیید شده‌ها", callback_data="adm_approved")],
        [B("📦 در حال تحویل", callback_data="adm_delivery")],
        [B("✅ تکمیل شده‌ها", callback_data="adm_completed")],
        [B("🔴 رد شده‌ها", callback_data="adm_rejected")],
        [B("📊 آمار سفارش‌ها", callback_data="adm_stats")],
        [B("🔄 بروزرسانی", callback_data="adm_home")],
    ])


def back_for_status(status):
    if status == "pending":
        return "adm_new"
    if status == "approved":
        return "adm_approved"
    if status == "delivery":
        return "adm_delivery"
    if status == "completed":
        return "adm_completed"
    if status == "rejected":
        return "adm_rejected"

    return "adm_home"


# =========================
# /start
# =========================

async def start(u, c):
    await u.message.reply_text(
        "🛒 فروشگاه OpenVppn ❤️\n\n"
        "سرویس موردنظر خود را انتخاب کنید:",
        reply_markup=home_markup(),
    )


# =========================
# پنل ادمین
# =========================

async def admin_menu(u, c):
    if u.effective_user.id != ADMIN:
        return

    orders = c.bot_data.get("orders", {})

    text = (
        "🛠 پنل مدیریت OpenVppn\n\n"
        f"📦 کل سفارش‌ها: {len(orders)}\n\n"
        "یکی از گزینه‌های زیر را انتخاب کنید:"
    )

    if u.callback_query:
        await u.callback_query.edit_message_text(
            text,
            reply_markup=admin_home_markup(),
        )
    else:
        await u.message.reply_text(
            text,
            reply_markup=admin_home_markup(),
        )


async def show_admin_orders(u, c, status):
    if u.effective_user.id != ADMIN:
        return

    orders = c.bot_data.get("orders", {})

    found = [
        o for o in orders.values()
        if o["status"] == status
    ]

    title = {
        "pending": "🆕 سفارش‌های جدید",
        "approved": "🟢 سفارش‌های تأیید شده",
        "delivery": "📦 سفارش‌های در حال تحویل",
        "completed": "✅ سفارش‌های تکمیل شده",
        "rejected": "🔴 سفارش‌های رد شده",
    }.get(status, "📦 سفارش‌ها")

    if not found:
        text = f"{title}\n\nهیچ سفارشی وجود ندارد."
        markup = M([
            [B("🔙 بازگشت", callback_data="adm_home")]
        ])

        await u.callback_query.edit_message_text(
            text,
            reply_markup=markup,
        )
        return

    rows = []

    for order in found:
        rows.append([
            B(
                f"#{order['number']} | {order['service']} | {order['price']}",
                callback_data=f"order_{order['number']}",
            )
        ])

    rows.append([
        B("🔙 بازگشت", callback_data="adm_home")
    ])

    await u.callback_query.edit_message_text(
        title,
        reply_markup=M(rows),
    )


# =========================
# جزئیات سفارش
# =========================

async def order_detail(u, c, number):
    if u.effective_user.id != ADMIN:
        return

    orders = c.bot_data.get("orders", {})

    order = None

    for o in orders.values():
        if str(o["number"]) == str(number):
            order = o
            break

    if not order:
        await u.callback_query.answer("سفارش پیدا نشد.", show_alert=True)
        return

    text = order_text(order)

    buttons = []

    if order["status"] == "pending":
        buttons.append([
            B("✅ تأیید سفارش", callback_data=f"approve_{number}"),
            B("❌ رد سفارش", callback_data=f"reject_{number}"),
        ])

    elif order["status"] == "approved":
        buttons.append([
            B("📦 شروع تحویل", callback_data=f"deliver_{number}"),
        ])

    elif order["status"] == "delivery":
        buttons.append([
            B("📦 ادامه تحویل", callback_data=f"deliver_{number}"),
        ])

    buttons.append([
        B(
            "🔙 بازگشت",
            callback_data=back_for_status(order["status"]),
        )
    ])

    await u.callback_query.edit_message_text(
        text,
        reply_markup=M(buttons),
    )


# =========================
# نمایش پلن‌ها
# =========================

async def show_ov(u, c):
    await u.callback_query.edit_message_text(
        "🟢 OPEN VPN | VIP\n\n"
        "یک گزینه را انتخاب کنید:",
        reply_markup=M([
            [B("👤 1 کاربر | 30 روز", callback_data="ov_single")],
            [B("👥 3 کاربر | بدون محدودیت", callback_data="ov_three")],
            [B("🔙 بازگشت", callback_data="home")],
        ]),
    )


async def show_ov_single(u, c):
    await u.callback_query.edit_message_text(
        "👤 OPEN VPN VIP\n"
        "یک کاربر | 30 روز\n\n"
        "حجم موردنظر را انتخاب کنید:",
        reply_markup=M([
            [B("20GB — 199,000 تومان", callback_data="plan_ov20")],
            [B("30GB — 249,000 تومان", callback_data="plan_ov30")],
            [B("50GB — 299,000 تومان", callback_data="plan_ov50")],
            [B("100GB — 499,000 تومان", callback_data="plan_ov100")],
            [B("200GB — 990,000 تومان", callback_data="plan_ov200")],
            [B("🔙 بازگشت", callback_data="ov")],
        ]),
    )


async def show_ov_three(u, c):
    await u.callback_query.edit_message_text(
        "👥 OPEN VPN VIP\n"
        "سه کاربر | بدون محدودیت زمانی\n\n"
        "حجم موردنظر را انتخاب کنید:",
        reply_markup=M([
            [B("30GB — 299,000 تومان", callback_data="plan_ov330")],
            [B("50GB — 499,000 تومان", callback_data="plan_ov350")],
            [B("100GB — 990,000 تومان", callback_data="plan_ov3100")],
            [B("200GB — 1,900,000 تومان", callback_data="plan_ov3200")],
            [B("🔙 بازگشت", callback_data="ov")],
        ]),
    )


async def show_npv(u, c):
    await u.callback_query.edit_message_text(
        "🔵 NPV Tunnel | اقتصادی\n\n"
        "مدت: 1 ماه\n"
        "تعداد کاربران: نامحدود\n\n"
        "حجم موردنظر را انتخاب کنید:",
        reply_markup=M([
            [B("25GB — 145,000 تومان", callback_data="plan_npv25")],
            [B("50GB — 220,000 تومان", callback_data="plan_npv50")],
            [B("80GB — 300,000 تومان", callback_data="plan_npv80")],
            [B("🔙 بازگشت", callback_data="home")],
        ]),
    )


# =========================
# انتخاب پلن
# =========================

async def show_plan(u, c, key):
    if key not in P:
        await u.callback_query.answer("پلن پیدا نشد.", show_alert=True)
        return

    service, volume, users, duration, price = P[key]

    text = (
        f"📦 {service}\n\n"
        f"💾 حجم: {volume}\n"
        f"👥 کاربران: {users}\n"
        f"⏱ مدت: {duration}\n"
        f"💰 مبلغ: {price} تومان\n\n"
        "برای ادامه روی «پرداخت» بزنید."
    )

    await u.callback_query.edit_message_text(
        text,
        reply_markup=M([
            [B("💳 اطلاعات پرداخت", callback_data=f"pay_{key}")],
            [B("🔙 بازگشت", callback_data="home")],
        ]),
    )


# =========================
# اطلاعات پرداخت
# =========================

async def payment_info(u, c, key):
    if key not in P:
        return

    service, volume, users, duration, price = P[key]

    await u.callback_query.edit_message_text(
        "💳 اطلاعات پرداخت\n\n"
        f"📦 سرویس: {service}\n"
        f"💾 حجم: {volume}\n"
        f"💰 مبلغ: {price} تومان\n\n"
        f"🏦 شماره کارت:\n"
        f"`{CARD}`\n\n"
        "👤 به نام:\n"
        "محمدحسین شیخی\n\n"
        "بعد از پرداخت، تصویر رسید را ارسال کنید.",
        parse_mode="Markdown",
        reply_markup=M([
            [B("📤 ارسال رسید", callback_data=f"receipt_{key}")],
            [B("🔙 بازگشت", callback_data=f"plan_{key}")],
        ]),
    )


# =========================
# شروع ارسال رسید
# =========================

async def receipt_start(u, c, key):
    if key not in P:
        return

    c.user_data["receipt_plan"] = key

    await u.callback_query.edit_message_text(
        "📤 ارسال رسید\n\n"
        "لطفاً تصویر رسید پرداخت را همینجا ارسال کنید.\n\n"
        "⚠️ رسید باید واضح و خوانا باشد."
    )


# =========================
# دریافت رسید
# =========================

async def receipt(u, c):
    key = c.user_data.get("receipt_plan")

    if not key or key not in P:
        return

    if not u.message.photo:
        await u.message.reply_text(
            "❌ لطفاً تصویر رسید را به صورت عکس ارسال کنید."
        )
        return

    service, volume, users, duration, price = P[key]

    number = oid()

    order = {
        "number": number,
        "user_id": u.effective_user.id,
        "username": u.effective_user.username or "بدون یوزرنیم",
        "name": u.effective_user.full_name,
        "service": service,
        "volume": volume,
        "users": users,
        "duration": duration,
        "price": price,
        "plan": key,
        "status": "pending",
        "step": None,
    }

    if "orders" not in c.bot_data:
        c.bot_data["orders"] = {}

    c.bot_data["orders"][number] = order

    caption = (
        "🧾 سفارش جدید\n\n"
        f"{order_text(order)}\n\n"
        "⬆️ تصویر رسید در پیام بالا/پایین ارسال شده است."
    )

    # ارسال عکس رسید به ادمین
    photo = u.message.photo[-1]

    await c.bot.send_photo(
        chat_id=ADMIN,
        photo=photo.file_id,
        caption=caption,
        reply_markup=M([
            [
                B("✅ تأیید", callback_data=f"approve_{number}"),
                B("❌ رد", callback_data=f"reject_{number}"),
            ]
        ]),
    )

    await u.message.reply_text(
        f"✅ رسید شما دریافت شد.\n\n"
        f"🧾 شماره سفارش: #{number}\n\n"
        "⏳ سفارش شما در حال بررسی است.\n"
        "پس از تأیید پرداخت، سرویس برای شما ارسال خواهد شد."
    )

    c.user_data.pop("receipt_plan", None)


# =========================
# تأیید / رد سفارش
# =========================

async def admin_action(u, c, action, number):
    if u.effective_user.id != ADMIN:
        return

    orders = c.bot_data.get("orders", {})
    order = None

    for o in orders.values():
        if str(o["number"]) == str(number):
            order = o
            break

    if not order:
        await u.callback_query.answer(
            "سفارش پیدا نشد.",
            show_alert=True,
        )
        return

    uid = order["user_id"]

    if action == "approve":
        order["status"] = "approved"

        await c.bot.send_message(
            uid,
            f"✅ پرداخت سفارش #{number} تأیید شد.\n\n"
            "⏳ سفارش شما وارد مرحله آماده‌سازی شد."
        )

        await u.callback_query.edit_message_text(
            order_text(order) +
            "\n\n🟢 سفارش تأیید شد.",
            reply_markup=M([
                [B("📦 شروع تحویل", callback_data=f"deliver_{number}")],
                [B("🔙 پنل مدیریت", callback_data="adm_home")],
            ]),
        )

    elif action == "reject":
        order["status"] = "rejected"

        await c.bot.send_message(
            uid,
            f"❌ پرداخت سفارش #{number} تأیید نشد.\n\n"
            "در صورت نیاز با پشتیبانی تماس بگیرید."
        )

        await u.callback_query.edit_message_text(
            order_text(order) +
            "\n\n🔴 سفارش رد شد.",
            reply_markup=M([
                [B("🔙 پنل مدیریت", callback_data="adm_home")]
            ]),
        )


# =========================
# انتخاب سفارش برای تحویل
# =========================

async def select_delivery_order(u, c, number):
    if u.effective_user.id != ADMIN:
        return

    orders = c.bot_data.get("orders", {})
    order = None

    for o in orders.values():
        if str(o["number"]) == str(number):
            order = o
            break

    if not order:
        await u.callback_query.answer(
            "سفارش پیدا نشد.",
            show_alert=True,
        )
        return

    if order["status"] not in ("approved", "delivery"):
        await u.callback_query.answer(
            "این سفارش در وضعیت قابل تحویل نیست.",
            show_alert=True,
        )
        return

    order["status"] = "delivery"

    c.user_data["delivery_order"] = number

    if order["service"] == "OPEN VPN VIP":
        order["step"] = "login"

        await u.callback_query.edit_message_text(
            order_text(order) +
            "\n\n📦 مرحله تحویل:\n"
            "لطفاً یوزرنیم و پسورد OpenVPN را در پیام بعدی ارسال کنید.",
            reply_markup=M([
                [B("❌ لغو تحویل", callback_data="cancel_delivery")]
            ]),
        )

    else:
        order["step"] = "npv"

        await u.callback_query.edit_message_text(
            order_text(order) +
            "\n\n📦 مرحله تحویل:\n"
            "لطفاً لینک اشتراک NPV را در پیام بعدی ارسال کنید.",
            reply_markup=M([
                [B("❌ لغو تحویل", callback_data="cancel_delivery")]
            ]),
        )


# =========================
# لغو تحویل
# =========================

async def cancel_delivery(u, c):
    if u.effective_user.id != ADMIN:
        return

    number = c.user_data.get("delivery_order")

    if number:
        orders = c.bot_data.get("orders", {})

        for order in orders.values():
            if str(order["number"]) == str(number):
                if order["status"] == "delivery":
                    order["status"] = "approved"

                order["step"] = None
                break

    c.user_data.pop("delivery_order", None)

    await admin_menu(u, c)


# =========================
# تحویل سرویس
# =========================

async def delivery(u, c):
    if u.effective_user.id != ADMIN:
        return

    number = c.user_data.get("delivery_order")

    if not number:
        return

    orders = c.bot_data.get("orders", {})
    order = None

    for o in orders.values():
        if str(o["number"]) == str(number):
            order = o
            break

    if not order:
        await u.message.reply_text("❌ سفارش پیدا نشد.")
        c.user_data.pop("delivery_order", None)
        return

    uid = order["user_id"]

    # -------------------------
    # OpenVPN
    # -------------------------

    if order.get("step") == "login":

        if not u.message.text:
            await u.message.reply_text(
                "❌ لطفاً یوزرنیم و پسورد OpenVPN را به صورت متن ارسال کنید."
            )
            return

        await c.bot.send_message(
            uid,
            "🎉 اشتراک OpenVPN شما آماده است.\n\n"
            "🔐 اطلاعات ورود:\n\n"
            + u.message.text
        )

        order["status"] = "completed"
        order["step"] = "done"

        c.user_data.pop("delivery_order", None)

        await u.message.reply_text(
            f"✅ سفارش #{number} تکمیل شد. 🎉"
        )

        # بازگشت خودکار مشتری به منوی اصلی
        await c.bot.send_message(
            uid,
            "🛒 برای خرید مجدد، سرویس موردنظر را انتخاب کنید:",
            reply_markup=home_markup(),
        )

        return

    # -------------------------
    # NPV
    # -------------------------

    if order.get("step") == "npv":

        if not u.message.text:
            await u.message.reply_text(
                "❌ لطفاً لینک اشتراک NPV را به صورت متن ارسال کنید."
            )
            return

        await c.bot.send_message(
            uid,
            "🎉 اشتراک NPV شما با موفقیت ساخته شد ❤️\n\n"
            "🔗 لینک اشتراک شما:\n\n"
            + u.message.text
        )

        order["status"] = "completed"
        order["step"] = "done"

        c.user_data.pop("delivery_order", None)

        await u.message.reply_text(
            f"✅ سفارش #{number} تکمیل شد. 🎉"
        )

        # بازگشت خودکار مشتری به منوی اصلی
        await c.bot.send_message(
            uid,
            "🛒 برای خرید مجدد، سرویس موردنظر را انتخاب کنید:",
            reply_markup=home_markup(),
        )

        return


# =========================
# پشتیبانی
# =========================

async def support(u, c):
    await u.callback_query.edit_message_text(
        "📞 پشتیبانی\n\n"
        "در صورت وجود هرگونه مشکل یا سؤال، با پشتیبانی در ارتباط باشید:\n\n"
        "👤 @mammadhossein1",
        reply_markup=M([
            [B("🔙 بازگشت", callback_data="home")]
        ]),
    )


# =========================
# آمار
# =========================

async def admin_stats(u, c):
    if u.effective_user.id != ADMIN:
        return

    orders = c.bot_data.get("orders", {})

    total = len(orders)

    pending = sum(
        1 for o in orders.values()
        if o["status"] == "pending"
    )

    approved = sum(
        1 for o in orders.values()
        if o["status"] == "approved"
    )

    delivery_count = sum(
        1 for o in orders.values()
        if o["status"] == "delivery"
    )

    completed = sum(
        1 for o in orders.values()
        if o["status"] == "completed"
    )

    rejected = sum(
        1 for o in orders.values()
        if o["status"] == "rejected"
    )

    text = (
        "📊 آمار سفارش‌ها\n\n"
        f"📦 کل: {total}\n"
        f"⏳ در انتظار بررسی: {pending}\n"
        f"🟢 تأیید شده: {approved}\n"
        f"📦 در حال تحویل: {delivery_count}\n"
        f"✅ تکمیل شده: {completed}\n"
        f"🔴 رد شده: {rejected}"
    )

    await u.callback_query.edit_message_text(
        text,
        reply_markup=M([
            [B("🔙 پنل مدیریت", callback_data="adm_home")]
        ]),
    )


# =========================
# مدیریت دکمه‌ها
# =========================

async def btn(u, c):
    q = u.callback_query
    await q.answer()

    data = q.data

    # -------------------------
    # منوی اصلی
    # -------------------------

    if data == "home":
        await q.edit_message_text(
            "🛒 فروشگاه OpenVppn ❤️\n\n"
            "سرویس موردنظر خود را انتخاب کنید:",
            reply_markup=home_markup(),
        )
        return

    # -------------------------
    # سرویس‌ها
    # -------------------------

    if data == "ov":
        await show_ov(u, c)
        return

    if data == "ov_single":
        await show_ov_single(u, c)
        return

    if data == "ov_three":
        await show_ov_three(u, c)
        return

    if data == "npv":
        await show_npv(u, c)
        return

    # -------------------------
    # پلن
    # -------------------------

    if data.startswith("plan_"):
        key = data.replace("plan_", "", 1)
        await show_plan(u, c, key)
        return

    # -------------------------
    # پرداخت
    # -------------------------

    if data.startswith("pay_"):
        key = data.replace("pay_", "", 1)
        await payment_info(u, c, key)
        return

    # -------------------------
    # رسید
    # -------------------------

    if data.startswith("receipt_"):
        key = data.replace("receipt_", "", 1)
        await receipt_start(u, c, key)
        return

    # -------------------------
    # پشتیبانی
    # -------------------------

    if data == "sup":
        await support(u, c)
        return

    # -------------------------
    # پنل ادمین
    # -------------------------

    if data == "adm_home":
        if u.effective_user.id != ADMIN:
            return

        await admin_menu(u, c)
        return

    if data == "adm_new":
        await show_admin_orders(u, c, "pending")
        return

    if data == "adm_approved":
        await show_admin_orders(u, c, "approved")
        return

    if data == "adm_delivery":
        await show_admin_orders(u, c, "delivery")
        return

    if data == "adm_completed":
        await show_admin_orders(u, c, "completed")
        return

    if data == "adm_rejected":
        await show_admin_orders(u, c, "rejected")
        return

    if data == "adm_stats":
        await admin_stats(u, c)
        return

    # -------------------------
    # جزئیات سفارش
    # -------------------------

    if data.startswith("order_"):
        number = data.replace("order_", "", 1)
        await order_detail(u, c, number)
        return

    # -------------------------
    # تأیید / رد
    # -------------------------

    if data.startswith("approve_"):
        number = data.replace("approve_", "", 1)
        await admin_action(u, c, "approve", number)
        return

    if data.startswith("reject_"):
        number = data.replace("reject_", "", 1)
        await admin_action(u, c, "reject", number)
        return

    # -------------------------
    # شروع تحویل
    # -------------------------

    if data.startswith("deliver_"):
        number = data.replace("deliver_", "", 1)
        await select_delivery_order(u, c, number)
        return

    # -------------------------
    # لغو تحویل
    # -------------------------

    if data == "cancel_delivery":
        await cancel_delivery(u, c)
        return


# =========================
# /admin
# =========================

async def admin_command(u, c):
    if u.effective_user.id != ADMIN:
        return

    await admin_menu(u, c)


# =========================
# اجرای ربات
# =========================

def main():
    app = Application.builder().token(TOKEN).build()

    # دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))

    # دکمه‌ها
    app.add_handler(
        CallbackQueryHandler(btn)
    )

    # رسید مشتری
    app.add_handler(
        MessageHandler(
            filters.PHOTO & ~filters.COMMAND,
            receipt,
        )
    )

    # تحویل سرویس توسط ادمین
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            delivery,
        )
    )

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
