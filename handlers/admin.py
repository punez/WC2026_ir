from telegram import Update, InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_all_matches, get_match, set_result, add_match, get_all_users
from config import ADMIN_IDS
from utils import flag, fmt_time
import re

ADMIN_RESULT_ID, ADMIN_RESULT_SCORE = range(20, 22)
ADMIN_MATCH_T1, ADMIN_MATCH_T2, ADMIN_MATCH_STAGE, ADMIN_MATCH_TIME, ADMIN_MATCH_CITY = range(30, 35)

def is_admin(uid): return uid in ADMIN_IDS

# ── پنل ادمین ─────────────────────────────────

async def cmd_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔"); return
    await _admin_menu(update.message.reply_text)

async def cb_adminpanel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id): return
    await _admin_menu(query.edit_message_text)

async def _admin_menu(send):
    await send("🛠 <b>Admin Panel</b>", parse_mode="HTML", reply_markup=Markup([
        [Btn("📋 لیست بازی‌ها", callback_data="admin_list")],
        [Btn("✅ ثبت نتیجه", callback_data="admin_result")],
        [Btn("➕ بازی جدید (حذفی)", callback_data="admin_addmatch")],
        [Btn("📢 پیام همگانی", callback_data="admin_broadcast")],
    ]))

# ── لیست بازی‌ها ──────────────────────────────

async def cb_admin_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id): return

    matches = await get_all_matches()
    if not matches:
        await query.edit_message_text("هنوز بازی‌ای نیست!"); return

    # گروه‌بندی بر اساس stage
    from wc_data import STAGE_LABEL
    stages_seen = {}
    for m in matches:
        stages_seen.setdefault(m["stage"], []).append(m)

    txt = "📋 <b>همه بازی‌ها:</b>\n\n"
    for stage, ms in stages_seen.items():
        lbl = STAGE_LABEL.get(stage, {}).get("fa", stage)
        txt += f"<b>── {lbl} ──</b>\n"
        for m in ms:
            status = "✅" if m["is_finished"] else ("🔒" if m["is_locked"] else "🟢")
            result = f" ({m['result1']}-{m['result2']})" if m["is_finished"] else ""
            txt += f"#{m['id']} {flag(m['team1'])}{m['team1']} vs {m['team2']}{flag(m['team2'])}{result} {status}\n"
        txt += "\n"

    # اگه طولانی بود برش بزن
    if len(txt) > 4000:
        txt = txt[:3900] + "\n...(ادامه)"

    await query.edit_message_text(txt, parse_mode="HTML", reply_markup=Markup([
        [Btn("🔙 برگشت", callback_data="adminpanel")]]))

# ── ثبت نتیجه (conversation) ──────────────────

async def cb_admin_result_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id): return ConversationHandler.END

    matches = await get_all_matches()
    unfinished = [m for m in matches if not m["is_finished"]]
    if not unfinished:
        await query.edit_message_text("همه بازی‌ها تموم شدن!"); return ConversationHandler.END

    txt = "شماره بازی رو بنویس:\n\n"
    for m in unfinished:
        txt += f"<b>#{m['id']}</b> {m['team1']} vs {m['team2']} | {fmt_time(m['match_time'],'fa')}\n"

    await query.edit_message_text(txt, parse_mode="HTML")
    return ADMIN_RESULT_ID

