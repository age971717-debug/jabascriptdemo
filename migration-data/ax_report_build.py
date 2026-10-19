"""AX 과제 결과보고 v13 — 시스템 구성도·설계 원칙 표 삭제, 핵심 두 가지만 문장으로, 사진 확대.
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
PHOTO_H = float(sys.argv[5]) if len(sys.argv) > 5 else 42
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
    p = doc.add_paragraph("", para_pr_id_ref="29", char_pr_id_ref="11", include_run=False); rich(p, "   - " + text, "11", "15")
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
# ================= 본문 =================
append(copy.deepcopy(SPACER))
doc.add_paragraph("- AI가 진단하고 답하는 견인전동기 통합관리 시스템 -", char_pr_id_ref="16"); center_last(spacing_after_pt=2)
ntable([
    ["TM 전수 자동 판정", "정비문서 AI 검색", "현장 의견 반영", "외부 개발 용역비"],
    [{"t": "144대", "cs": KPI_R}, {"t": "187쪽", "cs": KPI_N}, {"t": "13건", "cs": KPI_N}, {"t": "0원", "cs": KPI_R}],
    [{"t": "긴급 2·주의 31대 선별", "cs": T95}, {"t": "답변마다 근거 쪽수", "cs": T95}, {"t": "쓰면서 바로 고침", "cs": T95}, {"t": "소요예산 70천원", "cs": T95}],
], [25, 25, 25, 25])

append(H1)
O("(노후화) 운영 견인전동기의 96%가 사용 30년 이상, 노후화에 따른 고장 교체 지속")
D("운영 144대 중 **139대가 사용 30년 이상**, 평균 39년·최장 53년('73년 제작) 경과")
D("'26.3.23. 소사역 견인전동기 아크·연기 발생 ⇒ **승객하차·운행 중단**, 고장 징후 사전 식별 필요")
D("교체 123건 중 **106건(86%)이 고장 발생 후 교체** ⇒ 사후 대응 구조 고착")
caption("【 운영 견인전동기 사용연수 분포('26.10월 기준) 】")
ntable([
    ["사용연수", "30년 미만", "30~39년", "40~49년", "50년 이상", "계"],
    ["운영 대수", "5대(3.5%)", "98대(68.1%)", "9대(6.3%)", {"t": "32대(22.2%)", "cs": T10B}, "144대"],
], [16, 16, 18, 16, 19, 15])
O("(관리) 이력 기록부터 문서 검색, 수선의뢰, 고장분류까지 수작업 처리")
D("취부현황·교체이력을 Excel에 일일이 기록·취합 ⇒ 편성·차호별 추적 및 통계 활용 한계")
D("정비문서 4종 187쪽을 매번 직접 확인, 분류 기준이 사람마다 달라 **'기타' 고장분류 37.4%**")
O("(목적) 현업 담당자가 생성형 AI로 직접 만드는 상태기반정비(CBM) 체계, 업무 방식 전환(AX)")
D("담당자 경험에 의존하던 판단을 **데이터 기반으로 전환**, 고장 징후 전동기 선제 식별")
D("기록·검색·분류·판정의 반복 수작업을 **AI와 자동화로 대체**, 담당자는 판단·조치에 집중")

append(copy.deepcopy(SPACER)); append(H2)
caption("【 As-Is / To-Be : 업무별 구현 기능 】")
def tb(text): return {"t": [(text, T95, "L")]}
def ok(text): return {"t": text, "cs": T95B}
ntable([
    ["업 무", "As-Is", "To-Be (구현 기능)", "성 과"],
    ["현황 파악", "엑셀 시트 열어 검색", tb("취부 현황판(등급 색·시리얼 검색), 대시보드 위젯 19종"), tb("171대 한 화면")],
    ["위험 판단", "담당자 경험", tb("자동 판정·산출 근거, 위험도 TOP 10, 예방정비 임박, 반복 고장 위치"), tb("긴급 2·주의 31대")],
    ["고장 기록", "기록지 후 엑셀 재입력", tb("수선의뢰·챗봇·음성 입력, 사진 첨부, 고장코드 자동 분류"), tb("'기타' 37.4%⇒11.4%")],
    ["정비 기준", "문서 187쪽 직접 검색", tb("AI 문서 검색(근거 쪽수), 고장유형별 수선 절차 바로가기"), tb("현장에서 즉시")],
    ["보고·공유", "수작업 집계·작성", tb("TM 리포트 PDF·한글·워드, QR 라벨 일괄 인쇄, 엑셀 내보내기"), tb("즉시 발행")],
    ["관리·확장", "확인 수단 없음", tb("데이터 8항목 자동 점검, 변경 이력·백업, 장치 확장 템플릿"), tb("오류 5건 정리")],
], [12, 18, 52, 18], split=True)
O("(플랫폼) 생성형 AI로 자체 개발, 시리얼 기준 이력을 단일 DB로 통합")
D("'26.8월 착수, 휴대폰·PC 웹 브라우저로 **설치 없이 접속**, 조회·입력 권한 분리")
O("(위험도) 발생도×심각도(고장유형 7종) 매트릭스로 4단계 등급 자동 분류")
D("운영 144대 전수 판정 ⇒ **긴급 2대·주의 31대 우선 관리대상 지정**, 등록 시마다 재판정")
caption("【 발생도×심각도 판정표 및 등급별 조치 】")
M = {"상시": ["주의", "긴급", "긴급", "긴급"], "빈번": ["관찰", "주의", "긴급", "긴급"], "개연": ["관찰", "주의", "주의", "긴급"],
     "가끔": ["정상", "관찰", "주의", "주의"], "희박": ["정상", "정상", "관찰", "관찰"]}
FQ = ["희박", "가끔", "개연", "빈번", "상시"]; SV = ["치명", "위험", "한계", "경미"]
COL = {"긴급": RED, "주의": ORG, "관찰": YEL, "정상": GRN}
NB = {"l": NON, "r": NON, "t": NON, "b": NON}
GAP = {"t": "", "b": NB, "fill": None}
legend = [("긴급", "2대", "즉시 점검·교체 검토"), ("주의", "31대", "다음 정비 시 우선 확인"), ("관찰", "3대", "고장 추세 관찰"), ("정상", "108대", "정기 점검 유지")]
rows = [[{"t": "심각도＼발생도", "cs": SUB9B}] + FQ + [dict(GAP, b={"l": NON, "r": NON, "t": NON, "b": NON}), {"t": "등급", "b": {"l": NON}}, "대수", "조 치"]]
for i, sv in enumerate(SV):
    g, n, todo = legend[i]
    rows.append([{"t": sv, "cs": "18", "fill": HEAD_FILL}] +
                [{"t": M[f][3 - i], "fill": COL[M[f][3 - i]]} for f in FQ] +
                [dict(GAP), {"t": g, "cs": H10, "fill": COL[g], "b": {"l": NON}}, {"t": n, "cs": T10B},
                 {"t": todo, "align": "L"}])
ntable(rows, [24, 10, 10, 10, 10, 10, 2, 11, 12, 36])
photo_row([(f"{IMG}/r_board.png", PH, "① 취부 현황판"), (f"{IMG}/m_detail.png", PH, "② 산출 근거"),
           (f"{IMG}/r_repair.png", PH, "③ 자동 분류")], PHOTO_H, notes=[
    "[ 현장 화면으로 보는 위험도 판정 ]",
    "① 편성·위치별 TM을 **등급 색**으로 표시, 긴급·주의만 골라 보기",
    "② TM을 누르면 **발생도·심각도 점수와 산출 근거** 표시",
    "③ 고장 내용을 입력하면 **고장코드 자동 분류**, 관련 수선 절차 쪽수 안내"])
O("(AI 어시스턴트) 검색증강생성(RAG) 기반 문서 검색·데이터 분석·수선의뢰 등록")
D("정비문서 187쪽 검색, 답변마다 **근거 문서·쪽수 표시** ⇒ 임의 생성 방지, 답변 신뢰성 확보")
photo_row([(f"{CAP}/mic_repair_on.png", (0, 448, 780, 1688), "① 음성 입력"), (f"{IMG}/r_chat.png", (0, 360, 780, 1600), "② AI 답변"),
           (f"{IMG}/m_chat.png", PH, "③ 문서 검색")], PHOTO_H, notes=[
    "[ AI 어시스턴트 활용 ]",
    "① 마이크를 누르고 말하면 **글자로 입력**, 앱 안 화면은 녹음 후 AI가 받아쓰기",
    "② “오늘 뭐부터 점검해야 돼?” 질문에 **긴급 TM과 이유** 답변",
    "③ 정비 기준 질문 예시 제공, 문서에 없는 내용은 **답하지 않음**"])
O("(분석·리포트) 고장 통계 현황판, 전동기별 리포트(PDF·한글·워드)·QR 라벨")
photo_row([(f"{IMG}/m_report.png", PH, "① 리포트·QR"), (f"{IMG}/pc_dash.png", None, "② 대시보드 현황(PC)"),
           (f"{IMG}/pc_analysis.png", None, "③ 고장 통계 분석(PC)")], PHOTO_H)
O("(AX 설계) AI는 검색·설명에, 판정은 검증 가능한 규칙으로")
D("등급은 판정표로 계산 ⇒ 같은 이력이면 항상 같은 등급, AI 답변은 **근거 문서·쪽수**가 있을 때만 제시")
D("현장 의견을 받아 **바이브 코딩으로 즉시 수정(13건)**, 자동 시험 99건으로 판정 규칙 검증 후 반영")
photo_row([(f"{IMG}/m_feedback.png", PH, "① 현장 의견 접수"), (f"{CAP}/pc_updates.png", None, "② 업데이트 내역: 현장 의견 반영 표시(PC)")], PHOTO_H)

append(copy.deepcopy(SPACER)); append(H3)
O("적용 희망부서 : 1호선 111~116편성 견인전동기 정비 담당 차량사업소")
D("대상 : 견인전동기 171대(운영 144·예비 27) / 검수원·정비원(휴대폰), 담당자(PC)")
D("('26년) 현업 직원 사용성 평가(SUS) ⇒ ('27년) 사내 업무망 이전 후 정식 운영")
append(EFFECT)
D("**[업무 전환]** 기록·검색·분류 수작업을 AI·자동화로 처리 ⇒ 담당자는 **판단·조치 중심**으로 업무 재편")
D("**[예방정비]** 사후 교체에서 위험도 기반 **선제 정비**로 전환 ⇒ 운행장애 발생 가능성 저감")
D("**[노하우]** 숙련자의 경험 판단을 판정표·고장코드로 **정량화**, 인사 이동에도 같은 기준")
D("**[AX 확산]** 현업이 AI로 직접 만들고 고치는 방식을 **제동장치·SIV 등 타 장치·부서로 확대**")
append(NEED)
ntable([
    ["구 분", "필요사항", "비 고"],
    ["운영 환경", "사내 휴대폰·PC 접속 허용(사내망 이전 시 서버 1대)", "현재 외부 클라우드"],
    ["업무 연계", "수선의뢰·고장 이력 입력을 시스템으로 일원화", "사용 가이드 제공"],
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
