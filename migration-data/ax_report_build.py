"""AX 과제 결과보고 v8 — 중대재해 표현 빼고 AX 리더 과제(AI로 일하는 방식 전환) 관점으로.
v7 — 그림 대신 한글 표(양식 표 서식: 머리행 음영·이중선·양옆 트임)로 현황·판정표·절차·전후 비교를 직접 짠 모양.
숫자는 '26.10.19 DB 값, 판정표 색은 앱 tm.ts MATRIX 그대로. 사용: build7.py 양식 출력 화면폴더 캡처폴더 [사진폭mm]"""
import copy, io, re, sys, zipfile, shutil
from lxml import etree
from PIL import Image
from hwpx import HwpxDocument

FORM, OUT, IMG, CAP = sys.argv[1:5]
PHOTO_W = float(sys.argv[5]) if len(sys.argv) > 5 else 30
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
T10B = CS(size=10.5, font="한컴돋움", bold=True)
H10 = CS(size=10.5, font="한컴돋움", bold=True)
W10 = CS(size=10.5, font="한컴돋움", bold=True, color="#FFFFFF")
BIG_R = CS(size=13, font="HY헤드라인M", color="#C00000")
BIG_N = CS(size=13, font="HY헤드라인M", color="#1F3864")
SUB9 = CS(size=9.5, font="휴먼명조")
PHC = CS(size=9, font="한컴돋움", bold=True)
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
def ntable(rows, widths, total_mm=165, head_rows=1):
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

P_C = "30"
P_L = ppid(alignment="LEFT", line_spacing_percent=130)
P_C = ppid(alignment="CENTER", line_spacing_percent=130)

RED, ORG, YEL, GRN = "#F4B6B6", "#F8CBAD", "#FFE699", "#C6E0B4"   # 인쇄용 연한 등급 색
# ================= 본문 =================
append(copy.deepcopy(SPACER))
doc.add_paragraph("- AI가 진단하고 답하는 견인전동기 통합관리 시스템 -", char_pr_id_ref="16"); center_last(spacing_after_pt=2)

append(H1)
O("(노후화) 운영 견인전동기의 96%가 사용 30년 이상, 노후화에 따른 고장 교체 지속")
D("운영 144대 중 **139대가 사용 30년 이상**, 평균 39년·최장 53년('73년 제작) 경과")
D("'26.3.23. 소사역 견인전동기 아크·연기 발생 ⇒ **승객하차·운행 중단**, 고장 징후 사전 식별 필요")
D("교체 123건 중 **106건(86%)이 고장 발생 후 교체** ⇒ 사후 대응 구조 고착")
caption("【 운영 견인전동기 사용연수 및 교체 현황('26.10월 기준) 】")
ntable([
    ["구 분", "30년 미만", "30~39년", "40~49년", "50년 이상", "계"],
    ["운영 대수", "5대", "98대", "9대", {"t": "32대", "cs": BIG_R}, {"t": "144대", "cs": H10}],
    ["비 율", "3.5%", "68.1%", "6.3%", {"t": "22.2%", "cs": T10B}, "100%"],
    [{"t": "교체 이력", "cs": "18"}, {"t": [("고장 후 교체 **106건(86%)**", T10, "C")], "span": 2}, {"t": "정기·순환 교체 17건", "span": 2}, "123건"],
], [18, 15, 15, 15, 17, 14])
O("(관리) 이력 기록부터 문서 검색, 수선의뢰, 고장분류까지 수작업 처리")
D("취부현황·교체이력을 Excel에 일일이 기록·취합 ⇒ 편성·차호별 추적 및 통계 활용 한계")
D("정비문서 4종 187쪽을 매번 직접 확인, 분류 기준이 사람마다 달라 **'기타' 고장분류 37.4%**")
O("(목적) 현업 담당자가 생성형 AI로 직접 만드는 상태기반정비(CBM) 체계, 업무 방식 전환(AX)")
D("담당자 경험에 의존하던 판단을 **데이터 기반으로 전환**, 고장 징후 전동기 선제 식별")
D("기록·검색·분류·판정의 반복 수작업을 **AI와 자동화로 대체**, 담당자는 판단·조치에 집중")

append(copy.deepcopy(SPACER)); append(H2)
O("(플랫폼) 생성형 AI로 자체 개발, 시리얼 기준 이력을 단일 DB로 통합")
D("'26.8월 착수, 휴대폰·PC 웹 브라우저로 **설치 없이 접속**, 조회·입력 권한 분리")
D("취부현황 171대(운영 144·예비 27), 고장이력 123건, 외부수선 47건 통합 ⇒ **전수 현황 일괄 조회**")
D("비정형 고장 기록(세부 고장내용)을 지침서(SOP-TM-001) 기준 **고장코드 7종으로 자동 정형화**")
O("(위험도) 발생도×심각도(고장유형 7종) 매트릭스로 4단계 등급 자동 분류")
D("운영 144대 전수 판정 ⇒ **긴급 2대·주의 31대 우선 관리대상 지정**, 등록 시마다 재판정")
D("전동기별 산출 근거 제시, 평균 고장간격(MTBF) 기반 정비 시점 예측·반복 고장 위치 탐지")
caption("【 위험도 자동 판정 절차 】")
NB = {"l": NON, "r": NON, "t": NON, "b": NON}
BX = {"l": SOL, "r": SOL, "t": SOL, "b": SOL}
ARW = {"t": "⇒", "cs": BIG_N, "b": NB, "fill": None}
def step(title, *lines):
    return {"t": [(title, H10, "C")] + [(x, SUB9, "C") for x in lines], "b": BX, "fill": "#F2F2F2"}
