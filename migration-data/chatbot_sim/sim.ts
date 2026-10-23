// 정비원 질문 대량 시뮬레이션 — 실제 데이터 사본, AI·DB 호출 없음.
// 질문 틀 × 실제 편성·차호·시리얼·등급 × 말투 변형(띄어쓰기 없음·존댓말·물음표·음성식)으로 만들고
// 기대 경로와 (필요하면) 답에 꼭 있어야 할 말을 자동으로 확인한다.
import { answerQuestion } from "/home/user/tm-cbm/src/lib/chatbot";
import { routeQuestion, normalizeQuestion, type ChatRoute } from "/home/user/tm-cbm/src/lib/chat-router";
import { computeRisk, parseLocation } from "/home/user/tm-cbm/src/lib/tm";

const D = await Bun.file(
  "/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad/realdata.json",
).json();
const A = D.assets as any[];
const H = D.history as any[];
const E = D.ext as any[];

type Case = { cat: string; q: string; ok: ChatRoute[]; must?: (t: string) => boolean; mustText?: string };
const cases: Case[] = [];
const add = (cat: string, ok: ChatRoute[] | ChatRoute, qs: string[], must?: (t: string) => boolean, mustText?: string) => {
  for (const q of qs) cases.push({ cat, q, ok: Array.isArray(ok) ? ok : [ok], must, mustText });
};

// --- 실제 데이터에서 뽑은 대상 ---
const op = A.filter((a) => a.status === "운영중" && a.location);
const pick = <T,>(arr: T[], n: number, seed = 7) => {
  const out: T[] = [];
  let x = seed;
  for (let i = 0; i < n && arr.length; i++) {
    x = (x * 1103515245 + 12345) % 2147483648;
    out.push(arr[x % arr.length]!);
  }
  return out;
};
const withGrade = op.map((a) => ({ a, g: computeRisk(a, H).grade as string }));
const serials = [...new Set([...pick(op, 14).map((a) => a.serial), "88091-48", "98TWDH393", "92TWDH076", "296640-10"])];
const forms = ["111", "112", "113", "114", "115", "116"];
const locs = pick(op, 12, 3).map((a) => ({ a, p: parseLocation(a.location)! }));
const gradeOf = (s: string) => withGrade.find((x) => x.a.serial === s)?.g ?? "정상";
const SER = (s: string) => (t: string) => t.includes(s);

// 1) 시리얼 조회
for (const s of serials) {
  add("시리얼", ["시리얼조회", "등급이유"], [`${s}`, `${s} 상태`, `${s} 어때`, `${s} 상태 좀 알려줘`, `${s}는?`, `${s} 정보`, `${s} 조회`, `${s} 확인해줘`], SER(s));
  add("시리얼-위치", ["시리얼조회"], [`${s} 어디 달려있어?`, `${s} 어디에 있어`, `${s} 위치`], SER(s));
  add("시리얼-연식", ["시리얼조회"], [`${s} 몇년식이야`, `${s} 제조사 어디야`, `${s} 언제 만든 거야`, `${s} 몇 년 됐어`], SER(s));
  add("시리얼-이력", ["시리얼조회"], [`${s} 이력`, `${s} 고장 이력 보여줘`, `${s} 언제 교체했어?`, `${s} 교체 기록`], SER(s));
  add("등급이유", ["등급이유"], [`${s} 왜 ${gradeOf(s)}이야?`, `${s} 왜 ${gradeOf(s)}임`, `${s} ${gradeOf(s)}인 이유`, `${s} 등급 왜 이래`, `${s} 등급 근거`, `${s} 등급 어떻게 나온 거야`], SER(s));
}
// 음성식 시리얼 (공백, 하이픈 없음)
add("시리얼-음성", ["시리얼조회"], ["88091 48 상태", "8809148 상태", "88091 다시 48 상태", "88091-48번 상태"], SER("88091-48"));
add("시리얼-음성", ["시리얼조회"], ["92twdh076 상태", "92TWDH076 어때"], SER("92TWDH076"));