async def admin_result_id(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        mid = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("عدد بنویس!"); return ADMIN_RESULT_ID

    m = await get_match(mid)
    if not m:
        await update.message.reply_text(f"بازی #{mid} پیدا نشد!"); return ADMIN_RESULT_ID
    if m["is_finished"]:
        await update.message.reply_text("این بازی قبلاً نتیجه داره!"); return ADMIN_RESULT_ID

    ctx.user_data["result_mid"] = mid
    await update.message.reply_text(
        f"بازی: <b>{flag(m['team1'])}{m['team1']}  vs  {m['team2']}{flag(m['team2'])}</b>\n\n"
        f"نتیجه رو بنویس (مثلاً <code>2-1</code>):",
        parse_mode="HTML"
    )
    return ADMIN_RESULT_SCORE

async def admin_result_score(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from utils import parse_score
    score = parse_score(update.message.text)
    if not score:
        await update.message.reply_text("فرمت اشتباه! مثلاً: <code>2-1</code>", parse_mode="HTML")
        return ADMIN_RESULT_SCORE

    r1, r2 = score
    mid = ctx.user_data["result_mid"]
    m = await get_match(mid)
    count = await set_result(mid, r1, r2)

    await update.message.reply_text(
        f"✅ <b>نتیجه ثبت شد!</b>\n\n"
        f"{flag(m['team1'])}{m['team1']}  <b>{r1} – {r2}</b>  {m['team2']}{flag(m['team2'])}\n\n"
        f"🎯 امتیاز <b>{count}</b> نفر حساب شد!",
        parse_mode="HTML",
        reply_markup=Markup([
            [Btn("✅ نتیجه دیگه", callback_data="admin_result"),
             Btn("🛠 پنل", callback_data="adminpanel")]
        ])
    )
    return ConversationHandler.END

# ── بازی جدید حذفی (conversation) ─────────────

async def cb_admin_addmatch_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id): return ConversationHandler.END
    await query.edit_message_text(
        "نام تیم اول رو بنویس:\n(دقیقاً مثل لیست — مثلاً: <code>Iran</code>)\n\n/cancel لغو",
        parse_mode="HTML"
    )
    return ADMIN_MATCH_T1

async def admin_match_t1(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["m_t1"] = update.message.text.strip()
    await update.message.reply_text("نام تیم دوم:")
    return ADMIN_MATCH_T2

async def admin_match_t2(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["m_t2"] = update.message.text.strip()
    await update.message.reply_text(
        "مرحله رو بنویس:\n<code>r32</code> | <code>r16</code> | <code>qf</code> | <code>sf</code> | <code>final</code> | <code>third</code>",
        parse_mode="HTML"
    )
    return ADMIN_MATCH_STAGE

async def admin_match_stage(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    stage = update.message.text.strip().lower()
    valid = ["r32","r16","qf","sf","final","third"]
    if stage not in valid:
        await update.message.reply_text(f"باید یکی از اینا باشه: {', '.join(valid)}")
        return ADMIN_MATCH_STAGE
    ctx.user_data["m_stage"] = stage
    await update.message.reply_text(
        "زمان بازی (UTC):\nفرمت: <code>2026-07-01 20:00</code>",
        parse_mode="HTML"
    )
    return ADMIN_MATCH_TIME

async def admin_match_time(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        from datetime import datetime
        datetime.strptime(update.message.text.strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        await update.message.reply_text("فرمت اشتباه! مثلاً: <code>2026-07-01 20:00</code>", parse_mode="HTML")
        return ADMIN_MATCH_TIME
    ctx.user_data["m_time"] = update.message.text.strip() + ":00"
    await update.message.reply_text("شهر (یا Enter بزن برای خالی):")
    return ADMIN_MATCH_CITY

async def admin_match_city(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    t1    = ctx.user_data["m_t1"]
    t2    = ctx.user_data["m_t2"]
    stage = ctx.user_data["m_stage"]
    mtime = ctx.user_data["m_time"]
    is_final = 1 if stage == "final" else 0

    mid = await add_match(stage, t1, t2, mtime, city, is_final)
    await update.message.reply_text(
        f"✅ بازی اضافه شد!\n\n"
        f"<b>#{mid} {flag(t1)}{t1}  vs  {t2}{flag(t2)}</b>\n"
        f"📍 {city} | {mtime}",
        parse_mode="HTML",
        reply_markup=Markup([
            [Btn("➕ بازی دیگه", callback_data="admin_addmatch"),
             Btn("🛠 پنل", callback_data="adminpanel")]
        ])
    )
    return ConversationHandler.END

# ── پیام همگانی ───────────────────────────────

async def cb_admin_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id): return
    await query.edit_message_text(
        "متن پیام همگانی رو بنویس:\n(/sendall متن)",
    )

async def cmd_sendall(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not ctx.args:
        await update.message.reply_text("متن رو بنویس: /sendall متن پیام"); return

    msg = " ".join(ctx.args)
    users = await get_all_users()
    ok = 0
    for u in users:
        try:
            await ctx.bot.send_message(u["user_id"], f"📢 {msg}")
            ok += 1
        except Exception:
            pass
    await update.message.reply_text(f"✅ پیام به {ok} نفر ارسال شد.")

async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ لغو شد.")
    return ConversationHandler.END
