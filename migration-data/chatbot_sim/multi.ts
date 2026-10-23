// 이어지는 대화 시뮬레이션 — ChatWidget과 같은 방식으로 직전 편성·시리얼·주제를 넘긴다.
import { answerQuestion, detectRepairIntent, type BotContext } from "/home/user/tm-cbm/src/lib/chatbot";
import { normalizeQuestion } from "/home/user/tm-cbm/src/lib/chat-router";
const D = await Bun.file("/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad/realdata.json").json();
const A = D.assets as any[], H = D.history as any[], E = D.ext as any[];

// [대화, 마지막 답에 있어야 할 말]
const convs: [string[], string][] = [
  [["116편성 상태", "거기 긴급은?"], "98TWDH393"],
  [["116편성 상태", "그중 주의 몇 대야"], "116편성 주의"],
  [["116편성 상태", "그 편성 관찰 있어?"], "116편성에 관찰"],
  [["116편성 상태", "1416호차는?"], "1416호차 TM 4대"],
  [["116편성 상태", "3호차는?"], "1416호차 TM 4대"],
  [["116편성 상태", "3호차 2TM은?"], "116-1416-TM2"],
  [["116편성 상태", "고장 이력은?"], "116 편성 이력"],
  [["116편성 상태", "반복 고장 있어?"], "116편성에는"],
  [["88091-48 상태", "그거 왜 긴급이야"], "88091-48 (111편성"],
  [["88091-48 상태", "그거 이력"], "이력 7건"],
  [["88091-48 상태", "제조사는?"], "제조사 대우중공업"],
  [["88091-48 상태", "몇 년식이야?"], "1989"],
  [["88091-48 상태", "왜?"], "등급 계산 근거"],
  [["88091-48 상태", "언제 교체했어?"], "이력 7건"],
  [["88091-48 상태", "다음 고장 언제쯤?"], "평균 고장 간격(MTBF) 163일"],
  [["88091-48 상태", "바꿔야 돼?"], "→ 할 일"],
  [["88091-48 상태", "등급 근거"], "88091-48 (111편성"],
  [["관찰 TM 알려줘", "첫 번째 거 왜 관찰이야"], "관찰"],
  [["관찰이 뭐야", "그럼 주의는?"], "‘주의’ 등급"],
  [["관찰이 뭐야", "긴급은?"], "‘긴급’ 등급"],
  [["등급표 보여줘", "근거는?"], "EN 50126"],
  [["겨울에 고장 많아?", "여름은?"], "여름"],
  [["비 오면 고장 많아?", "추울 때는?"], "겨울"],
  [["111편성 상태", "116편성은?"], "116편성"],
  [["111편성 상태", "그럼 112는?"], "112편성"],
  [["예비품 몇 개", "충분해?"], "개월"],
  [["예비품 몇 개", "제일 오래된 건?"], "예비품 등급 TM은"],
  [["절연파괴 몇 건", "116편성은?"], "116"],
  [["88091-48 상태", "116편성 상태", "왜?"], "질문을"],
  [["88091-48 상태", "예비품 몇 개"], "가용 예비품"],
  [["88091-48 상태", "관찰이 뭐야"], "‘관찰’ 등급"],
  [["88091-48 상태", "116편성 1416호차 2TM 고장났어"], "[수선의뢰 시작]"],
  [["116편성 상태", "2TM 다 보여줘"], "116편성 2TM 6대"],
  [["관찰 TM 알려줘", "고마워"], "천만에요"],
  [["예비품 몇 개", "히타치는?"], "히타치 예비품"],
  [["주의 TM 목록", "두 번째 거 왜 주의야"], "최종 등급: 주의"],
  [["주의 TM 목록", "2번째 리포트"], "등급: 주의"],
  [["오늘 뭐부터 점검해", "첫 번째 거 이력"], "88091-48 · 111 111-1511-TM3 — 이력"],
  [["1416호차 상태", "세 번째 거 왜 주의야"], "88091-68 (116편성"],
  [["고장 많이 난 TM", "마지막 거 상태"], "등급:"],
  [["예비품 몇 개", "오늘 뭐부터 점검해야 돼"], "우선 점검 대상"],
  [["관찰이 뭐야", "긴급 몇 대?"], "긴급"],
  [["88091-48 상태", "그렇구나"], "네!"],
  [["116편성 상태", "긴급 TM 알려줘"], "우선 점검 대상(긴급) 2대"],
  [["116편성 상태", "긴급은?"], "116편성 긴급"],

];

let fail = 0;
for (const [turns, must] of convs) {
  const ctx: BotContext = { lastFormation: null, lastSerial: null, lastTopic: null };
  let last = "";
  for (const t of turns) {
    const q = normalizeQuestion(t, A);
    const repair = detectRepairIntent(q, A, ctx);
    if (repair) { last = `[수선의뢰 시작] ${t}`; break; }
    const a = answerQuestion(q, A, H, ctx, E);
    if (a.formation !== undefined) ctx.lastFormation = a.formation;
    if (a.serial !== undefined) ctx.lastSerial = a.serial;
    ctx.lastTopic = a.topic ?? null;
    if (a.list !== undefined) ctx.lastList = a.list;
    last = a.text;
  }
  const ok = last.includes(must);
  if (!ok) fail++;
  console.log(`${ok ? "OK " : "XX "} ${turns.join(" → ")}\n     ${last.split("\n").slice(0, 2).join(" / ").slice(0, 150)}`);
}
console.log(`\n대화 ${convs.length}개 · 실패 ${fail}`);
