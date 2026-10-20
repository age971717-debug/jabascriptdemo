"""AX 과제 결과보고 v31 — 사진을 해당 설명 밑으로(① 오늘 확인할 것, ② 문서검색·대화 수선의뢰·음성 입력), ③ 대시보드·보고서 자동 작성, 개발 방식 사진 삭제.
v30 — 판정표 한 표(아래 2줄 등급별 조치), As-Is/To-Be 같은 일 짝 비교, 개발 방식 사진(현장 의견·대화 수선의뢰).
v20 — 결과물 형태에 접속 주소·접근 비밀번호, 별도 담당자 비밀번호 안내.
v19 — 표 중간 빈칸 없앰(사용연수·교체 이력은 위아래, 판정표·조치는 이중 세로선).
v18 — 맨 위 성과 요약(AI·자동화 4칸) 복원, 본문에 AI·자동 처리 강조.
v17 — 기능 중요도 순으로 정리(핵심 6개 앞세우고 자잘한 편의 기능 삭제).
v16 — 빠졌던 구현 기능(취부 자동 전환·대시보드 세부·편의 기능)을 표 칸·문장에 채움.
v14 — 양식 안내(추진목적·개선점 / 개발 내용·결과물 형태) 그대로, As-Is/To-Be 사진 행, 사용연수·교체 이력 구분.
v13 — 시스템 구성도·설계 원칙 표 삭제, 핵심 두 가지만 문장으로, 사진 확대.
v12 — 표는 줄이고(As-Is 6행·설계 원칙 한 줄씩) 사진은 키움, 요약 상자에서 기타 비율 뺌.
v11 — 성과 요약 상자, 시스템 구성도, AX 설계 원칙 6가지(모두 한글 표).
v10 — 업무별 As-Is/To-Be(구현 기능·성과) 표를 추진성과 맨 앞에.
v9 — 화면을 한곳에 모으지 않고 해당 설명 바로 밑에 3장씩(설명 ⇒ 화면).
v8 — 중대재해 표현 빼고 AX 리더 과제(AI로 일하는 방식 전환) 관점으로.
v7 — 그림 대신 한글 표(양식 표 서식: 머리행 음영·이중선·양옆 트임)로 현황·판정표·절차·전후 비교를 직접 짠 모양.
숫자는 '26.10.19 DB 값, 판정표 색은 앱 tm.ts MATRIX 그대로. 사용: build7.py 양식 출력 화면폴더 캡처폴더 [사진폭mm]"""
import copy, io, re, sys, zipfile, shutil
from lxml import etree
from PIL import Image
from hwpx import HwpxDocument

FORM, OUT, IMG, CAP = sys.argv[1:5]
PHOTO_H = float(sys.argv[5]) if len(sys.argv) > 5 else 46
PHOTO_H2 = float(sys.argv[6]) if len(sys.argv) > 6 else 40
PHOTO_H3 = float(sys.argv[7]) if len(sys.argv) > 7 else 50
CAP2 = sys.argv[8] if len(sys.argv) > 8 else "gcap/annot"
PIC_W = float(sys.argv[9]) if len(sys.argv) > 9 else 72
PICB = sys.argv[10] if len(sys.argv) > 10 else "v_pcb_tobe.png"
FB_BOX, CR_BOX = (0, 90, 780, 940), (0, 90, 780, 1180)
HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
q = lambda t: f"{{{HP}}}{t}"
MM = 7200 / 25.4
LS = 170  # 본문 줄간격(양식 220%, '필요시 양식 변경 가능')

doc = HwpxDocument.open(FORM)
sec = doc.sections[0]
paras = list(sec.paragraphs)
def el_of(txt):
    for p in paras:
        if txt in "".join(p.element.itertext()): return copy.deepcopy(p.element)
    raise SystemExit("없음: " + txt)
