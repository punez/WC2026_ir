import os

BOT_TOKEN    = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DATABASE_URL = os.getenv("DATABASE_URL", "YOUR_SUPABASE_URL_HERE")
ADMIN_IDS    = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")]

POINTS = {
    "exact":        10,
    "diff":          7,
    "winner":        5,
    "participated":  2,
}
FINAL_MULTIPLIER = 2
