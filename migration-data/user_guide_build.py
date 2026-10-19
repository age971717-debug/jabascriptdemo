"""TM-CBM 현장 사용 가이드(정비원용, 3쪽) — '이럴 땐 이렇게' 형식. 문구는 앱 화면 그대로, 그림은 실제 화면."""
import sys
from hx import Doc, cell_pics

IMG, CAP, OUT = sys.argv[1:4]
PH = (0, 0, 780, 1240)
D = Doc(margins=(16, 16, 14, 12))
TITLE = D.cs(font="HY헤드라인M", size=21, color="#1F3864")
SUB = D.cs(font="한컴돋움", size=11, color="#404040")
H = D.cs(font="HY헤드라인M", size=14, color="#1F3864")
CT = D.cs(font="한컴돋움", size=12.5, bold=True, color="#FFFFFF")
STEP = D.cs(font="한컴돋움", size=10)
STEPB = D.cs(font="한컴돋움", size=10, bold=True)
TIP = D.cs(font="한컴돋움", size=9.5, color="#1F4E79")
TIPB = D.cs(font="한컴돋움", size=9.5, bold=True, color="#1F4E79")
CELL = D.cs(font="한컴돋움", size=10.5)
CELLB = D.cs(font="한컴돋움", size=10.5, bold=True)
SMALL = D.cs(font="한컴돋움", size=9.5)
WHITE = D.cs(font="한컴돋움", size=10.5, bold=True, color="#FFFFFF")
NAVY = "#1F3864"; HEAD = "#DFE6F7"; TIPBG = "#EEF3FB"

ctr = dict(alignment="CENTER", line_spacing_percent=125)
lft = dict(alignment="LEFT", line_spacing_percent=140)
def HD(t, page_break=False):
    D.para(t, H, spacing_before_pt=8, spacing_after_pt=4, line_spacing_percent=130,
           bottom_border=True, border_color="#1F3864", page_break_before=page_break, keep_with_next=True)
def gap(pt=4): D.para("", SMALL, line_spacing_percent=60, spacing_after_pt=pt)

# ===================== 1쪽 : 시작하기 =====================
D.para("TM-CBM 현장 사용 가이드", TITLE, alignment="CENTER", spacing_after_pt=2)
D.para("견인전동기(TM) 진단·수선의뢰 관리 앱 · 정비원용", SUB, alignment="CENTER", spacing_after_pt=8)

HD("1. 처음 한 번만 하면 됩니다")
t = D.table(2, 3, [1, 1, 1])
for c, (title, body) in enumerate([
    ("① 주소 누르기", ["휴대폰 인터넷(크롬·삼성 인터넷)이나", "카카오톡으로 받은 주소를 누릅니다.", "**tm-cbm.lovable.app**"]),
    ("② 접근 비밀번호", ["처음 한 번만 입력합니다.", "같은 휴대폰에서는 다시 묻지 않습니다.", "(비밀번호는 담당자에게 문의)"]),
    ("③ 홈 화면에 추가(선택)", ["브라우저 메뉴 ⇒ '홈 화면에 추가'", "다음부터는 앱처럼", "아이콘을 눌러 바로 엽니다."]),
]):
    D.cell(t, 0, c, title, CT, shade=NAVY, **ctr)
    D.cell(t, 1, c, body, CELL, CELLB, **ctr)
gap()

HD("2. 첫 화면(현황판) 보는 법")
t = D.table(1, 2, [34, 66])
cell_pics(D, t, 0, 0, [(f"{IMG}/r_board.png", (0, 0, 780, 1280))], 74, D.pp(alignment="CENTER", line_spacing_percent=100))
D.cell(t, 0, 1, [
    "① **등급 버튼** : 긴급·주의 등을 누르면 그 등급 TM만 남습니다.",
    "② **검색칸** : 시리얼 앞자리 일부만 넣어도 찾습니다.",
    "③ **TM 칸** : 편성 ⇒ 호차 ⇒ TM1~4 순서, 테두리 색이 등급입니다. 누르면 상세가 열립니다.",
    "④ **말풍선(챗봇)** : 말이나 글로 묻고 답을 받습니다.",
    "⑤ **아래 탭** : 현황판·리포트·수선의뢰·이력·대시보드로 이동합니다.",
    "※ 위쪽 **[데이터 내보내기]** 로 엑셀 파일을 받을 수 있습니다.",
], STEP, STEPB, alignment="LEFT", line_spacing_percent=165)
gap()

