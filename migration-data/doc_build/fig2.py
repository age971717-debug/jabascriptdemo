"""결과보고 그림(인쇄 크기 그대로, 300dpi) — 숫자는 '26.10.19 DB 값."""
import sys
from PIL import Image, ImageDraw, ImageFont
FD = sys.argv[1]; OUT = sys.argv[2]
DPI = 300; px = lambda mm: round(mm / 25.4 * DPI); pt = lambda p: round(p / 72 * DPI)
F = lambda w, size: ImageFont.truetype(f"{FD}/Pretendard-{w}.otf", pt(size))
NAVY, RED, ORANGE, YELLOW, GREEN, GRAY = "#1F3864", "#C00000", "#ED7D31", "#E0A800", "#4E9A3A", "#595959"

def center_text(d, cx, y, text, font, fill):
    w = d.textlength(text, font=font); d.text((cx - w / 2, y), text, font=font, fill=fill)

def tiles(path, items, title=None, title_color=NAVY, h_mm=30):
    W, H = px(165), px(h_mm + (7 if title else 0))
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    y0 = 0
    if title:
        d.rounded_rectangle((0, 0, W, px(6)), radius=px(1.2), fill=title_color)
        center_text(d, W / 2, px(0.9), title, F("Bold", 11), "white"); y0 = px(7)
    n = len(items); gap = px(2.5); tw = (W - gap * (n - 1)) / n
    for i, (big, color, label, sub) in enumerate(items):
        x = i * (tw + gap)
        d.rounded_rectangle((x, y0, x + tw, H - 2), radius=px(2), fill="#F4F6FA", outline="#C9D1E3", width=3)
        d.rounded_rectangle((x, y0, x + tw, y0 + px(1.6)), radius=px(1), fill=color)
        size = 30 if len(big) <= 5 else 22
        center_text(d, x + tw / 2, y0 + px(3.2), big, F("Black", size), color)
        center_text(d, x + tw / 2, y0 + px(17), label, F("Bold", 10.5), "#111111")
        center_text(d, x + tw / 2, y0 + px(23.5), sub, F("Medium", 8.5), GRAY)
    im.save(path, dpi=(DPI, DPI))

# ① 문제(추진개요)
tiles(f"{OUT}/kpi_problem.png", [
    ("96%", RED, "사용 30년 이상", "144대 중 139대 · 평균 39년"),
    ("53년", RED, "최고령 견인전동기", "'73년 제작, 지금도 승객 운송"),
    ("86%", ORANGE, "고장 난 뒤에야 교체", "교체 123건 중 106건"),
    ("187쪽", NAVY, "손으로 찾는 정비문서", "지침서·사양서·절차서 4종"),
], title="숫자로 본 현황 — 노후 전동기, 사후 교체, 수작업 관리", title_color=RED)

# ③ 성과(추진성과)
tiles(f"{OUT}/kpi_result.png", [
    ("37→11%", GREEN, "'기타' 고장분류 감소", "46건 → 14건 (26%p↓)"),
    ("33대", RED, "사고 전 관리대상 선별", "긴급 2 · 주의 31 (144대 전수)"),
    ("즉답", NAVY, "정비문서 187쪽 AI 검색", "답마다 근거 문서·쪽수"),
    ("0원", GREEN, "외부 개발·유지 용역비", "자체 개발 · 소요예산 7만원"),
], title="성과 — 실제 데이터 기준('26.10.19)", title_color=GREEN)

# ② 위험도 자동 판정 절차
W, H = px(165), px(60)
im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
def box(x, y, w, h, fill, outline, lines, fonts, colors, r=2):
    d.rounded_rectangle((px(x), px(y), px(x + w), px(y + h)), radius=px(r), fill=fill, outline=outline, width=4)
    total = sum(f.size * 1.25 for f in fonts); yy = px(y + h / 2) - total / 2
    for t, f, c in zip(lines, fonts, colors):
        center_text(d, px(x + w / 2), yy, t, f, c); yy += f.size * 1.25
def arrow(x1, y1, x2, y2, c="#7F7F7F"):
    d.line((px(x1), px(y1), px(x2), px(y2)), fill=c, width=7)
    import math
    a = math.atan2(y2 - y1, x2 - x1); L = px(2.2)
    p = [(px(x2), px(y2)), (px(x2) - L * math.cos(a - 0.45), px(y2) - L * math.sin(a - 0.45)),
         (px(x2) - L * math.cos(a + 0.45), px(y2) - L * math.sin(a + 0.45))]
    d.polygon(p, fill=c)
