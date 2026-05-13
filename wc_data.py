# ══════════════════════════════════════════════
#  جام جهانی ۲۰۲۶ — همه بازی‌های مرحله گروهی
#  زمان‌ها UTC هستن
# ══════════════════════════════════════════════

TEAM_FLAG = {
    "Mexico":"🇲🇽","South Africa":"🇿🇦","South Korea":"🇰🇷","Czechia":"🇨🇿",
    "Canada":"🇨🇦","Bosnia and Herzegovina":"🇧🇦","Qatar":"🇶🇦","Switzerland":"🇨🇭",
    "Brazil":"🇧🇷","Morocco":"🇲🇦","Haiti":"🇭🇹","Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "United States":"🇺🇸","Paraguay":"🇵🇾","Australia":"🇦🇺","Turkiye":"🇹🇷",
    "Germany":"🇩🇪","Curacao":"🇨🇼","Ivory Coast":"🇨🇮","Ecuador":"🇪🇨",
    "Netherlands":"🇳🇱","Japan":"🇯🇵","Sweden":"🇸🇪","Tunisia":"🇹🇳",
    "Belgium":"🇧🇪","Egypt":"🇪🇬","Iran":"🇮🇷","New Zealand":"🇳🇿",
    "Spain":"🇪🇸","Cape Verde":"🇨🇻","Saudi Arabia":"🇸🇦","Uruguay":"🇺🇾",
    "France":"🇫🇷","Senegal":"🇸🇳","Iraq":"🇮🇶","Norway":"🇳🇴",
    "Argentina":"🇦🇷","Algeria":"🇩🇿","Austria":"🇦🇹","Jordan":"🇯🇴",
    "Portugal":"🇵🇹","DR Congo":"🇨🇩","Uzbekistan":"🇺🇿","Colombia":"🇨🇴",
    "England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","Croatia":"🇭🇷","Ghana":"🇬🇭","Panama":"🇵🇦",
}

TEAM_FA = {
    "Mexico":"مکزیک","South Africa":"آفریقای جنوبی","South Korea":"کره جنوبی",
    "Czechia":"چک","Canada":"کانادا","Bosnia and Herzegovina":"بوسنی",
    "Qatar":"قطر","Switzerland":"سوئیس","Brazil":"برزیل","Morocco":"مراکش",
    "Haiti":"هائیتی","Scotland":"اسکاتلند","United States":"آمریکا",
    "Paraguay":"پاراگوئه","Australia":"استرالیا","Turkiye":"ترکیه",
    "Germany":"آلمان","Curacao":"کوراسائو","Ivory Coast":"ساحل عاج",
    "Ecuador":"اکوادور","Netherlands":"هلند","Japan":"ژاپن",
    "Sweden":"سوئد","Tunisia":"تونس","Belgium":"بلژیک","Egypt":"مصر",
    "Iran":"ایران","New Zealand":"نیوزیلند","Spain":"اسپانیا",
    "Cape Verde":"کیپ‌ورد","Saudi Arabia":"عربستان","Uruguay":"اروگوئه",
    "France":"فرانسه","Senegal":"سنگال","Iraq":"عراق","Norway":"نروژ",
    "Argentina":"آرژانتین","Algeria":"الجزایر","Austria":"اتریش",
    "Jordan":"اردن","Portugal":"پرتغال","DR Congo":"کنگو",
    "Uzbekistan":"ازبکستان","Colombia":"کلمبیا","England":"انگلیس",
    "Croatia":"کرواسی","Ghana":"غنا","Panama":"پاناما",
}