HD("3. 아래 탭 5개만 알면 됩니다")
t = D.table(3, 5, [1, 1, 1, 1, 1])
pc = D.pp(alignment="CENTER", line_spacing_percent=100)
cell_pics(D, t, 0, 0, [(f"{IMG}/r_board.png", (0, 1170, 780, 1280))], 7.5, pc)
t.merge_cells(0, 0, 0, 4)
for c, (name, what) in enumerate([
    ("현황판", ["TM 전체를 등급 색으로", "빨간 숫자 = 긴급 TM 수"]),
    ("리포트", ["TM 한 대의 진단서", "고장 이력·PDF·QR"]),
    ("수선의뢰", ["TM 교체 기록", "말로 입력 가능"]),
    ("이력", ["고장·외부수선 기록", "주황 숫자 = 반복 고장"]),
    ("대시보드", ["오늘 확인할 것", "고장 추이·통계"]),
]):
    D.cell(t, 1, c, name, CELLB, shade=HEAD, **ctr)
    D.cell(t, 2, c, what, SMALL, **ctr)
D.para("※ 오른쪽 아래 **말풍선 = 챗봇**(말로 묻고 답 받기), 오른쪽 위 **현장 의견** = 불편한 점 보내기", TIP, TIPB,
       spacing_before_pt=4, line_spacing_percent=140)
gap()

HD("4. 등급 색깔의 뜻")
t = D.table(7, 3, [18, 40, 42])
for c, v in enumerate(["등급", "뜻", "할 일"]):
    D.cell(t, 0, c, v, CELLB, shade=HEAD, **ctr)
rows = [("긴급", "#C00000", "고장이 잦고 심각했던 TM", "**지금 바로 점검·교체 검토**"),
        ("주의", "#ED7D31", "고장 이력이 있어 위험이 큰 TM", "**다음 정비 때 우선 확인**"),
        ("관찰", "#BF9000", "특이사항은 있으나 당장 조치 불필요", "고장 추세만 지켜봄"),
        ("정상", "#548235", "최근 5년 문제 이력이 거의 없음", "정기 점검 유지"),
        ("예비품", "#2E75B6", "차량에서 떼어 보관 중인 TM", "-"),
        ("불용대기", "#7F7F7F", "폐기를 기다리는 TM", "-")]
for r, (g, col, mean, todo) in enumerate(rows, 1):
    D.cell(t, r, 0, g, WHITE, shade=col, **ctr)
    D.cell(t, r, 1, mean, CELL, **lft)
    D.cell(t, r, 2, todo, CELL, CELLB, **lft)
D.para("※ 등급은 사람이 정하지 않습니다. 최근 5년 **고장 횟수**와 **가장 심했던 고장**으로 자동 계산합니다. "
       "TM을 누르면 '위험도 산출 근거'에서 계산 과정을 볼 수 있습니다.", TIP, TIPB, spacing_before_pt=4, line_spacing_percent=140)

