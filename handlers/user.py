from telegram import Update, InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup
from telegram.ext import ContextTypes, ConversationHandler
from database import (upsert_user, get_user, set_lang, get_open_matches_by_stage,
                      get_all_matches, get_prediction, save_prediction,
                      get_user_predictions, get_user_total, leaderboard)
from wc_data import STAGE_LABEL
from utils import flag, tname, fmt_time, make_display_name, parse_score, chunks

PREDICT_INPUT = 10   # conversation state

# ── /start ────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    existing = await get_user(u.id)
    lang = existing["lang"] if existing else None

    if not lang:
        # اول انتخاب زبان
        await update.message.reply_text(
            "🌐 Choose your language / زبان خود را انتخاب کنید:",
            reply_markup=Markup([[
                Btn("🇮🇷 فارسی", callback_data="lang_fa"),
                Btn("🇬🇧 English", callback_data="lang_en"),
            ]])
        )
        return

    await upsert_user(u.id, make_display_name(u), lang)
    await _send_main(update.message.reply_text, u, lang)

async def cb_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    u = query.from_user
    await upsert_user(u.id, make_display_name(u), lang)
    await query.edit_message_text(
        "✅ زبان ذخیره شد! / Language saved!" if lang=="fa" else "✅ Language saved!",
    )
    await _send_main(query.message.reply_text, u, lang)

async def _send_main(send_fn, u, lang: str):
    name = u.first_name or "کاربر"
    if lang == "fa":
        text = (f"سلام {name}! 👋\n\n"
                "🏆 <b>بات پیش‌بینی جام جهانی ۲۰۲۶</b>\n\n"
                "نتیجه هر بازی رو قبل از شروعش پیش‌بینی کن و امتیاز بگیر!\n\n"
                "🎯 نتیجه دقیق: <b>+۱۰</b>\n"
                "📐 تفاضل گل: <b>+۷</b>\n"
                "✔️ فقط برنده: <b>+۵</b>\n"
                "🎟 شرکت: <b>+۲</b>\n"
                "🔥 فینال: همه امتیازها × ۲")
    else:
        text = (f"Hello {name}! 👋\n\n"
                "🏆 <b>FIFA World Cup 2026 Prediction Bot</b>\n\n"
                "Predict match scores before kickoff and earn points!\n\n"
                "🎯 Exact score: <b>+10</b>\n"
                "📐 Correct diff: <b>+7</b>\n"
                "✔️ Correct winner: <b>+5</b>\n"
                "🎟 Participate: <b>+2</b>\n"
                "🔥 Final: all points × 2")

    kb = [
        [Btn("⚽ پیش‌بینی بازی‌ها" if lang=="fa" else "⚽ Predict Matches",
             callback_data="show_stages")],
        [Btn("📊 امتیاز من" if lang=="fa" else "📊 My Stats", callback_data="mystats"),
         Btn("🏆 جدول" if lang=="fa" else "🏆 Leaderboard", callback_data="leaderboard")],
        [Btn("🌐 تغییر زبان" if lang=="fa" else "🌐 Change Language", callback_data="changelang")],
    ]
    await send_fn(text, parse_mode="HTML", reply_markup=Markup(kb))

# ── انتخاب مرحله ─────────────────────────────────────

