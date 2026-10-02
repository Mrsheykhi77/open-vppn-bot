import os
import random
import json
import sqlite3
import datetime

from telegram import InlineKeyboardButton as B
from telegram import InlineKeyboardMarkup as M
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)


# =========================================================
# SETTINGS
# =========================================================

TOKEN = os.environ["BOT_TOKEN"]
CARD = os.environ["CARD_NUMBER"]

ADMIN = 704985066


# =========================================================
# PRODUCTS
# =========================================================

P = {
    # OPEN VPN VIP - 1 User - 30 Days
    "ov20": ("OPEN VPN VIP", "20GB", "1", "30 روز", "199,000"),
    "ov30": ("OPEN VPN VIP", "30GB", "1", "30 روز", "249,000"),
    "ov50": ("OPEN VPN VIP", "50GB", "1", "30 روز", "299,000"),
    "ov100": ("OPEN VPN VIP", "100GB", "1", "30 روز", "499,000"),
    "ov200": ("OPEN VPN VIP", "200GB", "1", "30 روز", "990,000"),

    # OPEN VPN VIP - 3 Users - No Time Limit
    "ov330": ("OPEN VPN VIP", "30GB", "3", "بدون محدودیت", "299,000"),
    "ov350": ("OPEN VPN VIP", "50GB", "3", "بدون محدودیت", "499,000"),
    "ov3100": ("OPEN VPN VIP", "100GB", "3", "بدون محدودیت", "990,000"),
    "ov3200": ("OPEN VPN VIP", "200GB", "3", "بدون محدودیت", "1,900,000"),

    # NPV Tunnel
    "npv25": ("NPV Tunnel", "25GB", "نامحدود", "30 روز", "145,000"),
    "npv50": ("NPV Tunnel", "50GB", "نامحدود", "30 روز", "220,000"),
    "npv80": ("NPV Tunnel", "80GB", "نامحدود", "30 روز", "300,000"),
}


# =========================================================
# MAIN MENU
# =========================================================

def home_markup():
    return M([
        [B("🟢 OPEN VPN | VIP", callback_data="ov")],
        [B("🔵 NPV Tunnel | اقتصادی", callback_data="npv")],
        [B("📞 پشتیبانی", callback_data="sup")],
    ])


# =========================================================
# SQLITE DATABASE
# =========================================================
DB_FILE = "/root/open-vppn-bot/orders.db"

def db_init():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            number TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            first_start TEXT NOT NULL,
            last_start TEXT NOT NULL,
            start_count INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()

def db_save_user(user):
    conn = sqlite3.connect(DB_FILE)
    now = datetime.datetime.now().isoformat(timespec="seconds")
    user_id = user.id
    username = user.username or ""
    first_name = user.first_name or ""

    conn.execute("""
        INSERT INTO users (
            user_id, username, first_name,
            first_start, last_start, start_count
        )
        VALUES (?, ?, ?, ?, ?, 1)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_start = excluded.last_start,
            start_count = users.start_count + 1
    """, (
        user_id,
        username,
        first_name,
        now,
        now
    ))

    conn.commit()
    conn.close()

def db_load_orders():
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT number, data FROM orders").fetchall()
    conn.close()
    return {
        number: json.loads(data)
        for number, data in rows
    }

def db_save_order(number, order):
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "INSERT OR REPLACE INTO orders(number, data) VALUES(?, ?)",
        (number, json.dumps(order, ensure_ascii=False))
    )
    conn.commit()
    conn.close()

# =========================================================
# ORDER HELPERS
# =========================================================

def new_order_id():
    return f"OV-{random.randint(1000, 9999)}"


def status_fa(status):
    return {
        "review": "در انتظار بررسی پرداخت",
        "delivery": "در حال آماده‌سازی / تحویل",
        "completed": "تکمیل‌شده",
        "rejected": "ردشده",
    }.get(status, "نامشخص")


