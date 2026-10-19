"""AX 과제 결과보고 v4 — 사용자 작성 문서(제안서·AX 리더·중대재해 제안) 구성·문장 기반.
v3 — 양식 서식 유지(줄간격만 220→180%), 사고 사례·노후 통계·판정 절차 그림, 최신 기능·성과 반영 (3쪽 이내)."""
import copy, io, re, sys, zipfile, shutil
from lxml import etree
from PIL import Image
from hwpx import HwpxDocument

FORM, OUT, IMG, FIG = sys.argv[1:5]
HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
q = lambda t: f"{{{HP}}}{t}"
MM = 7200 / 25.4
LS = 180  # 본문 줄간격(양식 220%)

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

# ---- 과제명·수행팀 칸 ----
head = paras[0].element
for run in head.iter(q("run")):
    if run.get("charPrIDRef") == "11" and run.find(q("t")) is None and len(run) == 0:
        t = etree.SubElement(run, q("t")); t.text = "AI가 진단하고 답하는 견인전동기 통합관리 시스템"; break
for t in head.iter(q("t")):
    if t.text == "팀": t.text = "9팀"

# ---- 쪽수 추정(본문 폭 175mm, 쪽 높이 262mm) ----
EST = {"mm": 16.0}  # 과제명 머리표
def em(s): return sum(1.0 if ord(ch) > 0x2E80 else (0.3 if ch == " " else 0.55) for ch in s)
def lines(text, pt, width_mm): return max(1, -(-em(text.replace("**", "")) * pt * 0.3528 // width_mm))
def add_mm(v): EST["mm"] += v

def strip_layout(el):
    for ls in el.iter(q("linesegarray")): ls.getparent().remove(ls)
    return el
def append(el, h_mm=11):
    sec.element.append(strip_layout(el)); add_mm(h_mm)
def rich(p, text, normal, bold):
    for i, part in enumerate(re.split(r"\*\*", text)):
        if part: p.add_run(part, char_pr_id_ref=bold if i % 2 else normal)
def O(text):
    p = doc.add_paragraph("", para_pr_id_ref="28", char_pr_id_ref="12", include_run=False)
    rich(p, f" ㅇ {text}", "12", "12"); add_mm(lines(text, 15, 168) * 15 * 0.3528 * LS / 100)
def D(text):
    p = doc.add_paragraph("", para_pr_id_ref="29", char_pr_id_ref="11", include_run=False)
    rich(p, "   - " + text, "11", "15"); add_mm(lines(text, 14, 160) * 14 * 0.3528 * LS / 100)
def center_last(**kw):
    doc.set_paragraph_format(paragraph_index=len(doc.paragraphs) - 1, alignment="CENTER", **kw)
def caption(text):
    doc.add_paragraph(text, char_pr_id_ref="19"); center_last(spacing_after_pt=4); add_mm(8)

def table(rows, widths):
    """양식의 3칸 표를 복제해 행을 늘린다. 첫 행은 머리행(진하게), **굵게** 표기 지원."""
    el = copy.deepcopy(TBL); tbl = el.find(f".//{q('tbl')}")
    trs = tbl.findall(q("tr")); head_tr, body_tr = trs[0], trs[1]
    for tr in trs: tbl.remove(tr)
    total = sum(widths)
    for r, cells in enumerate(rows):
        tr = copy.deepcopy(head_tr if r == 0 else body_tr)
        for c, tc in enumerate(tr.findall(q("tc"))):
            tc.find(q("cellAddr")).set("rowAddr", str(r))
            tc.find(q("cellSz")).set("width", str(round(46716 * widths[c] / total)))
            p = tc.find(f".//{q('p')}")
            for run in p.findall(q("run")): p.remove(run)
            base = "18" if r == 0 else "19"
            for i, part in enumerate(re.split(r"\*\*", cells[c])):
                if not part: continue
                run = etree.SubElement(p, q("run")); run.set("charPrIDRef", "18" if (i % 2 or r == 0) else base)
                t = etree.SubElement(run, q("t")); t.text = part
            for ls in p.findall(q("linesegarray")): p.remove(ls)
        tbl.append(tr)
        n = max(lines(cells[c], 12, 165 * widths[c] / total - 4) for c in range(len(cells)))
        add_mm(n * 12 * 0.3528 * 1.6 + 2)
    tbl.set("rowCnt", str(len(rows)))
    sz = tbl.find(q("sz")); sz.set("height", str(2266 * len(rows)))
    sec.element.append(strip_layout(el)); add_mm(4)

def pic_row(items, gap="  "):
    """items: (path, box|None, width_mm) — 한 줄에 나란히."""
    p = doc.add_paragraph("", include_run=False); tallest = 0
    for path, box, wmm in items:
        im = Image.open(path).convert("RGB")
        if box: im = im.crop(box)
        b = io.BytesIO(); im.save(b, "PNG", optimize=True)
        item = doc.add_image(b.getvalue(), "png"); w, h = im.size
        W = round(wmm * MM); H = round(W * h / w); tallest = max(tallest, H / MM)
        p.add_picture(item, width=W, height=H, treat_as_char=True)
        p.add_run(gap, char_pr_id_ref="19")
    center_last(spacing_before_pt=4); add_mm(tallest + 3)

PH = (0, 0, 780, 1240)
# ================= 본문 (사용자 작성 문서 3종의 구성·문장 기반, 숫자는 '26.10.19 DB) =================
append(copy.deepcopy(SPACER), 6)
doc.add_paragraph("53년째 승객 태운 전동기, 다음 사고는 언제인가 — 고장 이력 기반 위험도 자동 판정", char_pr_id_ref="16")
center_last(spacing_after_pt=4); add_mm(9)

append(H1)
O("(노후화) 운영 견인전동기의 96%가 사용 30년 이상, 노후화에 따른 고장 교체 지속")
D("운영 144대 중 **139대가 사용 30년 이상**, 평균 39년·최장 53년('73년 제작) 경과")
D("'26.3.23. 소사역 견인전동기 절연파괴로 아크·연기 ⇒ **승객하차·운행 중단**(중대시민재해 요건)")
D("교체 123건 중 **106건(86%)이 고장 발생 후 교체** ⇒ 사후 대응 구조 고착")
O("(관리) 이력 기록부터 문서 검색, 수선의뢰, 고장분류까지 수작업 처리")
D("취부현황·교체이력을 Excel에 일일이 기록·취합 ⇒ 편성·차호별 추적 및 통계 활용 한계")
D("정비문서 4종 187쪽을 매번 직접 확인, 분류 기준이 사람마다 달라 **'기타' 고장분류 37.4%**")
O("(목적) 고장 이력 기반 위험등급 자동 판정으로 상태기반정비(CBM) 체계 구축")
D("담당자 경험에 의존하던 판단을 **데이터 기반으로 전환**, 사고 전 위험 전동기 사전 식별")
pic_row([(f"{FIG}/age_dist.png", None, 66), (f"{FIG}/risk_flow.png", None, 78)])
caption("[운영 전동기 144대 사용연수 분포]                    [위험도 자동 판정 절차]")

append(copy.deepcopy(SPACER), 6); append(H2)
O("(플랫폼) 생성형 AI로 자체 개발, 견인전동기 데이터를 단일 DB로 통합")
D("'26.8월 착수 ⇒ **'26.9월부터 군자차량사업소 시범운영**, 휴대폰·PC에서 설치 없이 접속")
D("취부현황 171대(운영 144·예비 27), 고장이력 123건, 외부수선 47건 통합 ⇒ **전수 현황 일괄 조회**")
O("(위험도) 발생도×심각도(고장유형 7종) 매트릭스로 4단계 등급 자동 분류")
D("운영 144대 전수 판정 ⇒ **긴급 2대·주의 31대 우선 관리대상 지정**, 등록 시마다 재판정")
D("전동기별 산출 근거 제시, 평균 고장간격(MTBF) 기반 정비 시점 예측·반복 고장 위치 탐지")
O("(AI 어시스턴트) 검색증강생성(RAG) 기반 문서 검색·데이터 분석·수선의뢰 등록")
D("정비문서 187쪽 검색, 답변마다 **근거 문서·쪽수 표시** ⇒ 임의 생성 방지, 답변 신뢰성 확보")
D("대화·**음성**만으로 수선의뢰 등록, 고장코드 자동 분류(카카오톡 화면에서도 동작)")
O("(분석·리포트) 고장 통계 현황판, 전동기별 리포트(PDF·한글·워드)·QR 라벨")
pic_row([(f"{IMG}/r_board.png", PH, 34), (f"{IMG}/r_repair.png", PH, 34), (f"{IMG}/r_chat.png", (0, 360, 780, 1600), 34), (f"{IMG}/m_report.png", PH, 34)], gap=" ")
caption("[취부 현황판]      [수선의뢰·고장코드 자동 분류]      [AI 어시스턴트]      [이력 리포트]")
table([
    ["구분", "기존", "개선"],
    ["이력 관리", "Excel 분산 기록·취합", "171대·123건·47건 **단일 DB**, 등록 즉시 갱신"],
    ["점검 대상 선정", "담당자 경험", "**긴급 2대·주의 31대** 자동 선별(근거 제시)"],
    ["고장 '기타' 분류", "46건(**37.4%**)", "14건(**11.4%**), **26%p 감소**"],
    ["정비 기준 확인", "문서 187쪽 수작업 검색", "AI 어시스턴트 **즉답**(근거 쪽수)"],
    ["데이터 검증", "확인 수단 없음", "8개 항목 자동 점검(다른 노선 이력 5건 정리)"],
    ["개발·유지 비용", "외부 용역 발주", "**용역비 0원**(소요예산 70천원)"],
], [22, 30, 48])
O("(자체개발) 바이브 코딩 기반 설계·개발·검증 전 과정 담당자 직접 수행")
D("현장 직원과 소통하며 **현장 의견 13건 즉시 반영**, 자동 시험 99건으로 판정 기준 검증")

append(copy.deepcopy(SPACER), 6); append(H3)
O("적용 희망부서 : 군자차량사업소('26.9월부터 시범운영 중)")
D("대상 : 1호선 111~116편성 견인전동기 171대 / 검수원·정비원(휴대폰), 담당자(PC)")
D("('26년) 현업 직원 사용성 평가(SUS) ⇒ ('27년) 사내 업무망 이전 후 정식 운영")
append(EFFECT)
D("**[안전]** 사후 대응에서 사전 조치로 전환, 판정 근거·조치 이력은 **안전보건 확보의무 이행 근거**")
D("**[예산]** 발주·계약 절차 없는 자체 구축, 외부 솔루션의 연간 유지관리비 부담 없음")
D("**[확산]** 대상 부품 이력만 이관하면 **제동장치·SIV·공기압축기** 등으로 즉시 확대 적용")
append(NEED)
table([
    ["구분", "필요사항", "비고"],
    ["운영 환경", "사내 휴대폰·PC 접속 허용(사내망 이전 시 서버 1대)", "현재 외부 클라우드"],
    ["업무 연계", "수선의뢰·고장 이력 입력을 시스템으로 일원화", "사용 가이드 제공"],
    ["확대 적용", "제동장치·SIV 고장 이력 자료 제공", "'27년"],
], [18, 54, 28])
append(FOOT1, 7); append(FOOT2, 7)

doc.save_to_path(OUT)

# 줄간격 220% → LS%(양식 '필요시 변경 가능' 범위, 글꼴·크기는 그대로)
tmp = OUT + ".tmp"
with zipfile.ZipFile(OUT) as zin, zipfile.ZipFile(tmp, "w") as zout:
    for info in zin.infolist():
        data = zin.read(info.filename)
        if info.filename == "Contents/header.xml":
            s = data.decode("utf-8")
            def fix(m):
                return re.sub(r'(<hh:lineSpacing type="PERCENT" value=")220(")', rf"\g<1>{LS}\g<2>", m.group(0))
            s = re.sub(r'<hh:paraPr id="(28|29)".*?</hh:paraPr>', fix, s, flags=re.S)
            data = s.encode("utf-8")
        zout.writestr(info, data, compress_type=zipfile.ZIP_STORED if info.filename == "mimetype" else zipfile.ZIP_DEFLATED)
shutil.move(tmp, OUT)
print("saved", OUT, f"추정 {EST['mm'] / 262:.2f}쪽 (본문 {EST['mm']:.0f}mm)")
