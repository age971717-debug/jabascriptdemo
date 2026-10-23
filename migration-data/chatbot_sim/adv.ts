// 버그 찾기 — 이상한 입력(오류·느림), 일어나면 안 되는 일(등록 오인·거절 오인·엉뚱한 TM), 없는 대상.
import { answerQuestion, detectRepairIntent } from "/home/user/tm-cbm/src/lib/chatbot";
import { routeQuestion, normalizeQuestion } from "/home/user/tm-cbm/src/lib/chat-router";
const D = await Bun.file("/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad/realdata.json").json();
const A = D.assets as any[], H = D.history as any[], E = D.ext as any[];
const run = (q0: string) => {
  const q = normalizeQuestion(q0, A);
  const t0 = performance.now();
  const r = routeQuestion(q, A, H, undefined, E);
  const a = answerQuestion(q, A, H, undefined, E);
  return { q, r, a, ms: performance.now() - t0 };
};
const out: string[] = [];
const bad = (s: string) => out.push(s);

// 1) 이상한 입력 — 오류·느림
const weird = [
  "", " ", "?", "??", "!!!", "ㅋ", "ㅠㅠ", "...", "😀", "👍👍", "TM", "tm", "편성", "호차", "1", "0", "0000", "9999", "-", "--", "88091-", "-48",
  "1".repeat(200), "가".repeat(500), "116편성 ".repeat(100), "88091-48 ".repeat(50), "a(b[c{d", ".*+?^$", "\\d+", "<script>alert(1)</script>",
  "'; DROP TABLE tm_assets; --", "null", "undefined", "NaN", "[object Object]", "%00", "\u0000", "\t\n", "ＴＭ 상태", "１１６편성", "88091－48 상태",
  "116편성116편성116편성", "1416호차1416호차", "왜왜왜왜왜왜왜왜왜왜왜왜왜왜왜왜왜왜왜왜왜왜왜왜", "tm".repeat(300), "1416 ".repeat(200),
];
for (const w of weird) {
  try {
    const { r, ms } = run(w);
    if (ms > 150) bad(`[느림 ${ms.toFixed(0)}ms] ${JSON.stringify(w.slice(0, 40))} → ${r}`);
  } catch (e) {
    bad(`[오류] ${JSON.stringify(w.slice(0, 40))} ${(e as Error).message}`);
  }
}

// 2) 등록이 시작되면 안 되는 말
const notRepair = [
  "88091-48 교체해야 할까?", "88091-48 교체 이력", "88091-48 언제 교체했지", "교체 방법 알려줘", "브러시 교체 주기", "교체 기준이 뭐야",
  "116편성 1416호차 2TM 교체했었나?", "고장난 거 목록", "최근 고장난 TM", "고장나면 어떻게 해", "소손 나면 어떻게 해야 돼", "절연파괴 몇 건",
  "수선의뢰 화면 어디", "수선의뢰 목록", "수선의뢰 현황 보여줘", "교체된 거 몇 개", "이번달 교체 몇 건", "작년에 교체한 거",
  "교체하면 등급 바뀌어?", "교체 후에 뭐 해야 돼", "떼어낸 TM 어디 있어", "탈거 절차", "취거 방법", "고장났을 때 누구한테 말해",
];
for (const q of notRepair) {
  const { r } = run(q);
  if (r === "수선의뢰") bad(`[등록 오인] ${q}`);
}
// 3) 등록이 시작돼야 하는 말
const isRepair = [
  "116편성 1416호차 2TM 교체했어", "1416호차 2TM 교체 완료", "88091-48 떼어냈어", "88091-48 소손 났어", "116편성 1416 2TM 고장남",
  "1416호차 3TM 절연파괴로 교체함", "수선의뢰 등록", "고장 접수", "이력 등록할게", "116편성 2TM 고장났어요", "오늘 1416호차 1TM 갈았어",
];
for (const q of isRepair) {
  const { r } = run(q);
  if (r !== "수선의뢰") bad(`[등록 놓침] ${q} → ${r}`);
}
// 4) 거절되면 안 되는 업무 질문
const notOff = [
  "오늘 몇 건 고장났어", "오늘 날짜로 등록된 거", "이름이 뭐야 이 TM", "TM 나이 몇 살", "계산 방식", "몇 시에 등록됐어", "제조사 이름", "88091-48 몇 살",
  "요일별 고장", "뉴스에 나온 고장", "더울 때 고장 많아?", "추우면 고장 나?", "비 오면 절연 문제 생겨?", "사랑하는 TM 88091-48", "고마워 88091-48 상태",
];
for (const q of notOff) {
  const { r, a } = run(q);
  if (a.kind === "offDomain" || /TM 진단·수선 관련 정보만/.test(a.text)) bad(`[거절 오인] ${q} → ${r}`);
}
// 5) 없는 대상
const ghost = ["88091-49 상태", "88091-999 상태", "99TWDH999 상태", "1419호차 상태", "1416호차 5TM", "117편성 상태", "116편성 1999호차", "FC09가 뭐야", "1416호차 0TM"];
for (const q of ghost) {
  const { r, a } = run(q);
  out.push(`[없는 대상] ${q} → [${r}] ${a.text.split("\n").slice(0, 2).join(" / ").slice(0, 120)}`);
}
// 6) 엉뚱한 TM — 질문 속 시리얼과 다른 TM으로 답
for (const a0 of A.filter((x: any) => x.location)) {
  for (const tpl of ["{s} 상태", "{s}왜긴급", "{s} 이력", "{s} 다음 고장 언제", "{s} 바꿔야 돼", "{s} 제조사", "{s} 사진 있어?"]) {
    const q = tpl.replace("{s}", a0.serial);
    const { r, a } = run(q);
    if (r === "사진") continue;
    if (!a.text.includes(a0.serial)) bad(`[엉뚱한 TM] ${q} → [${r}] ${a.text.split("\n")[0]!.slice(0, 80)}`);
  }
}
// 시리얼끼리 겹치는 경우 (한 시리얼이 다른 시리얼을 포함)
const ser = A.map((a: any) => a.serial as string);
const overlap = ser.filter((s) => ser.some((t) => t !== s && t.includes(s)));
out.push(`[겹치는 시리얼] ${overlap.join(", ") || "없음"}`);
for (const s of overlap) {
  const { a } = run(`${s} 상태`);
  if (!a.text.startsWith(s) && !a.text.includes(`${s} ·`)) bad(`[겹침 오답] ${s} 상태 → ${a.text.split("\n")[0]}`);
}
console.log(out.join("\n"));