# (group, team1, team2, utc_time, city)
GROUP_MATCHES = [
    # Group A
    ("A","Mexico","South Africa","2026-06-11 20:00","Mexico City"),
    ("A","South Korea","Czechia","2026-06-12 01:00","Guadalajara"),
    ("A","Mexico","Czechia","2026-06-16 00:00","Mexico City"),
    ("A","South Africa","South Korea","2026-06-16 23:00","Guadalajara"),
    ("A","Mexico","South Korea","2026-06-20 23:00","Mexico City"),
    ("A","Czechia","South Africa","2026-06-20 23:00","Guadalajara"),
    # Group B
    ("B","Canada","Bosnia and Herzegovina","2026-06-12 19:00","Toronto"),
    ("B","Qatar","Switzerland","2026-06-13 19:00","San Francisco"),
    ("B","Canada","Switzerland","2026-06-17 01:00","Toronto"),
    ("B","Qatar","Bosnia and Herzegovina","2026-06-17 22:00","Vancouver"),
    ("B","Canada","Qatar","2026-06-21 22:00","Toronto"),
    ("B","Switzerland","Bosnia and Herzegovina","2026-06-21 22:00","San Francisco"),
    # Group C
    ("C","Brazil","Morocco","2026-06-13 22:00","New York"),
    ("C","Haiti","Scotland","2026-06-14 01:00","Boston"),
    ("C","Brazil","Scotland","2026-06-18 01:00","San Francisco"),
    ("C","Haiti","Morocco","2026-06-18 22:00","Philadelphia"),
    ("C","Brazil","Haiti","2026-06-22 22:00","New York"),
    ("C","Scotland","Morocco","2026-06-22 22:00","Boston"),
    # Group D
    ("D","United States","Paraguay","2026-06-12 23:00","Los Angeles"),
    ("D","Australia","Turkiye","2026-06-14 04:00","Vancouver"),
    ("D","United States","Turkiye","2026-06-18 23:00","Los Angeles"),
    ("D","Australia","Paraguay","2026-06-19 22:00","Seattle"),
    ("D","United States","Australia","2026-06-23 22:00","Los Angeles"),
    ("D","Turkiye","Paraguay","2026-06-23 22:00","Seattle"),
    # Group E
    ("E","Germany","Curacao","2026-06-14 18:00","Houston"),
    ("E","Ivory Coast","Ecuador","2026-06-15 00:00","Philadelphia"),
    ("E","Germany","Ecuador","2026-06-19 01:00","Dallas"),
    ("E","Ivory Coast","Curacao","2026-06-19 22:00","Miami"),
    ("E","Germany","Ivory Coast","2026-06-23 23:00","Houston"),
    ("E","Ecuador","Curacao","2026-06-23 23:00","Dallas"),
    # Group F
    ("F","Netherlands","Japan","2026-06-14 21:00","Dallas"),
    ("F","Sweden","Tunisia","2026-06-15 03:00","Monterrey"),
    ("F","Netherlands","Tunisia","2026-06-19 23:00","Houston"),
    ("F","Sweden","Japan","2026-06-20 22:00","Dallas"),
    ("F","Netherlands","Sweden","2026-06-24 22:00","Dallas"),
    ("F","Japan","Tunisia","2026-06-24 22:00","Houston"),
    # Group G
    ("G","Belgium","Egypt","2026-06-15 23:00","Seattle"),
    ("G","Iran","New Zealand","2026-06-16 04:00","Los Angeles"),
    ("G","Belgium","New Zealand","2026-06-20 01:00","Seattle"),
    ("G","Iran","Egypt","2026-06-20 22:00","Los Angeles"),
    ("G","Belgium","Iran","2026-06-24 23:00","Seattle"),
    ("G","New Zealand","Egypt","2026-06-24 23:00","Los Angeles"),
    # Group H
    ("H","Spain","Cape Verde","2026-06-15 18:00","Atlanta"),
    ("H","Saudi Arabia","Uruguay","2026-06-15 23:00","Miami"),
    ("H","Spain","Uruguay","2026-06-19 18:00","Atlanta"),
    ("H","Saudi Arabia","Cape Verde","2026-06-20 01:00","Miami"),
    ("H","Spain","Saudi Arabia","2026-06-24 01:00","Atlanta"),
    ("H","Uruguay","Cape Verde","2026-06-24 01:00","Miami"),
    # Group I
    ("I","France","Senegal","2026-06-16 19:00","New York"),
    ("I","Iraq","Norway","2026-06-16 23:00","Boston"),
    ("I","France","Norway","2026-06-21 01:00","New York"),
    ("I","Iraq","Senegal","2026-06-21 22:00","Boston"),
    ("I","France","Iraq","2026-06-25 22:00","New York"),
    ("I","Norway","Senegal","2026-06-25 22:00","Philadelphia"),
    # Group J
    ("J","Argentina","Algeria","2026-06-17 01:00","Kansas City"),
    ("J","Austria","Jordan","2026-06-17 04:00","San Francisco"),
    ("J","Argentina","Jordan","2026-06-21 01:00","Kansas City"),
    ("J","Austria","Algeria","2026-06-21 22:00","San Francisco"),
    ("J","Argentina","Austria","2026-06-25 23:00","Kansas City"),
    ("J","Jordan","Algeria","2026-06-25 23:00","San Francisco"),
    # Group K
    ("K","Portugal","DR Congo","2026-06-17 18:00","Houston"),
    ("K","Uzbekistan","Colombia","2026-06-18 01:00","Kansas City"),
    ("K","Portugal","Colombia","2026-06-22 01:00","Houston"),
    ("K","Uzbekistan","DR Congo","2026-06-22 22:00","Kansas City"),
    ("K","Portugal","Uzbekistan","2026-06-26 22:00","Houston"),
    ("K","Colombia","DR Congo","2026-06-26 22:00","Kansas City"),
    # Group L
    ("L","England","Croatia","2026-06-18 23:00","Dallas"),
    ("L","Ghana","Panama","2026-06-19 01:00","Atlanta"),
    ("L","England","Panama","2026-06-22 23:00","Dallas"),
    ("L","Ghana","Croatia","2026-06-23 22:00","Atlanta"),
    ("L","England","Ghana","2026-06-27 22:00","Dallas"),
    ("L","Croatia","Panama","2026-06-27 22:00","Atlanta"),
]

STAGE_LABEL = {
    "group": {"fa":"مرحله گروهی","en":"Group Stage"},
    "r32":   {"fa":"یک‌سی‌ودوم","en":"Round of 32"},
    "r16":   {"fa":"یک‌شانزدهم","en":"Round of 16"},
    "qf":    {"fa":"یک‌چهارم","en":"Quarter-finals"},
    "sf":    {"fa":"نیمه‌نهایی","en":"Semi-finals"},
    "final": {"fa":"فینال","en":"Final"},
    "third": {"fa":"رده‌بندی سوم","en":"Third Place"},
}