H1, H2, H3 = el_of("□ 추진개요"), el_of("□ 추진성과"), el_of("□ 실증계획")
EFFECT, NEED = el_of(" ㅇ 기대효과"), el_of(" ㅇ 실증 시 필요사항")
FOOT1, FOOT2 = el_of("※ 적용 희망부서에"), el_of("※ 반드시 개발 성과물")
TBL = next(copy.deepcopy(p.element) for p in paras if p.element.find(f".//{q('tbl')}") is not None and "실증" not in "".join(p.element.itertext()) and p is not paras[0])
SPACER = copy.deepcopy(paras[1].element)
for p in paras[1:]: sec.remove_paragraph(p)

head = paras[0].element
for run in head.iter(q("run")):
    if run.get("charPrIDRef") == "11" and run.find(q("t")) is None and len(run) == 0:
        t = etree.SubElement(run, q("t")); t.text = "바이브 코딩 기반 AI 에이전트를 활용한 노후 견인전동기(TM) CBM 자동 진단 시스템"; break
for t in head.iter(q("t")):
    if t.text == "팀": t.text = "9팀"
TITLE_CS = doc.ensure_run_style(size=13, font="휴먼명조", bold=True)
_hp = doc.add_paragraph(""); doc.set_paragraph_format(paragraph_index=len(doc.paragraphs) - 1, alignment="LEFT", line_spacing_percent=130)
TITLE_PP = _hp.para_pr_id_ref; _hp.remove()
widths_h = [7086, 32598, 5669, 4251]   # 과제명 25mm · 제목 115mm · 수행팀 20mm · 팀 15mm (합 49604 = 원래 표 폭)
trh = head.find(f".//{q('tbl')}").find(q("tr"))
for tc, w in zip(trh.findall(q("tc")), widths_h):
    tc.find(q("cellSz")).set("width", str(w))
for t in head.iter(q("t")):
    if t.text and t.text.startswith("바이브 코딩"):
        run = t.getparent(); run.set("charPrIDRef", TITLE_CS)
        pp_ = run.getparent(); pp_.set("paraPrIDRef", TITLE_PP)

def strip_layout(el):
    for ls in el.iter(q("linesegarray")): ls.getparent().remove(ls)
    return el
def append(el): sec.element.append(strip_layout(el))
def rich(p, text, normal, bold):
    for i, part in enumerate(re.split(r"\*\*", text)):
        if part: p.add_run(part, char_pr_id_ref=bold if i % 2 else normal)
def O(text):
    p = doc.add_paragraph("", para_pr_id_ref="28", char_pr_id_ref="12", include_run=False); rich(p, f" ㅇ {text}", "12", "12")
    doc.set_paragraph_format(paragraph_index=len(doc.paragraphs) - 1, keep_with_next=True)
def D(text):
    p = doc.add_paragraph("", para_pr_id_ref="29", char_pr_id_ref="11", include_run=False); rich(p, "- " + text, "11", "15")
def center_last(**kw):
    doc.set_paragraph_format(paragraph_index=len(doc.paragraphs) - 1, alignment="CENTER", **kw)
def caption(text, after=2, before=4):
    doc.add_paragraph(text, char_pr_id_ref=CAPB); center_last(spacing_before_pt=before, spacing_after_pt=after, keep_with_next=True)

# ---- 글자 모양(양식 글꼴 계열) ----
CS = lambda **k: doc.ensure_run_style(**k)
CAPB = CS(size=11, font="한컴돋움", bold=True)
T10 = CS(size=10.5, font="휴먼명조")
T95 = CS(size=9.5, font="휴먼명조")
T95B = CS(size=9.5, font="한컴돋움", bold=True)
T10B = CS(size=10.5, font="한컴돋움", bold=True)
H10 = CS(size=10.5, font="한컴돋움", bold=True)
W10 = CS(size=10.5, font="한컴돋움", bold=True, color="#FFFFFF")
BIG_R = CS(size=13, font="HY헤드라인M", color="#C00000")
BIG_N = CS(size=13, font="HY헤드라인M", color="#1F3864")
KPI_R = CS(size=17, font="HY헤드라인M", color="#C00000")
KPI_N = CS(size=17, font="HY헤드라인M", color="#1F3864")
KPI_N2 = CS(size=15, font="HY헤드라인M", color="#1F3864")
BOXT = CS(size=10.5, font="HY헤드라인M", color="#1F3864")
SUB9 = CS(size=9.5, font="휴먼명조")
PHC = CS(size=9, font="한컴돋움", bold=True)
NOTE = CS(size=10, font="휴먼명조")
NOTEB = CS(size=10, font="한컴돋움", bold=True)
SUB9B = CS(size=9.5, font="한컴돋움", bold=True)

