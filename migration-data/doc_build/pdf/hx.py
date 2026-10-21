"""hx.Doc 과 같은 호출 방식으로 HTML을 만들고 Chromium으로 PDF를 뽑는다(한글 조판에 기대지 않는 최종 PDF용).
가이드 스크립트는 그대로 두고 이 모듈을 먼저 불러오게 하면 된다."""
import base64, html, json, os, re, subprocess

MM = 7200 / 25.4
FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts", "pt", "package", "dist", "public", "static")
PDF_JS = os.path.join(os.path.dirname(__file__), "pdf_guide.cjs")


class Item:
    def __init__(self, data):
        self.uri = "data:image/png;base64," + base64.b64encode(data).decode()


class Run:
    def __init__(self, owner, kind, *a):
        self.owner, self.kind, self.a = owner, kind, a

    def remove(self):
        self.owner.runs.remove(self)


class Para:
    def __init__(self, ppid=None, cs=None):
        self.para_pr_id_ref, self.cs, self.runs = ppid, cs, []

    def add_run(self, text, char_pr_id_ref=None):
        r = Run(self, "t", text, char_pr_id_ref or self.cs); self.runs.append(r); return r

    def add_picture(self, item, width, height, treat_as_char=True):
        r = Run(self, "img", item, width / MM, height / MM); self.runs.append(r); return r


class Cell:
    def __init__(self):
        self.paragraphs, self.shade = [Para()], None

    def add_paragraph(self, text="", para_pr_id_ref=None, char_pr_id_ref=None):
        p = Para(para_pr_id_ref, char_pr_id_ref); self.paragraphs.append(p)
        if text:
            p.add_run(text, char_pr_id_ref)
        return p


class Table:
    def __init__(self, rows, cols, widths, width_mm=None):
        self.rows, self.cols, self.width_mm = rows, cols, width_mm
        self.widths = list(widths)
        self.grid = [[Cell() for _ in range(cols)] for _ in range(rows)]

    def cell(self, r, c):
        return self.grid[r][c]

    def set_cell_shading(self, r, c, color):
        self.grid[r][c].shade = color


class _Inner:
    def __init__(self, doc):
        self.doc = doc

    def add_image(self, data, fmt="png"):
        return Item(data)

    def set_header_text(self, text, **kw):
        self.doc.header = text

    def set_page_number(self, **kw):
        pass


