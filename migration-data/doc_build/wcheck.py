"""한글 한 줄 폭 어림: 한글 1.0, 공백 0.5, 그 밖 0.55 (휴먼명조·한컴돋움 기준 em)."""
import re, sys
def em(s):
    s = s.replace("**", "")
    return sum(1.0 if ord(c) > 0x2E80 or c in "⇒×·【】①②③" else (0.5 if c == " " else 0.55) for c in s)
def cap(width_mm, pt, ratio=0.96, spacing=-0.04):
    return 39.8 * 14 / pt  # 사용자 확인: "(노후화) … 최장 53년" 39.6em이 딱 한 줄
    return width_mm / (pt * 0.3528 * ratio * (1 + spacing))
if __name__ == "__main__":
    src = open(sys.argv[1]).read()
    for kind, pre, pt, w in (("O", " ㅇ ", 15, 175), ("D", "   - ", 14, 175)):
        c = cap(w, pt)
        for m in re.finditer(rf'^{kind}\("(.*)"\)', src, re.M):
            e = em(pre + m.group(1))
            if e > c - 0.5: print(f"{kind} {e:5.1f}/{c:4.1f}  {m.group(1)[:60]}")