ntable([[step("① 고장 이력 수집", "최근 5년 교체 횟수", "고장 간격·고장유형"), ARW,
         step("② 점수 산정", "발생도 O (1~10)", "심각도 S (1~10)"), ARW,
         step("③ 매트릭스 판정", "발생도 5단계", "× 심각도 4단계"), ARW,
         {"t": [("④ 등급 부여", H10, "C"), ("긴급 2 · 주의 31", T10B, "C"), ("관찰 3 · 정상 108", SUB9, "C")], "b": BX, "fill": "#FCE4E4"}]],
       [36, 7, 36, 7, 36, 7, 36], head_rows=0)
caption("【 발생도×심각도 판정표 및 등급별 조치 】")
M = {"상시": ["주의", "긴급", "긴급", "긴급"], "빈번": ["관찰", "주의", "긴급", "긴급"], "개연": ["관찰", "주의", "주의", "긴급"],
     "가끔": ["정상", "관찰", "주의", "주의"], "희박": ["정상", "정상", "관찰", "관찰"]}
FQ = ["희박", "가끔", "개연", "빈번", "상시"]; SV = ["치명", "위험", "한계", "경미"]
COL = {"긴급": RED, "주의": ORG, "관찰": YEL, "정상": GRN}
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
O("(AI 어시스턴트) 검색증강생성(RAG) 기반 문서 검색·데이터 분석·수선의뢰 등록")
D("정비문서 187쪽 검색, 답변마다 **근거 문서·쪽수 표시** ⇒ 임의 생성 방지, 답변 신뢰성 확보")
D("대화·**음성**만으로 수선의뢰 등록, 고장코드 자동 분류(카카오톡 화면에서도 동작)")
O("(분석·리포트) 고장 통계 현황판, 전동기별 리포트(PDF·한글·워드)·QR 라벨")
caption("【 시스템 주요 화면 】")
photo_grid([
    [(f"{IMG}/r_board.png", PH, "취부 현황판"), (f"{IMG}/m_detail.png", PH, "위험도 산출 근거"),
     (f"{IMG}/m_report.png", PH, "이력 리포트·QR"), (f"{IMG}/r_repair.png", PH, "고장코드 자동 분류")],
    [(f"{CAP}/mic_repair_on.png", (0, 448, 780, 1688), "음성 입력"), (f"{IMG}/r_chat.png", (0, 360, 780, 1600), "AI 어시스턴트 답변"),
     (f"{IMG}/m_chat.png", PH, "정비문서 검색"), (f"{IMG}/m_feedback.png", PH, "현장 의견 접수")],
], PHOTO_W)
photo_grid([
    [(f"{IMG}/pc_dash.png", None, "대시보드(PC)"), (f"{IMG}/pc_grade.png", None, "등급 판정 기준(PC)")],
], PHOTO_W)
caption("【 추진 전·후 비교 】")
ntable([
    ["구 분", "추진 전", "추진 후", "효 과"],
    ["이력 관리", "Excel 분산 기록·취합", "171대·123건·47건 단일 DB", "등록 즉시 현황·등급 갱신"],
    ["점검 대상 선정", "담당자 경험", "144대 전수 자동 판정", {"t": "긴급 2·주의 31대 선별", "cs": T10B}],
    ["'기타' 고장분류", "46건(37.4%)", "14건(11.4%)", {"t": "26%p 감소", "cs": T10B}],
    ["정비 기준 확인", "문서 187쪽 수작업 검색", "AI 검색·근거 쪽수 표시", "현장에서 즉시 확인"],
    ["데이터 검증", "확인 수단 없음", "8개 항목 자동 점검", "입력 오류 5건 정리"],
    ["개발·유지 비용", "외부 용역 발주", "자체 개발", {"t": "용역비 0원(예산 70천원)", "cs": T10B}],
], [20, 25, 28, 27])
O("(AX 적용) 개발부터 현장 운영까지 단계별 AI 활용")
ntable([
    ["단 계", "AI 활용 방법", "결 과"],
    ["설계·개발", "생성형 AI 바이브 코딩, 요구사항 정의·화면 설계는 담당자 직접 수행", {"t": "개발 용역 없이 자체 구축", "cs": T10B}],
    ["데이터 정형화", "비정형 고장 기록을 지침서 키워드로 고장코드 자동 분류", "'기타' 37.4% ⇒ 11.4%"],
    ["위험도 판정", "발생도×심각도 자동 판정, 챗봇에 물으면 판정 근거 설명", "긴급 2·주의 31대 선별"],
    ["문서 검색", "검색증강생성(RAG)으로 정비문서 187쪽 검색", "답변마다 근거 쪽수 표시"],
    ["현장 입력", "AI 음성 받아쓰기(카카오톡 화면 포함)", "말로 수선의뢰·질문"],
    ["유지·개선", "현장 의견 접수 ⇒ AI 코딩으로 즉시 수정, 자동 시험 99건 검증", {"t": "현장 의견 13건 반영", "cs": T10B}],
], [17, 52, 31])

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
    hx = re.sub(r'<hh:paraPr id="(28|29)".*?</hh:paraPr>',
                lambda m: re.sub(r'(<hh:lineSpacing type="PERCENT" value=")220(")', rf"\g<1>{LS}\g<2>", m.group(0)), hx, flags=re.S)
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
