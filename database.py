"""
دیتابیس — SQLite با aiosqlite
برای Railway: فایل رو روی /data/wc.db ذخیره می‌کنه (persistent volume)
"""
import aiosqlite
import os
from config import POINTS, FINAL_MULTIPLIER

DB_PATH = os.getenv("DB_PATH", "/data/wc.db")
# اگه /data وجود نداشت (local test) بذار کنار bot.py
if not os.path.exists("/data"):
    DB_PATH = "wc.db"

async def get_db():
    return await aiosqlite.connect(DB_PATH)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id      INTEGER PRIMARY KEY,
            display_name TEXT NOT NULL,
            lang         TEXT DEFAULT 'fa',
            joined_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS matches (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            grp         TEXT,
            stage       TEXT NOT NULL DEFAULT 'group',
            team1       TEXT NOT NULL,
            team2       TEXT NOT NULL,
            match_time  TEXT NOT NULL,
            city        TEXT,
            result1     INTEGER DEFAULT NULL,
            result2     INTEGER DEFAULT NULL,
            is_locked   INTEGER DEFAULT 0,
            is_finished INTEGER DEFAULT 0,
            is_final    INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            match_id   INTEGER NOT NULL,
            pred1      INTEGER NOT NULL,
            pred2      INTEGER NOT NULL,
            points     INTEGER DEFAULT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, match_id),
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(match_id) REFERENCES matches(id)
        );

        CREATE INDEX IF NOT EXISTS idx_pred_user ON predictions(user_id);
        CREATE INDEX IF NOT EXISTS idx_match_stage ON matches(stage);
        CREATE INDEX IF NOT EXISTS idx_match_locked ON matches(is_locked);
        """)
        await db.commit()

# ── USERS ─────────────────────────────────────

async def upsert_user(user_id: int, display_name: str, lang: str = "fa"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users(user_id, display_name, lang) VALUES(?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET display_name=excluded.display_name
        """, (user_id, display_name, lang))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return await cur.fetchone()

async def set_lang(user_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
        await db.commit()

# ── MATCHES ───────────────────────────────────

async def bulk_insert_group_matches(matches: list):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT COUNT(*) as c FROM matches WHERE stage='group'")
        row = await cur.fetchone()
        if row["c"] > 0:
            return  # قبلاً درج شده
        await db.executemany("""
            INSERT INTO matches(grp, stage, team1, team2, match_time, city)
            VALUES(?,?,?,?,?,?)
        """, [(m[0],"group",m[1],m[2],m[3],m[4]) for m in matches])
        await db.commit()

async def add_match(stage: str, team1: str, team2: str,
                    match_time: str, city: str = "", is_final: int = 0) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO matches(stage,team1,team2,match_time,city,is_final)
            VALUES(?,?,?,?,?,?)
        """, (stage, team1, team2, match_time, city, is_final))
        await db.commit()
        return cur.lastrowid

async def get_match(match_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM matches WHERE id=?", (match_id,))
        return await cur.fetchone()

async def get_open_matches_by_stage(stage: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT * FROM matches
            WHERE stage=? AND is_locked=0 AND is_finished=0
            ORDER BY match_time
        """, (stage,))
        return await cur.fetchall()

async def get_all_matches(stage: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if stage:
            cur = await db.execute(
                "SELECT * FROM matches WHERE stage=? ORDER BY match_time", (stage,))
        else:
            cur = await db.execute("SELECT * FROM matches ORDER BY match_time")
        return await cur.fetchall()

async def lock_matches_before(cutoff_time: str):
    """قفل کردن همه بازی‌هایی که زمانشون گذشته"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE matches SET is_locked=1
            WHERE match_time <= ? AND is_locked=0
        """, (cutoff_time,))
        await db.commit()

async def set_result(match_id: int, r1: int, r2: int) -> int:
    """ثبت نتیجه و محاسبه امتیاز — برمیگردونه تعداد کسایی که امتیاز گرفتن"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        m = await (await db.execute("SELECT * FROM matches WHERE id=?", (match_id,))).fetchone()
        if not m or m["is_finished"]:
            return 0

        await db.execute("""
            UPDATE matches SET result1=?, result2=?, is_locked=1, is_finished=1
            WHERE id=?
        """, (r1, r2, match_id))

        preds = await (await db.execute("""
            SELECT * FROM predictions WHERE match_id=? AND points IS NULL
        """, (match_id,))).fetchall()

        count = 0
        for p in preds:
            pts = _calc(p["pred1"], p["pred2"], r1, r2, bool(m["is_final"]))
            await db.execute(
                "UPDATE predictions SET points=? WHERE id=?", (pts, p["id"]))
            count += 1

        await db.commit()
        return count

# ── PREDICTIONS ───────────────────────────────

async def save_prediction(user_id: int, match_id: int, p1: int, p2: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        m = await (await db.execute(
            "SELECT is_locked FROM matches WHERE id=?", (match_id,))).fetchone()
        if not m or m["is_locked"]:
            return False
        await db.execute("""
            INSERT INTO predictions(user_id, match_id, pred1, pred2)
            VALUES(?,?,?,?)
            ON CONFLICT(user_id, match_id) DO UPDATE
              SET pred1=excluded.pred1, pred2=excluded.pred2,
                  updated_at=CURRENT_TIMESTAMP, points=NULL
        """, (user_id, match_id, p1, p2))
        await db.commit()
        return True

async def get_prediction(user_id: int, match_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT * FROM predictions WHERE user_id=? AND match_id=?
        """, (user_id, match_id))
        return await cur.fetchone()

async def get_user_predictions(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT p.*, m.team1, m.team2, m.stage, m.match_time, m.grp,
                   m.result1, m.result2, m.is_finished, m.is_final, m.city
            FROM predictions p
            JOIN matches m ON m.id=p.match_id
            WHERE p.user_id=?
            ORDER BY m.match_time DESC
        """, (user_id,))
        return await cur.fetchall()

async def get_user_total(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            SELECT COALESCE(SUM(points),0) FROM predictions WHERE user_id=?
        """, (user_id,))
        row = await cur.fetchone()
        return int(row[0])

# ── LEADERBOARD ───────────────────────────────

async def leaderboard(limit: int = 30):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT u.display_name,
                   COALESCE(SUM(p.points), 0) AS total,
                   COUNT(p.id) AS preds,
                   SUM(CASE WHEN p.points >= 12 THEN 1 ELSE 0 END) AS exact_c
            FROM users u
            LEFT JOIN predictions p ON p.user_id=u.user_id
            GROUP BY u.user_id
            ORDER BY total DESC, preds DESC
            LIMIT ?
        """, (limit,))
        return await cur.fetchall()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT user_id FROM users")
        return await cur.fetchall()

# ── HELPER ────────────────────────────────────

def _calc(p1, p2, r1, r2, is_final: bool) -> int:
    pts = POINTS["participated"]
    if p1 == r1 and p2 == r2:
        pts += POINTS["exact"]
    elif (p1 - p2) == (r1 - r2):
        pts += POINTS["diff"]
    elif (p1 > p2 and r1 > r2) or (p1 < p2 and r1 < r2) or (p1 == p2 and r1 == r2):
        pts += POINTS["winner"]
    if is_final:
        pts *= FINAL_MULTIPLIER
    return pts
