import re, sys, shutil, zipfile, os, html
SRC = sys.argv[1]; OUT = sys.argv[2]; X = sys.argv[3]
s = open(os.path.join(X, 'Contents/section0.xml'), encoding='utf-8').read()

P_ATTR = 'id="2147483648" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"'
def esc(t): return html.escape(t, quote=False)
def runs(text, normal='11', bold='15'):
    # **굵게** 구간은 bold 글자모양
    out = []
    for i, part in enumerate(re.split(r'\*\*', text)):
        if part: out.append(f'<hp:run charPrIDRef="{bold if i % 2 else normal}"><hp:t>{esc(part)}</hp:t></hp:run>')
    return ''.join(out)
def O(text, para='28'):  # ㅇ 한컴돋움 15 진하게
    return f'<hp:p paraPrIDRef="{para}" {P_ATTR}><hp:run charPrIDRef="12"><hp:t> ㅇ {esc(text)}</hp:t></hp:run></hp:p>'
def D(text):  # - 휴먼명조 14 (중요 부분 진하게)
    return f'<hp:p paraPrIDRef="29" {P_ATTR}>{runs("   - " + text)}</hp:p>'

# ---------- 내용 (실제 앱·DB 값만 사용) ----------
B1 = [
  O('추진배경'),
  D('1호선 111~116편성 견인전동기(TM) **운영 144대·예비품 27대**의 고장·교체 이력 **123건**(2021.2~2026.4)이 엑셀·수기로 흩어져, 반복 고장 위치·노후 TM 고장 경향을 사람이 일일이 찾아야 했음'),
  D('고장 원인 분류가 사람마다 달라 **"기타" 비율 43%**(실제 고장 106건 중 46건) → 원인별 대책 수립이 어려움'),
  O('추진목적'),
  D('고장 이력을 데이터로 모아 **TM마다 위험 등급을 자동 산출**하고, 현장 수선의뢰부터 외주수선 대상 선정까지 **한 화면에서 처리** → 상태기반 정비(CBM) 전환 기반 마련'),
  O('개선점(기존 → 개선)'),
  D('엑셀 조회 → **휴대폰에서 편성·호차·위치별 TM 상태 즉시 확인**(취부 현황판)'),
  D('수기 분류 → 고장 내용만 적으면(말로도 가능) **지침서(SOP-TM-001) 기준 고장코드 자동 분류**'),
  D('개인 경험 판단 → **발생도×심각도(FMEA 방식) 위험 등급**과 판단 근거 자동 제시'),
]
B2 = [
  O('결과물 형태 : 웹 앱(휴대폰·PC 겸용, 설치 불필요)'),
  D('구성 : 취부 현황판 · TM 리포트 · 수선의뢰 · 고장 이력(고장 이력 → 외부수선 발송 → 외주수선 대상) · 대시보드 · 문서 · AI 챗봇'),
  D('주소 : tm-cbm.lovable.app (현장 접속 코드, 저장 시 담당자 비밀번호 확인)'),
  O('주요 기능'),
  D('**위험 등급 자동 산출** : 최근 5년 고장 횟수(발생도) × 최고 심각도 → 긴급·주의·관찰·정상, 등급 기준은 화면에서 조정'),
  D('**현장 수선의뢰** : TM 선택 + 고장 내용 입력(음성 입력 지원) → 고장코드 자동 추천, 등록 즉시 취부 현황 자동 갱신'),
  D('**AI 챗봇** : "오늘 뭐부터 점검해야 돼?" 등 현황 질문, 정비지침서·수선사양서·표준작업절차서 검색 답변(출처 쪽수 표시), 대화로 수선의뢰 등록'),
  D('**대시보드** : 편성 건강 현황판, 위험도 상위 TM, 반복 고장 위치, 예비품 여유(가용 22대, 약 29개월분), 고장 추이'),
  D('**데이터 관리** : 데이터 점검·정합성 검토, 변경 이력(감사기록), 스냅샷 백업, 현장 의견 접수·반영 표시'),
  O('데이터 정비 성과'),
  D('지침서 기준으로 고장 분류 재정리 → **"기타" 46건 → 14건(43% → 13%)**, 다른 노선 이력 5건 제거'),
  D('현재 운영 TM 144대 등급 : **긴급 2 · 주의 31 · 관찰 3 · 정상 108대**, 반복 고장 위치 1곳'),
]
B3_dept = [
  O('적용 희망부서 : [                    ]  ※ 확인 필요'),
  D('적용 대상 : 1호선 111~116편성 TM 운영 144대 + 예비품 27대'),
  D('사용 방법 : 검수원·정비원은 휴대폰으로 현황 확인·수선의뢰, 담당자는 PC로 대시보드·데이터 관리'),
]
B3_effect = [
  D('**정비 우선순위 판단 표준화** : 긴급·주의 TM과 반복 고장 위치를 매일 자동 제시'),
  D('**이력 관리 일원화** : 수선의뢰 1회 입력으로 고장 이력·취부 현황·외부수선 흐름이 함께 갱신'),
  D('**원인 분석 정확도 향상** : 고장코드 자동 분류로 "기타" 감소 → 유형별 대책 수립'),
  D('**확장성** : 장치 확장 설정으로 다른 부품(장치)에도 같은 방식 적용 가능'),
]
TABLE = [
  ['구분', '필요사항', '비고'],
  ['운영 환경', '사내 휴대폰·PC 접속 허용, 사내망 이전 시 서버 1대', '현재 외부 클라우드'],
  ['업무 연계', '수선의뢰·고장 이력 입력을 앱으로 일원화', '[  ]'],
]

