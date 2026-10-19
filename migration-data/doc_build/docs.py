"""사용자가 직접 쓴 문서 3종(제안서·AX 리더·중대재해 개선 제안)을 최신 앱·데이터로 다시 만든다.
숫자는 2026-10-19 DB 조회값. 원문 구성·문장은 그대로 두고, 바뀐 숫자와 새 기능만 고친다."""
import sys
from hx import Doc, cell_pics

IMG, CAP, FIG, OUT = sys.argv[1:5]
PH = (0, 0, 780, 1240)  # 휴대폰 화면 위쪽
BOARD, DASH, GRADE = f"{IMG}/pc_board.png", f"{IMG}/pc_dash.png", f"{IMG}/pc_grade.png"
CHAT_M = [(f"{IMG}/r_chat.png", (0, 360, 780, 1600)), (f"{IMG}/m_chat.png", PH)]
REPAIR_M = [(f"{IMG}/r_repair.png", PH), (f"{CAP}/mic_repair_on.png", (0, 448, 780, 1688))]
REPORT_M = [(f"{IMG}/m_detail.png", PH), (f"{IMG}/m_report.png", PH)]
EXCEL = f"{FIG}/excel_placeholder.png"


# =====================================================================
# (a) 제안서 — AI가 진단하고 답하는 전동기 통합관리 시스템
# =====================================================================
def proposal(path):
    D = Doc(margins=(20, 20, 15, 15))
    TITLE = D.cs(font="HY헤드라인M", size=22)
    LBL = D.cs(font="한컴돋움", size=11.5, bold=True)
    CEL = D.cs(font="휴먼명조", size=11.5, ratio=95)
    H = D.cs(font="HY헤드라인M", size=15)
    O = D.cs(font="한컴돋움", size=13.5, bold=True, ratio=95)
    T = D.cs(font="휴먼명조", size=12.5, ratio=95, letter_spacing=-3)
    TB = D.cs(font="휴먼명조", size=12.5, ratio=95, letter_spacing=-3, bold=True)
    CAPS = D.cs(font="한컴돋움", size=10.5, ratio=95)

    D.para("AI가 진단하고 답하는 전동기 통합관리 시스템", TITLE, alignment="CENTER", spacing_after_pt=8)

    t = D.table(6, 6, [15, 24, 11, 13, 15, 22])
    left = dict(alignment="LEFT", line_spacing_percent=135)
    ctr = dict(alignment="CENTER", line_spacing_percent=130)
    D.cell(t, 0, 0, "제안요지", LBL, shade="#E7E6E6", **ctr)
    D.cell(t, 0, 1, ["- 최고 53년 사용 견인전동기의 교체이력 65%가 절연파괴 등 중대 고장",
                     "- 보유 171대 위험도 자동판정·시계열분석·RAG 답변·음성 입력 시스템 구현",
                     "- 개발 용역 없이 자체 구축, 데이터만 바꾸면 즉시 수평 전개 가능"], CEL, **left)
    D.cell(t, 1, 0, "제안분야", LBL, shade="#E7E6E6", **ctr)
    D.cell(t, 1, 1, "지정주제 ②", CEL, **ctr)
    D.cell(t, 1, 4, "업무구분", LBL, shade="#E7E6E6", **ctr)
    D.cell(t, 1, 5, "내업무", CEL, **ctr)
    D.cell(t, 2, 0, "실행여부/시기", LBL, shade="#E7E6E6", **ctr)
    D.cell(t, 2, 1, "■ 실행 중(2026년 8월)        □ 실행 전", CEL, **left)
    D.cell(t, 3, 0, "제 안 자", LBL, shade="#E7E6E6", **ctr)
    for c, v in enumerate(["부서명", "직급", "성명", "기여도", "연락처"], 1):
        D.cell(t, 3, c, v, LBL, **ctr)
    for r, row in enumerate([["도시철도연구팀", "3급", "허문강", "30%", "6110-8130"],
                             ["도시철도연구팀", "5급", "권휘진", "70%(주)*", "6110-8134"]], 4):
        for c, v in enumerate(row, 1):
            D.cell(t, r, c, v, CEL, **ctr)
    t.merge_cells(0, 1, 0, 5); t.merge_cells(1, 1, 1, 3); t.merge_cells(2, 1, 2, 5); t.merge_cells(3, 0, 5, 0)

    def HD(x): D.para("□ " + x, H, spacing_before_pt=10, spacing_after_pt=3, line_spacing_percent=150, keep_with_next=True)
    def OO(x): D.para("  ○ " + x, O, spacing_before_pt=3, line_spacing_percent=150)
    def DD(x): D.para("    - " + x, T, TB, line_spacing_percent=150, indent_left_mm=6, first_line_indent_mm=-4)

    HD("현황 및 문제점")
    OO("내구연한 초과 견인전동기의 중대고장 반복 발생")
    DD("운영 144대 중 139대(96%)가 사용 30년 이상, 평균 39년, 최고 53년('73년 제작)")
    DD("교체이력 65%가 절연파괴 등 중대고장, ('26.3.23)소사역 아크·연무로 승객하차 및 운휴")
    OO("이력·기준 정보 수기 관리로 상태 판단 및 조치 지연")
    DD("전동기 취부현황·교체이력이 엑셀 시트에 분산, 편성·차호별 추적 및 통계분석 불가")
    DD("정비지침서·작업절차서·수선사양서 등 문서 4종 187쪽을 매번 수작업 검색")
    HD("개선방안")
    OO("기존 관리시트 그대로 활용, 정량적 위험도 자동 판정으로 전환")
    DD("현행 엑셀 양식 시스템 DB로 이관(171대·고장이력 123건 구축), 수정 시 최신 시트 자동 생성")
    D.para("      → 기존 업무방식 변경 없이 엑셀과 시스템이 양방향 연동, 별도 입력 작업 불필요", T, TB, line_spacing_percent=150, indent_left_mm=6)
    DD("발생도(고장 교체 횟수)×심각도(7개 코드) 매트릭스 판정으로 **2대 긴급 / 31대 주의** 자동 도출")
    DD("데이터 8개 항목 자동 점검 → 관리 편성 밖 이력 5건 등 입력 오류 자동 검출·정리")
    OO("고장 추세 분석부터 이력보고서 발행까지 일괄 처리")
    DD("전동기별 고장 이력 시계열로 정렬, 발생 간격 변화 추적 → 열화 진행 추세 판별")
    DD("평균 고장간격(MTBF) 기반 차기 정비 시점 예측 → 경과 대상 자동 표시(장기 무고장 구분)")
    DD("개별 전동기 이력보고서 자동 생성 → PDF·한글·워드로 즉시 발행, 차량 부착 QR 라벨")
    OO("RAG 기반 AI 어시스턴트로 조회·등록·분석 일원화")
    DD("정비지침서 등을 AI가 검색→답변마다 출처 문서·페이지 함께 표시, 임의 생성 방지")
    DD("대화만으로 수선의뢰 접수 → 고장코드 자동 분류, 이력·위험도·현황판 자동 갱신")
    DD("**음성 입력**: 말로 고장내용·질문 입력, 카카오톡 안 화면은 녹음 후 AI 받아쓰기")
    OO("생성형 AI 기반 자체 풀스택(Full-Stack) 신속 개발")
    DD("백엔드·DB·보안인증 기반으로 여러 담당자가 동시 접속·기록하는 구조로 구현")
    DD("설계·개발·검증 전 과정 자체 수행, 현장 요구사항 13건을 담당자가 직접 수정·반영")
    DD("등급 판정 규칙 등 자동 시험 99건 → 수정해도 판정 기준이 바뀌지 않음을 배포 전 확인")
    HD("기대효과")
    OO("[안전] 사후 대응에서 사전 조치로 전환")
    DD("이력 갱신 즉시 171대 전수 위험도 재판정 → 경험 판단으로 놓치던 대상까지 선별")
    DD("자연어·음성 등록으로 이력이 쌓일수록 판정 정확도 상승 → 데이터 축적에 따른 안전관리 강화")
    OO("[예산] 프로그램의 발주·계약 절차 없는 자체 구축(비예산 구축)")
    DD("요구사항 정의부터 개발·검증까지 자체 수행 → 용역 발주·계약 전 과정 생략")
    DD("기능 추가·수정을 담당자가 직접 반영, 외부 솔루션의 연간 유지관리비 부담 없음")
    OO("[확산] 부품 하나에서 차량 전체 부품으로 즉시 전개 가능")
    DD("전동기 실데이터로 PoC 완료, 군자차량사업소 시범운영 중 → 편성·분석·검색 기능 전체를 그대로 사용")
    DD("장치 템플릿(제동장치 등록)으로 대상 부품 이력만 이관하면 공기압축기·출입문 등 확대 적용")
    DD("웹 기반 구조로 별도 설치 없이 사내망 적용 가능, 공사 CBM 정책 실현의 실행 수단")

    D.para("", T)
    g = D.table(4, 2, [50, 50])
    pc = D.pp(alignment="CENTER", line_spacing_percent=100)
    cell_pics(D, g, 0, 0, [(DASH, None)], 47, pc)
    cell_pics(D, g, 0, 1, [(BOARD, None)], 47, pc)
    cell_pics(D, g, 2, 0, CHAT_M, 52, pc)
    cell_pics(D, g, 2, 1, REPAIR_M, 52, pc)
    for (r, c), v in {(1, 0): "전동기 171대 위험도 현황", (1, 1): "편성별 취부 현황판(등급 색)",
                      (3, 0): "AI 어시스턴트 응답(현황 조회·문서 검색)",
                      (3, 1): "수선의뢰 등록·음성 입력·고장코드 자동 분류"}.items():
        D.cell(g, r, c, v, CAPS, **ctr)
    return D.save(path)


