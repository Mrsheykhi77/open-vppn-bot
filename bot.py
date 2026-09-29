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


def status_fa(status):
    return {
        "review": "در انتظار بررسی پرداخت",
        "delivery": "در حال آماده‌سازی / تحویل",
        "completed": "تکمیل‌شده",
        "rejected": "ردشده",
    }.get(status, "نامشخص")


def order_text(number, order):
    p = P.get(order["key"])

    if not p:
        return f"🔖 سفارش #{number}"

    return (
        f"🔖 سفارش #{number}\n\n"
        f"👤 {order.get('name', 'نامشخص')}\n"
        f"🆔 {order['uid']}\n\n"
        f"📦 {p[0]}\n"
        f"📊 حجم: {p[1]}\n"
        f"👥 کاربران: {p[2]}\n"
        f"⏳ اعتبار: {p[3]}\n"
        f"💰 مبلغ: {p[4]} تومان\n\n"
        f"📌 وضعیت: {status_fa(order.get('status'))}"
    )


def admin_home_markup():
    return M([
        [B("📦 سفارش‌های جدید", callback_data="adm_new")],
        [B("⏳ سفارش‌های در حال انجام", callback_data="adm_work")],
        [B("✅ سفارش‌های تکمیل‌شده", callback_data="adm_done")],
        [B("❌ سفارش‌های ردشده", callback_data="adm_no")],
        [B("📊 آمار فروش", callback_data="adm_stats")],
    ])


def back_for_status(status):
    return {
        "review": "adm_new",
        "delivery": "adm_work",
        "completed": "adm_done",
        "rejected": "adm_no",
    }.get(status, "adm_home")


async def menu(q, text, buttons):
    await q.edit_message_text(
        text,
        reply_markup=M([
            [B(x, callback_data=y)]
            for x, y in buttons
        ]),
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
        reply_markup=admin_home_markup(),
    )


async def show_admin_orders(
    q,
    c,
    status,
    title,
    callback_name,
):
    orders = c.bot_data.get("orders", {})
    found = []

    for number, order in orders.items():

        if order.get("status") != status:
            continue

        p = P.get(order.get("key"))

        if not p:
            continue

        label = (
            f"🔖 #{number}\n"
            f"📦 {p[0]} | {p[1]}\n"
            f"👤 {order.get('name', 'نامشخص')}\n"
            f"🆔 {order['uid']}"
        )

        found.append(
            (number, label)
        )

    buttons = []

    for number, label in found:
        buttons.append([
            B(
                label,
                callback_data=f"ord_{number}"
            )
        ])

    if not found:
        text = (
            f"{title}\n\n"
            "هیچ سفارشی وجود ندارد."
        )
    else:
        text = (
            f"{title}\n\n"
            "برای دیدن جزئیات، روی سفارش موردنظر بزنید."
        )

    buttons.append([
        B(
            "🔄 بروزرسانی",
            callback_data=callback_name
        )
    ])

    buttons.append([
        B(
            "🔙 پنل مدیریت",
            callback_data="adm_home"
        )
    ])

    await q.edit_message_text(
        text,
        reply_markup=M(buttons),
    )


async def admin_menu(u, c):
    q = u.callback_query
    await q.answer()

    if u.effective_user.id != ADMIN:
        return

    d = q.data

    # HOME
    if d == "adm_home":

        return await q.edit_message_text(
            "🛠️ پنل مدیریت OpenVppn\n\n"
            "مدیریت سفارش‌ها و فروشگاه:",
            reply_markup=admin_home_markup(),
        )

    # ORDERS
    if d in [
        "adm_new",
        "adm_work",
        "adm_done",
        "adm_no",
    ]:

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

        return await show_admin_orders(
            q,
            c,
            status,
            title,
            d,
        )

    # STATS
    if d == "adm_stats":

        orders = c.bot_data.get(
            "orders",
            {}
        )

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
                        "🔄 بروزرسانی",
                        callback_data="adm_stats"
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


# =========================
# ORDER DETAIL
# =========================

