"""가이드용 화면에 번호 표시(빨간 테두리 + 번호 동그라미). 좌표는 CSS px(화면 기준), crop도 CSS px."""
import os
from PIL import Image, ImageDraw, ImageFont

FONT = "/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad/fonts/pt/package/dist/public/static/Pretendard-Bold.otf"
HERE = os.path.dirname(__file__)
RED = (255, 59, 48)

# name: (dpr, [(번호, x, y, w, h)], crop(x0, y0, x1, y1) | None)
A = {
    "m_board": (2, [(1, 14, 143, 288, 104), (2, 27, 292, 205, 46), (3, 262, 298, 100, 40), (4, 36, 443, 150, 60),
                    (5, 240, 90, 136, 36), (6, 316, 630, 60, 60), (7, 2, 703, 386, 55),
                    (8, 238, 12, 40, 42), (9, 283, 10, 48, 46), (10, 334, 10, 50, 46), (11, 10, 12, 45, 40)], None),
    "m_detail": (2, [(1, 17, 180, 176, 48), (2, 198, 180, 176, 48), (3, 14, 245, 362, 170), (4, 14, 430, 362, 210),
                     (5, 14, 645, 362, 110)], None),
    "m_report": (2, [(1, 14, 135, 362, 48), (2, 8, 203, 372, 92), (3, 8, 305, 372, 45), (4, 8, 358, 372, 44),
                     (5, 38, 532, 316, 42), (6, 38, 580, 316, 44), (7, 38, 630, 316, 46), (8, 38, 688, 154, 44),
                     (9, 38, 742, 316, 46)], (0, 50, 390, 800)),
    "m_report_body": (2, [(1, 14, 827, 362, 258), (2, 14, 1112, 362, 465), (3, 14, 1590, 362, 660), (4, 14, 2298, 362, 205)],
                      (0, 815, 390, 2515)),
    "m_repair_a": (2, [(1, 28, 190, 180, 40), (2, 30, 312, 332, 62), (3, 30, 384, 332, 62), (4, 30, 456, 332, 62),
                       (5, 30, 528, 332, 62), (6, 30, 600, 276, 100), (7, 308, 618, 50, 50)], (0, 90, 390, 705)),
    "m_repair_b": (2, [(8, 30, 712, 332, 190), (9, 45, 905, 305, 170), (10, 30, 1105, 332, 62), (11, 30, 1178, 332, 85),
                       (12, 30, 1280, 332, 46)], (0, 700, 390, 1335)),
    "pc_board": (1.25, [(1, 0, 48, 198, 330), (2, 210, 106, 465, 32), (3, 210, 152, 215, 30), (4, 220, 202, 455, 40),
                        (5, 226, 404, 114, 50), (6, 676, 55, 312, 565), (7, 718, 8, 70, 30), (8, 795, 8, 92, 30),
                        (9, 890, 6, 98, 32), (10, 210, 4, 38, 38)], (0, 0, 1000, 640)),
    "pc_records": (1.25, [(1, 214, 112, 462, 42), (2, 220, 234, 758, 32), (3, 212, 330, 778, 40)], (200, 50, 1000, 560)),
    "pc_record_edit": (1.25, [(1, 250, 100, 250, 112), (2, 502, 100, 248, 112), (3, 250, 225, 500, 170), (4, 250, 405, 500, 58),
                              (5, 250, 470, 500, 38), (6, 250, 512, 500, 68), (7, 642, 60, 82, 28)], (235, 45, 765, 590)),
    "pc_dash": (1.25, [(1, 213, 123, 124, 40), (2, 838, 125, 150, 36), (3, 212, 176, 778, 72), (4, 212, 260, 318, 255),
                       (5, 538, 258, 452, 355), (6, 212, 624, 778, 248)], (200, 50, 1000, 880)),
    "pc_picker": (1.25, [(1, 220, 184, 690, 70), (2, 222, 256, 90, 32), (3, 868, 256, 112, 32)], (200, 110, 1000, 300)),
    "pc_export": (1.25, [(1, 722, 100, 266, 388), (2, 885, 64, 103, 28)], (700, 55, 1000, 495)),
}
A["m_feedback"] = (2, [(1, 22, 188, 348, 50), (2, 318, 272, 52, 46), (3, 22, 320, 348, 142), (4, 22, 520, 348, 46),
                       (5, 22, 580, 348, 40), (6, 22, 630, 348, 46)], (0, 50, 390, 690))
A["m_board_simple"] = (2, [(1, 14, 143, 288, 104), (2, 27, 292, 205, 46), (3, 36, 443, 150, 60), (4, 316, 630, 60, 60),
                           (5, 2, 703, 386, 55), (6, 10, 12, 45, 40)], None)