def get_order(c, number):
    orders = c.bot_data.get("orders", {})
    return orders.get(number)


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
        [B("👥 کاربران ربات", callback_data="adm_users")],
        [B("🔎 جستجوی سفارش", callback_data="adm_search")],
    ])


def price_to_int(price):
    return int(str(price).replace(",", "").replace("٬", ""))


def back_for_status(status):
    return {
        "review": "adm_new",
        "delivery": "adm_work",
        "completed": "adm_done",
        "rejected": "adm_no",
    }.get(status, "adm_home")


# =========================================================
# /START
# =========================================================

async def start(u, c):
    db_save_user(u.effective_user)
    await u.message.reply_text(
        "🛒 فروشگاه OpenVppn ❤️\n\n"
        "سرویس را انتخاب کنید:",
        reply_markup=home_markup(),
    )


# =========================================================
# ADMIN PANEL
# =========================================================

async def admin_panel(u, c):
    if u.effective_user.id != ADMIN:
        return await u.message.reply_text("⛔ دسترسی ندارید.")

    await u.message.reply_text(
        "🛠️ پنل مدیریت OpenVppn\n\n"
        "مدیریت سفارش‌ها و فروشگاه:",
        reply_markup=admin_home_markup(),
    )


async def show_admin_orders(q, c, status, title, callback_name):
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

        found.append((number, label))

    buttons = []

    for number, label in found:
        buttons.append([
            B(
                label,
                callback_data=f"ord_{number}"
            )
        ])

    if not found:
        text = f"{title}\n\nهیچ سفارشی وجود ندارد."
    else:
        text = (
            f"{title}\n\n"
            "برای دیدن جزئیات، روی سفارش موردنظر بزنید."
        )

    buttons.append([
        B("🔄 بروزرسانی", callback_data=callback_name)
    ])

    buttons.append([
        B("🔙 پنل مدیریت", callback_data="adm_home")
    ])

    await q.edit_message_text(
        text,
        reply_markup=M(buttons),
    )


