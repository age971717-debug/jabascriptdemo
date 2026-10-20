"""AX 과제 결과보고 v20 — 결과물 형태에 접속 주소·접근 비밀번호, 별도 담당자 비밀번호 안내.
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
            span = spec.get("span", 1)
            tc = copy.deepcopy(tc_t); tr.append(tc)
            tc.find(q("cellAddr")).set("colAddr", str(c)); tc.find(q("cellAddr")).set("rowAddr", str(r))
            tc.find(q("cellSpan")).set("colSpan", str(span)); tc.find(q("cellSpan")).set("rowSpan", "1")
            tc.find(q("cellSz")).set("width", str(round(W * sum(widths[c:c + span]) / tw)))
            is_head = r < head_rows
            left = NON if c == 0 else SOL
            right = NON if c + span == ncol else SOL
            top = THK if r == 0 else (DBL if r == head_rows else SOL)
            bottom = DBL if r == head_rows - 1 else (THK if r == nrow - 1 else SOL)
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
                for i, part in enumerate(re.split(r"\*\*", text)):
                    if not part: continue
                    run = etree.SubElement(p, q("run")); run.set("charPrIDRef", T10B if (i % 2) else cs)
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
# ================= 본문 (양식 안내 문구대로) =================
def tb(text): return {"t": [(text, T95, "L")]}
append(copy.deepcopy(SPACER))

append(H1)
O("추진목적 : 노후 TM 고장 징후를 데이터로 선제 식별하는 CBM 체계 구축")
D("(노후화) 운영 144대 중 **139대(96%)가 사용 30년 이상**, 평균 39년·최장 53년")
D("(사후 대응) 교체 123건 중 **106건(86%)이 고장 발생 후 교체**, 위험 TM 사전 식별 부재")
D("(사고 사례) '26.3.23. 소사역 견인전동기 아크·연기 발생 ⇒ **승객하차 및 운행 중단**")
D("(수작업) 취부현황·교체이력은 엑셀에 분산, 정비 기준은 문서 4종을 매번 직접 검색")
caption("【 운영 견인전동기 사용연수 분포(144대) 】")
ntable([
    ["사용연수", "30년 미만", "30~39년", "40~49년", "50년 이상", "계"],
    ["운영 대수", "5대(3.5%)", "98대(68.1%)", "9대(6.3%)", {"t": "32대(22.2%)", "cs": T10B}, "144대"],
], [16, 16, 18, 16, 19, 15])
O("개선점 : 경험·수작업 중심 업무를 데이터·AI 기반으로 전환")
D("현업 담당자가 생성형 AI(바이브 코딩)로 **설계부터 개발·개선까지 직접 수행**")
caption("【 As-Is / To-Be 】")
ntable([
    ["As-Is : 엑셀 분산 관리", "To-Be : 취부현황판(등급 색·즉시 갱신)"],
    [{"t": [("[ 기존 엑셀 관리 시트 그림 ]", H10, "C"), ("원본 문서의 그림을 붙여 넣으세요", T95, "C")], "fill": "#F2F2F2"},
     {"pic": (f"{IMG}/pc_board.png", None, 76)}],
], [50, 50])
def wk(text): return {"t": text, "cs": T95B}
def asis(text): return {"t": text, "cs": T95}
ntable([
    ["업 무", "As-Is (기존)", "To-Be (TM-CBM)"],
    [wk("현황 파악"), asis("엑셀 검색"), tb("휴대폰에서 171대를 등급 색으로 한눈에, 새 긴급·예비품 부족 알림")],
    [wk("위험 판단"), asis("담당자 경험"), tb("**144대 자동 판정**(긴급 2·주의 31대), TM마다 산출 근거 제시")],
    [wk("고장 기록"), asis("기록지·재입력"), tb("현장에서 **말로 1번 입력**, 분류·갱신 자동('기타' 37.4⇒11.4%)")],
    [wk("정비 기준"), asis("문서 직접 검색"), tb("**AI 즉답**, 답변마다 근거 문서·쪽수 표시")],
    [wk("이력 관리"), asis("파일 분산"), tb("시리얼 기준 고장·외부수선·예비품 이력 한 곳에(123건·47건)")],
    [wk("보고·공유"), asis("수작업 집계"), tb("리포트·통계 자동 생성(PDF·한글·워드·QR 라벨)")],
    [wk("개발 비용"), asis("외부 용역 발주"), tb("**0원 자체 개발**(현업 담당자가 바이브 코딩)")],
], [12, 15, 73], split=True)

append(copy.deepcopy(SPACER)); append(H2)
O("개발 내용 ① 위험도 자동 판정 및 고장 징후 선제 식별")
D("발생도(최근 5년 고장 횟수)×심각도(고장유형 7종) 판정표로 **등급 4단계 자동 산출**")
D("이력이 등록되면 **171대 전수 즉시 재판정**, TM마다 점수와 산출 근거를 화면에 제시")
D("평균 고장간격(MTBF)으로 **다음 정비 시점 예측**, 같은 위치의 **반복 고장 자동 탐지**")
caption("【 발생도×심각도 판정표 및 등급별 조치 】")
M = {"상시": ["주의", "긴급", "긴급", "긴급"], "빈번": ["관찰", "주의", "긴급", "긴급"], "개연": ["관찰", "주의", "주의", "긴급"],
     "가끔": ["정상", "관찰", "주의", "주의"], "희박": ["정상", "정상", "관찰", "관찰"]}
FQ = ["희박", "가끔", "개연", "빈번", "상시"]; SV = ["치명", "위험", "한계", "경미"]
COL = {"긴급": RED, "주의": ORG, "관찰": YEL, "정상": GRN}
GAP = {"t": "", "b": NB, "fill": None}
legend = [("긴급", "2대", "즉시 점검·교체 검토"), ("주의", "31대", "다음 정비 시 우선 확인"), ("관찰", "3대", "고장 추세 관찰"), ("정상", "108대", "정기 점검 유지")]
rows = [[{"t": "심각도＼발생도", "cs": SUB9B}] + FQ + [{"t": "등급", "b": {"l": DBL, "t": THK, "b": DBL}}, "대수", "조 치"]]
for i, sv in enumerate(SV):
    g, n, todo = legend[i]
    rows.append([{"t": sv, "cs": "18", "fill": HEAD_FILL}] +
                [{"t": M[f][3 - i], "fill": COL[M[f][3 - i]]} for f in FQ] +
                [{"t": g, "cs": H10, "fill": COL[g], "b": {"l": DBL}}, {"t": n, "cs": T10B},
                 {"t": todo, "align": "L"}])
ntable(rows, [24, 10, 10, 10, 10, 10, 11, 12, 37])
photo_row([(f"{IMG}/r_board.png", PH, "① 현황판 : 등급 색 표시"), (f"{IMG}/m_detail.png", PH, "② 누르면 점수·산출 근거"),
           (f"{IMG}/r_repair.png", PH, "③ 고장코드 자동 분류")], PHOTO_H)
O("개발 내용 ② AI 어시스턴트 : 검색증강생성(RAG)·음성 입력")
D("**AI가 정비지침서·수선사양서·절차서를 검색해 답변**, 답마다 근거 문서·쪽수 표시")
D("말하면 **AI가 받아쓰기**(카카오톡 안 화면 포함), 대화만으로 수선의뢰·사진 첨부")
D("고장 내용의 단어로 **고장코드 자동 분류**(SOP-TM-001), 이력·취부현황 동시 갱신")
photo_row([(f"{CAP}/mic_repair_on.png", (0, 448, 780, 1688), "① 말하면 글자로 입력"), (f"{IMG}/r_chat.png", (0, 360, 780, 1600), "② 긴급 TM과 이유 답변"),
           (f"{IMG}/m_chat.png", PH, "③ 정비문서 검색")], PHOTO_H)
O("개발 내용 ③ 분석·리포트 : 대시보드 위젯 19종·TM 리포트")
D("고장 추이·제작년도·제조사별 신뢰도·편성별 위험을 **대시보드가 자동 집계**")
D("TM별 **이력 요약 리포트를 PDF·한글·워드로 즉시 발행**, QR 라벨로 현장에서 조회")
photo_row([(f"{IMG}/m_report.png", PH, "① 리포트·QR"), (f"{IMG}/pc_dash.png", None, "② 대시보드 현황(PC)"),
           (f"{IMG}/pc_analysis.png", None, "③ 고장 통계 분석(PC)")], PHOTO_H2)
O("개발 방식 : 바이브 코딩으로 설계·개발·검증을 자체 수행")
D("현장 의견을 받아 바로 수정·반영, 판정 규칙은 **자동 시험 99건으로 배포 전 검증**")
D("데이터 8개 항목 자동 점검·변경 이력·백업으로 **다른 노선 이력 등 오류 5건 정리**")
photo_row([(f"{IMG}/pc_check_crop.png", None, "① 데이터 자동 점검(8개 항목)"), (f"{IMG}/pc_changes.png", None, "② 변경 이력(감사 기록)")], PHOTO_H2)
O("결과물 형태 : 휴대폰·PC 겸용 웹 앱(설치 없음) + 사용 가이드")
D("**접속 : https://tm-cbm.lovable.app (접근 비밀번호 1488)**, 메뉴 12개")
D("조회·검색·출력은 누구나, 데이터 등록·수정(관리용)은 **별도 담당자 비밀번호**")

O("차별성 : 시제품이 아닌, 실데이터로 바로 쓰는 완성형 서비스")
D("TM 171대·이력 123건 **실데이터로 동작**, 진단·기록·검색·리포트를 **한 흐름**으로")
D("판정은 규칙으로 재현·검증, AI는 근거 있는 답만 ⇒ **현장에서 믿고 쓰는 AI**")
append(copy.deepcopy(SPACER)); append(H3)
O("적용 희망부서 : 1호선 111~116편성 견인전동기 정비 차량사업소")
D("대상 : 견인전동기 171대(운영 144·예비 27), 검수원·정비원(휴대폰)·담당자(PC)")
D("('26년) 현업 직원 사용성 평가(SUS) ⇒ ('27년) 사내 업무망 이전 후 정식 운영")
append(EFFECT)
D("**[업무 전환]** 기록·검색·분류는 시스템이 자동 처리, 담당자는 **판단·조치 중심**")
D("**[예방정비]** 사후 교체에서 위험도 기반 **선제 정비**로 전환, 운행장애 가능성 저감")
D("**[노하우]** 숙련자의 경험 판단을 판정표·고장코드로 **정량화**, 인사 이동에도 유지")
D("**[AX 확산]** 현업이 AI로 직접 만들고 고치는 방식을 **제동장치·SIV 등으로 확대**")
append(NEED)
ntable([
    ["구 분", "필요사항", "비 고"],
    ["운영 환경", "사내 휴대폰·PC 접속 허용(서버 1대)", "현재 외부 클라우드"],
    ["업무 연계", "수선의뢰·고장 이력 입력 일원화", "사용 가이드 제공"],
    ["확대 적용", "제동장치·SIV 고장 이력 자료 제공", "'27년"],
], [18, 54, 28])
append(FOOT1); append(FOOT2)

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
