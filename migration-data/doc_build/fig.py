"""문서용 그림 — 숫자는 2026-10-19 DB 조회값(운영 144대 사용연수, 등급 분포)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
F = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
fm.fontManager.addfont(F); plt.rcParams["font.family"] = fm.FontProperties(fname=F).get_name()
OUT = "fig"

# 1) 운영 144대 사용연수 분포
bins = ["30년 미만", "30~39년", "40~49년", "50년 이상"]; n = [5, 98, 9, 32]
fig, ax = plt.subplots(figsize=(5.2, 3.0), dpi=200)
cols = ["#A6A6A6", "#5B7DB1", "#5B7DB1", "#D9534F"]
b = ax.bar(bins, n, color=cols, width=0.6)
for r, v in zip(b, n):
    ax.text(r.get_x() + r.get_width() / 2, v + 2, f"{v}대", ha="center", fontsize=10, fontweight="bold")
ax.set_ylim(0, 115); ax.set_ylabel("대수", fontsize=9)
ax.spines[["top", "right"]].set_visible(False); ax.tick_params(labelsize=9)
ax.text(0.98, 0.95, "30년 이상 139대(96%)\n평균 39년 · 최고 53년('73년 제작)", transform=ax.transAxes,
        ha="right", va="top", fontsize=8.5, color="#C00000",
        bbox=dict(boxstyle="round,pad=0.35", fc="#FFF2F2", ec="#E6B8B8"))
fig.tight_layout(); fig.savefig(f"{OUT}/age_dist.png"); plt.close(fig)

# 2) 위험도 자동 판정 절차
fig, ax = plt.subplots(figsize=(6.4, 3.0), dpi=200); ax.set_xlim(0, 64); ax.set_ylim(0, 30); ax.axis("off")
def box(x, y, w, h, text, fc="#FFFFFF", ec="#5B7DB1", fs=8, bold=False, color="#000"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=0.8", fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", color=color, linespacing=1.4)
def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=10, lw=1.1, color="#404040"))
ax.text(8.5, 28.2, "최근 5년 고장 이력", ha="center", fontsize=8.5, fontweight="bold")
box(1, 20, 15, 5, "고장 교체 횟수")
box(1, 12.5, 15, 5, "평균 고장간격\n(1년 미만 시 가산)")
box(1, 5, 15, 5, "가장 심한 고장유형\n(고장코드 7종)")
box(21, 17, 12, 7, "발생도 O\n1~10단계", fc="#EAF0FA", bold=True)
box(21, 5, 12, 7, "심각도 S\n1~10단계", fc="#EAF0FA", bold=True)
box(37, 10.5, 10.5, 8, "O × S\n매트릭스 판정", fc="#F2F2F2", ec="#7F7F7F", bold=True)
box(51.5, 15, 12, 10, "위험등급 부여\n긴급 2 · 주의 31\n관찰 3 · 정상 108", fc="#FFF2F2", ec="#D9534F", fs=7.5, bold=True, color="#C00000")
box(51.5, 2.5, 12, 9, "관리대상 지정\n우선순위 정비·점검\n이력 등록 시 재판정", fc="#FFFFFF", ec="#D9534F", fs=7.5)
arrow(16.3, 22.5, 20.7, 21); arrow(16.3, 15, 20.7, 19.5); arrow(16.3, 7.5, 20.7, 8.5)
arrow(33.3, 20.5, 36.7, 16.5); arrow(33.3, 8.5, 36.7, 12.5); arrow(47.8, 15.5, 51.2, 19); arrow(57.5, 14.7, 57.5, 11.8)
fig.savefig(f"{OUT}/risk_flow.png", bbox_inches="tight", pad_inches=0.05); plt.close(fig)

# 3) 기존 엑셀 그림 자리(원본 그림은 사용자 PC에만 있음)
fig, ax = plt.subplots(figsize=(4.0, 2.4), dpi=200); ax.axis("off")
ax.add_patch(plt.Rectangle((0.01, 0.01), 0.98, 0.98, fc="#F2F2F2", ec="#A6A6A6", ls="--", lw=1.5, transform=ax.transAxes))
ax.text(0.5, 0.5, "기존 엑셀 관리시트 화면\n(원본 문서의 그림을 여기에 붙여 넣기)", ha="center", va="center", fontsize=10, color="#7F7F7F", transform=ax.transAxes)
fig.savefig(f"{OUT}/excel_placeholder.png", bbox_inches="tight", pad_inches=0.02); plt.close(fig)