class Doc:
    def __init__(self, margins=(20, 20, 15, 15)):
        self.margins = margins
        self.d = _Inner(self)
        self.styles, self.paras, self.blocks, self.header = {}, {}, [], ""

    def cs(self, **kw):
        k = f"c{len(self.styles)}"; self.styles[k] = kw; return k

    def pp(self, **fmt):
        k = f"p{len(self.paras)}"; self.paras[k] = fmt; return k

    def para(self, text, cs, bold_cs=None, target=None, **fmt):
        ppid = self.pp(**fmt) if fmt else None
        p = Para(ppid, cs)
        for i, part in enumerate(text.split("**")):
            if part:
                p.add_run(part, bold_cs if (i % 2 and bold_cs) else cs)
        if target is None:
            self.blocks.append(("p", p))
        else:
            target.paragraphs.append(p)
        return p

    def table(self, rows, cols, widths, width_mm=None):
        t = Table(rows, cols, widths, width_mm); self.blocks.append(("t", t)); return t

    def cell(self, t, r, c, lines, cs, bold_cs=None, shade=None, **fmt):
        cell = t.cell(r, c); first = True
        for ln in ([lines] if isinstance(lines, str) else lines):
            text, lcs, lfmt = (ln, cs, fmt) if isinstance(ln, str) else (ln[0], ln[1], {**fmt, **(ln[2] if len(ln) > 2 else {})})
            if first:
                p = cell.paragraphs[0]; p.runs.clear(); p.para_pr_id_ref = self.pp(**lfmt) if lfmt else None; p.cs = lcs
                first = False
            else:
                p = Para(self.pp(**lfmt) if lfmt else None, lcs); cell.paragraphs.append(p)
            for i, part in enumerate(text.split("**")):
                if part:
                    p.add_run(part, bold_cs if (i % 2 and bold_cs) else lcs)
        if shade:
            cell.shade = shade
        return cell

    # ------------------------------------------------------------------ HTML
    def _span(self, text, cs):
        s = self.styles.get(cs, {})
        plain = not s.get("color") and s.get("font") != "HY헤드라인M"
        if plain and s.get("bold"):
            s = {**s, "color": "#1F3864"}   # 본문 굵은 글씨 = 남색 강조
        sz = s.get('size', 10)
        sz = round(sz * 1.12, 2) if sz < 12 else sz   # 본문 글씨 12% 키움(사진 확대에 맞춤)
        css = [f"font-size:{sz}pt"]
        if s.get("color"):
            css.append(f"color:{s['color']}")
        if s.get("font") == "HY헤드라인M":
            css.append("font-weight:800;letter-spacing:-0.01em")
        elif s.get("bold"):
            css.append("font-weight:700")
        t = html.escape(text)
        if plain:
            # 등급 이름은 등급 색으로, 번호(①②…)는 화면 표시와 같은 빨강, ⇒ 는 파랑
            t = re.sub(r"(?<![가-힣])(긴급|주의|관찰|정상|예비품|불용대기)(?![가-힣]*(?:사항|하세요|깊))",
                       lambda m: f'<b class="g g{["긴급","주의","관찰","정상","예비품","불용대기"].index(m.group(1))}">{m.group(1)}</b>', t)
            t = re.sub(r"([①-⑮])", lambda m: f'<b class="cn" data-n="{ord(m.group(1)) - 0x245F}">{m.group(1)}</b>', t)
            t = t.replace("⇒", '<span class="ar">⇒</span>')
        if s.get("color") == "#1F4E79" and (text.startswith("TIP  ") or text.startswith("주의  ")):
            lead, rest = text.split("  ", 1)
            return f'<span class="badge{" warn" if lead == "주의" else ""}">{lead}</span>' + self._span(rest, cs)
        if s.get("font") != "HY헤드라인M":
            # 누르면 이동하는 참조 (2-1)·(3-1·3-2)·(부록 1) : 파란 밑줄로 표시
            t = re.sub(r"\((?:\d-\d|부록 \d)(?:[·,]\s?(?:\d-\d|부록 \d))*\)", lambda m: f'<span class="ref">{m.group(0)}</span>', t)
        t = t.replace("✔", '<span class="sym">✔</span>').replace("⠿", '<span class="sym">⠿</span>').replace("☰", '<span class="sym">☰</span>')
        return f'<span style="{";".join(css)}">{t}</span>'

    def _para(self, p, in_cell=False):
        f = self.paras.get(p.para_pr_id_ref, {})
        css = []
        al = {"CENTER": "center", "LEFT": "left", "RIGHT": "right"}.get(f.get("alignment", "LEFT" if in_cell else "JUSTIFY"), "justify")
        css.append(f"text-align:{al}")
        css.append(f"line-height:{max(f.get('line_spacing_percent', 150), 105) / 100 * 0.92:.2f}")
        if f.get("spacing_before_pt"):
            css.append(f"margin-top:{f['spacing_before_pt']}pt")
        if f.get("spacing_after_pt"):
            css.append(f"margin-bottom:{f['spacing_after_pt']}pt")
        cls = f' class="{f["cls"]}"' if f.get("cls") else ""
        raw0 = "".join(r.a[0] for r in p.runs if r.kind == "t").lstrip()
        if re.match(r"^(- |[①-⑳] |✔ |□ |\d\) )", raw0):   # 내어쓰기: 둘째 줄부터 글머리 뒤에 맞춤
            extra = " hang2" if re.match(r"^[①-⑳✔□]|^\d\)", raw0) else ""
            cls = ' class="' + (f.get("cls") or "") + " hang" + extra + '"'
        if al == "justify":
            css[0] = "text-align:left"
        if f.get("bottom_border"):
            cls = ' class="h2"'
            raw = "".join(r.a[0] for r in p.runs if r.kind == "t")
            m = re.match(r"^((?:\d-\d|부록 \d))\.\s*(.*)$", raw)
            num, rest = (m.group(1), m.group(2)) if m else ("", raw)
            main, _, sub = rest.partition(" : ")
            badge = f'<span class="hn">{html.escape(num)}</span>' if num else '<span class="hn dot"></span>'
            subh = f'<span class="hs">{html.escape(sub)}</span>' if sub else ""
            return f'<p class="h2">{badge}<span class="ht">{html.escape(main)}</span>{subh}</p>'
        inner = []
        for r in p.runs:
            if r.kind == "t":
                inner.append(self._span(r.a[0], r.a[1]))
            else:
                item, w, h = r.a
                inner.append(f'<img class="sc" data-w="{w:.2f}" data-h="{h:.2f}" src="{item.uri}" style="width:{w:.1f}mm;height:{h:.1f}mm">')
        if not inner:
            # 빈 문단 = 간격(한글 50% 여백 문단과 같은 역할)
            gap = f.get("spacing_after_pt", 0) + f.get("spacing_before_pt", 0)
            return f'<div style="height:{max(gap, 1) * 0.8:.1f}pt"></div>' if not in_cell else ""
        return f'<p{cls} style="{";".join(css)}">{"".join(inner)}</p>'

    def _table(self, t):
        tw = sum(t.widths)
        cols = "".join(f'<col style="width:{w / tw * 100:.2f}%">' for w in t.widths)
        first = t.grid[0][0].paragraphs[0].runs
        kind = ""
        if first and first[0].kind == "t" and first[0].a[0] == "PART":
            kind = " part"
        elif t.rows == 1 and t.cols == 1 and t.grid[0][0].shade in ("#EEF3FB", "#FFF4E5"):
            kind = " tipbox" if t.grid[0][0].shade == "#EEF3FB" else " warnbox"
        elif all(not any(r.kind == "t" for p in c.paragraphs for r in p.runs) for row in t.grid[:1] for c in row) and any(
                r.kind == "img" for c in t.grid[0] for p in c.paragraphs for r in p.runs):
            kind = " pics"
        elif t.rows == 1 and t.cols == 1 and t.grid[0][0].shade == "#1F3864":
            kind = " chapter"
        if not kind and t.rows == 1 and t.cols == 2 and any(r.kind == "img" for p in t.grid[0][0].paragraphs for r in p.runs):
            kind = " pics side"
        t0 = "".join(r.a[0] for p in t.grid[0][0].paragraphs for r in p.runs if r.kind == "t").strip()
        if t0[:1] and "①" <= t0[:1] <= "⑮":
            kind += " nums"
        if any("".join(r.a[0] for p in c.paragraphs for r in p.runs if r.kind == "t").strip() == "⇒" for row in t.grid for c in row):
            kind += " flow"
        rows = []
        for row in t.grid:
            tds = []
            for c in row:
                st = f' style="background:{c.shade}"' if c.shade else ""
                txt = "".join(r.a[0] for p in c.paragraphs for r in p.runs if r.kind == "t").strip()
                if not c.shade and txt in GRADE_FILL:
                    st = f' class="gc" style="background:{GRADE_FILL[txt]}"'
                    tds.append(f"<td{st}>" + "".join(self._para(p, True) for p in c.paragraphs) + "</td>"); continue
                has_img = any(r.kind == "img" for p in c.paragraphs for r in p.runs)
                cl = ' class="img"' if has_img else ""
                tds.append(f"<td{cl}{st}>" + "".join(self._para(p, True) for p in c.paragraphs) + "</td>")
            rows.append("<tr>" + "".join(tds) + "</tr>")
        width = f"width:{t.width_mm}mm" if t.width_mm else "width:100%"
        return f'<table class="t{kind}" style="{width}"><colgroup>{cols}</colgroup>{"".join(rows)}</table>'

    def _blocks_html(self, blocks):
        return "".join(self._chunks(blocks))

    def _chunks(self, blocks):
        out, i = [], 0
        while i < len(blocks):
            kind, b = blocks[i]
            if kind == "p" and self.paras.get(b.para_pr_id_ref, {}).get("keep_with_next"):
                # 소제목은 다음 덩어리와 떨어지지 않게 묶음
                grp = [self._para(b)]
                j = i + 1
                while j < len(blocks) and blocks[j][0] == "p" and not blocks[j][1].runs:
                    j += 1
                if j < len(blocks):
                    grp.append(self._para(blocks[j][1]) if blocks[j][0] == "p" else self._table(blocks[j][1]))
                    # 소제목 다음이 한 줄 설명이면 그 아래 표·그림까지 함께
                    if blocks[j][0] == "p" and j + 1 < len(blocks) and blocks[j + 1][0] == "t":
                        j += 1; grp.append(self._table(blocks[j][1]))
                out.append('<div class="keep">' + "".join(grp) + "</div>"); i = j + 1; continue
            h = self._para(b) if kind == "p" else self._table(b)
            if kind == "t" and ('class="t tipbox"' in h or 'class="t warnbox"' in h) and out:
                k = len(out) - 1   # 사이의 빈 간격 문단은 건너뛰고 앞 덩어리와 함께 묶음
                while k > 0 and out[k].startswith('<div style="height:'):
                    k -= 1
                out[k:] = ['<div class="keep">' + "".join(out[k:]) + h + "</div>"]
            else:
                out.append(h)
            i += 1
        # 빈 간격 문단은 쪽 배치에서 따로 쓰지 않음(간격은 쪽마다 고르게 나눔)
        out = [c for c in out if not c.startswith('<div style="height:')]
        # 그림 + 바로 뒤 번호 설명표(①②…로 시작)는 같은 쪽에
        merged = []
        for c in out:
            follows_pic = merged and 'img class="sc"' in merged[-1]
            is_nums = c.startswith('<table class="t nums') or bool(re.match(r'^<table class="t"[^>]*><colgroup>.*?</colgroup><tr><td[^>]*><p[^>]*><span[^>]*><b class="cn">', c))
            is_note = (c.startswith('<p') or c.startswith('<div class="keep"><p')) and re.search(r'>- ', c[:700]) and not re.search(r'>- (<[^>]+>)*(현황|분석) 탭', c[:900])
            if follows_pic and (is_nums or is_note):
                merged[-1] = '<div class="keep">' + merged[-1] + c + "</div>"
            else:
                merged.append(c)
        # 짧은 안내 줄(- 현황 탭 : … 등)은 바로 뒤 표와, 표 사이의 한 줄 메모는 앞뒤 표와 같은 쪽에
        plain = lambda c: re.sub(r"<[^>]+>", "", c)
        is_p = lambda c: c.startswith("<p") and 'class="h2"' not in c[:40] and len(plain(c)) < 90
        is_tbl = lambda c: c.startswith("<table") or (c.startswith('<div class="keep"><table') and 'class="h2"' not in c)
        # 연속된 안내 줄(- …)은 한 덩어리로, 소제목 묶음 끝이 안내 줄이면 뒤 안내 줄도 붙임
        tmp = []
        for c in merged:
            if tmp and is_p(c) and re.search(r">- ", c[:300]) and (is_p(tmp[-1]) or (tmp[-1].startswith('<div class="keep"><p class="h2"') and tmp[-1].endswith("</p></div>"))):
                prev_ = tmp.pop()
                tmp.append(prev_[:-6] + c + "</div>" if prev_.endswith("</p></div>") else '<div class="keep">' + prev_ + c + "</div>")
            else:
                tmp.append(c)
        merged = tmp
        out2, k = [], 0
        while k < len(merged):
            c = merged[k]
            if is_p(c) and k + 1 < len(merged) and is_tbl(merged[k + 1]):
                grp = c + merged[k + 1]
                if out2 and is_tbl(out2[-1]) and not c.lstrip("<p").startswith(">-") and not re.search(r">- ", c[:300]):
                    grp = out2.pop() + grp
                out2.append('<div class="keep">' + grp + "</div>"); k += 2; continue
            out2.append(c); k += 1
        return out2

    def save(self, path):
        cover, body, seen = [], [], False
        for kind, b in self.blocks:
            if kind == "p" and self.paras.get(b.para_pr_id_ref, {}).get("page_break_before"):
                if seen:
                    body.append(("brk", None))
                seen = True
                continue
            (body if seen else cover).append((kind, b))
        while cover and cover[0][0] == "p" and not cover[0][1].runs:
            cover.pop(0)
        css = open(os.path.join(os.path.dirname(__file__), "guide.css"), encoding="utf-8").read().replace("FONT_DIR", os.path.abspath(FONT_DIR))
        head = f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>{css}</style></head>'
        path = os.path.abspath(path); base = os.path.splitext(path)[0]
        with open(base + "_cover.html", "w", encoding="utf-8") as f:
            f.write(head + '<body class="cover"><div class="band"></div><div class="coverwrap">' + self._blocks_html(cover)
                    + '</div><div class="coverfoot"><span>AX 리더 팀 프로젝트 · 9팀</span><span>2026. 10.</span></div></body></html>')
        chunks, forced = [], set()
        seg = []
        for kind, b in body + [("brk", None)]:
            if kind == "brk":
                if seg:
                    chunks += self._chunks(seg); seg = []
                forced.add(len(chunks))
            else:
                seg.append((kind, b))
        is_part = ['class="t part"' in c or 'class="t chapter"' in c for c in chunks]
        ax = next((k for k, c in enumerate(chunks) if "APPENDIX" in c), 10 ** 9)   # 부록부터는 촘촘한 표
        # ① 덩어리 높이 재기
        with open(base + "_measure.html", "w", encoding="utf-8") as f:
            f.write(head + '<style>body{width:176mm}</style><body><div style="width:176mm">' + "".join(f'<div class="blk{" appx" if k >= ax else ""}">{c}</div>' for k, c in enumerate(chunks)) + f"</div><script>{SETSCALE_JS % {}}</script></body></html>")
        import json
        m = json.loads(subprocess.run(["node", MEASURE_JS, base + "_measure.html"], check=True, capture_output=True, text=True).stdout)
        # ② 쪽 나누기: 그림은 0.82~1.35배로 줄이고 늘릴 수 있다고 보고 순서대로 채움, 장 띠는 쪽 아래 40%에 오지 않게
        H, SMIN, SMAX = PAGE_H, 0.72, 1.25
        n = len(m)
        def fits(i, j):   # 덩어리 i..j-1 을 한 쪽에
            if any(k in forced for k in range(i + 1, j)):
                return None
            for q in range(i, j):   # 장 띠 뒤로 두 덩어리는 같은 쪽에
                if is_part[q] and q + 2 > j - 1 and not (j == n or j in forced):
                    return None
            lo = sum(m[k][1] for k in range(i, j)) + GAP_MIN * (j - i - 1)
            if lo > H and j - i > 1:
                return None
            hi = sum(m[k][2] for k in range(i, j)) + (GAP_MIN + 2.3) * (j - i - 1)
            return max(0.0, H - hi)
        INF = float("inf"); best = [INF] * (n + 1); prev = [0] * (n + 1); best[0] = 0
        for j in range(1, n + 1):
            for i in range(j - 1, -1, -1):
                w = fits(i, j)
                if w is None:
                    if any(k in forced for k in range(i + 1, j)):
                        break
                    continue
                last = (j == n)
                c = best[i] + (0 if last and w < H * 0.5 else w * w) + 20000
                if c < best[j]:
                    best[j], prev[j] = c, i
        pages, j = [], n
        while j > 0:
            pages.insert(0, list(range(prev[j], j))); j = prev[j]
        appx = lambda pg: any('APPENDIX' in chunks[k] for k in pg)
        with open(base + "_body.html", "w", encoding="utf-8") as f:
            f.write(head + "<style>@page{size:A4;margin:19mm 17mm 16mm 17mm} body{width:176mm}</style><body>"
                    + "".join(f'<section class="page{" appx" if appx(pg) else ""}">' + "".join(f'<div class="blk">{chunks[k]}</div>' for k in pg) + "</section>" for pg in pages)
                    + f"<script>{FILL_JS}</script></body></html>")
        self.layout = subprocess.run(["node", PDF_JS, base + "_cover.html", base + "_body.html", path, self.header], check=True, capture_output=True, text=True).stdout
        import pymupdf
        doc = pymupdf.open(path + ".cover.pdf"); doc.insert_pdf(pymupdf.open(path + ".body.pdf"))
        # 표지 'N쪽 바로 가기' 를 누르면 그 쪽으로 이동(본문 N쪽 = PDF N+1번째 장)
        cov = doc[0]
        for w in cov.get_text("words"):
            m = re.match(r"^(\d+)쪽$", w[4])
            if m and int(m.group(1)) + 1 <= len(doc):
                r = pymupdf.Rect(w[0] - 10, w[1] - 4, w[2] + 70, w[3] + 4)
                cov.insert_link({"kind": pymupdf.LINK_GOTO, "from": r, "page": int(m.group(1)), "to": pymupdf.Point(0, 0)})
        # 본문 안 '(2-1)' 같은 참조도 그 절이 있는 쪽으로
        secmap = json.loads(self.layout.strip().splitlines()[-1]) if self.layout.strip().splitlines()[-1].startswith("{") else {}
        for pno in range(1, len(doc)):
            pg = doc[pno]
            for k, target in secmap.items():
                pats = (f"({k})", f"({k}·", f"·{k})", f"({k},", f"{k}(")
                if k.startswith("PART"):
                    pats = (k,)
                for r in [x for pat in pats for x in pg.search_for(pat)]:
                    if target + 0 != pno:
                        pg.insert_link({"kind": pymupdf.LINK_GOTO, "from": r, "page": target, "to": pymupdf.Point(0, 0)})
        # 앱 주소·QR 코드는 누르면 앱 홈페이지로
        APP = "https://tm-cbm.lovable.app"
        for pg in doc:
            for r in pg.search_for("tm-cbm.lovable.app"):
                pg.insert_link({"kind": pymupdf.LINK_URI, "from": r, "uri": APP})
            for info in pg.get_image_info(xrefs=True):
                bb = pymupdf.Rect(info["bbox"])
                if abs(bb.width - bb.height) < 3 and "QR을 찍으면" in pg.get_text("text", clip=pymupdf.Rect(bb.x1, bb.y0, pg.rect.x1, bb.y1)):
                    pg.insert_link({"kind": pymupdf.LINK_URI, "from": bb, "uri": APP})
        for pno in range(1, len(doc)):
            pg = doc[pno]
            for k, label in (("2-1", "2-1 현황판 ▶"), ("2-2", "2-2 TM 리포트 ▶"), ("2-3", "2-3 수선의뢰 ▶"), ("2-4", "2-4 이력 ▶")):
                if k in secmap:
                    for r in pg.search_for(label):
                        pg.insert_link({"kind": pymupdf.LINK_GOTO, "from": pymupdf.Rect(r.x0 - 30, r.y0 - 8, r.x1 + 30, r.y1 + 8), "page": secmap[k], "to": pymupdf.Point(0, 0)})
        doc.set_metadata({"title": "TM-CBM 사용 가이드", "author": "9팀", "subject": "견인전동기(TM) 진단·수선의뢰 관리 앱 사용 가이드"})
        doc.save(path, deflate=True, garbage=3); os.remove(path + ".cover.pdf"); os.remove(path + ".body.pdf")
        print(self.layout)
        return True, ()