async def cb_show_stages(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = await get_user(query.from_user.id)
    if not user:
        await query.answer("اول /start بزن!", show_alert=True); return
    lang = user["lang"]

    kb = []
    for stage_key, label in STAGE_LABEL.items():
        matches = await get_open_matches_by_stage(stage_key)
        if matches:
            kb.append([Btn(f"{label[lang]} ({len(matches)})",
                           callback_data=f"stage_{stage_key}")])

    if not kb:
        txt = "😔 فعلاً بازی باز برای پیش‌بینی نیست." if lang=="fa" else "😔 No open matches right now."
        await query.edit_message_text(txt, reply_markup=Markup([[
            Btn("🔙 برگشت" if lang=="fa" else "🔙 Back", callback_data="main")]]))
        return

    title = "⚽ کدوم مرحله؟" if lang=="fa" else "⚽ Which stage?"
    kb.append([Btn("🔙 برگشت" if lang=="fa" else "🔙 Back", callback_data="main")])
    await query.edit_message_text(title, reply_markup=Markup(kb))

# ── لیست بازی‌های یه مرحله ───────────────────────────

async def cb_stage(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    stage = query.data.split("_",1)[1]
    user = await get_user(query.from_user.id)
    lang = user["lang"] if user else "fa"

    matches = await get_open_matches_by_stage(stage)
    if not matches:
        await query.edit_message_text("بازی باز نیست!", reply_markup=Markup([[
            Btn("🔙", callback_data="show_stages")]]))
        return

    stage_lbl = STAGE_LABEL.get(stage, {}).get(lang, stage)
    txt = f"<b>{stage_lbl}</b>\n\n"
    kb = []

    for m in matches:
        f1, f2 = flag(m["team1"]), flag(m["team2"])
        t1 = tname(m["team1"], lang)
        t2 = tname(m["team2"], lang)
        pred = await get_prediction(query.from_user.id, m["id"])
        pred_txt = f" ✏️{pred['pred1']}-{pred['pred2']}" if pred else ""
        grp = f"[{m['grp']}] " if m["grp"] else ""
        txt += f"{grp}{f1}{t1} vs {t2}{f2} — {fmt_time(m['match_time'],lang)}{pred_txt}\n"
        label = f"{f1}{m['team1']} vs {m['team2']}{f2}{pred_txt}"
        kb.append([Btn(label, callback_data=f"predict_{m['id']}")])

    kb.append([Btn("🔙 برگشت" if lang=="fa" else "🔙 Back", callback_data="show_stages")])
    await query.edit_message_text(txt, parse_mode="HTML", reply_markup=Markup(kb))

# ── شروع پیش‌بینی (Conversation) ─────────────────────

async def cb_predict_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    match_id = int(query.data.split("_")[1])
    user = await get_user(query.from_user.id)
    lang = user["lang"] if user else "fa"

    from database import get_match
    m = await get_match(match_id)
    if not m or m["is_locked"]:
        txt = "⛔ این بازی قفل شده!" if lang=="fa" else "⛔ This match is locked!"
        await query.answer(txt, show_alert=True)
        return ConversationHandler.END

    ctx.user_data["match_id"] = match_id
    ctx.user_data["lang"] = lang
    ctx.user_data["stage"] = m["stage"]

    f1, f2 = flag(m["team1"]), flag(m["team2"])
    t1 = tname(m["team1"], lang)
    t2 = tname(m["team2"], lang)
    pred = await get_prediction(query.from_user.id, match_id)
    existing = ""
    if pred:
        existing = (f"✏️ پیش‌بینی فعلی: <b>{pred['pred1']}-{pred['pred2']}</b>\n\n"
                    if lang=="fa" else
                    f"✏️ Current: <b>{pred['pred1']}-{pred['pred2']}</b>\n\n")

    is_final_txt = (" 🔥 (× ۲)" if lang=="fa" else " 🔥 (× 2)") if m["is_final"] else ""
    if lang == "fa":
        txt = (f"⚽ <b>{f1}{t1}  vs  {t2}{f2}</b>{is_final_txt}\n"
               f"🗓 {fmt_time(m['match_time'], lang)} | {m['city']}\n\n"
               f"{existing}نتیجه‌ات رو بنویس:\n"
               f"مثلاً: <code>2-1</code> یا <code>0-0</code>\n\n"
               f"/cancel برای لغو")
    else:
        txt = (f"⚽ <b>{f1}{t1}  vs  {t2}{f2}</b>{is_final_txt}\n"
               f"🗓 {fmt_time(m['match_time'], lang)} | {m['city']}\n\n"
               f"{existing}Enter your prediction:\n"
               f"e.g. <code>2-1</code> or <code>0-0</code>\n\n"
               f"/cancel to cancel")

    await query.edit_message_text(txt, parse_mode="HTML")
    return PREDICT_INPUT

async def handle_prediction_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = ctx.user_data.get("lang", "fa")
    match_id = ctx.user_data.get("match_id")
    score = parse_score(update.message.text)

    if not score:
        err = "❌ فرمت اشتباه! مثلاً: <code>2-1</code>" if lang=="fa" else "❌ Wrong format! e.g. <code>2-1</code>"
        await update.message.reply_text(err, parse_mode="HTML")
        return PREDICT_INPUT

    p1, p2 = score
    ok = await save_prediction(update.effective_user.id, match_id, p1, p2)
    if not ok:
        txt = "⛔ بازی قفل شد!" if lang=="fa" else "⛔ Match just locked!"
        await update.message.reply_text(txt)
        return ConversationHandler.END

    from database import get_match
    m = await get_match(match_id)
    f1, f2 = flag(m["team1"]), flag(m["team2"])
    t1 = tname(m["team1"], lang)
    t2 = tname(m["team2"], lang)

    if lang == "fa":
        txt = (f"✅ ثبت شد!\n\n"
               f"{f1} <b>{t1}  {p1} – {p2}  {t2}</b> {f2}\n\n"
               f"تا شروع بازی می‌تونی عوض کنی 🔄")
    else:
        txt = (f"✅ Saved!\n\n"
               f"{f1} <b>{t1}  {p1} – {p2}  {t2}</b> {f2}\n\n"
               f"You can change it until kickoff 🔄")

    stage = ctx.user_data.get("stage", "group")
    await update.message.reply_text(txt, parse_mode="HTML", reply_markup=Markup([
        [Btn("⚽ بازی‌های بیشتر" if lang=="fa" else "⚽ More matches",
             callback_data=f"stage_{stage}")],
        [Btn("🏠 منو" if lang=="fa" else "🏠 Menu", callback_data="main")],
    ]))
    return ConversationHandler.END

async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_user.id)
    lang = user["lang"] if user else "fa"
    await update.message.reply_text("❌ لغو شد." if lang=="fa" else "❌ Cancelled.")
    return ConversationHandler.END

# ── آمار شخصی ─────────────────────────────────────────

async def cb_mystats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = await get_user(query.from_user.id)
    if not user:
        await query.answer("اول /start بزن!", show_alert=True); return
    lang = user["lang"]
    preds = await get_user_predictions(query.from_user.id)
    total = await get_user_total(query.from_user.id)

    finished = [p for p in preds if p["is_finished"]]
    exact  = sum(1 for p in finished if p["points"] and p["points"] >= 12)
    diff_c = sum(1 for p in finished if p["points"] and p["points"] in (9, 18))
    win_c  = sum(1 for p in finished if p["points"] and p["points"] in (7, 14))

    if lang == "fa":
        txt = (f"📊 <b>آمار {user['display_name']}</b>\n\n"
               f"⭐ کل امتیاز: <b>{total}</b>\n"
               f"🎯 پیش‌بینی‌ها: {len(preds)}\n"
               f"✅ بازی‌های تموم‌شده: {len(finished)}\n\n"
               f"🏆 نتیجه دقیق: {exact}\n"
               f"📐 تفاضل درست: {diff_c}\n"
               f"✔️ فقط برنده: {win_c}\n\n"
               "<b>آخرین ۵ پیش‌بینی:</b>\n")
    else:
        txt = (f"📊 <b>Stats: {user['display_name']}</b>\n\n"
               f"⭐ Total points: <b>{total}</b>\n"
               f"🎯 Predictions: {len(preds)}\n"
               f"✅ Finished: {len(finished)}\n\n"
               f"🏆 Exact: {exact}\n"
               f"📐 Correct diff: {diff_c}\n"
               f"✔️ Correct winner: {win_c}\n\n"
               "<b>Last 5 predictions:</b>\n")

    for p in preds[:5]:
        f1, f2 = flag(p["team1"]), flag(p["team2"])
        if p["is_finished"]:
            pts_txt = f"+{p['points']}" if p["points"] else "0"
            status = f"نتیجه: {p['result1']}-{p['result2']} | {pts_txt}pt" if lang=="en" else \
                     f"نتیجه: {p['result1']}-{p['result2']} | {pts_txt} امتیاز"
        else:
            status = "⏳"
        txt += f"\n{f1}{p['team1']} vs {p['team2']}{f2}: <b>{p['pred1']}-{p['pred2']}</b> {status}"

    await query.edit_message_text(txt, parse_mode="HTML", reply_markup=Markup([
        [Btn("🔙 برگشت" if lang=="fa" else "🔙 Back", callback_data="main")]]))

# ── جدول ──────────────────────────────────────────────

async def cb_leaderboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = await get_user(query.from_user.id)
    lang = user["lang"] if user else "fa"
    rows = await leaderboard(30)

    medals = ["🥇","🥈","🥉"]
    title = "🏆 جدول امتیازات" if lang=="fa" else "🏆 Leaderboard"
    txt = f"<b>{title}</b>\n\n"
    for i, r in enumerate(rows):
        m = medals[i] if i < 3 else f"{i+1}."
        pts_lbl = "امتیاز" if lang=="fa" else "pts"
        txt += f"{m} <b>{r['display_name']}</b> — {r['total']} {pts_lbl} ({r['preds']} 🎯)\n"

    if not rows:
        txt += "هنوز کسی امتیاز نگرفته!" if lang=="fa" else "No scores yet!"

    await query.edit_message_text(txt, parse_mode="HTML", reply_markup=Markup([
        [Btn("🔙 برگشت" if lang=="fa" else "🔙 Back", callback_data="main")]]))

# ── برگشت به منو ──────────────────────────────────────

async def cb_main(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = await get_user(query.from_user.id)
    lang = user["lang"] if user else "fa"
    await _send_main(query.edit_message_text, query.from_user, lang)

async def cb_changelang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🌐 Choose language / انتخاب زبان:",
        reply_markup=Markup([[
            Btn("🇮🇷 فارسی", callback_data="lang_fa"),
            Btn("🇬🇧 English", callback_data="lang_en"),
        ]])
    )