# ---------- 원본 구조에 끼워 넣기 ----------
paras = [m for m in re.finditer(r'<hp:p [^>]*>.*?</hp:p>', s, re.S)]
def find(txt):
    for m in paras:
        if txt in m.group(0): return m
    raise SystemExit('not found: ' + txt)
h1, h2, h3 = find('□ 추진개요'), find('□ 추진성과'), find('□ 실증계획')
eff, need = find(' ㅇ 기대효과'), find(' ㅇ 실증 시 필요사항')
# 머리말 다음 빈 줄(paraPr 26) 위치
sp2 = s.rfind('<hp:p ', 0, h2.start()); sp3 = s.rfind('<hp:p ', 0, h3.start())
out = (s[:h1.end()] + ''.join(B1) + s[sp2:h2.end()] + ''.join(B2) + s[sp3:h3.end()]
       + ''.join(B3_dept) + eff.group(0) + ''.join(B3_effect) + s[need.start():])

# 과제명·수행팀 칸
out, n = re.subn(r'(<hp:p [^>]*paraPrIDRef="24"[^>]*>)<hp:run charPrIDRef="11"/>',
                 r'\1<hp:run charPrIDRef="11"><hp:t>견인전동기(TM) 상태기반 진단·수선의뢰 관리시스템(TM-CBM)</hp:t></hp:run>', out, count=1)
assert n == 1, '과제명 칸'
out = re.sub(r'(<hp:run charPrIDRef="11"><hp:t>)팀(</hp:t></hp:run>)', r'\1[        ]팀\2', out, count=1)

# 필요사항 표 9칸
tstart = out.find('<hp:tbl id="1183004026"'); tend = out.find('</hp:tbl>', tstart)
tbl = out[tstart:tend]
cells = iter([(r, c, TABLE[r][c]) for r in range(3) for c in range(3)])
def fill(m):
    r, c, t = next(cells)
    return f'<hp:run charPrIDRef="{m.group(1)}"><hp:t>{esc(t)}</hp:t></hp:run>'
tbl2, n = re.subn(r'<hp:run charPrIDRef="(18|19)"/>', fill, tbl)
assert n == 9, n
out = out[:tstart] + tbl2 + out[tend:]
open(os.path.join(X, 'Contents/section0.xml'), 'w', encoding='utf-8').write(out)

# 미리보기 글자도 새 내용으로
txt = re.sub(r'<[^>]+>', '', re.sub(r'</hp:p>', '\n', out))
open(os.path.join(X, 'Preview/PrvText.txt'), 'w', encoding='utf-8').write(html.unescape(txt)[:1000])

# 다시 묶기: mimetype은 첫 번째·무압축
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(OUT, 'w') as zout:
    for info in zin.infolist():
        data = open(os.path.join(X, info.filename), 'rb').read()
        zout.writestr(info, data, compress_type=zipfile.ZIP_STORED if info.filename == 'mimetype' else zipfile.ZIP_DEFLATED)
print('ok', OUT)