# =====================================================================
# (b) AX 리더 — AI가 진단하고 답하는 견인전동기 통합관리 시스템 (9팀)
# =====================================================================
def axleader(path):
    D = Doc(margins=(13, 13, 12, 12))
    HDR = D.cs(font="HY견고딕", size=20, color="#FFFFFF")
    TTL = D.cs(font="HY견고딕", size=16)
    TEAM = D.cs(font="HY견고딕", size=15, color="#1F3C88")
    SUB = D.cs(font="한컴돋움", size=11)
    H = D.cs(font="HY견고딕", size=14.5)
    O = D.cs(font="한컴돋움", size=12, bold=True, ratio=95, letter_spacing=-3)
    T = D.cs(font="휴먼명조", size=11.5, ratio=93, letter_spacing=-4)
    TB = D.cs(font="휴먼명조", size=11.5, ratio=93, letter_spacing=-4, bold=True)
    CAPS = D.cs(font="한컴돋움", size=8.5, bold=True, color="#1F3C88", ratio=92)

    h = D.table(2, 3, [21, 64, 15])
    ctr = dict(alignment="CENTER", line_spacing_percent=120)
    D.cell(h, 0, 0, "AX 리더", HDR, shade="#2E3A59", **ctr)
    D.cell(h, 0, 1, "AI가 진단하고 답하는 견인전동기 통합관리 시스템", TTL, shade="#F2F2F2", **ctr)
    D.cell(h, 0, 2, "9팀", TEAM, shade="#D9E1F2", **ctr)
    D.cell(h, 1, 1, "AX 리더", SUB, alignment="RIGHT", line_spacing_percent=120)
    D.cell(h, 1, 2, "권휘진 8134", SUB, **ctr)
    h.merge_cells(0, 0, 1, 0)

    body = dict(line_spacing_percent=140)
    def HD(x): return ("□ " + x, H, dict(spacing_before_pt=6, spacing_after_pt=2, **body))
    def OO(x): return (" ○ " + x, O, dict(spacing_before_pt=2, **body))
    def DD(x): return ("   - " + x, T, dict(indent_left_mm=5, first_line_indent_mm=-3, **body))

    def page(lines, pics):
        t = D.table(1, 2, [79, 21])
        cell = t.cell(0, 0)
        first = True
        for text, cs, fmt in lines:
            if first:
                D.cell(t, 0, 0, [(text, cs, fmt)], cs, TB)
                first = False
            else:
                D.para(text, cs, TB, target=cell, **fmt)
        rc = t.cell(0, 1)
        pc = D.pp(alignment="CENTER", line_spacing_percent=110, spacing_before_pt=4)
        k = 0
        for items, hmm, cap in pics:
            if k == 0:
                cell_pics(D, t, 0, 1, items, hmm, pc, gap="")
            else:
                p = rc.add_paragraph("", para_pr_id_ref=pc)
                for run in list(p.runs):
                    run.remove()
                from hx import _png, MM
                for path_, box in items:
                    data, (w, hh) = _png(path_, box)
                    it = D.d.add_image(data, "png")
                    H_ = round(hmm * MM); W_ = round(H_ * w / hh)
                    if W_ > round(34 * MM):
                        W_ = round(34 * MM); H_ = round(W_ * hh / w)
                    p.add_picture(it, width=W_, height=H_, treat_as_char=True)
            if cap: D.para(cap, CAPS, target=rc, alignment="CENTER", line_spacing_percent=110, spacing_after_pt=4)
            k += 1
        return t

    page([
        HD("추진배경"),
        OO("(노후화) 운영 견인전동기의 96%가 사용 30년 이상, 노후화에 따른 고장 교체 지속"),
        DD("운영 144대 중 **139대가 사용 30년 이상**, 평균 39년·최장 53년(1973년 제작) 경과"),
        DD("2026.3.23. 소사역 견인전동기 아크·연무 발생 ⇒ **승객하차·운행휴무**, 고장 징후 사전 식별 필요"),
        OO("(관리) 이력 기록부터 문서 검색, 수선의뢰 처리, 고장분류까지 수작업 처리"),
        DD("교체 이력을 담당자가 Excel에 일일이 기록·취합 ⇒ **반복 업무 발생**, 통계 활용 한계"),
        DD("정비문서 187쪽을 매번 직접 확인, 수선의뢰 처리, 고장 분류까지 수작업 ⇒ **업무 부담 가중**"),
        OO("(목적) 고장 이력 기반 위험등급 자동 판정으로 상태기반정비(CBM) 체계 구축"),
        DD("고장 이력을 분석 가능한 형태로 축적, 담당자 경험에 의존하던 판단을 **데이터 기반으로 전환**"),
        DD("위험등급 판정부터 수선의뢰 처리까지 전 과정을 하나의 플랫폼에서 수행"),
        HD("추진현황('26.9월부터 시범운영, 고도화 진행 중, 진행률 70%, 소요예산 70천원)"),
        OO("(플랫폼) 클라우드 서버·DB 기반 웹 플랫폼 구축, 견인전동기 관련 데이터를 단일 DB 통합"),
        DD("취부현황 171대(운영144대·예비27대), 고장이력 123건, 외부수선 47건 통합 ⇒ **전수 현황 일괄 조회**"),
        DD("데이터 등록 시 취부현황·위험등급·통계가 **동시에 갱신**, 조회·입력 권한 분리로 데이터 보호"),
        DD("데이터 8개 항목 자동 점검 ⇒ 관리 편성(111~116) 밖 이력 5건 검출·정리, 변경 이력 자동 기록"),
        OO("(위험도) 발생도(고장횟수)×심각도(고장유형7종) 매트릭스로 위험도 판정, 4단계 등급 자동 분류"),
        DD("절연파괴·소손 등 중대고장에 최고 심각도 적용, **긴급·주의·관찰·정상 4단계** 등급 자동 분류"),
        DD("견인전동기별 발생도·심각도 점수와 위험등급 산출 근거 제시, 정비 계획 수립 근거로 활용"),
    ], [
        ([(EXCEL, None)], 22, ""),
        ([(BOARD, None)], 22, "【기존 엑셀 ⇒ 개발 플랫폼】"),
        ([(DASH, None)], 22, "【전동기 171대 위험도 현황】"),
        ([(f"{IMG}/r_repair.png", PH)], 50, "【수선의뢰 등록 및 고장 분류】"),
    ])
    D.para("", T, page_break_before=True)
    page([
        OO("(분석·리포트) 고장 통계 분석 현황판 구축, 견인전동기별 이력 리포트 자동 생성"),
        DD("제작년도·제작사별 고장률, 편성별 위험도 분포, 위험도 상위 10대 견인전동기 자동 집계"),
        DD("리포트(PDF·워드·한글) 자동 생성, 현황 자료를 Excel·PDF로 추출 ⇒ **보고 자료로 즉시 활용**"),
        OO("(AI 어시스턴트) 검색증강생성(RAG) 기반 문서 검색·데이터 분석·수선의뢰 등록"),
        DD("정비문서 187쪽 기반 검색, 답변마다 **근거 문서·쪽수 표시** ⇒ 답변 신뢰성 확보"),
        DD("챗봇과 대화만으로 수선의뢰 등록, 누락 항목·고장 유형 확인 유도 ⇒ 고장 분류 일관성 강화"),
        DD("**음성 입력**: 말로 고장내용·질문 입력, 카카오톡 안 화면은 녹음 후 AI 받아쓰기 ⇒ 현장 즉시 기록"),
        HD("추진성과"),
        OO("(예방정비) 운영 견인전동기 144대 전수 판정, 긴급 2대·주의 31대 우선 관리대상 지정"),
        DD("이력 등록 시마다 재판정되어 관리대상 자동 갱신, 데이터 축적에 따른 신뢰도 향상"),
        DD("긴급·주의 등급 견인전동기 별도 관리, **고장 발생 전 선제 조치**로 운행 장애 예방"),
        OO("(업무효율) 챗봇 대화 한 번으로 접수·이력 기록·고장 분류·위험등급 갱신까지 일괄 처리"),
        DD("고장코드 판별 기준 보강(SOP-TM-001), 등록 시 확인 유도 질문으로 '기타' 고장분류 비율 **37.4% ⇒ 11.4%(26%p) 감소**"),
        DD("정비문서 수작업 검색·자료 집계 업무 축소, 정비 기준·절차 확인부터 자료 추출까지 한 번에 처리"),
        OO("(자체개발) AI 기반 바이브 코딩 활용 자체 구축, 유지보수·기능 개선까지 자체 수행"),
        DD("설계·개발·검증 전 과정 담당자 직접 수행 ⇒ **외부 개발·유지보수 용역비 0원**"),
        DD("현장 직원과 소통하며 요구사항 반영, **현장 의견 13건 즉시 업데이트**, 자동 시험 99건으로 판정 기준 검증"),
        HD("향후계획"),
        OO("('26년) 현장 사용성 평가 실시 및 기능 고도화"),
        DD("현업 직원 대상 사용성 평가(System Usability Scale) 실시 ⇒ 문서 검색 속도·UI·데이터 검증 기능 개선"),
        OO("('27년) 사내 업무망 이전 후 정식 운영, 타 장치로 확대 적용"),
        DD("사내 서버 설치·자료 반입 절차 협의 후 이전, 제동장치·SIV 등 장치별 이력 확보 후 **동일 시스템 확대 적용**"),
    ], [
        ([REPORT_M[0]], 40, ""),
        ([REPORT_M[1]], 40, "【전동기 위험도 산출 및 보고서】"),
        ([(f"{IMG}/r_chat.png", (0, 360, 780, 1600))], 50, "【AI 어시스턴트 응답 화면】"),
        ([(GRADE, None)], 22, "【매트릭스 판정 기준 및 등급별 조치】"),
        ([(f"{CAP}/pc_top10.png", None)], 14, "【위험도 TOP 10 TM】"),
    ])
    return D.save(path)