// 2) 위치로 TM 찾기
for (const { a, p } of locs) {
  const f = a.formation;
  add("위치", ["시리얼조회"], [
    `${f}편성 ${p.car}호차 ${p.tm}TM`,
    `${f}편성 ${p.car}호차 ${p.tm}TM 상태`,
    `${p.car}호차 ${p.tm}TM 상태`,
    `${p.car}호차 TM${p.tm} 어때`,
    `${p.car} ${p.tm}TM`,
    `${a.location}`,
    `${f} ${p.car} ${p.tm}번 TM`,
    `${p.car}호차 ${p.tm}번 모터`,
  ], SER(a.serial));
}

// 3) 편성 현황
for (const f of forms) {
  add("편성", ["편성현황"], [`${f}편성`, `${f}편성 상태`, `${f} 편성 어때`, `${f}편성 TM 현황`, `${f}편성 이상 없어?`, `${f}편성 괜찮아?`, `${f}편성 긴급 있어?`, `${f}편성 주의 몇 대야`, `${f}편성 고장 이력`, `${f}편성 고장내역 알려줘`, `${f}편성 문제 있는 거`, `${f}편성 점검할 거 있어?`], (t) => t.includes(f));
}

// 4) 등급 목록·설명
for (const g of ["긴급", "주의", "관찰", "정상"]) {
  add("등급목록", ["등급목록", "기타"], [`${g} TM 알려줘`, `${g} 뭐 있어`, `${g} 몇 대야`, `${g}인 거 다 보여줘`, `${g} 리스트`, `${g} 등급 TM 목록`, `${g} 걸린 거`], (t) => t.includes(g) && !t.includes("주행용 전동기"));
  add("등급설명", ["등급설명"], [`${g}이 뭐야`, `${g} 등급은 뭘 해야 돼`, `${g} 뜻`, `${g} 나오면 어떻게 해`, `${g}은 어떤 TM이야`], (t) => t.includes("할 일") || t.includes("어떤 TM"));
}
add("등급설명", ["등급설명"], ["관찰은 왜 있어?", "관찰은 왜 있는거야", "관찰 등급 굳이 왜 나눠?", "주의랑 정상 사이에 관찰은 뭐야", "관찰이랑 주의 차이", "긴급하고 주의 뭐가 달라", "등급 몇 단계야", "등급 종류", "등급별로 뭐 해야 돼", "등급표 보여줘", "매트릭스 보여줘", "등급 기준 근거", "이 등급 누가 정한 거야", "등급 기준 어디서 나온 거", "EN50126", "en 50126 뭐야", "IEC 62278", "RAMS가 뭐야", "국제 표준 근거 있어?"]);
add("산출", ["기타", "등급설명"], ["위험도 산출 방식", "위험도 어떻게 계산해", "등급 어떻게 정해져", "발생도가 뭐야", "심각도 뜻", "MTBF가 뭐야", "평균 고장 간격이 뭐야"]);

// 5) 우선 점검·예방정비·반복
add("우선점검", ["기타", "등급목록"], ["오늘 뭐부터 봐야 돼", "오늘 뭐부터 점검해", "급한 거 있어?", "제일 위험한 TM", "위험한 거 알려줘", "점검 우선순위", "뭐 먼저 해야 돼", "제일 심각한 거", "당장 봐야 할 거", "긴급한 거 있어?", "우선 점검 대상", "지금 문제 있는 TM"], (t) => t.includes("88091-48"));
add("예방정비", ["기타"], ["예방정비 대상", "예방정비 필요한 거", "곧 고장날 거", "다음에 고장날 TM", "정비 시기 된 거", "교체 시기 다 된 거 있어", "미리 봐야 할 거"], (t) => t.includes("예방정비") || t.includes("예상"));
add("반복", ["반복고장"], ["반복고장", "반복 고장 위치", "같은 자리 계속 고장나는 데", "자꾸 고장나는 위치", "반복해서 고장나는 곳", "112편성 반복 고장"]);

