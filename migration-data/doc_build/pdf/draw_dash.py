"""대시보드 PC 화면 두 장(맨 위 줄·고정 요약)에 번호 상자. 번호는 종이 위 약 5mm(badge.py)."""
import json
from PIL import Image, ImageDraw, ImageFont
from badge import badge_px, printed
FONT = "../fonts/pt/package/dist/public/static/Pretendard-Bold.otf"
RED = (235, 51, 42); BG = (247, 249, 252); S = 2; T = 8


def draw(src, info, items, box, out, w_mm=170, place=None):
    x0, y0, x1, y1 = box
    w_mm = printed(out.split("/")[-1][:-4], w_mm)
    r, fs, M = badge_px(w_mm, x1 - x0, S)
    im = Image.open(src).convert("RGB").crop((x0 * S, y0 * S, x1 * S, y1 * S))
    can = Image.new("RGB", (im.width + M * S, im.height + 2 * T * S), BG); can.paste(im, (M * S, T * S))
    g = ImageDraw.Draw(can); f = ImageFont.truetype(FONT, fs)
    for n, (x, y, w, h) in enumerate(items, 1):
        x -= x0; y = y - y0 + T
        X0, Y0, X1, Y1 = (x - 4 + M) * S, (y - 4) * S, (min(x + w + 4, x1 - x0 - 2) + M) * S, (y + h + 4) * S
        g.rounded_rectangle((X0, Y0, X1, Y1), radius=6 * S, outline=RED, width=round(2.6 * S))
        bx, by = max(r + S, X0 - r - 2 * S), Y0 + r
        if place and n in place:   # 왼쪽에 자리가 없으면 상자 안 빈 곳(제목 오른쪽 등)
            bx, by = (place[n][0] - x0 + M) * S, (place[n][1] - y0 + T) * S
        g.ellipse((bx - r, by - r, bx + r, by + r), fill=RED, outline=(255, 255, 255), width=2 * S)
        tw = g.textlength(str(n), font=f); g.text((bx - tw / 2, by - f.size * 0.6), str(n), font=f, fill=(255, 255, 255))
    can.save(out); print(out, can.size, "r", r)


B = json.load(open("v12/topbar.json"))
draw("v12/topbar_full.png", B, [B["tabs"], B["btn"]], (262, 94, 1274, 222), "annot/pc_dash_bar.png")
D = json.load(open("v12/dash.json"))
ban = list(D["banner"]); ban[0], ban[2] = 272, 992   # 알림 띠는 화면 폭 전체
rk = D["risk"]
# ③ '지금 위험·조치 필요': 왼쪽은 ② 상자와 붙어 있어 번호를 제목 오른쪽 빈 곳에
draw("v12/dash_full.png", D, [ban, D["today"], rk, D["health"]], (262, 226, 1274, 1124), "annot/pc_dash_top.png",
     place={3: (rk[0] + 200, rk[1] + 12)})