GRADE_FILL = {"긴급": "#F8D0D0", "주의": "#FBDDC6", "관찰": "#FFF0B8", "정상": "#D7EDCB"}
PAGE_H = 297 - 19 - 16 - 2   # 본문 높이(mm), 2mm 여유
GAP_MIN = 2.2                 # 덩어리 사이 최소 간격(mm)
MEASURE_JS = os.path.join(os.path.dirname(__file__), "measure.cjs")
SETSCALE_JS = """
function setScale(imgs, s) { imgs.forEach(im => { const w = im.dataset.w >= 165 ? 168 : Math.min(im.dataset.w * s, 168);
    const td = im.closest('td'), tb = im.closest('table'); const tds = tb ? [...tb.querySelectorAll('td')] : [];
    // 사진 왼쪽 + 설명 오른쪽(1줄 2칸) 표: 사진 칸을 사진 폭에 맞춰 넓힘, 설명 칸은 70mm 이상
    const side = tb && tds.length === 2 && td === tds[0] && !tds[1].querySelector('img') && tb.querySelectorAll('col').length === 2;
    const ww = side ? Math.min(w, 100) : w;
    im.style.width = ww + 'mm'; im.style.height = (im.dataset.h * ww / im.dataset.w) + 'mm';
    if (side) { const cols = tb.querySelectorAll('col'); cols[0].style.width = (ww + 5) + 'mm'; cols[1].style.width = 'auto'; } });
    // 어떤 사진도 칸 밖으로 나가지 않게
    imgs.forEach(im => { const td = im.closest('td'); if (!td) return; const cs = getComputedStyle(td);
      const room = td.getBoundingClientRect().width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) - 2;
      const cur = im.getBoundingClientRect().width;
      if (cur > room) { const r = room / cur; im.style.width = (cur * r) + 'px'; im.style.height = (im.getBoundingClientRect().height * r) + 'px'; } }); }
"""
FILL_JS = SETSCALE_JS + """
// 쪽마다: 그림 배율을 맞춰 높이를 채우고, 남는 공간은 덩어리 사이에 고르게 나눔
const MM = 96 / 25.4, H = %(H)s * MM, GMIN = %(G)s * MM, GMAX = 7 * MM;
const report = [];
// 외톨이 줄 없애기: 마지막 줄에 글자가 조금만 남는 문단은 자간을 아주 조금 줄여 한 줄 덜 쓰게
const lines = el => { const r = document.createRange(); r.selectNodeContents(el);
  const ys = new Set([...r.getClientRects()].filter(x => x.width > 1).map(x => Math.round(x.top))); return ys.size; };
document.querySelectorAll('section.page p').forEach(el => {
  if (el.classList.contains('h2') || !el.textContent.trim()) return;
  const n = lines(el); if (n < 2) return;
  for (const ls of [-0.015, -0.03, -0.045]) {
    el.style.letterSpacing = ls + 'em'; el.querySelectorAll('span').forEach(sp => sp.style.letterSpacing = ls + 'em');
    if (lines(el) < n) return;
  }
  el.style.letterSpacing = ''; el.querySelectorAll('span').forEach(sp => sp.style.letterSpacing = '');
});
document.querySelectorAll('section.page').forEach((pg, n) => {
  const blks = [...pg.querySelectorAll(':scope > .blk')], imgs = [...pg.querySelectorAll('img.sc')];
  const used = () => blks.reduce((a, b) => a + b.getBoundingClientRect().height, 0) + GMIN * (blks.length - 1);
  const setS = sc => setScale(imgs, sc);
  let lo = 0.7, hi = 2.2, s = 1;
  if (imgs.length) { setS(hi); if (used() > H) { for (let i = 0; i < 18; i++) { s = (lo + hi) / 2; setS(s); if (used() > H) hi = s; else lo = s; } s = lo; setS(s); } else s = hi; }
  let free = H - used();
  if (free > blks.length * GMAX) {
    const tds = [...pg.querySelectorAll('table.t:not(.part):not(.chapter) td:not(.img)')];
    const base = tds.map(td => parseFloat(getComputedStyle(td).paddingTop));
    for (let add = 0.5; add <= 4; add += 0.5) {
      tds.forEach((td, i) => { td.style.paddingTop = td.style.paddingBottom = (base[i] + add) + 'px'; });
      if (H - used() < blks.length * GMAX * 0.6) break;
    }
    if (H - used() < 0) tds.forEach((td, i) => { td.style.paddingTop = td.style.paddingBottom = base[i] + 'px'; });
    free = H - used();
  }
  const gap = blks.length > 1 ? Math.min(GMAX, GMIN + Math.max(0, free) / (blks.length - 1)) : 0;
  blks.forEach((b, i) => { b.style.marginTop = i ? gap + 'px' : '0'; });
  const end = blks.length ? blks[blks.length - 1].getBoundingClientRect().bottom - blks[0].getBoundingClientRect().top : 0;
  report.push({ page: n + 1, scale: +s.toFixed(2), fill: +(end / H * 100).toFixed(1), overflow: end > H + 1 });
});
const secmap = {};
document.querySelectorAll('section.page').forEach((pg, n) => pg.querySelectorAll('p.h2 .hn').forEach(h => { const k = h.textContent.trim(); if (k && !(k in secmap)) secmap[k] = n + 1; }));
document.querySelectorAll('section.page').forEach((pg, n) => pg.querySelectorAll('table.part').forEach(t => { const m = t.innerText.match(/PART\s*(\d)/); if (m && !(('PART ' + m[1]) in secmap)) secmap['PART ' + m[1]] = n + 1; }));
window.__secmap = secmap;
window.__layout = report;
""" % {"H": PAGE_H, "G": GAP_MIN}