async def admin_menu(u, c):
    q = u.callback_query

    if u.effective_user.id != ADMIN:
        return

    d = q.data

    if d == "adm_home":
        await q.edit_message_text(
            "🛠️ پنل مدیریت OpenVppn\n\n"
            "مدیریت سفارش‌ها و فروشگاه:",
            reply_markup=admin_home_markup(),
        )
        return

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

        await show_admin_orders(
            q,
            c,
            status,
            title,
            d,
        )
        return

    if d == "adm_users":
        conn = sqlite3.connect(DB_FILE)
        users = conn.execute(
            "SELECT user_id, username, first_name, start_count "
            "FROM users ORDER BY first_start ASC"
        ).fetchall()
        conn.close()

        if not users:
            text = "👥 کاربران ربات\n\nهنوز کاربری ثبت نشده است."
        else:
            lines = [
                f"👥 کاربران ربات — {len(users)} نفر\n"
            ]
            for i, (user_id, username, first_name, start_count) in enumerate(users, 1):
                name = first_name or "بدون نام"
                user_text = f"@{username}" if username else f"ID: {user_id}"
                lines.append(
                    f"{i}. {name}\n"
                    f"   {user_text}\n"
                    f"   /start: {start_count} بار"
                )
            text = "\n\n".join(lines)

        await q.edit_message_text(
            text,
            reply_markup=M([
                [B("🔄 بروزرسانی", callback_data="adm_users")],
                [B("🔙 پنل مدیریت", callback_data="adm_home")],
            ]),
        )
        return

    if d == "adm_stats":
        orders = c.bot_data.get("orders", {})

        conn = sqlite3.connect(DB_FILE)
        users_count = conn.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]
        conn.close()

        now = datetime.datetime.now()
        today = now.date()
        this_month = now.strftime("%Y-%m")

        total = len(orders)

        review = sum(
            1 for o in orders.values()
            if o.get("status") == "review"
        )

        work = sum(
            1 for o in orders.values()
            if o.get("status") == "delivery"
        )

        done_orders = [
            o for o in orders.values()
            if o.get("status") == "completed"
        ]

        done = len(done_orders)

        rejected = sum(
            1 for o in orders.values()
            if o.get("status") == "rejected"
        )

        total_revenue = sum(
            price_to_int(P[o["key"]][4])
            for o in done_orders
            if o.get("key") in P
        )

        today_orders = []
        month_orders = []

        for o in done_orders:
            completed_at = o.get("completed_at")

            if not completed_at:
                continue

            try:
                completed_time = datetime.datetime.fromisoformat(completed_at)
            except ValueError:
                continue

            if completed_time.date() == today:
                today_orders.append(o)

            if completed_time.strftime("%Y-%m") == this_month:
                month_orders.append(o)

        today_revenue = sum(
            price_to_int(P[o["key"]][4])
            for o in today_orders
            if o.get("key") in P
        )

        month_revenue = sum(
            price_to_int(P[o["key"]][4])
            for o in month_orders
            if o.get("key") in P
        )

        await q.edit_message_text(
            "📊 آمار فروشگاه\n\n"
            f"👥 کل کاربران: {users_count}\n"
            f"📦 کل سفارش‌ها: {total}\n"
            f"📦 در انتظار بررسی: {review}\n"
            f"⏳ در حال انجام: {work}\n"
            f"✅ تکمیل‌شده: {done}\n"
            f"❌ ردشده: {rejected}\n\n"
            f"💰 مجموع فروش: {total_revenue:,} تومان\n"
            f"📅 فروش امروز: {len(today_orders)} سفارش | {today_revenue:,} تومان\n"
            f"🗓 فروش این ماه: {len(month_orders)} سفارش | {month_revenue:,} تومان",
            reply_markup=M([
                [B("🔄 بروزرسانی", callback_data="adm_stats")],
                [B("🔙 پنل مدیریت", callback_data="adm_home")],
            ]),
        )


    if d == "adm_search":
        c.user_data["search_order"] = True

        await q.edit_message_text(
            "🔎 جستجوی سفارش\n\n"
            "لطفاً شماره سفارش را وارد کنید.\n"
            "مثال: 12345",
            reply_markup=M([
                [B("🔙 پنل مدیریت", callback_data="adm_home")]
            ]),
        )
        return


# =========================================================
# ORDER DETAIL
# =========================================================