// 6) 예비품
add("예비품수량", ["예비품수량"], ["예비품 몇 개", "예비품 재고", "예비품 남은 거 몇 개", "예비 몇 대 있어", "예비품 몇 대 남았어요", "예비품 수량"]);
add("예비품여유", ["예비품여유", "예비품수량"], ["예비품 충분해?", "예비품 부족해?", "예비품 언제 바닥나", "예비품 몇 달 버텨", "예비품 여유 있어"]);
add("예비품목록", ["등급목록"], ["예비품 목록", "예비품 뭐 있어", "예비품 시리얼 알려줘", "예비품 리스트"]);
add("예비품-동의어", ["예비품수량", "등급목록", "예비품여유"], ["스페어 몇 개", "여분 TM 몇 대", "창고에 몇 개 있어"]);

// 7) 이력·외부수선·외주
add("이력", ["고장이력", "기타"], ["고장 이력 보여줘", "최근 고장", "최근에 고장난 거", "최근 교체 이력", "요즘 고장 뭐 났어", "마지막으로 고장난 거 뭐야", "최근 등록된 거"], (t) => t.includes("2026-04-07"));
add("기간", ["기타"], ["오늘 등록된 거 있어?", "이번주 몇 건", "이번달 고장 몇 건", "올해 고장 몇 건", "작년 고장 몇 건", "지난달 등록 건수", "어제 뭐 등록됐어"]);
add("외부수선", ["외부수선"], ["외부수선 보낸 거", "외부수선 몇 건", "수선 반출 현황", "협력업체 보낸 거", "외주 보낸 거 뭐 있어", "불용 처리된 거"]);
add("외주대상", ["외주대상"], ["외주수선 대상", "외주 대상 목록", "외주로 보낼 거"]);

// 8) 통계
add("월별", ["기타"], ["몇 월에 고장 많아", "월별 고장", "겨울에 고장 많아?", "여름에 고장 많아", "계절별 고장"]);
add("제조사", ["기타"], ["제조사별 고장", "어느 회사가 고장 많아", "히타치 몇 대", "현대 TM 고장률", "대우 꺼 몇 대야", "도시바 몇 대", "미쓰비시 TM"], (t) => t.includes("보유"));
add("연식", ["기타", "등급목록"], ["제일 오래된 TM", "가장 오래된 거", "제일 최신 TM", "90년대 이전 TM", "1989년 TM", "노후 TM", "30년 넘은 TM 몇 대"], (t) => t.includes("년"));
add("요약", ["기타"], ["전체 현황", "몇 대야 전체", "총 몇 대", "운영 요약", "전체 요약해줘"], (t) => t.includes("171"));

// 9) 고장코드
add("고장코드", ["기타"], ["고장코드 목록", "고장분류 뭐 있어", "FC05", "fc 3이 뭐야", "절연파괴는 어떤 코드", "물유입은 무슨 분류야", "홀더 열화는 심각도 몇이야", "리드선 단선은 어디 들어가", "그을림은 코드 뭐야", "소손 심각도"], (t) => t.includes("심각도"));

// 10) 수선의뢰 등록 시작
for (const { a, p } of locs.slice(0, 6)) {
  add("수선의뢰", ["수선의뢰"], [
    `${a.formation}편성 ${p.car}호차 ${p.tm}TM 고장났어`,
    `${p.car}호차 ${p.tm}TM 절연파괴로 갈았어`,
    `${a.serial} 교체했어`,
    `${a.serial} 소손 났어`,
    `${a.formation}편성 ${p.car} ${p.tm}TM 탈거함`,
    `${p.car}호차 ${p.tm}TM 교체 완료`,
    `${a.serial} 떼어냈어`,
  ]);
}
add("수선의뢰", ["수선의뢰"], ["수선의뢰 등록", "수선의뢰 등록할래", "고장 접수", "이력 등록", "수선의뢰 접수할게"]);

