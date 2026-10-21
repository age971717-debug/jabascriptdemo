"""a2/boxes.json → 번호 상자 그림. 상자는 요소 바깥 4px, 번호 동그라미는 상자 왼쪽 바깥(화면 왼쪽에 여백 띠)."""
import json
from badge import badge_px
from PIL import Image, ImageDraw, ImageFont
FONT = "../fonts/pt/package/dist/public/static/Pretendard-Bold.otf"
RED = (235, 51, 42); BG = (247, 249, 252)
J = json.load(open("a2/boxes.json"))
def draw(name, out, crop=None, only=None, w_mm=72):
    d = J[name]; S = d["dpr"]; im = Image.open(f"a2/{name}.png").convert("RGB")
    cx0, cy0, cw, ch = crop or d.get("clip") or (0, 0, im.width / S, im.height / S)
    im = im.crop(tuple(round(v * S) for v in (cx0, cy0, cx0 + cw, cy0 + ch)))
    r, fs, M = badge_px(w_mm, cw, S)   # 번호 크기: 종이 위 지름 약 5mm(인쇄 폭 w_mm 기준), M = 왼쪽 여백(css px)
    T = 8  # 위·아래 여백(상자가 화면 끝에서 잘리지 않게)
    can = Image.new("RGB", (im.width + M * S, im.height + 2 * T * S), BG); can.paste(im, (M * S, T * S))
    g = ImageDraw.Draw(can); f = ImageFont.truetype(FONT, fs)
    for n, bx in d["boxes"]:
        if not bx or (only and n not in only): continue
        x, y, w, h = bx; x -= cx0; y -= cy0
        if y + h < 0 or y > ch: continue
        if y + h > ch + 5:
            print("  CLIPPED", name, n); h = ch + 5 - y   # 잘린 쪽은 사진 끝 바로 밖에서 닫음
        y += T
        X0, Y0 = (x - 3 + M) * S, (y - 3) * S; X1, Y1 = (x + w + 3 + M) * S, (y + h + 3) * S
        g.rounded_rectangle((X0, Y0, X1, Y1), radius=6 * S, outline=RED, width=round(2.4 * S))
        bx_ = max(r + S, X0 - r - 2 * S); by_ = max(r + S, Y0 + r)
        if n in d.get("below", []):   # 붙어 있는 버튼은 번호를 상자 아래 가운데에
            bx_ = (X0 + X1) / 2; by_ = Y1 + r + 1 * S
        g.ellipse((bx_ - r, by_ - r, bx_ + r, by_ + r), fill=RED, outline=(255, 255, 255), width=2 * S)
        t = str(n); tw = g.textlength(t, font=f); g.text((bx_ - tw / 2, by_ - f.size * 0.6), t, font=f, fill=(255, 255, 255))
    can.save(out); print(out, can.size)
O = "annot/"
draw("board", O + "m_board_simple.png")
dl = J["detail"]; c = dl["clip"]; b5 = dict(dl["boxes"])[5]
draw("detail", O + "m_detail.png", crop=(c[0], c[1], c[2], b5[1] + b5[3] + 12 - c[1]))   # ⑤ 고장 이력 칸 전체가 보이게
draw("report", O + "m_report.png", crop=(0, 78, 390, 720))
rb = dict(J["repair"]["boxes"])
draw("repair", O + "m_repair_a.png", crop=(0, 80, 390, rb[7][1] + rb[7][3] + 45 - 80), only=range(1, 8))
y8 = rb[8][1] - 14
draw("repair", O + "m_repair_b.png", crop=(0, y8, 390, rb[12][1] + rb[12][3] + 14 - y8), only=range(8, 13))
draw("feedback", O + "m_feedback.png")
c = J["pcnav"]["clip"]; b7 = dict(J["pcnav"]["boxes"])[7]
draw("pcnav", O + "nav_pc.png", crop=(c[0], c[1] + 56, c[2], b7[1] + b7[3] + 14 - (c[1] + 56)), w_mm=58)
