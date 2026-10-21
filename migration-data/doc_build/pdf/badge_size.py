"""사진 속 빨간 번호 동그라미의 종이 위 지름(mm) 재기: 빨간 덩어리 중 정사각형에 가까운 것의 폭."""
import re, sys
import numpy as np
from PIL import Image
s = open('docs_out/guide_pdf.py').read()
uses = re.findall(r'(?:wide|phone)\("([a-z_0-9]+)", [^\n]*?(?:\n[^\n]*?)*?w_mm=(\d+)\)', s)
seen = {}
for name, w in uses:
    if name in seen: continue
    im = np.asarray(Image.open(f'gcap/annot/{name}.png').convert('RGB')).astype(int)
    red = (im[..., 0] > 200) & (im[..., 1] < 90) & (im[..., 2] < 90)
    ds = []
    seenpx = np.zeros_like(red)
    H, W = red.shape
    for y0, x0 in zip(*np.nonzero(red[::2, ::2])):
        y0, x0 = y0 * 2, x0 * 2
        if seenpx[y0, x0]: continue
        st = [(y0, x0)]; seenpx[y0, x0] = True; ys = []; xs = []
        while st:
            y, x = st.pop(); ys.append(y); xs.append(x)
            for yy, xx in ((y+1,x),(y-1,x),(y,x+1),(y,x-1)):
                if 0 <= yy < H and 0 <= xx < W and red[yy, xx] and not seenpx[yy, xx]:
                    seenpx[yy, xx] = True; st.append((yy, xx))
        h = max(ys) - min(ys) + 1; ww = max(xs) - min(xs) + 1
        if ww > 8 and 0.8 < h / ww < 1.25 and len(ys) / (h * ww) > 0.55: ds.append(ww)
    mm = int(w) / im.shape[1]
    seen[name] = (round(np.median(ds) * mm, 1) if ds else None, len(ds))
for k, v in seen.items(): print(f'{k:16s} 지름 {v[0]} mm  (동그라미 {v[1]}개)')