# =====================================================================
# (c) 2026년 하반기 중대재해 개선 제안 — 53년째 승객 태운 전동기
# =====================================================================
def safety(path):
    D = Doc(margins=(20, 20, 15, 15))
    TTL = D.cs(font="HY헤드라인M", size=18)
    SUBT = D.cs(font="HY헤드라인M", size=14)
    INF = D.cs(font="한컴돋움", size=10, letter_spacing=5)
    TYP = D.cs(font="한컴돋움", size=12, bold=True)
    H = D.cs(font="HY헤드라인M", size=15)
    O = D.cs(font="한컴돋움", size=13.5, bold=True, ratio=95, letter_spacing=-3)
    T = D.cs(font="휴먼명조", size=13, ratio=93, letter_spacing=-4)
    TB = D.cs(font="휴먼명조", size=13, ratio=93, letter_spacing=-4, bold=True)
    CAPS = D.cs(font="한컴돋움", size=11.5, ratio=95)
    CELL = D.cs(font="휴먼명조", size=12, ratio=95)
    CELLB = D.cs(font="한컴돋움", size=12.5, bold=True)

    h = D.table(4, 4, [30, 26, 28, 16])
    ctr = dict(alignment="CENTER", line_spacing_percent=120)
    D.cell(h, 0, 0, "53년째 승객 태운 전동기, 다음 사고는 언제인가", TTL, **ctr)
    D.cell(h, 2, 0, "-노후 견인전동기 위험도 자동판정으로 중대시민재해 예방-", SUBT, **ctr)
    D.cell(h, 3, 0, "소 속 명 : 서울교통공사", INF, **ctr)
    D.cell(h, 3, 1, "제출자 : 권휘진", INF, **ctr)
    D.cell(h, 3, 2, "연락처 : 010-6007-1488", INF, **ctr)
    for r, v in enumerate(["유형선택", "아이디어 □", "사    례 ■", "실행사례 □"]):
        D.cell(h, r, 3, v, TYP, **ctr)
    h.merge_cells(0, 0, 1, 2); h.merge_cells(2, 0, 2, 2)

    body = dict(line_spacing_percent=165)
    def HD(x): D.para("□ " + x, H, spacing_before_pt=10, spacing_after_pt=3, line_spacing_percent=150, keep_with_next=True)
    def OO(x): D.para(" ○ " + x, O, spacing_before_pt=3, **body)
    def DD(x): D.para("   - " + x, T, TB, indent_left_mm=6, first_line_indent_mm=-4, **body)

    HD("아이디어 · 사례 개요")
    OO("`26.3.23.소사역, 승객 탑승 중 아크·연기 발생 → 하차 및 열차 운행 중단")
    DD("원인은 전동차 구동 핵심장치인 견인전동기의 절연 파괴로 확인")
    DD("도시철도차량은 ‘중대재해처벌법’ 상 공중교통수단, 관리상 결함은 중대시민재해 요건")
    OO("`73년 제작 등 장기 사용 전동기 운행 중, 30년 이상 사용한 139대의 위험도 파악 곤란")
    DD("교체 123건 중 106건이 고장 발생 후 교체로, 사후 대응 구조가 고착된 상태")
    DD("제작년도만으로는 위험 전동기 판별이 어렵고, 교체 대상 선정이 담당자 경험에 의존")
    OO("고장 이력만으로 위험등급 자동 판정, 사고 발생 전 위험 전동기 사전 식별")
    DD("보유 171대 전수 판정으로 긴급 2대·주의 31대 특정→우선순위 정비 관리대상 지정")
    DD("소사역 사례와 동일한 절연파괴 사고를 사전에 차단하는 관리체계로 전환")
    D.para("", T, line_spacing_percent=60)
    f = D.table(2, 2, [45, 55])
    pc = D.pp(alignment="CENTER", line_spacing_percent=100)
    cell_pics(D, f, 0, 0, [(f"{FIG}/age_dist.png", None)], 40, pc)
    cell_pics(D, f, 0, 1, [(f"{FIG}/risk_flow.png", None)], 40, pc)
    D.cell(f, 1, 0, "운영 전동기 144대 사용연수 분포", CAPS, shade="#D6DCF0", **ctr)
    D.cell(f, 1, 1, "위험도 자동 판정 절차", CAPS, shade="#D6DCF0", **ctr)

    HD("아이디어 · 사례 내용")
    OO("발생도(고장횟수)×심각도(고장7종) Matrix 판정 → 긴급 2대·주의 31대 자동 도출")
    DD("절연 계통이 고장 교체의 55%를 차지, 절연파괴·소손에 최고 심각도 적용")
    DD("판정 기준·행동 요령과 전동기별 산출 근거를 화면 제공, 담당자 검토·검증 지원")
    OO("평균 고장간격(MTBF) 기반 정비 시점 예측 → 본선 고장 발생 전 선제 조치")
    DD("고장 간격 축소 시점을 놓치지 않고 검출 → 고장 발생 전 교체 대상으로 전환")
    DD("예상 정비 시점 경과 대상을 자동 표시, 점검 주기에서 벗어난 전동기 누락 방지")
    D.para("", T, line_spacing_percent=60)
    a = D.table(8, 2, [50, 50])
    D.cell(a, 0, 0, "As-Is", CELLB, shade="#D6DCF0", **ctr)
    D.cell(a, 0, 1, "To-Be", CELLB, shade="#D6DCF0", **ctr)
    cell_pics(D, a, 1, 0, [(EXCEL, None)], 45, pc)
    cell_pics(D, a, 1, 1, [(BOARD, None)], 45, pc)
    for r, (x, y) in enumerate([
        ("취부현황·교체이력 엑셀 분산 관리", "이력 등록 즉시 전체 전동기 위험도에 자동 반영"),
        ("제작년도 또는 담당자 경험에 의존", "발생도×심각도 매트릭스 기반 위험등급 자동 산출"),
        ("고장 발생 후 교체", "고장 이전 위험 전동기 사전 식별"),
        ("종이 지침서 직접 검색", "고장유형별 수선 절차 화면 연결"),
        ("사무실에서 기록지·엑셀 재입력", "현장 휴대폰에서 말로 입력, 즉시 등록"),
        ("입력 오류 확인 수단 없음", "데이터 8개 항목 자동 점검(오류 5건 검출)"),
    ], 2):
        D.cell(a, r, 0, x, CELL, **ctr); D.cell(a, r, 1, y, CELL, **ctr)

    OO("정비 문서 187쪽을 현황판·이력과 연계하여 고장유형별 조치 절차 즉시 확인")
    DD("검색증강생성(RAG)방식으로 답변마다 근거 문서·쪽수 표시, 임의 생성 가능성 최소화")
    DD("종이 지침서 휴대 없이 등록 화면·현황판·이력조회에서 수선 절차 바로 연결")
    OO("이력 등록 즉시 전체 전동기 재판정하고, 웹 접속만으로 누구나 최신 결과 확인")
    DD("수선의뢰 등록시 171대 전동기 상태·위험등급 자동 갱신, 별도 분석 작업 불필요")
    DD("별도 설치 없이 현장·사무실 어디서나 조회, 휴대폰 음성 입력으로 현장에서 바로 기록")
    OO("개발 용역 없이 바이브 코딩 기반 자체 구축 → 예산 투입 없이 즉시 운영")
    DD("설계·개발·검증 전 과정 담당자 직접 수행, 현장 요구사항 실시간 반영(13건 반영)")
    DD("부품 단위를 넘어 이력이 쌓이는 모든 대상에 그대로 적용, 타 부서 확산 가능")
    HD("서울교통공사 적용 현황")
    OO("서울교통공사 군자차량사업소에 적용하여 현재 시범운영 중")
    DD("전동기 171대(운영144대·예비품27대) 및 고장이력 123건을 대상으로 위험도 판정 시행")
    DD("담당자·현장 직원 공동 사용, 위험등급 확인 및 수선 이력 등록에 상시 활용")
    OO("판정 결과 도출된 긴급 2대·주의 31대 관리대상 지정, 상시 모니터링 진행")
    DD("이력 등록 시마다 재판정되어 관리대상 자동 갱신")
    DD("향후 검수 주기·교체 계획 수립 시 판정 결과를 우선순위 근거로 활용")
    HD("관련사진 · 자료")
    g = D.table(5, 2, [50, 50])
    cell_pics(D, g, 0, 0, [(DASH, None)], 47, pc)
    cell_pics(D, g, 0, 1, REPORT_M, 52, pc)
    cell_pics(D, g, 2, 0, CHAT_M, 52, pc)
    cell_pics(D, g, 2, 1, REPAIR_M, 52, pc)
    for (r, c), v in {(1, 0): "전동기 171대 위험도 현황", (1, 1): "전동기 위험도 산출 근거 및 보고서",
                      (3, 0): "AI 어시스턴트 응답 화면(현황 조회·문서 검색)",
                      (3, 1): "수선의뢰 등록·음성 입력·고장코드 자동 분류"}.items():
        D.cell(g, r, c, v, CAPS, shade="#D6DCF0", **ctr)
    D.cell(g, 4, 0, "접속링크: https://tm-cbm.lovable.app/ , 비밀번호: 1488", CAPS, **ctr)
    g.merge_cells(4, 0, 4, 1)
    HD("기대효과")
    OO("승객 탑승 중 아크·연기 사고 재발 위험 저감, 중대시민재해 발생 가능성 최소화")
    DD("사고 발생 후 대응 중심에서 사고 이전 위험을 사전 식별·조치하는 구조로 전환")
    DD("노후 전동기의 절연 계통 고장이 반복될 여지를 사전에 차단")
    OO("사전 판단에 근거한 정비 수행으로 긴급 작업 상황 최소화, 산업재해 위험 저감")
    DD("본선 고장 시 야간·주말 긴급 수선 불가피, 준비 부족 상태의 작업이 재해로 연결")
    DD("위험 전동기를 미리 파악하여 정규 정비 일정에 맞춰 교체 수행")
    OO("위험요인 파악을 담당자 개인 역량 의존 방식에서 조직 차원의 관리체계로 전환")
    DD("담당자 교체·인사 이동과 무관하게 동일 기준의 위험 판단 유지")
    DD("판정 근거와 조치 이력을 축적하여 안전보건 확보의무 이행 근거로 활용")
    OO("별도 예산 투입 없이 구축 가능한 구조로 타 사업장·타 기관 확산 가능")
    DD("별도 상용 솔루션 도입 없이 구축하여 추가 예산 부담을 최소화하고 즉시 적용 가능")
    DD("이력이 쌓이는 모든 대상에 적용, 부품·설비 종류와 무관하게 전개 가능")
    return D.save(path)


for name, fn in [("1_제안서_AI가_진단하고_답하는_전동기_통합관리_시스템", proposal),
                 ("2_AX리더_9팀_견인전동기_통합관리_시스템", axleader),
                 ("3_중대재해_개선제안_53년째_승객_태운_전동기", safety)]:
    print(name, fn(f"{OUT}/{name}.hwpx"))