_PP = {}
def ppid(**fmt):
    key = tuple(sorted(fmt.items()))
    if key not in _PP:
        p = doc.add_paragraph("")
        doc.set_paragraph_format(paragraph_index=len(doc.paragraphs) - 1, **fmt)
        _PP[key] = p.para_pr_id_ref; p.remove()
    return _PP[key]
P_C = None  # 표 안 가운데(양식 paraPr 30)
P_L = None

# ---- 테두리·음영(양식 표와 같은 선: 머리행 위 0.4·아래 이중선, 양 끝 세로선 없음, 마지막 줄 0.4) ----
BF = {}  # key -> 임시 id (저장 후 header.xml에 추가)
def bf(left, right, top, bottom, fill=None):
    key = (left, right, top, bottom, fill)
    if key not in BF: BF[key] = str(900 + len(BF))
    return BF[key]
SOL, THK, DBL, NON = ("SOLID", "0.12 mm"), ("SOLID", "0.4 mm"), ("DOUBLE_SLIM", "0.4 mm"), ("NONE", "0.1 mm")
def bf_xml(rid, key):
    l, r, t, b, fill = key
    side = lambda n, v: f'<hh:{n}Border type="{v[0]}" width="{v[1]}" color="#000000"/>'
    brush = f'<hc:fillBrush><hc:winBrush faceColor="{fill}" hatchColor="{fill}" alpha="0"/></hc:fillBrush>' if fill else ""
    return (f'<hh:borderFill id="{rid}" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">'
            '<hh:slash type="NONE" Crooked="0" isCounter="0"/><hh:backSlash type="NONE" Crooked="0" isCounter="0"/>'
            f'{side("left", l)}{side("right", r)}{side("top", t)}{side("bottom", b)}'
            f'<hh:diagonal type="SOLID" width="0.1 mm" color="#000000"/>{brush}</hh:borderFill>')

HEAD_FILL = "#DFE6F7"
def pic_run(path, box, w_mm):
    """그림 한 장을 담은 run(표 칸에 넣기용)."""
    im = Image.open(path).convert("RGB")
    if box: im = im.crop(box)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    item = doc.add_image(b.getvalue(), "png"); w, h = im.size
    tp = doc.add_paragraph("", include_run=False)
    tp.add_picture(item, width=round(w_mm * MM), height=round(w_mm * MM * h / w), treat_as_char=True)
    run = next(r for r in tp.element.findall(q("run")) if r.find(f".//{q('pic')}") is not None)
    run = copy.deepcopy(run); tp.remove()
    return run