async def order_detail(u, c):
    q = u.callback_query

    if u.effective_user.id != ADMIN:
        return

    number = q.data[4:]

    order = get_order(c, number)

    if not order:
        await q.edit_message_text(
            "❌ سفارش پیدا نشد.",
            reply_markup=M([
                [B("🔙 پنل مدیریت", callback_data="adm_home")]
            ]),
        )
        return

    text = order_text(number, order)

    status = order.get("status")

    buttons = []

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

    elif status == "delivery":
        buttons.append([
            B(
                "📤 انتخاب برای تحویل",
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


# =========================================================
# CUSTOMER MENUS
# =========================================================

async def show_openvpn(q):
    await q.edit_message_text(
        "🟢 OPEN VPN VIP\n\n"
        "تک‌کاربره — 30 روزه",
        reply_markup=M([
            [B("20GB — 199,000", callback_data="ov20")],
            [B("30GB — 249,000", callback_data="ov30")],
            [B("50GB — 299,000", callback_data="ov50")],
            [B("100GB — 499,000", callback_data="ov100")],
            [B("200GB — 990,000", callback_data="ov200")],
            [B("👥 سه کاربره", callback_data="three")],
            [B("🔙 برگشت", callback_data="home")],
        ]),
    )


async def show_three_users(q):
    await q.edit_message_text(
        "👥 OPEN VPN | سه کاربره\n\n"
        "⏳ بدون محدودیت زمانی",
        reply_markup=M([
            [B("30GB — 299,000", callback_data="ov330")],
            [B("50GB — 499,000", callback_data="ov350")],
            [B("100GB — 990,000", callback_data="ov3100")],
            [B("200GB — 1,900,000", callback_data="ov3200")],
            [B("🔙 برگشت", callback_data="ov")],
        ]),
    )


async def show_npv(q):
    await q.edit_message_text(
        "🔵 NPV Tunnel | اقتصادی\n\n"
        "👥 کاربر نامحدود\n"
        "⏳ 30 روز",
        reply_markup=M([
            [B("25GB — 145,000", callback_data="npv25")],
            [B("50GB — 220,000", callback_data="npv50")],
            [B("80GB — 300,000", callback_data="npv80")],
            [B("🔙 برگشت", callback_data="home")],
        ]),
    )


async def show_plan(q, key):
    p = P.get(key)

    if not p:
        return

    await q.edit_message_text(
        f"📦 {p[0]}\n\n"
        f"📊 {p[1]}\n"
        f"👤 کاربران: {p[2]}\n"
        f"⏳ {p[3]}\n"
        f"💰 {p[4]} تومان",
        reply_markup=M([
            [
                B(
                    "💳 اطلاعات پرداخت",
                    callback_data=f"pay{key}"
                )
            ],
            [
                B(
                    "🔙 برگشت",
                    callback_data="home"
                )
            ],
        ]),
    )


async def payment_info(q, key):
    p = P.get(key)

    if not p:
        return

    await q.edit_message_text(
        f"💳 اطلاعات پرداخت\n\n"
        f"📦 {p[0]} | {p[1]}\n"
        f"💰 {p[4]} تومان\n\n"
        f"💳 کارت:\n"
        f"{CARD}\n\n"
        "👤 محمدحسین شیخی\n\n"
        "پس از واریز رسید را بفرستید.",
        reply_markup=M([
            [
                B(
                    "📤 ارسال رسید",
                    callback_data=f"rec{key}"
                )
            ],
            [
                B(
                    "🔙 برگشت",
                    callback_data=key
                )
            ],
        ]),
    )


# =========================================================
# MAIN BUTTON HANDLER
# =========================================================

async def btn(u, c):
    q = u.callback_query

    await q.answer()

    d = q.data

    # -------------------------
    # HOME
    # -------------------------

    if d == "home":
        await q.message.reply_text(
            "🛒 فروشگاه OpenVppn ❤️\n\n"
            "سرویس را انتخاب کنید:",
            reply_markup=home_markup(),
        )
        return

    # -------------------------
    # OPEN VPN
    # -------------------------

    if d == "ov":
        await show_openvpn(q)
        return

    if d == "three":
        await show_three_users(q)
        return

    # -------------------------
    # NPV
    # -------------------------

    if d == "npv":
        await show_npv(q)
        return

    # -------------------------
    # SUPPORT
    # -------------------------

    if d == "sup":
        await q.edit_message_text(
            "📞 پشتیبانی OpenVppn\n\n"
            "@mammadhossein1",
            reply_markup=M([
                [B("🔙 برگشت", callback_data="home")]
            ]),
        )
        return

    # -------------------------
    # PLAN
    # -------------------------

    if d in P:
        await show_plan(q, d)
        return

    # -------------------------
    # PAYMENT
    # -------------------------

    if d.startswith("pay"):
        key = d[3:]

        await payment_info(q, key)
        return

    # -------------------------
    # RECEIPT
    # -------------------------

    if d.startswith("rec"):
        key = d[3:]

        if key not in P:
            return

        c.user_data["order"] = key

        await q.message.reply_text(
            "📸 لطفاً عکس رسید پرداخت را همینجا ارسال کنید."
        )

        return

    # -------------------------
    # ADMIN
    # -------------------------

    if d.startswith("adm_"):
        await admin_menu(u, c)
        return

    # -------------------------
    # ORDER DETAIL
    # -------------------------

    if d.startswith("ord_"):
        await order_detail(u, c)
        return

    # -------------------------
    # DELIVERY
    # -------------------------

    if d.startswith("deliver_"):
        await select_delivery_order(u, c)
        return

    # -------------------------
    # CANCEL DELIVERY
    # -------------------------

    if d == "cancel_delivery":
        await cancel_delivery(u, c)
        return


# =========================================================
# CUSTOMER RECEIPT
# =========================================================

async def receipt(u, c):
    key = c.user_data.get("order")

    if key not in P:
        return

    p = P[key]

    x = u.effective_user

    number = new_order_id()

    orders = c.bot_data.setdefault(
        "orders",
        {}
    )

    while number in orders:
        number = new_order_id()

    orders[number] = {
        "uid": x.id,
        "name": x.full_name,
        "username": x.username or "",
        "key": key,
        "status": "review",
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }

    db_save_order(number, orders[number])

    text = (
        f"🧾 سفارش جدید\n\n"
        f"🔖 شماره سفارش: #{number}\n\n"
        f"👤 {x.full_name}\n"
        f"🆔 {x.id}\n\n"
        f"📦 {p[0]}\n"
        f"📊 {p[1]}\n"
        f"👥 {p[2]}\n"
        f"⏳ {p[3]}\n"
        f"💰 {p[4]} تومان"
    )

    # ارسال خود رسید به ادمین
    await u.message.forward(ADMIN)

    # ارسال اطلاعات سفارش + دکمه‌ها
    await c.bot.send_message(
        ADMIN,
        text,
        reply_markup=M([
            [
                B(
                    "✅ تأیید پرداخت",
                    callback_data=f"ok{number}"
                ),
                B(
                    "❌ رد پرداخت",
                    callback_data=f"no{number}"
                ),
            ]
        ]),
    )

    await u.message.reply_text(
        f"✅ رسید دریافت شد.\n\n"
        f"🔖 شماره سفارش: #{number}\n"
        "🕐 وضعیت: در حال بررسی پرداخت"
    )

    c.user_data.pop("order", None)


# =========================================================
# ADMIN APPROVE / REJECT
# =========================================================

async def admin_action(u, c):
    q = u.callback_query

    if u.effective_user.id != ADMIN:
        return

    d = q.data

    number = d[2:]

    order = get_order(c, number)

    if not order:
        await q.answer(
            "❌ سفارش پیدا نشد.",
            show_alert=True,
        )
        return

    uid = order["uid"]

    key = order["key"]

    # -------------------------
    # REJECT
    # -------------------------

    if d.startswith("no"):
        order["status"] = "rejected"
        db_save_order(number, order)

        await c.bot.send_message(
            uid,
            f"❌ پرداخت سفارش #{number} تأیید نشد.\n\n"
            "پشتیبانی: @mammadhossein1"
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

    # -------------------------
    # APPROVE
    # -------------------------

    order["status"] = "delivery"

    if key.startswith("ov"):
        order["step"] = "file"

        msg = (
            f"📎 فایل OpenVPN را برای همین سفارش بفرستید.\n\n"
            f"🔖 سفارش: #{number}"
        )

    else:
        order["step"] = "npv"

        msg = (
            f"📝 ساب‌لینک NPV را برای همین سفارش بفرستید.\n\n"
            f"🔖 سفارش: #{number}"
        )

    await c.bot.send_message(
        uid,
        f"✅ پرداخت سفارش #{number} تأیید شد.\n\n"
        "🕐 در حال آماده‌سازی سفارش شما..."
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


# =========================================================
# SELECT ORDER FOR DELIVERY
# =========================================================

async def select_delivery_order(u, c):
    q = u.callback_query

    if u.effective_user.id != ADMIN:
        return

    number = q.data[len("deliver_"):]

    order = get_order(c, number)

    if not order:
        await q.edit_message_text(
            "❌ سفارش پیدا نشد."
        )
        return

    if order.get("status") != "delivery":
        await q.edit_message_text(
            "⚠️ این سفارش دیگر در وضعیت تحویل نیست.",
            reply_markup=M([
                [
                    B(
                        "🔙 سفارش‌های در حال انجام",
                        callback_data="adm_work"
                    )
                ]
            ]),
        )
        return

    c.user_data["delivery_order"] = number

    if order.get("step") == "file":

        text = (
            f"📤 تحویل سفارش #{number}\n\n"
            "📎 حالا فایل OpenVPN همین سفارش را "
            "به صورت فایل (Document) ارسال کنید.\n\n"
            "⚠️ فایل فقط برای مشتری همین سفارش ارسال خواهد شد."
        )

    else:

        text = (
            f"📤 تحویل سفارش #{number}\n\n"
            "📝 حالا ساب‌لینک NPV همین سفارش را "
            "به صورت متن ارسال کنید.\n\n"
            "⚠️ لینک فقط برای مشتری همین سفارش ارسال خواهد شد."
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


# =========================================================
# CANCEL DELIVERY
# =========================================================

async def cancel_delivery(u, c):
    q = u.callback_query

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


# =========================================================
# DELIVERY
# =========================================================

async def delivery(u, c):
    if u.effective_user.id != ADMIN:
        return

    if c.user_data.get("search_order"):
        number = (u.message.text or "").strip()

        if not number.isdigit():
            await u.message.reply_text(
                "⚠️ شماره سفارش باید فقط عدد باشد.\n"
                "مثال: 12345"
            )
            return

        order = get_order(c, number)

        if not order:
            await u.message.reply_text(
                f"❌ سفارش #{number} پیدا نشد.",
                reply_markup=M([
                    [B("🔎 جستجوی دوباره", callback_data="adm_search")],
                    [B("🔙 پنل مدیریت", callback_data="adm_home")],
                ]),
            )
            return

        c.user_data.pop("search_order", None)

        await u.message.reply_text(
            order_text(number, order),
            reply_markup=M([
                [B("🔙 پنل مدیریت", callback_data="adm_home")],
            ]),
        )
        return

    number = c.user_data.get(
        "delivery_order"
    )

    if not number:
        return

    order = get_order(c, number)

    if not order or order.get("status") != "delivery":
        c.user_data.pop(
            "delivery_order",
            None
        )

        await u.message.reply_text(
            "⚠️ سفارش انتخاب‌شده دیگر قابل تحویل نیست."
        )

        return

    uid = order["uid"]

    # =====================================================
    # OPEN VPN - STEP 1: FILE
    # =====================================================

    if order.get("step") == "file":

        if not u.message.document:
            await u.message.reply_text(
                f"📎 لطفاً فایل OpenVPN سفارش #{number} "
                "را به صورت فایل (Document) ارسال کنید."
            )
            return

        # ارسال فایل به مشتری
        await u.message.copy(uid)

        # ارسال اطلاعات تکمیلی
        await c.bot.send_message(
            uid,
            "✔️ پروفایل سرور (برای همه سرویس‌ها)\n\n"
            "✔️ سایت کاربران جهت نمایش میزان\n"
            "اعتبار (بدون VPN)\n\n"
            "🌐 https://promiec.com/users/\n\n"
            "⚠️ لینک بالا را بدون VPN باز کنید."
        )

        # مرحله بعد
        order["step"] = "login"

        await u.message.reply_text(
            f"✅ فایل سفارش #{number} ارسال شد.\n\n"
            "👤 حالا یوزرنیم و پسورد همین سفارش "
            "را در یک پیام متنی بفرستید."
        )

        return

    # =====================================================
    # OPEN VPN - STEP 2: USERNAME / PASSWORD
    # =====================================================

    if order.get("step") == "login":

        if not u.message.text:
            await u.message.reply_text(
                f"📝 لطفاً یوزرنیم و پسورد سفارش "
                f"#{number} را به صورت متن ارسال کنید."
            )
            return

        await c.bot.send_message(
            uid,
            "🔐 اطلاعات ورود OpenVPN:\n\n"
            + u.message.text
        )

        order["status"] = "completed"
        order["completed_at"] = datetime.datetime.now().isoformat(timespec="seconds")
        order["step"] = "done"

        c.user_data.pop(
            "delivery_order",
            None
        )

        await u.message.reply_text(
            f"✅ سفارش #{number} تکمیل شد. 🎉"
        )

        # بازگشت خودکار مشتری به منوی اصلی
        await c.bot.send_message(
            uid,
            f"✅ سفارش #{number} با موفقیت تکمیل شد. 🎉\n\n"
            "🛒 برای خرید مجدد، سرویس موردنظر را انتخاب کنید:",
            reply_markup=home_markup(),
        )

        return

    # =====================================================
    # NPV
    # =====================================================

    if order.get("step") == "npv":

        if not u.message.text:
            await u.message.reply_text(
                f"📝 لطفاً ساب‌لینک سفارش #{number} "
                "را به صورت متن ارسال کنید."
            )
            return

        await c.bot.send_message(
            uid,
            "🎉 تبریک! اشتراک شما با موفقیت ساخته شد ❤️\n\n"
            "🔗 لینک اشتراک شما:\n\n"
            + u.message.text
        )

        order["status"] = "completed"
        order["completed_at"] = datetime.datetime.now().isoformat(timespec="seconds")
        order["step"] = "done"

        c.user_data.pop(
            "delivery_order",
            None
        )

        await u.message.reply_text(
            f"✅ سفارش #{number} تکمیل شد. 🎉"
        )

        # بازگشت خودکار مشتری به منوی اصلی
        await c.bot.send_message(
            uid,
            f"✅ سفارش #{number} با موفقیت تکمیل شد. 🎉\n\n"
            "🛒 برای خرید مجدد، سرویس موردنظر را انتخاب کنید:",
            reply_markup=home_markup(),
        )

        return


# =========================================================
# ADMIN COMMAND
# =========================================================

async def admin_command(u, c):
    if u.effective_user.id != ADMIN:
        return

    await u.message.reply_text(
        "🛠️ پنل مدیریت OpenVppn\n\n"
        "مدیریت سفارش‌ها و فروشگاه:",
        reply_markup=admin_home_markup(),
    )


# =========================================================
# APPLICATION
# =========================================================

def main():

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    db_init()
    app.bot_data["orders"] = db_load_orders()

    # -------------------------
    # Commands
    # -------------------------

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "admin",
            admin_command
        )
    )

    # -------------------------
    # Admin approve / reject
    # -------------------------

    app.add_handler(
        CallbackQueryHandler(
            admin_action,
            pattern=r"^(ok|no)"
        )
    )

    # -------------------------
    # Order details
    # -------------------------

    app.add_handler(
        CallbackQueryHandler(
            order_detail,
            pattern=r"^ord_"
        )
    )

    # -------------------------
    # Delivery selection
    # -------------------------

    app.add_handler(
        CallbackQueryHandler(
            select_delivery_order,
            pattern=r"^deliver_"
        )
    )

    # -------------------------
    # Cancel delivery
    # -------------------------

    app.add_handler(
        CallbackQueryHandler(
            cancel_delivery,
            pattern=r"^cancel_delivery$"
        )
    )

    # -------------------------
    # Admin menu
    # -------------------------

    app.add_handler(
        CallbackQueryHandler(
            admin_menu,
            pattern=r"^adm_"
        )
    )

    # -------------------------
    # General buttons
    # -------------------------

    app.add_handler(
        CallbackQueryHandler(btn)
    )

    # -------------------------
    # Customer receipt
    # -------------------------

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            receipt
        )
    )

    # -------------------------
    # Admin delivery
    # -------------------------

    app.add_handler(
        MessageHandler(
            filters.Document.ALL | filters.TEXT,
            delivery
        )
    )

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