d.rounded_rectangle((0, 0, W, px(6)), radius=px(1.2), fill=NAVY)
center_text(d, W / 2, px(0.9), "위험도 자동 판정 — 고장 이력만 넣으면 171대 전수 등급이 바로 나온다", F("Bold", 11), "white")
fb, fm, fs = F("Bold", 10), F("Medium", 8.5), F("Medium", 7.5)
# 입력
center_text(d, px(16), px(8.2), "최근 5년 고장 이력", F("Bold", 8.5), GRAY)
for i, (a, b) in enumerate([("고장 교체 횟수", "5년간 몇 번"), ("평균 고장간격", "1년 미만이면 가산"), ("가장 심한 고장", "고장코드 7종")]):
    box(1, 13 + i * 14.5, 30, 12, "#EEF2F9", "#8EA3C8", [a, b], [fb, fs], ["#111111", GRAY])
# O, S
box(37, 14, 22, 17, "#DCE6F4", NAVY, ["발생도 O", "1~10점"], [F("Black", 12), fm], [NAVY, "#333333"])
box(37, 35, 22, 17, "#DCE6F4", NAVY, ["심각도 S", "1~10점"], [F("Black", 12), fm], [NAVY, "#333333"])
for y in (19, 33.5): arrow(31.5, y, 36.5, 22.5)
arrow(31.5, 48, 36.5, 43.5)
# 실제 판정표(앱 tm.ts MATRIX): 가로 발생도 5단계, 세로 심각도 4단계
FREQ = ["희박", "가끔", "개연", "빈번", "상시"]; SEV = ["경미", "한계", "위험", "치명"]
M = {"상시": ["주의", "긴급", "긴급", "긴급"], "빈번": ["관찰", "주의", "긴급", "긴급"], "개연": ["관찰", "주의", "주의", "긴급"],
     "가끔": ["정상", "관찰", "주의", "주의"], "희박": ["정상", "정상", "관찰", "관찰"]}
gc = {"긴급": RED, "주의": ORANGE, "관찰": YELLOW, "정상": GREEN}
mx, my, cs = 66, 13.5, 6.4
center_text(d, px(mx + 2.5 * cs), px(my - 5), "발생도 × 심각도 판정표", F("Bold", 9), NAVY)
for ci, fb in enumerate(FREQ):
    for ri, sb in enumerate(SEV):
        x0, y0 = px(mx + ci * cs), px(my + (3 - ri) * cs)
        d.rectangle((x0, y0, x0 + px(cs) - 5, y0 + px(cs) - 5), fill=gc[M[fb][ri]])
center_text(d, px(mx + 2.5 * cs), px(my + 4 * cs + 0.8), "가로 발생도 희박→상시", fs, GRAY)
center_text(d, px(mx + 2.5 * cs), px(my + 4 * cs + 4.4), "세로 심각도 경미→치명", fs, GRAY)
arrow(59.5, 22.5, 65.5, 24); arrow(59.5, 43.5, 65.5, 36)
# 등급 결과
arrow(98.5, 26.5, 102.5, 26.5)
gx = 103
for i, (g, n, c, todo) in enumerate([("긴급", "2대", RED, "즉시 점검·교체 검토"), ("주의", "31대", ORANGE, "다음 정비 때 우선 확인"),
                                       ("관찰", "3대", YELLOW, "추세 관찰"), ("정상", "108대", GREEN, "정기 점검")]):
    y = 9.0 + i * 11.2
    d.rounded_rectangle((px(gx), px(y), px(gx + 14), px(y + 9.2)), radius=px(1.5), fill=c)
    center_text(d, px(gx + 7), px(y + 1.5), g, F("Black", 11), "white")
    d.text((px(gx + 16), px(y + 0.8)), n, font=F("Black", 13), fill=c)
    d.text((px(gx + 33), px(y + 2.8)), todo, font=F("Medium", 7.8), fill="#333333")
center_text(d, px(115), px(55.2), "이력 등록 시마다 자동 재판정 · 등급마다 산출 근거 표시", F("Bold", 8), NAVY)
im.save(f"{OUT}/risk_flow2.png", dpi=(DPI, DPI))