def ntable(rows, widths, total_mm=165, head_rows=1, split=False):
    """양식 표를 본떠 만든 표. 셀: str | dict(t=str|[(text, cs, align)], cs, fill, align, b=dict(l,r,t,b), span=n)."""
    el = copy.deepcopy(TBL); tbl = el.find(f".//{q('tbl')}")
    trs = tbl.findall(q("tr")); tc_t = copy.deepcopy(trs[0].findall(q("tc"))[0])
    for tr in trs: tbl.remove(tr)
    W = round(total_mm * MM); tw = sum(widths)
    nrow, ncol = len(rows), len(widths)
    for r, row in enumerate(rows):
        tr = etree.SubElement(tbl, q("tr")); c = 0
        for spec in row:
            spec = {"t": spec} if isinstance(spec, str) else dict(spec)
            span = spec.get("span", 1); rspan = spec.get("rspan", 1); c = spec.get("col", c)
            tc = copy.deepcopy(tc_t); tr.append(tc)
            tc.find(q("cellAddr")).set("colAddr", str(c)); tc.find(q("cellAddr")).set("rowAddr", str(r))
            tc.find(q("cellSpan")).set("colSpan", str(span)); tc.find(q("cellSpan")).set("rowSpan", str(rspan))
            tc.find(q("cellSz")).set("width", str(round(W * sum(widths[c:c + span]) / tw)))
            is_head = r < head_rows
            left = NON if c == 0 else SOL
            right = NON if c + span == ncol else SOL
            top = THK if r == 0 else (DBL if r == head_rows else SOL)
            bottom = DBL if r == head_rows - 1 else (THK if r + rspan - 1 == nrow - 1 else SOL)
            b = spec.get("b", {})
            left, right, top, bottom = b.get("l", left), b.get("r", right), b.get("t", top), b.get("b", bottom)
            fill = spec.get("fill", HEAD_FILL if is_head else None)
            tc.set("borderFillIDRef", bf(left, right, top, bottom, fill))
            sub = tc.find(q("subList")); p_t = sub.find(q("p"))
            for p in sub.findall(q("p")): sub.remove(p)
            if "pic" in spec:
                p = copy.deepcopy(p_t); p.set("paraPrIDRef", P_C)
                for run in p.findall(q("run")): p.remove(run)
                for ls in p.findall(q("linesegarray")): p.remove(ls)
                p.append(pic_run(*spec["pic"])); sub.append(p); c += span; continue
            lines = spec["t"] if isinstance(spec["t"], list) else [(spec["t"], spec.get("cs", "18" if is_head else "19"), spec.get("align", "C"))]
            for text, cs, al in lines:
                p = copy.deepcopy(p_t); p.set("paraPrIDRef", P_C if al == "C" else P_L)
                for run in p.findall(q("run")): p.remove(run)
                for ls in p.findall(q("linesegarray")): p.remove(ls)
                pieces = text if isinstance(text, list) else [(part, spec.get("bcs", T10B) if i % 2 else cs)
                                                              for i, part in enumerate(re.split(r"\*\*", text))]
                for part, pcs in pieces:
                    if not part: continue
                    run = etree.SubElement(p, q("run")); run.set("charPrIDRef", pcs)
                    etree.SubElement(run, q("t")).text = part
                sub.append(p)
            c += span
    tbl.set("rowCnt", str(nrow)); tbl.set("colCnt", str(ncol))
    tbl.find(q("sz")).set("width", str(W)); tbl.find(q("sz")).set("height", str(1700 * nrow))
    if split:  # 쪽 경계에서 줄 단위로 나눔, 머리행 반복(글자처럼 취급 해제)
        tbl.set("pageBreak", "CELL"); tbl.set("repeatHeader", "1")
        pos = tbl.find(q("pos")); pos.set("treatAsChar", "0"); pos.set("horzAlign", "CENTER")
        for tc in tbl.find(q("tr")).findall(q("tc")): tc.set("header", "1")
    append(el)

PH = (0, 0, 780, 1240)
def photo_grid(rows, img_w_mm, cap_shade="#DFE6F7"):
    ncol = len(rows[0])
    t = doc.add_table(rows=2 * len(rows), cols=ncol, width=round(165 * MM))
    t.set_column_widths([1] * ncol)
    pc = ppid(alignment="CENTER", line_spacing_percent=100)
    for r, row in enumerate(rows):
        for c, (path, box, cap) in enumerate(row):
            im = Image.open(path).convert("RGB")
            if box: im = im.crop(box)
            b = io.BytesIO(); im.save(b, "PNG", optimize=True)
            item = doc.add_image(b.getvalue(), "png"); w, h = im.size
            wmm = img_w_mm * (2.4 if ncol == 2 else 1)
            W_ = round(wmm * MM)
            p = t.cell(2 * r, c).paragraphs[0]
            for run in list(p.runs): run.remove()
            p.para_pr_id_ref = pc; p.add_picture(item, width=W_, height=round(W_ * h / w), treat_as_char=True)
            q2 = t.cell(2 * r + 1, c).paragraphs[0]
            for run in list(q2.runs): run.remove()
            q2.para_pr_id_ref = pc; q2.add_run(cap, char_pr_id_ref=PHC)
            t.set_cell_shading(2 * r + 1, c, cap_shade)


