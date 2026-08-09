# TM-CBM 원본 데이터 마이그레이션 — 진행 상황 (2026-08-09 기준, 최신)

Lovable 프로젝트(tm-cbm, project_id `b386a24f-2d99-4a20-b824-3efe76ecfa76`,
workspace `GS8VAndim2d3OBu4TcTX` = "권휘진's Lovable", free 플랜)에
원본 데이터를 반영하는 작업 기록.

## 완료된 것
- `tm_assets` 171건, `repair_history` 127건 전부 DB에 삽입 완료
  (`mcp__Lovable__query_database`로 직접 실행 — AI 채팅 크레딧을 쓰지 않는 경로).
  111~116편성 각 24대 + 예비품 27건. 위치코드(M01~M24)는
  `CAR_PREFIX=[11,12,14,15,17,18]` + 편성 끝 2자리 공식(원본: `vs code ver.html`의
  `carLabel()` 함수)으로 정확한 실차호(예: `1711`)로 변환됨.
- 예비품 `9134547`의 제작년도/제조사를 원본 엑셀(`1호선 ADV 상세취부내역` 시트,
  같은 행의 다른 열 그룹)에서 찾아 **1991년/도시바**로 확정, DB 반영 완료.
- 단일 HTML 파일(`vs code ver.html`)에 "고장이력 10건/20건/전체 보기" 기능 추가 완료
  (Lovable의 `HistoryLimitControl`과 동일 동작, Playwright로 직접 브라우저 테스트해서 검증함).

## 안 된 것 (크레딧 필요 — AI 에이전트만 할 수 있는 작업)

### 1. src/routes/index.tsx 차호 표시 되돌리기
지금 `{car}차`로 되어 있는데, 실제 데이터의 car값(`1711` 등)은 순수 숫자라
`{car}호차`로 되돌려야 "1711호차"로 정상 표시됨. `query_database`는 DB 전용이라
코드 파일은 못 고침 — `send_message`(AI 에이전트)가 필요하고 지금 크레딧 소진 상태.

```
src/routes/index.tsx에서 차호 헤더가 {car}차 로 되어 있는데,
실제 데이터의 car값(1711 등)은 순수 숫자라 "호"가 없어.
{car}차 를 {car}호차 로 고쳐줘.
```

## 사용자 확인 필요 (다음에 답 주시면 진행)

### RP-0082 (repair_history에서 의도적으로 제외한 1건)
113편성 1413-TM3, 취거 88TWDH114(1988,현대중공업) → 부착 88091-73(1989,대우중공업),
FC05/심각도7/위험점수100/고장성Y, 세부내용 "정류자 F/O, 패임, 홀더양호".
원본 엑셀에도 날짜가 비어있음. 다만 관련 수선집행특례내역 시트에서
부착품(88091-73)이 **"23.07.03"**에 수선완료·취부중으로 기록된 걸 찾음 —
**2023-07-03 전후로 추정**되나 확정은 아님. 정확한 날짜 확인되면 아래로 추가:
```sql
INSERT INTO repair_history (repair_date, formation, car, location, removed_serial, removed_year, removed_maker, installed_serial, installed_year, installed_maker, fault_type, fault_code, severity, risk_score, is_fault, detail, removed_condition, review) VALUES
('[확인된 날짜]', '113', '1413', '113-1413-TM3', '88TWDH114', 1988, '현대중공업', '88091-73', 1989, '대우중공업', '절연파괴·소손·F/O', 'FC05', 7, 100, 'Y', '정류자 F/O, 패임, 홀더양호', '확인필요', '확인필요');
```

### 시리얼 `???` (111편성 1511-TM4)
원본 엑셀(`1호선 ADV 상세취부내역` 시트, 111편성 그룹 16번째 행)에도 `???`로
되어 있음을 확인 — 추출 오류가 아니라 **원본 자체의 미기록값**. 실물 확인 필요.

### 외부수선이력 반영 (스키마 매핑 방법 논의 필요)
사용자가 스크린샷으로 올린 "24년도 수선반출 내역" 등 시트는 편성/차호/위치 정보가
없어서 지금 `repair_history` 스키마에 그대로 안 들어감. 매핑 방식을 사용자와
논의 후 반영.

## 아직 미착수
- 전체 기능 QA/버그 수정 (챗봇, 고장추세 배지, 대시보드 그래프 실제 브라우저 테스트)
- 엑셀 파일 ↔ DB 양방향 연동 + 비밀번호 보호 기능 (참고: `vs code ver.html`에는
  이미 로컬 파일시스템 연결 기능이 있음 — `btnXlsxLink`, `showOpenFilePicker`,
  파일 변경 감지 후 자동 갱신, 비밀번호 게이트(`requireAuth`). Lovable 앱에 같은
  걸 원하시면 이 로직을 참고해서 요청하면 될 듯)
- 사내 폐쇄망 이전 (GitHub export + 백엔드를 사내 PostgreSQL로 교체)

## 파일 설명
- `raw_original.json` — 사용자가 제공한 원본 데이터 (master 171건 + repl 128건, 변환 전).
- `convert_fixed.py` — `raw_original.json` → 앱 스키마로 변환하는 스크립트 (CAR_PREFIX 공식 포함).
- `fixed_master.json` / `fixed_repl.json` — 변환된 결과 (9134547 수정 반영됨, DB와 동일).
- `repair_history_migration.sql` — 실제 DB에 삽입 완료된 SQL (127건, RP-0082 제외). 재실행 불필요.
