// 무작위 조합 퍼즈 — 말머리·대상·의도·말끝을 섞어 수천 개를 만들고, 오류·엉뚱한 대상·모름 비율을 본다.
import { answerQuestion } from "/home/user/tm-cbm/src/lib/chatbot";
import { routeQuestion, normalizeQuestion } from "/home/user/tm-cbm/src/lib/chat-router";
import { parseLocation } from "/home/user/tm-cbm/src/lib/tm";
const D = await Bun.file("/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad/realdata.json").json();
const A = D.assets as any[], H = D.history as any[], E = D.ext as any[];
let seed = 12345;
const rnd = (n: number) => ((seed = (seed * 1103515245 + 12345) % 2147483648), Math.floor(seed / 65536) % n);
const one = <T,>(a: T[]) => a[rnd(a.length)]!;
const op = A.filter((a) => a.location);
const pre = ["", "", "", "어 ", "저기 ", "그 ", "음 ", "혹시 ", "근데 ", "아 "];
const end = ["", "", "?", "요", " 좀", " 좀 알려줘", " 알려주세요", " 확인 부탁", "~", "??"];
type T = { kind: string; make: () => { q: string; serial?: string; formation?: string; car?: string } };
const T: T[] = [
  { kind: "serial", make: () => { const a = one(op); return { q: `${a.serial} ${one(["상태", "어때", "등급", "정보", "이력", "어디 달려있어", "몇년식", "제조사"])}`, serial: a.serial }; } },
  { kind: "why", make: () => { const a = one(op); return { q: `${a.serial} ${one(["왜 이 등급이야", "등급 이유", "등급 근거", "바꿔야 돼", "괜찮아"])}`, serial: a.serial }; } },
  { kind: "loc", make: () => { const a = one(op); const p = parseLocation(a.location)!; return { q: one([`${a.formation}편성 ${p.car}호차 ${p.tm}TM`, `${p.car}호차 ${p.tm}TM`, `${p.car} ${p.tm}번`, `${p.car}호차 ${p.tm}번 모터`, `${a.formation} ${p.car} ${p.tm}tm`]) + " " + one(["상태", "어때", "", "등급"]), serial: a.serial }; } },
  { kind: "car", make: () => { const a = one(op); const p = parseLocation(a.location)!; return { q: `${p.car}호차 ${one(["상태", "어때", "TM", "전부", "TM 다 보여줘"])}`, car: p.car }; } },
  { kind: "form", make: () => { const f = one(["111", "112", "113", "114", "115", "116"]); return { q: `${f}편성 ${one(["상태", "어때", "현황", "긴급 있어", "주의 몇 대", "고장 이력", "괜찮아", "문제 있는 거", "반복 고장", "제조사"])}`, formation: f }; } },
  { kind: "free", make: () => ({ q: one(["오늘 뭐부터 봐", "급한 거", "예비품 몇 개", "예비품 충분해", "관찰 뭐야", "관찰 왜 있어", "등급표", "긴급 목록", "주의 리스트", "반복 고장", "예방정비", "고장 많이 난 TM", "절연파괴 몇 건", "홀더 고장 몇 번", "최근 고장", "올해 고장 몇 건", "외부수선 몇 건", "외주 대상", "QR 라벨", "엑셀 받기", "사진 첨부 방법", "스냅샷", "백업", "도움말", "고마워", "브러시 규격", "정류자 외경 한도", "절연저항 기준", "제일 오래된 TM", "히타치 몇 대", "MTBF 짧은 TM", "등급 바뀐 거", "등급 언제 바뀌어"]) }) },
];
const routes: Record<string, number> = {};
const bad: string[] = [];
let unknown = 0, total = 0;
for (let i = 0; i < 5000; i++) {
  const t = one(T);
  const m = t.make();
  const q0 = one(pre) + m.q.trim() + one(end);
  const q1 = rnd(3) === 0 ? q0.replace(/\s+/g, "") : q0;
  total++;
  try {
    const q = normalizeQuestion(q1, A);
    const r = routeQuestion(q, A, H, undefined, E);
    routes[`${t.kind}:${r}`] = (routes[`${t.kind}:${r}`] ?? 0) + 1;
    if (r === "모르는질문") { unknown++; bad.push(`[모름] ${q1}`); continue; }
    if (r === "수선의뢰" && t.kind !== "free") { bad.push(`[수선의뢰로 오인] ${q1}`); continue; }
    const a = answerQuestion(q, A, H, undefined, E).text;
    if (m.serial && r !== "사진" && !a.includes(m.serial)) bad.push(`[다른 TM] ${q1} → ${a.split("\n")[0]}`);
    if (m.formation && !a.includes(m.formation)) bad.push(`[다른 편성] ${q1} → ${a.split("\n")[0]}`);
    if (m.car && !a.includes(m.car)) bad.push(`[다른 차호] ${q1} → ${a.split("\n")[0]}`);
  } catch (e) {
    bad.push(`[오류] ${q1} ${(e as Error).message}`);
  }
}
console.log(`퍼즈 ${total}개 · 문제 ${bad.length}개 (모름 ${unknown})`);
console.log(Object.entries(routes).sort().map(([k, v]) => `${k} ${v}`).join("\n"));
const uniq = [...new Set(bad)];
console.log("\n" + uniq.slice(0, 80).join("\n"));