def photo_row(items, h_mm, notes=None):
    """한 줄 사진표: 같은 높이로 맞추고 사진마다 설명 칸. items: (path, box, caption)."""
    ims = []
    for path, box, cap in items:
        im = Image.open(path).convert("RGB")
        if box: im = im.crop(box)
        ims.append((im, cap))
    ratio = [im.size[0] / im.size[1] for im, _ in ims]
    if not notes and h_mm * sum(ratio) + 4 * len(ims) > 165:  # 폭이 넘치면 줄 높이를 낮춰 165mm 안에
        h_mm = (165 - 4 * len(ims)) / sum(ratio)
    wmm = [h_mm * r for r in ratio]
    total = sum(w + 4 for w in wmm)
    ncol = len(ims) + (1 if notes else 0)
    widths = [w + 4 for w in wmm] + ([165 - total] if notes else [])
    t = doc.add_table(rows=2, cols=ncol, width=round((165 if notes else min(165, total)) * MM))
    t.set_column_widths(widths)
    pc = ppid(alignment="CENTER", line_spacing_percent=100)
    for c, ((im, cap), w) in enumerate(zip(ims, wmm)):
        b = io.BytesIO(); im.save(b, "PNG", optimize=True)
        item = doc.add_image(b.getvalue(), "png")
        p = t.cell(0, c).paragraphs[0]
        for run in list(p.runs): run.remove()
        p.para_pr_id_ref = pc; p.add_picture(item, width=round(w * MM), height=round(h_mm * MM), treat_as_char=True)
        q2 = t.cell(1, c).paragraphs[0]
        for run in list(q2.runs): run.remove()
        q2.para_pr_id_ref = pc; q2.add_run(cap, char_pr_id_ref=PHC)
        t.set_cell_shading(1, c, "#DFE6F7")
    if notes:
        k = len(ims); t.merge_cells(0, k, 1, k)
        cell = t.cell(0, k); pl = ppid(alignment="LEFT", line_spacing_percent=150)
        first = True
        for i, line in enumerate(notes):
            p = cell.paragraphs[0] if first else cell.add_paragraph("")
            for run in list(p.runs): run.remove()
            p.para_pr_id_ref = pl
            rich(p, line, NOTE, NOTEB) if i else p.add_run(line, char_pr_id_ref=NOTEB)
            first = False
    doc.add_paragraph("", char_pr_id_ref=PHC); doc.set_paragraph_format(paragraph_index=len(doc.paragraphs) - 1, line_spacing_percent=60)
P_C = "30"
P_L = ppid(alignment="LEFT", line_spacing_percent=130)
P_C = ppid(alignment="CENTER", line_spacing_percent=130)

