"""휴대폰 맨 아래 탭 그림(①~⑤). 번호는 종이 위 BADGE_MM(badge.py), 인쇄 폭 170mm."""
from PIL import Image, ImageDraw, ImageFont
from badge import BADGE_MM, printed
FONT = "../fonts/pt/package/dist/public/static/Pretendard-Bold.otf"
RED = (235, 51, 42)
m = Image.open("rimg/m_board.png").convert("RGB").crop((0, 2340, 1170, 2532))
pad = Image.new("RGB", (1170, 230), (13, 17, 23)); pad.paste(m, (0, 38)); m = pad
red = BADGE_MM / (printed("nav_phone", 170) / m.width); r = round(red / 2 + 3); f = ImageFont.truetype(FONT, round(r * 1.15))
d = ImageDraw.Draw(m)
for n, (x, w) in enumerate([(30, 195), (255, 195), (480, 215), (720, 215), (960, 200)], 1):
    y, h = 50, 170
    d.rounded_rectangle((x, y, x + w, y + h), radius=13, outline=RED, width=5)
    cx, cy = x + 6, y + 6
    cx, cy = max(r + 2, cx), max(r + 2, cy)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RED, outline=(255, 255, 255), width=3)
    t = str(n); tw = d.textlength(t, font=f); d.text((cx - tw / 2, cy - f.size * 0.62), t, font=f, fill=(255, 255, 255))
m.save("annot/nav_phone.png"); print("nav_phone r", r)