async def order_detail(u, c):
    q = u.callback_query
    await q.answer()

    if u.effective_user.id != ADMIN:
        return

    number = q.data[4:]

    order = c.bot_data.get(
        "orders",
        {}
    ).get(number)

    if not order:
        return await q.edit_message_text(
            "❌ سفارش پیدا نشد.",
            reply_markup=M([
                [
                    B(
                        "🔙 پنل مدیریت",
                        callback_data="adm_home"
                    )
                ]
            ]),
        )

    text = order_text(
        number,
        order
    )

    status = order.get("status")

    buttons = []

    # در انتظار بررسی
    if status == "review":

        buttons.append([
            B(
                "✅ تأیید پرداخت",
                callback_data=f"ok{number}"
            ),
            B(
                "❌ رد پرداخت",
                callback_data=f"no{number}"
            ),
        ])

    # در حال تحویل
    elif status == "delivery":

        buttons.append([
            B(
                "📤 تحویل این سفارش",
                callback_data=f"deliver_{number}"
            )
        ])

    buttons.append([
        B(
            "🔙 برگشت",
            callback_data=back_for_status(status)
        )
    ])

    await q.edit_message_text(
        text,
        reply_markup=M(buttons),
    )


# =========================
# SHOP BUTTONS
# =========================

async def btn(u, c):
    q = u.callback_query
    await q.answer()

    d = q.data

    # Admin callbacks
    if d.startswith("adm_"):
        return await admin_menu(u, c)

    if d.startswith("ord_"):
        return await order_detail(u, c)

    if d.startswith("deliver_"):
        return await select_delivery_order(u, c)

    if d == "cancel_delivery":
        return await cancel_delivery(u, c)

    # HOME
    if d == "home":

        await q.message.reply_text(
            "🛒 فروشگاه OpenVppn ❤️\n\n"
            "سرویس را انتخاب کنید:",
            reply_markup=M([
                [
                    B(
                        "🟢 OPEN VPN | VIP",
                        callback_data="ov"
                    )
                ],
                [
                    B(
                        "🔵 NPV Tunnel | اقتصادی",
                        callback_data="npv"
                    )
                ],
                [
                    B(
                        "📞 پشتیبانی",
                        callback_data="sup"
                    )
                ],
            ]),
        )

        return

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

    # THREE USERS
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

    # SUPPORT
    if d == "sup":

        return await menu(
            q,
            "📞 پشتیبانی OpenVppn\n\n"
            "@mammadhossein1",
            [
                ("🔙 برگشت", "home")
            ],
        )

    # PLAN
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
                (
                    "💳 اطلاعات پرداخت",
                    "pay" + d
                ),
                (
                    "🔙 برگشت",
                    "home"
                ),
            ],
        )

    # PAYMENT
    if d.startswith("pay"):

        k = d[3:]
        p = P[k]

        return await menu(
            q,
            f"💳 اطلاعات پرداخت\n\n"
            f"📦 {p[0]} | {p[1]}\n"
            f"💰 {p[4]} تومان\n\n"
            f"💳 کارت:\n{CARD}\n\n"
            f"👤 محمدحسین شیخی\n\n"
            f"پس از واریز رسید را بفرستید.",
            [
                (
                    "📤 ارسال رسید",
                    "rec" + k
                ),
                (
                    "🔙 برگشت",
                    k
                ),
            ],
        )

    # SEND RECEIPT
    if d.startswith("rec"):

        k = d[3:]

        if k not in P:
            return

        c.user_data["order"] = k

        await q.message.reply_text(
            "📸 لطفاً عکس رسید پرداخت را "
            "همینجا ارسال کنید."
        )


# =========================
# RECEIPT
# =========================

