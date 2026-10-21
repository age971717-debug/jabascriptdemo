"""사진 번호 동그라미 크기: 종이 위에서 빨간 원 지름이 BADGE_MM 이 되도록(사진마다 인쇄 폭이 달라도 같은 크기)."""
import math
BADGE_MM = 5.6   # 본문 번호(16pt)와 같은 지름


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


def printed(name, default):
    """배치가 끝난 가이드에서 잰 실제 인쇄 폭(mm). printed_mm.json 은 pdfmod/imgwidths.cjs 로 만듦(쪽을 채우려 사진을 키우므로)."""
    import json, os
    f = os.path.join(os.path.dirname(__file__), "printed_mm.json")
    try:
        return json.load(open(f)).get(name, default)
    except (OSError, ValueError):
        return default
