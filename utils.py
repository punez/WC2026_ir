import re
from datetime import datetime, timezone
from wc_data import TEAM_FLAG, TEAM_FA

MONTHS_FA = ["","ژانویه","فوریه","مارس","آوریل","مه","ژوئن",
             "ژوئیه","اوت","سپتامبر","اکتبر","نوامبر","دسامبر"]

def flag(team: str) -> str:
    return TEAM_FLAG.get(team, "🏳️")

def tname(team: str, lang: str) -> str:
    return TEAM_FA.get(team, team) if lang == "fa" else team

def fmt_time(dt_str: str, lang: str) -> str:
    try:
        dt = datetime.strptime(str(dt_str)[:16], "%Y-%m-%d %H:%M")
    except Exception:
        return str(dt_str)
    if lang == "fa":
        return f"{dt.day} {MONTHS_FA[dt.month]}، {dt.strftime('%H:%M')} UTC"
    return dt.strftime("%b %d, %H:%M UTC")

def make_display_name(user) -> str:
    name = (user.full_name or user.first_name or "User").strip()
    return f"{name} #{user.id}"

def parse_score(text: str):
    m = re.match(r"^(\d{1,2})\s*[-–]\s*(\d{1,2})$", text.strip())
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    return (a, b) if a <= 20 and b <= 20 else None

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]
