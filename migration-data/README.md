# TM-CBM 원본 데이터 마이그레이션 — 진행 상황 (2026-08-09 기준)

이 폴더는 Lovable 프로젝트(tm-cbm, project_id `b386a24f-2d99-4a20-b824-3efe76ecfa76`,
workspace `GS8VAndim2d3OBu4TcTX` = "권휘진's Lovable", free 플랜)에 원본 데이터를
반영하던 작업을 크레딧 소진으로 중단한 상태의 백업입니다.

## 완료된 것
- `tm_assets` 테이블에 마스터 171건 삽입 완료 (111~116편성 각 24대 + 예비품 27건).
  `raw_original.json`의 위치코드(M01~M24)를 `CAR_PREFIX=[11,12,14,15,17,18]` + 편성 끝 2자리
  공식(원본: `vs code ver.html`의 `carLabel()` 함수)으로 정확히 변환한 값.

## 안 된 것 (내일 할 일)

### 1. repair_history 127건 삽입
`repair_history_migration.sql` 파일 내용을 그대로 Lovable AI 에이전트에게
(`mcp__Lovable__send_message`, project_id `b386a24f-2d99-4a20-b824-3efe76ecfa76`)
"재해석하지 말고 정확히 그대로 실행해줘"라고 보내면 됨. 6개의 INSERT 문으로 나뉘어 있음.

원본 128건 중 **RP-0082 1건은 의도적으로 제외**됨 (113편성 1413-TM3, 취거 88TWDH114 →
부착 88091-73, 원본에 일자가 `"None"` 문자열로 비어있어서 NOT NULL 컬럼에 넣을 수 없었음).
사용자에게 정확한 날짜를 확인한 후 별도 INSERT 필요.

### 2. src/routes/index.tsx 차호 표시 되돌리기
지금 `{car}차`로 되어 있는데(가짜 mock 데이터가 차호에 "호"를 이미 포함하고 있던 시절 고친 것),
실제 데이터의 car값(`1711` 등)은 순수 숫자라 `{car}호차`로 되돌려야 "1711호차"로 정상 표시됨.

### 3. 원본 데이터 자체의 미상값 확인 (사용자 확인 필요)
- 시리얼 `???` (111편성 1511-TM4) — 원본 파일 자체에 미상 표시.
- 예비품 시리얼 `9134547`의 제작년도/제조사가 원본에 `?`로 되어 있어 NULL 처리함.

### 4. 외부수선이력 반영 (스키마 매핑 방법 논의 필요)
사용자가 스크린샷으로 올린 "24년도 수선반출 내역" 등 시트는 편성/차호/위치 정보가 없어서
지금 `repair_history` 스키마에 그대로 안 들어감. 매핑 방식을 사용자와 논의 후 반영.

### 5. 전체 기능 QA/버그 수정 (아직 미착수)
챗봇 대화형 등록, 고장추세 배지, 대시보드 그래프를 실제 브라우저로 하나씩 테스트.

### 6. 단일 HTML 파일(`vs code ver.html`)에 "고장이력 10/20/전체 보기" 기능 반영
Lovable 앱에만 있고 GitHub의 단일 파일에는 아직 미반영.

## 파일 설명
- `raw_original.json` — 사용자가 제공한 원본 데이터 (master 171건 + repl 128건, 변환 전).
- `convert_fixed.py` — `raw_original.json` → 앱 스키마로 변환하는 스크립트 (CAR_PREFIX 공식 포함).
- `fixed_master.json` / `fixed_repl.json` — 변환된 결과 (`convert_fixed.py`의 출력).
- `repair_history_migration.sql` — `fixed_repl.json`을 SQL INSERT 문으로 변환한 것 (127건, RP-0082 제외).