// 11) 정비 문서(규격·방법)
add("문서", ["문서검색"], [
  "브러시 길이 한도", "브러시 마모 한도 몇 mm", "정류자 외경 얼마", "정류자 외경 사용한도", "절연저항 몇 메가 이상", "절연저항 기준",
  "베어링 그리스 얼마나 넣어", "브러시 압력 기준", "볼트 토크 값", "계자코일 저항값", "브러시 교체 방법", "정류자 삭정 어떻게 해",
  "베어링 분해 순서", "언더컷 깊이", "브러시 홀더 간극", "정기검사 주기", "브러시 규격", "고압리드선 규격", "전기자 점검 방법",
  "TM 분해 절차", "TM 조립 순서", "건조 온도", "함침 방법", "내압시험 기준", "브러시 교체 주의할 점", "정비지침서에 브러시 뭐라고 나와",
]);
add("문서-포괄", ["문서검색"], ["정비 어떻게 해", "점검 방법", "정비는 어케해?"]);

// 12) 앱 사용법
add("사용법", ["사용법"], [
  "수선의뢰 어떻게 해", "수선의뢰 하는 법", "이력 등록 어떻게 해", "사진 첨부 어떻게 해", "사진 올리는 법", "사진 추가하고 싶어",
  "QR 라벨 뽑는 법", "QR코드 어떻게 만들어", "라벨 인쇄", "엑셀로 받고 싶어", "엑셀 다운로드", "PDF로 저장", "리포트 출력",
  "한글 파일로 받기", "현장 의견 보내는 법", "건의하고 싶어", "오류 신고", "스냅샷 뭐야", "백업 어떻게 해", "복원 방법",
  "음성으로 입력", "마이크 어떻게 써", "말로 입력 돼?", "로그인 어떻게 해", "위젯 추가", "즐겨찾기 어떻게 해",
  "문서 어디서 봐", "지침서 어디 있어", "문서가 안 열려", "등급 기준 어디서 봐", "PDF 다운이 안돼",
]);

// 13) 잡담·보안·범위 밖
add("잡담", ["인사"], ["안녕", "안녕하세요", "하이", "고마워", "감사합니다", "수고했어", "ㅎㅎ", "ㅇㅋ", "알겠어", "너 누구야", "이 앱 뭐야", "넌 뭐하는 봇이야"]);
add("도움말", ["도움말"], ["도움말", "뭐 할 수 있어?", "뭘 물어볼 수 있어", "사용법 알려줘"]);
add("보안", ["기타"], ["비밀번호 뭐야", "담당자 비번 알려줘", "관리자 비밀번호"], (t) => t.includes("보안"));
add("범위밖", ["모르는질문"], ["오늘 날씨 어때", "점심 뭐 먹지", "지금 몇 시야", "퇴근 몇 시", "로또 번호", "주식 추천"]);

// ---- 말투 변형 ----
const variants = (q: string): string[] => {
  const v = new Set([q]);
  v.add(q.replace(/\s+/g, "")); // 띄어쓰기 없음(음성·급하게 칠 때)
  if (!/[?요]$/.test(q)) v.add(q + "?");
  if (/(줘|해|어|야)$/.test(q)) v.add(q + "요");
  return [...v];
};

let total = 0;
const fails: Record<string, string[]> = {};
for (const c of cases) {
  for (const q0 of variants(c.q)) {
    total++;
    const q = normalizeQuestion(q0, A);
    let route: ChatRoute;
    let text = "";
    try {
      route = routeQuestion(q, A, H, undefined, E);
      text = answerQuestion(q, A, H, undefined, E).text;
    } catch (e) {
      (fails[c.cat] ??= []).push(`${q0}  → 오류 ${(e as Error).message}`);
      continue;
    }
    const okRoute = c.ok.includes(route);
    const okText = route === "수선의뢰" || route === "문서검색" || !c.must || c.must(text);
    if (!okRoute || !okText)
      (fails[c.cat] ??= []).push(`${q0}  → [${route}]${okRoute ? " (내용 불일치)" : ""} ${text.split("\n")[0]!.slice(0, 70)}`);
  }
}
const nf = Object.values(fails).reduce((s, x) => s + x.length, 0);
console.log(`질문 ${total}개 (기본 ${cases.length}개 × 말투 변형) · 실패 ${nf}개`);
for (const [cat, list] of Object.entries(fails)) {
  console.log(`\n## ${cat} (${list.length})`);
  for (const l of [...new Set(list)].slice(0, 40)) console.log("  " + l);
}
