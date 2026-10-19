"""AX 과제 결과보고 v3 — 양식 서식 유지(줄간격만 220→180%), 사고 사례·노후 통계·판정 절차 그림, 최신 기능·성과 반영 (3쪽 이내)."""
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
        t = etree.SubElement(run, q("t")); t.text = "견인전동기(TM) 상태기반 진단·수선의뢰 관리시스템(TM-CBM)"; break
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
# ================= 본문 =================
append(copy.deepcopy(SPACER), 6)
doc.add_paragraph("53년 된 전동기의 다음 고장을, 사고 전에 — 엑셀 속 고장 기록을 ‘오늘 점검할 TM’으로", char_pr_id_ref="16")
center_last(spacing_after_pt=4); add_mm(9)

append(H1)
O("배경 : 평균 39년 된 전동기, 고장은 사고로 다가온다")
D("1호선 111~116편성 운영 TM 144대 중 **139대(96%)가 사용 30년 이상**, 최고 53년('73년 제작)")
D("'26.3.23 소사역 TM **절연파괴로 아크·연기 → 승객 하차·운행 중단**, 도시철도차량은 중대재해처벌법상 공중교통수단(관리상 결함 = 중대시민재해 요건)")
D("교체 123건 중 **106건(86%)이 고장 난 뒤 교체** → 사후 대응 구조 고착")
O("문제 : 기록은 쌓이는데, 판단은 사람 기억에 의존")
D("취부현황·고장 이력이 엑셀에 분산, 원인 분류가 사람마다 달라 **‘기타’ 37%**")
D("정비문서 4종 **187쪽**을 매번 수작업 검색 → 판단·조치 지연")
O("해결 : 현업 담당자가 생성형 AI로 직접 만든 현장 맞춤 앱")
D("외부 용역 없이 **'26.8 착수 → '26.9 군자차량사업소 시범운영**, 현장 의견을 받아 수시 개선(소요예산 7만원)")
pic_row([(f"{FIG}/age_dist.png", None, 74), (f"{FIG}/risk_flow.png", None, 86)])
caption("① 운영 TM 144대 사용연수 분포                    ② 위험도 자동 판정 절차(발생도 × 심각도)")

append(copy.deepcopy(SPACER), 6); append(H2)
O("결과물 : 휴대폰·PC 겸용 웹 앱(설치 없이 주소로 접속) + 사용 가이드")
pic_row([(f"{IMG}/r_board.png", PH, 36), (f"{IMG}/r_repair.png", PH, 36), (f"{IMG}/r_chat.png", (0, 360, 780, 1600), 36), (f"{IMG}/m_report.png", PH, 36)], gap=" ")
caption("③ 취부 현황판        ④ 말로 수선의뢰·자동 분류        ⑤ AI 챗봇        ⑥ TM 진단서")
O("핵심 기능 : 판정은 규칙대로, 설명은 AI가, 입력은 말로")
table([
    ["기능", "하는 일", "현장 효과"],
    ["위험도 자동 판정", "고장 횟수·간격(발생도) × 고장유형 7종(심각도) **매트릭스(FMEA)**, 이력 등록 즉시 171대 재판정", "등급마다 **산출 근거** 제시"],
    ["예방정비 예측", "평균 고장간격으로 다음 정비 시점 예측(장기 무고장 구분), **반복 고장 위치** 탐지", "예비품 여유(22대 ≈ 29개월) 자동 계산"],
    ["AI 문서 챗봇(RAG)", "정비문서 4종 **187쪽 검색, 답마다 출처 문서·쪽수**, 대화로 수선의뢰 등록", "문서에 없으면 지어내지 않음"],
    ["AI 음성 입력", "말로 고장 내용·질문 입력, **카카오톡 안 화면은 녹음 후 AI 받아쓰기**", "“88091 다시 48” → 88091-48"],
    ["리포트·QR", "TM별 진단서 PDF·한글·워드 즉시 발행, 차량 부착 **QR 라벨**", "현장에서 찍으면 바로 조회"],
    ["데이터 신뢰", "**8개 항목 자동 점검**, 변경 이력(감사 기록)·스냅샷 백업", "판정 규칙 **자동 시험 99건**"],
], [19, 53, 28])
O("성과(실제 데이터 기준, '26.10.19)")
table([
    ["성과 지표", "이전", "현재"],
    ["기록 통합", "엑셀 여러 파일", "TM **171대**·고장 이력 **123건**·외부수선 **47건** 한곳"],
    ["점검 대상 선별", "담당자 경험", "긴급 **2대**·주의 **31대** 자동 선별(근거 제시)"],
    ["고장 ‘기타’ 분류", "**46건(37%)**", "**14건(11%)**, 26%p 감소"],
    ["데이터 오류", "확인 수단 없음", "다른 노선 이력 **5건** 발견·정리"],
    ["현장 의견 반영", "-", "시범운영 중 **13건** 반영(업데이트 내역 공개)"],
    ["개발·유지 비용", "용역 발주·연간 유지비", "**용역비 0원**, 소요예산 7만원"],
], [22, 30, 48])

append(copy.deepcopy(SPACER), 6); append(H3)
O("적용 희망부서 : 군자차량사업소('26.9월부터 시범운영 중)")
D("대상 : 111~116편성 TM 171대 / 검수원·정비원(휴대폰), 담당자(PC)")
D("'26년 현업 사용성 평가(SUS) → '27년 사내 업무망 이전·정식 운영")
append(EFFECT)
D("**[안전]** 사고 전 위험 TM 선별 → 소사역형 절연파괴 재발 방지, 판정 근거·조치 이력이 **안전보건 확보의무 이행 근거**로 축적")
D("**[효율]** 기록 1번으로 이력·취부·등급 동시 갱신, 정비 기준은 챗봇 즉답 → 이중 입력·문서 검색 제거")
D("**[확산]** 장치 템플릿 구조(제동장치 템플릿 등록) → 제동장치·SIV·공기압축기 등으로 **이력만 넣으면 확대**")
append(NEED)
table([
    ["구분", "필요사항", "비고"],
    ["운영 환경", "사내 휴대폰·PC 접속 허용(사내망 이전 시 서버 1대)", "현재 외부 클라우드"],
    ["업무 연계", "수선의뢰·고장 이력 입력을 앱으로 일원화", "사용 가이드 제공"],
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