# ===================== 2쪽 : 이럴 땐 이렇게 =====================
HD("5. 이럴 땐 이렇게", page_break=True)
CARDS = [
    ("A. 오늘 뭐부터 점검하지?", (f"{IMG}/r_chat.png", (0, 360, 780, 1600)), [
        "1) **현황판** 위쪽 **[긴급]** 버튼 ⇒ 긴급 TM만 남습니다.",
        "2) 또는 오른쪽 아래 **말풍선** ⇒ **'오늘 뭐부터 점검해야 돼?'** 누르기",
        "3) 긴급 TM과 이유(최근 5년 고장 횟수·평균 고장 간격)가 나옵니다."],
     "등급이 이상해 보이면 TM을 눌러 '위험도 산출 근거'를 확인하세요."),
    ("B. 이 TM 상태가 궁금해", (f"{IMG}/m_detail.png", PH), [
        "1) 현황판 검색칸에 **시리얼 앞자리 일부**만 입력(예: 88091)",
        "2) TM 칸을 누르면 **상세**(위치·제작년도·등급 근거)가 열립니다.",
        "3) **[TM 리포트 열기]** ⇒ 고장 이력 전체, PDF·한글 파일 받기"],
     "TM에 QR 라벨이 붙어 있으면 휴대폰 카메라로 찍기만 해도 리포트가 열립니다."),
    ("C. TM을 교체했어 (수선의뢰)", (f"{IMG}/r_repair.png", PH), [
        "1) 아래 탭 **[수선의뢰]** ⇒ 교체일자·편성·**취거 TM**(떼어낸 TM) 선택",
        "2) 세부 고장내용 옆 **마이크**를 누르고 말하기(예: '주행 중 절연파괴 발생')",
        "3) **자동 분류된 고장코드** 확인(다르면 직접 바꾸기) ⇒ 부착 TM 고르고 **저장**",
        "4) 처음 저장할 때만 **담당자 비밀번호** 확인"],
     "저장하면 떼어낸 TM은 예비품, 부착한 TM은 운영중으로 자동으로 바뀝니다. 시리얼 '다시'는 '-'로 적힙니다."),
    ("D. 정비 기준이 궁금해", (f"{IMG}/m_chat.png", PH), [
        "1) 오른쪽 아래 **말풍선** ⇒ 질문 입력 또는 마이크로 말하기",
        "2) 예: '정류자 삭정 기준이 뭐야?', '계자코일 절연저항 기준'",
        "3) 답 아래 **근거 문서·쪽수**를 확인합니다."],
     "정비지침서·수선사양서·표준작업절차서에 없는 내용은 지어내지 않고 '확인되지 않습니다'라고 답합니다."),
    ("E. 불편한 점이 있어", (f"{IMG}/m_feedback.png", PH), [
        "1) 오른쪽 위 **[현장 의견]** ⇒ 불편 / 개선 / 오류 중 고르기",
        "2) 내용 입력(마이크로 말해도 됨) ⇒ 보내기",
        "3) 보고 있던 화면과 TM이 함께 저장되어 담당자가 바로 확인합니다."],
     "반영된 내용은 도움말 '업데이트 내역'에서 볼 수 있습니다."),
]
for i, (title, (path, box), steps, tip) in enumerate(CARDS):
    t = D.table(3, 2, [17, 83])
    D.cell(t, 0, 0, title, CT, shade=NAVY, **lft)
    t.merge_cells(0, 0, 0, 1)
    cell_pics(D, t, 1, 0, [(path, box)], 32, pc)
    t.merge_cells(1, 0, 2, 0)
    D.cell(t, 1, 1, steps, STEP, STEPB, **dict(alignment="LEFT", line_spacing_percent=135))
    D.cell(t, 2, 1, "TIP  " + tip, TIP, TIPB, shade=TIPBG, **dict(alignment="LEFT", line_spacing_percent=125))
    gap(2)

# ===================== 3쪽 : 알아 두면 좋은 것 =====================
HD("6. 말로 입력할 때 이렇게 말하면 정확해요")
D.para("고장 내용에 아래 단어가 들어가면 고장코드가 자동으로 정확하게 분류됩니다(지침서 SOP-TM-001 기준).", STEP,
       line_spacing_percent=140, spacing_after_pt=3, keep_with_next=True)
t = D.table(8, 3, [12, 30, 58])
for c, v in enumerate(["코드", "고장 유형", "이런 단어를 넣어 말하세요"]):
    D.cell(t, 0, c, v, CELLB, shade=HEAD, **ctr)
