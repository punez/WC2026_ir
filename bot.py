import logging
import asyncio
from datetime import datetime, timezone

from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)

from config import BOT_TOKEN
from database import init_db, bulk_insert_group_matches, lock_matches_before
from wc_data import GROUP_MATCHES
from handlers.user import (
    cmd_start, cb_lang, cb_show_stages, cb_stage,
    cb_predict_start, handle_prediction_input, cmd_cancel,
    cb_mystats, cb_leaderboard, cb_main, cb_changelang,
    PREDICT_INPUT
)
from handlers.admin import (
    cmd_admin, cb_adminpanel, cb_admin_list,
    cb_admin_result_start, admin_result_id, admin_result_score,
    cb_admin_addmatch_start, admin_match_t1, admin_match_t2,
    admin_match_stage, admin_match_time, admin_match_city,
    cb_admin_broadcast, cmd_sendall,
    cmd_cancel as admin_cancel,
    ADMIN_RESULT_ID, ADMIN_RESULT_SCORE,
    ADMIN_MATCH_T1, ADMIN_MATCH_T2, ADMIN_MATCH_STAGE,
    ADMIN_MATCH_TIME, ADMIN_MATCH_CITY
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)

# ── Scheduler: قفل خودکار بازی‌ها ────────────────────

async def auto_lock_job(app):
    """هر ۳۰ ثانیه بازی‌هایی که وقتشون گذشته رو قفل می‌کنه"""
    while True:
        try:
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            await lock_matches_before(now)
        except Exception as e:
            log.error(f"auto_lock error: {e}")
        await asyncio.sleep(30)

# ── Conversation: پیش‌بینی کاربر ─────────────────────

def predict_conv():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_predict_start, pattern=r"^predict_\d+$")],
        states={
            PREDICT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prediction_input)],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
        per_user=True, per_chat=False,
    )

# ── Conversation: ثبت نتیجه ادمین ─────────────────────

def admin_result_conv():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_admin_result_start, pattern="^admin_result$")],
        states={
            ADMIN_RESULT_ID:    [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_result_id)],
            ADMIN_RESULT_SCORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_result_score)],
        },
        fallbacks=[CommandHandler("cancel", admin_cancel)],
    )

# ── Conversation: بازی جدید ادمین ────────────────────

def admin_addmatch_conv():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_admin_addmatch_start, pattern="^admin_addmatch$")],
        states={
            ADMIN_MATCH_T1:    [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_match_t1)],
            ADMIN_MATCH_T2:    [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_match_t2)],
            ADMIN_MATCH_STAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_match_stage)],
            ADMIN_MATCH_TIME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_match_time)],
            ADMIN_MATCH_CITY:  [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_match_city)],
        },
        fallbacks=[CommandHandler("cancel", admin_cancel)],
    )

# ── Main ──────────────────────────────────────────────

async def post_init(app):
    await init_db()
    await bulk_insert_group_matches(GROUP_MATCHES)
    log.info("✅ DB ready, matches loaded")
    asyncio.create_task(auto_lock_job(app))

def main():
    app = (ApplicationBuilder()
           .token(BOT_TOKEN)
           .post_init(post_init)
           .build())

    # Conversations اول
    app.add_handler(predict_conv())
    app.add_handler(admin_result_conv())
    app.add_handler(admin_addmatch_conv())

    # Commands
    app.add_handler(CommandHandler("start",      cmd_start))
    app.add_handler(CommandHandler("admin",      cmd_admin))
    app.add_handler(CommandHandler("sendall",    cmd_sendall))
    app.add_handler(CommandHandler("cancel",     cmd_cancel))

    # Callbacks
    app.add_handler(CallbackQueryHandler(cb_lang,         pattern=r"^lang_"))
    app.add_handler(CallbackQueryHandler(cb_main,         pattern="^main$"))
    app.add_handler(CallbackQueryHandler(cb_changelang,   pattern="^changelang$"))
    app.add_handler(CallbackQueryHandler(cb_show_stages,  pattern="^show_stages$"))
    app.add_handler(CallbackQueryHandler(cb_stage,        pattern=r"^stage_"))
    app.add_handler(CallbackQueryHandler(cb_mystats,      pattern="^mystats$"))
    app.add_handler(CallbackQueryHandler(cb_leaderboard,  pattern="^leaderboard$"))
    app.add_handler(CallbackQueryHandler(cb_adminpanel,   pattern="^adminpanel$"))
    app.add_handler(CallbackQueryHandler(cb_admin_list,   pattern="^admin_list$"))
    app.add_handler(CallbackQueryHandler(cb_admin_broadcast, pattern="^admin_broadcast$"))

    log.info("🚀 Bot starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