SRC = {"m_board_simple": "m_board", "m_repair_a": "m_repair", "m_repair_b": "m_repair", "m_report_body": "m_report"}
# 번호 없이 잘라 쓰는 화면
CROP = {
    "m_board_critical": (2, (0, 90, 390, 700)), "m_chat": (2, (0, 50, 390, 760)), "m_chat_answer": (2, (0, 50, 390, 760)),
    "m_chat_repair": (2, (0, 50, 390, 760)), "m_records": (2, (0, 50, 390, 700)),
    "m_dash": (2, (0, 50, 390, 700)),
    "pc_external": (1.25, (200, 50, 1000, 520)), "pc_outsourcing": (1.25, (200, 50, 1000, 400)),
    "pc_dm_manage": (1.25, (200, 50, 1000, 560)), "pc_check": (1.25, (200, 50, 1000, 640)),
    "pc_changes": (1.25, (200, 50, 1000, 640)), "pc_dm_feedback": (1.25, (200, 50, 1000, 330)),
    "pc_integrity": (1.25, (200, 50, 1000, 640)), "pc_raw": (1.25, (200, 50, 1000, 640)),
    "pc_grade": (1.25, (200, 50, 1000, 880)), "pc_grade_settings": (1.25, (200, 50, 1000, 640)),
    "pc_expansion": (1.25, (200, 50, 1000, 600)), "pc_help": (1.25, (200, 50, 1000, 640)),
    "pc_docs": (1.25, (200, 50, 1000, 300)), "pc_analysis": (1.25, (200, 50, 1000, 1150)),
}


K = 1280 / 1000  # PC 좌표는 1000px 축소 그림에서 읽은 값 → 실제 화면(CSS) 좌표로
for _n, (_d, _m, _c) in list(A.items()):
    if _n.startswith("pc_"):
        A[_n] = (_d, [(n, x * K, y * K, w * K, h * K) for n, x, y, w, h in _m], tuple(v * K for v in _c) if _c else None)
for _n, (_d, _c) in list(CROP.items()):
    if _n.startswith("pc_"):
        CROP[_n] = (_d, tuple(v * K for v in _c))


def run(out, only=None, badge_mm=None):
    os.makedirs(out, exist_ok=True)
    for name, (dpr, marks, crop) in A.items():
        if only and name not in only:
            continue
        src = SRC.get(name, name)
        im = Image.open(f"{HERE}/img/{src}.png").convert("RGB"); d = ImageDraw.Draw(im)
        r = round(13 * dpr); f = ImageFont.truetype(FONT, round(17 * dpr))
        if badge_mm:   # 종이 위 지름 지정: badge_mm = {이름: (인쇄 폭 mm, 지름 mm)}
            w_mm, dm = badge_mm[name]; cw = (crop[2] - crop[0]) * dpr if crop else im.width
            r = round(dm / (w_mm / cw) / 2 + 2); f = ImageFont.truetype(FONT, round(r * 1.15))
        for n, x, y, w, h in marks:
            X, Y, W, H = [round(v * dpr) for v in (x, y, w, h)]
            d.rounded_rectangle((X, Y, X + W, Y + H), radius=round(6 * dpr), outline=RED, width=round(2.5 * dpr))
            cx, cy = X + r // 2, Y + r // 2
            cx = max(r + 2, min(im.width - r - 2, cx)); cy = max(r + 2, min(im.height - r - 2, cy))
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RED, outline=(255, 255, 255), width=round(1.5 * dpr))
            t = str(n); tw = d.textlength(t, font=f)
            d.text((cx - tw / 2, cy - f.size * 0.62), t, font=f, fill=(255, 255, 255))
        if crop:
            im = im.crop(tuple(round(v * dpr) for v in crop))
        im.save(f"{out}/{name}.png")
    for name, (dpr, crop) in ({} if only else CROP).items():
        im = Image.open(f"{HERE}/img/{name}.png").convert("RGB")
        im = im.crop(tuple(min(round(v * dpr), lim) for v, lim in zip(crop, (im.width, im.height, im.width, im.height))))
        im.save(f"{out}/{name}.png")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:   # 이름을 주면 그 사진만 다시 그림(다른 사진은 draw2.py 등이 만든 것이라 덮어쓰지 않게)
        run(f"{HERE}/annot", only=sys.argv[1:], badge_mm={"pc_records": (170, 5.0), "pc_record_edit": (150, 5.0)})
    else:
        run(f"{HERE}/annot")
    print("ok")
