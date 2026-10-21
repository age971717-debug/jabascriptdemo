"""v12/report_card.png → 리포트 실제 화면 두 조각(①② / ③④), 각 절 제목에 번호 상자."""
import json
from PIL import Image, ImageDraw, ImageFont
FONT = "../fonts/pt/package/dist/public/static/Pretendard-Bold.otf"
RED = (235, 51, 42); BG = (247, 249, 252); S = 2; M = 30
info = json.load(open("v12/report_card.json")); im = Image.open("v12/report_card.png").convert("RGB")
W = im.width // S
can = Image.new("RGB", (im.width + M * S, im.height), BG); can.paste(im, (M * S, 0))
g = ImageDraw.Draw(can); r = 11 * S; f = ImageFont.truetype(FONT, 14 * S)
for n, (t, x, y, w, h) in enumerate(info["hs"], 1):
    w = [160, 182, 262, 160][n - 1]   # 제목 글자 폭만 감싸기
    X0, Y0, X1, Y1 = (x - 6 + M) * S, (y - 5) * S, (x + w + M) * S, (y + h + 5) * S
    g.rounded_rectangle((X0, Y0, X1, Y1), radius=6 * S, outline=RED, width=round(2.4 * S))
    bx, by = X0 - r - 3 * S, (Y0 + Y1) / 2
    g.ellipse((bx - r, by - r, bx + r, by + r), fill=RED, outline=(255, 255, 255), width=2 * S)
    tw = g.textlength(str(n), font=f); g.text((bx - tw / 2, by - f.size * 0.6), str(n), font=f, fill=(255, 255, 255))
cut = round((info["hs"][2][2] - 16) * S)
can.crop((0, 0, can.width, cut)).save("annot/rep_card_a.png")
can.crop((0, cut, can.width, can.height - 52 * S)).save("annot/rep_card_b.png")
print(can.size, cut)
