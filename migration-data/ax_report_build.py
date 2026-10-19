"""AX 과제 결과보고 v2 — 양식 서식 유지 + 화면 사진·비교표·성과표 (3쪽 이내)."""
import copy, io, re, sys
from lxml import etree
from PIL import Image
from hwpx import HwpxDocument

FORM, OUT, IMG = sys.argv[1], sys.argv[2], sys.argv[3]
WITH_DASH = len(sys.argv) > 4 and sys.argv[4] == "dash"
HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
q = lambda t: f"{{{HP}}}{t}"
MM = 7200 / 25.4

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
    if t.text == "팀": t.text = "[        ]팀"

def strip_layout(el):
    for ls in el.iter(q("linesegarray")): ls.getparent().remove(ls)
    return el
def append(el): sec.element.append(strip_layout(el))
def rich(p, text, normal, bold):
    for i, part in enumerate(re.split(r"\*\*", text)):
        if part: p.add_run(part, char_pr_id_ref=bold if i % 2 else normal)
def O(text): doc.add_paragraph(f" ㅇ {text}", para_pr_id_ref="28", char_pr_id_ref="12")
def D(text):
    p = doc.add_paragraph("", para_pr_id_ref="29", char_pr_id_ref="11", include_run=False)
    rich(p, "   - " + text, "11", "15")
def center_last(**kw):
    doc.set_paragraph_format(paragraph_index=len(doc.paragraphs) - 1, alignment="CENTER", **kw)

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
            # 셀 안 문단을 맨 앞(run이 linesegarray보다 앞)으로
            for ls in p.findall(q("linesegarray")): p.remove(ls)
        tbl.append(tr)
    tbl.set("rowCnt", str(len(rows)))
    sz = tbl.find(q("sz")); sz.set("height", str(2266 * len(rows)))
    append(el)

def crop(path, box):
    im = Image.open(path).convert("RGB").crop(box)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True); return b.getvalue(), im.size

# ================= 본문 =================
append(copy.deepcopy(SPACER))
p = doc.add_paragraph("엑셀 속 고장 기록을, 매일 아침 ‘오늘 점검할 TM’으로", char_pr_id_ref="16")
center_last(spacing_after_pt=4)

append(H1)
O("문제 : 고장 기록은 쌓이는데, 판단은 사람 기억에 의존")
D("1호선 111~116편성 TM **171대**의 고장·교체 이력 **123건**이 엑셀·수기로 흩어져 반복 고장·노후 경향을 일일이 찾아야 함")
D("원인 분류가 사람마다 달라 **“기타” 43%** → 원인별 대책 수립 불가")
O("해결 : 현업 담당자가 AI로 직접 개발한 현장 맞춤 앱")
D("외부 용역 없이 **2026.8~10 개발** · 흩어진 기록 통합 → **위험 등급 자동 산출** → 현장 수선의뢰·외주수선까지 한 흐름")
table([
    ["구분", "기존", "TM-CBM"],
    ["TM 상태 확인", "엑셀 파일 열어 검색", "휴대폰에서 편성·위치별 **색으로 즉시**"],
    ["점검 우선순위", "담당자 경험", "**발생도×심각도 등급** + 근거 자동 제시"],
    ["고장 원인 분류", "사람마다 다름(“기타” 43%)", "지침서 기준 **자동 분류**(“기타” 13%)"],
    ["수선의뢰 기록", "기록지 작성 후 엑셀 재입력", "현장에서 **말로 입력**, 이력·취부 현황 자동 갱신"],
    ["정비 기준 찾기", "문서 파일 뒤지기", "**AI 챗봇**이 지침서 쪽수까지 답변"],
], [22, 34, 44])

append(copy.deepcopy(SPACER)); append(H2)
O("결과물 : 휴대폰·PC 겸용 웹 앱(설치 없이 주소로 접속) + 사용 가이드")
shots = [crop(f"{IMG}/r_board.png", (0, 0, 780, 1240)), crop(f"{IMG}/r_repair.png", (0, 0, 780, 1240)),
         crop(f"{IMG}/r_chat.png", (0, 360, 780, 1600))]
p = doc.add_paragraph("", include_run=False)
W = round(48 * MM)
for data, (w, h) in shots:
    item = doc.add_image(data, "png")
    p.add_picture(item, width=W, height=round(W * h / w), treat_as_char=True)
    p.add_run("  ", char_pr_id_ref="19")
center_last(spacing_before_pt=4)
doc.add_paragraph("① 취부 현황판(등급별 색)      ② 말로 수선의뢰 → 고장코드 자동 분류      ③ AI 챗봇 “오늘 뭐부터 점검?”", char_pr_id_ref="19")
center_last(spacing_after_pt=4)
if WITH_DASH:
    data, (w, h) = crop(f"{IMG}/r_dash.png", (0, 0, 1920, 1080))
    item = doc.add_image(data, "png"); p = doc.add_paragraph("", include_run=False)
    DW = round(130 * MM); p.add_picture(item, width=DW, height=round(DW * h / w), treat_as_char=True); center_last()
    doc.add_paragraph("④ 대시보드(PC) — 오늘 확인할 것 · 조치 필요 · 차량 건강 요약", char_pr_id_ref="19"); center_last(spacing_after_pt=4)
O("AI가 하는 일")
D("**AI 문서 챗봇** : 정비지침서·수선사양서·표준작업절차서를 찾아 출처 쪽수와 함께 답변, 대화로 수선의뢰까지")
D("**AI 음성 받아쓰기** : 장갑 낀 현장에서도 말로 고장 내용 입력(카카오톡 안에서도 동작)")
D("**자동 판단** : 고장 내용 → 고장코드(지침서 SOP-TM-001), 고장 이력 → 위험 등급·반복 고장 위치·예비품 여유")
O("성과(실제 데이터 기준)")
table([
    ["성과 지표", "이전", "현재"],
    ["흩어진 기록 통합", "엑셀 여러 파일", "TM **171대**·고장 **123건**·외부수선 **47건** 한곳"],
    ["고장 “기타” 분류", "**46건(43%)**", "**14건(13%)**"],
    ["데이터 오류 점검", "확인 수단 없음", "다른 노선 이력 **5건** 정리, 자동 점검 **8개** 항목"],
    ["점검 대상 선별", "수작업", "긴급 **2**·주의 **31**대 자동 선별"],
    ["현장 의견 반영", "-", "**13건** 반영(업데이트 내역 기록)"],
], [24, 26, 50])

append(copy.deepcopy(SPACER)); append(H3)
O("적용 희망부서 : [                    ]  ※ 확인 필요")
D("대상 : 111~116편성 TM 171대 / 검수원·정비원(휴대폰), 담당자(PC)")
append(EFFECT)
D("**매일 아침 “오늘 점검할 TM”** 자동 제시 → 정비 우선순위 판단 표준화")
D("**기록 1번**으로 고장 이력·취부 현황 동시 갱신 → 이중 입력 제거")
D("정확한 원인 데이터 축적 → **유형별 예방정비** 근거, 다른 장치로 확장 가능")
append(NEED)
table([
    ["구분", "필요사항", "비고"],
    ["운영 환경", "사내 휴대폰·PC 접속 허용(사내망 이전 시 서버 1대)", "현재 외부 클라우드"],
    ["업무 연계", "수선의뢰·고장 이력 입력을 앱으로 일원화", "[  ]"],
], [20, 52, 28])
append(FOOT1); append(FOOT2)

doc.save_to_path(OUT)
print("saved", OUT)
