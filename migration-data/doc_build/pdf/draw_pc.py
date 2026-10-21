"""PC 이력 화면 두 장(pc_records, pc_record_edit): 상자는 요소 둘레, 번호는 상자 왼쪽 바깥(왼쪽 여백 띠). 종이 위 약 5mm."""
import os
from PIL import Image, ImageDraw, ImageFont
from badge import badge_px, BADGE_MM, printed
from annotate import A, FONT, HERE
RED = (235, 51, 42); BG = (247, 249, 252); T = 6
W_MM = {"pc_records": 170, "pc_record_edit": 150}
for name, w_mm in W_MM.items():
    w_mm = printed(name, w_mm)
    dpr, marks, crop = A[name]
    S = dpr
    cx0, cy0, cx1, cy1 = crop
    r, fs, M = badge_px(w_mm, cx1 - cx0, S)
    im = Image.open(f"{HERE}/img/{name}.png").convert("RGB").crop(tuple(round(v * S) for v in crop))
    pad, top = round(M * S), round(T * S)
    can = Image.new("RGB", (im.width + pad, im.height + 2 * top), BG); can.paste(im, (pad, top))
    ow = 2   # 흰 테두리(px)
    r = round(BADGE_MM / (w_mm / can.width) / 2 + ow)   # 완성 그림 폭으로 다시 맞춤(반올림 오차 줄이기)
    g = ImageDraw.Draw(can); f = ImageFont.truetype(FONT, round(r * 1.15))
    for n, x, y, w, h in marks:
        X0, Y0 = round((x - cx0) * S) + pad, round((y - cy0) * S) + top
        X1, Y1 = X0 + round(w * S), Y0 + round(h * S)
        g.rounded_rectangle((X0, Y0, min(X1, can.width - 2), Y1), radius=round(6 * S), outline=RED, width=round(2.5 * S))
        bx, by = max(r + 2, X0 - r - round(2 * S)), max(r + 2, Y0 + r)
        g.ellipse((bx - r, by - r, bx + r, by + r), fill=RED, outline=(255, 255, 255), width=ow)
        t = str(n); tw = g.textlength(t, font=f); g.text((bx - tw / 2, by - f.size * 0.6), t, font=f, fill=(255, 255, 255))
    can.save(f"{HERE}/annot/{name}.png"); print(name, can.size, r)