async def receipt(u, c):

    k = c.user_data.get("order")

    if k not in P:
        return

    p = P[k]
    x = u.effective_user

    number = oid()

    orders = c.bot_data.setdefault(
        "orders",
        {}
    )

    while number in orders:
        number = oid()

    orders[number] = {
        "uid": x.id,
        "name": x.full_name,
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

    # Forward receipt to admin
    await u.message.forward(ADMIN)

    # Send order information
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

    c.user_data.pop(
        "order",
        None
    )


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
        "orders",
        {}
    ).get(number)

    if not order:
        return await q.message.reply_text(
            "❌ سفارش پیدا نشد."
        )

    uid = order["uid"]
    k = order["key"]

    # REJECT
    if d.startswith("no"):

        order["status"] = "rejected"

        await c.bot.send_message(
            uid,
            f"❌ پرداخت سفارش #{number} "
            f"تأیید نشد.\n\n"
            f"پشتیبانی: @mammadhossein1"
        )

        await q.edit_message_text(
            f"❌ سفارش #{number} رد شد.",
            reply_markup=M([
                [
                    B(
                        "🔙 سفارش‌های ردشده",
                        callback_data="adm_no"
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

        return

    # APPROVE
    order["status"] = "delivery"

    if k.startswith("ov"):

        order["step"] = "file"

        msg = (
            "📎 فایل OpenVPN را "
            "برای همین سفارش بفرستید.\n\n"
            f"🔖 سفارش: #{number}"
        )

    else:

        order["step"] = "npv"

        msg = (
            "📝 ساب‌لینک NPV را "
            "برای همین سفارش بفرستید.\n\n"
            f"🔖 سفارش: #{number}"
        )

    await c.bot.send_message(
        uid,
        f"✅ پرداخت سفارش #{number} تأیید شد.\n\n"
        f"🕐 در حال آماده‌سازی سفارش شما..."
    )

    await q.edit_message_text(
        f"✅ سفارش #{number} تأیید شد.\n\n"
        f"{msg}",
        reply_markup=M([
            [
                B(
                    "📤 انتخاب برای تحویل",
                    callback_data=f"deliver_{number}"
                )
            ],
            [
                B(
                    "🔙 سفارش‌های در حال انجام",
                    callback_data="adm_work"
                )
            ],
        ]),
    )


# =========================
# SELECT DELIVERY ORDER
# =========================

async def select_delivery_order(u, c):

    q = u.callback_query
    await q.answer()

    if u.effective_user.id != ADMIN:
        return

    number = q.data[len("deliver_"):]

    order = c.bot_data.get(
        "orders",
        {}
    ).get(number)

    if not order:
        return await q.edit_message_text(
            "❌ سفارش پیدا نشد."
        )

    if order.get("status") != "delivery":

        return await q.edit_message_text(
            "⚠️ این سفارش دیگر در وضعیت "
            "تحویل نیست.",
            reply_markup=M([
                [
                    B(
                        "🔙 سفارش‌های در حال انجام",
                        callback_data="adm_work"
                    )
                ]
            ]),
        )

    # مشخص کردن سفارش فعال
    c.user_data["delivery_order"] = number

    if order.get("step") == "file":

        text = (
            f"📤 تحویل سفارش #{number}\n\n"
            f"📎 حالا فایل OpenVPN همین سفارش "
            f"را به ربات بفرستید.\n\n"
            f"⚠️ فایل فقط برای مشتری همین سفارش "
            f"ارسال خواهد شد."
        )

    else:

        text = (
            f"📤 تحویل سفارش #{number}\n\n"
            f"📝 حالا ساب‌لینک NPV همین سفارش "
            f"را ارسال کنید.\n\n"
            f"⚠️ لینک فقط برای مشتری همین سفارش "
            f"ارسال خواهد شد."
        )

    await q.edit_message_text(
        text,
        reply_markup=M([
            [
                B(
                    "❌ لغو انتخاب",
                    callback_data="cancel_delivery"
                )
            ],
            [
                B(
                    "🔙 سفارش‌های در حال انجام",
                    callback_data="adm_work"
                )
            ],
        ]),
    )


# =========================
# CANCEL DELIVERY
# =========================

async def cancel_delivery(u, c):

    q = u.callback_query
    await q.answer()

    if u.effective_user.id != ADMIN:
        return

    c.user_data.pop(
        "delivery_order",
        None
    )

    await q.edit_message_text(
        "❌ انتخاب سفارش برای تحویل لغو شد.",
        reply_markup=M([
            [
                B(
                    "🔙 سفارش‌های در حال انجام",
                    callback_data="adm_work"
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


# =========================
# DELIVERY
# =========================

async def delivery(u, c):

    if u.effective_user.id != ADMIN:
        return

    # فقط سفارش انتخاب‌شده
    number = c.user_data.get(
        "delivery_order"
    )

    if not number:
        return

    order = c.bot_data.get(
        "orders",
        {}
    ).get(number)

    if not order or order.get("status") != "delivery":

        c.user_data.pop(
            "delivery_order",
            None
        )

        return await u.message.reply_text(
            "⚠️ سفارش انتخاب‌شده "
            "دیگر قابل تحویل نیست."
        )

    uid = order["uid"]

    # =====================
    # OPENVPN FILE
    # =====================

    if order.get("step") == "file":

        if not u.message.document:

            return await u.message.reply_text(
                f"📎 لطفاً فایل OpenVPN "
                f"سفارش #{number} را "
                f"به‌صورت فایل (Document) ارسال کنید."
            )

        await u.message.copy(uid)

        await c.bot.send_message(
            uid,
            "✔️ پروفایل سرور "
            "(برای همه سرویس‌ها)\n\n"
            "✔️ سایت کاربران جهت نمایش میزان\n"
            "اعتبار (بدون VPN)\n"
            "🌐 https://promiec.com/users/\n"
            "⚠️ لینک بالا را بدون VPN باز کنید."
        )

        order["step"] = "login"

        await u.message.reply_text(
            f"✅ فایل سفارش #{number} ارسال شد.\n\n"
            f"👤 حالا یوزرنیم و پسورد "
            f"همین سفارش را در یک پیام متنی "
            f"بفرستید."
        )

        return

    # =====================
    # OPENVPN LOGIN
    # =====================

    if order.get("step") == "login":

        if not u.message.text:

            return await u.message.reply_text(
                f"📝 لطفاً یوزرنیم و پسورد "
                f"سفارش #{number} را "
                f"به‌صورت متن ارسال کنید."
            )

        await c.bot.send_message(
            uid,
            u.message.text
        )

        order["status"] = "completed"
        order["step"] = "done"

        c.user_data.pop(
            "delivery_order",
            None
        )

        await u.message.reply_text(
            f"✅ سفارش #{number} تکمیل شد. 🎉"
        )

        return

    # =====================
    # NPV LINK
    # =====================

    if order.get("step") == "npv":

        if not u.message.text:

            return await u.message.reply_text(
                f"📝 لطفاً ساب‌لینک "
                f"سفارش #{number} را "
                f"به‌صورت متن ارسال کنید."
            )

        await c.bot.send_message(
            uid,
            "تبریک اشتراک شما با موفقیت ساخته شد ❤️\n\n"
            "🔗 لینک اشتراک شما:\n"
            + u.message.text
        )

        order["status"] = "completed"
        order["step"] = "done"

        c.user_data.pop(
            "delivery_order",
            None
        )

        await u.message.reply_text(
            f"✅ سفارش #{number} تکمیل شد. 🎉"
        )

        return


# =========================
# BOT
# =========================

app = Application.builder().token(TOKEN).build()


# Start
app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


# Admin panel
app.add_handler(
    CommandHandler(
        "admin",
        admin_panel
    )
)


# Approve / Reject
app.add_handler(
    CallbackQueryHandler(
        admin,
        pattern=r"^(ok|no)"
    )
)


# Order details
app.add_handler(
    CallbackQueryHandler(
        order_detail,
        pattern=r"^ord_"
    )
)


# Select delivery
app.add_handler(
    CallbackQueryHandler(
        select_delivery_order,
        pattern=r"^deliver_"
    )
)


# Cancel delivery
app.add_handler(
    CallbackQueryHandler(
        cancel_delivery,
        pattern=r"^cancel_delivery$"
    )
)


# Admin menu
app.add_handler(
    CallbackQueryHandler(
        admin_menu,
        pattern=r"^adm_"
    )
)


# General shop buttons
app.add_handler(
    CallbackQueryHandler(
        btn
    )
)


# Customer receipt
app.add_handler(
    MessageHandler(
        filters.PHOTO,
        receipt
    )
)


# Admin delivery
app.add_handler(
    MessageHandler(
        filters.Document.ALL | filters.TEXT,
        delivery
    )
)


app.run_polling()