NB = {"l": NON, "r": NON, "t": NON, "b": NON}
BX = {"l": THK, "r": THK, "t": THK, "b": THK}
RED, ORG, YEL, GRN = "#F4B6B6", "#F8CBAD", "#FFE699", "#C6E0B4"   # 인쇄용 연한 등급 색
# ================= As-Is / To-Be 표만 (고장 1건 처리 흐름) =================
NAVY = "#1F3864"
TOB = CS(size=10.5, font="한컴돋움", bold=True, color=NAVY)      # To-Be 강조
TON = CS(size=10, font="휴먼명조")                                 # To-Be 보통
ASG = CS(size=10, font="휴먼명조", color="#7F7F7F")               # As-Is 회색
STG = CS(size=10, font="한컴돋움", bold=True)                      # 단계
SUMA = CS(size=10.5, font="한컴돋움", bold=True, color="#7F7F7F")  # 요약 As-Is
SUMB = CS(size=10.5, font="HY헤드라인M", color=NAVY)                 # 요약 To-Be
HW = CS(size=11, font="한컴돋움", bold=True, color="#FFFFFF")
HG = CS(size=11, font="한컴돋움", bold=True, color="#404040")
GRAY, LIGHT, NAVYF, SUMF = "#F2F2F2", "#EAF0FA", "#1F3864", "#D6E1F5"
DL = {"l": DBL}   # As-Is | To-Be 사이 이중선
def step(t, fill=None): return {"t": t, "cs": STG, **({"fill": fill} if fill else {})}
def a(t): return {"t": t, "cs": ASG, "fill": GRAY}
def b(t): return {"t": [(t, TON, "L")], "bcs": TOB, "b": DL}
append(copy.deepcopy(SPACER))
caption("【 As-Is / To-Be : 고장 1건 발생 시 처리 흐름 】")
ntable([
    [{"t": "단 계", "cs": HG}, {"t": "As-Is (기존)", "cs": HG, "fill": "#D9D9D9"},
     {"t": "To-Be (TM-CBM)", "cs": HW, "fill": NAVYF, "b": {"l": DBL, "t": THK, "b": DBL}}],
    [{"t": [("[ 기존 엑셀 관리 시트 그림 ]", H10, "C"), ("원본 그림을 붙여 넣으세요", T95, "C")], "fill": GRAY, "span": 2},
     {"pic": (PICB, None, 92), "b": DL}],
    [step("① 대상 확인"), a("엑셀 열어 해당 TM 검색"), b("**위치만 말하면 시리얼 자동 확인**")],
    [step("② 위험 판단"), a("담당자 경험에 의존"), b("**이력 기반 등급 자동 판정**, 산출 근거 제시")],
    [step("③ 정비 기준"), a("문서 4종 직접 검색"), b("**AI가 근거 쪽수와 함께 즉시 답변**")],
    [step("④ 고장 기록"), a("엑셀 입력, 분류 제각각"), b("대화로 입력, **고장코드 자동 분류**")],
    [step("⑤ 보　고"), a("보고서 직접 작성"), b("**TM 리포트 자동 작성**(PDF·한글·워드)")],
    [step("처리 방식", SUMF), {"t": "단계마다 수작업", "cs": SUMA, "fill": GRAY},
     {"t": [("대화 한 번으로 기록·판정·보고까지 자동 연결", SUMB, "C")], "fill": SUMF, "b": DL}],
], [15, 27, 58])
doc.save_to_path(OUT)

# 저장 후: 줄간격 220→LS%, 새 테두리·음영 추가(임시 id → 실제 id)
tmp = OUT + ".tmp"
with zipfile.ZipFile(OUT) as zin, zipfile.ZipFile(tmp, "w") as zout:
    hx = zin.read("Contents/header.xml").decode("utf-8")
    n0 = int(re.search(r'<hh:borderFills itemCnt="(\d+)"', hx).group(1))
    real = {tmp_id: str(n0 + 1 + i) for i, (key, tmp_id) in enumerate(BF.items())}
    add = "".join(bf_xml(real[tid], key) for key, tid in BF.items())
    hx = hx.replace("</hh:borderFills>", add + "</hh:borderFills>")
    hx = re.sub(r'<hh:borderFills itemCnt="\d+"', f'<hh:borderFills itemCnt="{n0 + len(BF)}"', hx)
    hx = re.sub(r'<hh:paraPr [^>]*?\bid="(\d+)"[^>]*>.*?</hh:paraPr>',
                lambda m: re.sub(r'(<hh:lineSpacing type="PERCENT" value=")220(")', rf"\g<1>{LS}\g<2>", m.group(0))
                if (m.group(1) in ("28", "29") or int(m.group(1)) >= 34) else m.group(0), hx, flags=re.S)
    for info in zin.infolist():
        data = zin.read(info.filename)
        if info.filename == "Contents/header.xml":
            data = hx.encode("utf-8")
        elif info.filename == "Contents/section0.xml":
            s = data.decode("utf-8")
            s = re.sub(r'borderFillIDRef="(9\d\d)"', lambda m: f'borderFillIDRef="{real.get(m.group(1), m.group(1))}"', s)
            data = s.encode("utf-8")
        zout.writestr(info, data, compress_type=zipfile.ZIP_STORED if info.filename == "mimetype" else zipfile.ZIP_DEFLATED)
shutil.move(tmp, OUT)
print("saved", OUT, "borderFills +", len(BF))
