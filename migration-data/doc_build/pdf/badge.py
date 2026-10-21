"""사진 번호 동그라미 크기: 종이 위에서 빨간 원 지름이 BADGE_MM 이 되도록(사진마다 인쇄 폭이 달라도 같은 크기)."""
import math
BADGE_MM = 5.0


def badge_px(w_mm, content_w_css, S):
    """반지름 r(px), 글자 크기(px), 왼쪽 여백 M(css px). 흰 테두리 2S 안쪽이 빨강."""
    # 여백 M을 정하면 전체 폭이 바뀌므로 두 번 맞춤
    M = 30
    for _ in range(3):
        mm_per_px = w_mm / ((content_w_css + M) * S)
        red = BADGE_MM / mm_per_px
        r = red / 2 + 2 * S
        M = math.ceil((2 * r + 4 * S) / S) + 2
    return round(r), round(r * 1.15), M
