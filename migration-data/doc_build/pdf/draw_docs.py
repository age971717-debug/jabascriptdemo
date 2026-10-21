"""문서 화면(휴대폰) 카드 3장에 번호 상자. 번호는 종이 위 약 5mm(badge.py)."""
from PIL import Image, ImageDraw, ImageFont
from badge import badge_px
FONT = "../fonts/pt/package/dist/public/static/Pretendard-Bold.otf"
RED = (235, 51, 42); BG = (247, 249, 252); S = 3; T = 8
y0, y1 = 70, 506
r, fs, M = badge_px(72, 390, S)
im = Image.open("v12/m_docs_full.png").convert("RGB").crop((0, y0 * S, 390 * S, y1 * S))
can = Image.new("RGB", (im.width + M * S, im.height + 2 * T * S), BG); can.paste(im, (M * S, T * S))
g = ImageDraw.Draw(can); f = ImageFont.truetype(FONT, fs)
for n, (x, y, w, h) in enumerate([(16, 164, 358, 96.1), (16, 272.1, 358, 96.1), (16, 380.2, 358, 113.1)], 1):
    y = y - y0 + T
    X0, Y0, X1, Y1 = (x - 3 + M) * S, (y - 3) * S, (x + w + 3 + M) * S, (y + h + 3) * S
    g.rounded_rectangle((X0, Y0, X1, Y1), radius=6 * S, outline=RED, width=round(2.4 * S))
    bx, by = max(r + S, X0 - r - 2 * S), Y0 + r
    g.ellipse((bx - r, by - r, bx + r, by + r), fill=RED, outline=(255, 255, 255), width=2 * S)
    tw = g.textlength(str(n), font=f); g.text((bx - tw / 2, by - f.size * 0.6), str(n), font=f, fill=(255, 255, 255))
can.save("annot/m_docs.png"); print(can.size, r)