for r, (code, kind, kw) in enumerate([
    ("FC05", "절연파괴·소손·F/O", "절연파괴, 접지소손, 소손, 화재, 발화, F/O(에프오), 플래시오버, 전식, 아크"),
    ("FC04", "리드선 절손·열화", "리드선절손, 리드선열화, 단선"),
    ("FC03", "브러쉬홀더·코일 단락", "홀더열화, 절손, 계자코일단락, 코일단락, 권선단락, 권선소손"),
    ("FC02", "절연저항·물유입", "절연저항불량, 물유입, 침수, 세이프티너트, 냉각팬불량, 과열"),
    ("FC01", "정류자·브러쉬 경미", "그을림, 마모, 편마모, 스파크, 베어링, 소음, 진동"),
    ("FC00", "정기·순환교체", "정기, 순환, 예방, 중정비"),
    ("FC99", "기타", "위 단어가 없을 때(본 것을 구체적으로 말할수록 정확)"),
], 1):
    D.cell(t, r, 0, code, CELLB, **ctr)
    D.cell(t, r, 1, kind, CELL, **lft)
    D.cell(t, r, 2, kw, CELL, **lft)
gap()

HD("7. 마이크가 안 될 때")
t = D.table(4, 3, [30, 38, 32])
for c, v in enumerate(["상황", "앱이 하는 일", "이렇게 하세요"]):
    D.cell(t, 0, c, v, CELLB, shade=HEAD, **ctr)
for r, row in enumerate([
    ("크롬·삼성 인터넷·사파리", "말하는 즉시 글자로 받아 적음", "마이크 누르고 말하기"),
    ("카카오톡 안에서 연 화면", "녹음(빨간 네모) 후 AI가 받아 적음(최대 30초)", "말한 뒤 한 번 더 눌러 끝내기"),
    ("마이크 권한이 막힘", "입력칸을 열고 안내", "휴대폰 키보드의 마이크 버튼 사용"),
], 1):
    for c, v in enumerate(row):
        D.cell(t, r, c, v, CELL, **(ctr if c != 1 else lft))
gap()

HD("8. 자주 묻는 질문")
t = D.table(6, 2, [28, 72])
for c, v in enumerate(["질문", "답"]):
    D.cell(t, 0, c, v, CELLB, shade=HEAD, **ctr)
for r, (qq, aa) in enumerate([
    ("화면이 예전 그대로예요", "화면을 아래로 당기거나 새로고침하면 최신 화면이 보입니다."),
    ("저장이 안 돼요", "저장할 때 담당자 비밀번호를 확인합니다. 비밀번호는 담당자에게 문의하세요."),
    ("잘못 입력했어요", "담당자에게 알려 주세요. 담당자가 고장 이력에서 고치고, 고친 내용은 변경 이력에 남습니다."),
    ("등급이 이상해요", "TM 상세의 '위험도 산출 근거'를 확인하고, 이상하면 '현장 의견'으로 알려 주세요."),
    ("엑셀로 받고 싶어요", "현황판 위 '데이터 내보내기'로 TM·고장 이력·외부수선 이력을 엑셀로 받습니다."),
], 1):
    D.cell(t, r, 0, qq, CELLB, **lft)
    D.cell(t, r, 1, aa, CELL, **lft)
gap()

HD("9. 담당자용 (PC 왼쪽 메뉴)")
t = D.table(5, 2, [24, 76])
for r, (m, what) in enumerate([
    ("대시보드", "현황 탭(오늘 확인할 것·조치 필요·차량 건강·예방정비 임박) / 분석 탭(고장유형·제조사·제작년도별). '위젯 선택'으로 보이는 항목 조정"),
    ("고장 이력", "고장 이력 ⇒ 외부수선 발송 ⇒ 외주수선 대상 순서. 줄을 눌러 수정(사유 기록)"),
    ("데이터 관리", "백업·되돌리기, 데이터 점검(8개 항목), 변경 이력, 현장 의견 처리(접수·반영·보류)"),
    ("등급 기준", "등급 계산 방법 확인, 기준값 조정 시 모든 화면·챗봇·리포트에 바로 반영"),
    ("장치 확장", "제동장치 등 다른 장치를 같은 방식으로 관리하기 위한 템플릿 등록"),
]):
    D.cell(t, r, 0, m, CELLB, shade=HEAD, **ctr)
    D.cell(t, r, 1, what, CELL, **lft)
D.para("더 궁금한 점은 챗봇에게 묻거나 오른쪽 위 '현장 의견'으로 남겨 주세요.", TIP, alignment="CENTER", spacing_before_pt=8)

print(D.save(OUT))
