// 답에 나오는 숫자를 실제 자료로 따로 계산해 맞춰 보기 + 답 속도
import { answerQuestion } from "/home/user/tm-cbm/src/lib/chatbot";
import { normalizeQuestion } from "/home/user/tm-cbm/src/lib/chat-router";
import { computeRisk, isRetired } from "/home/user/tm-cbm/src/lib/tm";
const S = "/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad";
const D = await Bun.file(`${S}/realdata.json`).json();
const A = D.assets as any[], H = D.history as any[], E = D.ext as any[];
const ask = (q: string) => answerQuestion(normalizeQuestion(q, A), A, H, undefined, E).text;
const bad: string[] = [];
const check = (name: string, cond: boolean, detail: string) => {
  if (!cond) bad.push(`✗ ${name}: ${detail}`);
  else console.log(`✓ ${name}`);
};

// 등급별 대수
const grades: Record<string, number> = {};
for (const a of A) { const g = computeRisk(a, H).grade; grades[g] = (grades[g] ?? 0) + 1; }
for (const g of ["주의", "관찰", "정상", "불용대기"]) {
  const t = ask(`${g} TM 몇 대`);
  check(`${g} 대수`, t.includes(`${grades[g] ?? 0}대`), `${grades[g]} vs ${t.split("\n")[0]}`);
}
const crit = A.filter((a) => computeRisk(a, H).grade === "긴급").length;
check("긴급 대수", ask("긴급 몇 대").includes(`${crit}대`), ask("긴급 몇 대").split("\n")[0]!);
// 요약
const sum = ask("전체 현황");
check("전체 대수", sum.includes(`${A.length}대`), sum.split("\n")[0]!);
const spares = A.filter((a) => a.status === "예비품" && !isRetired(a)).length;
check("가용 예비품", ask("예비품 몇 개").includes(`가용 예비품 ${spares}대`), ask("예비품 몇 개").split("\n")[0]!);
// 편성 대수
for (const f of ["111", "112", "113", "114", "115", "116"]) {
  const n = A.filter((a) => a.formation === f).length;
  const t = ask(`${f}편성 상태`);
  check(`${f}편성 대수`, t.includes(`${n}대`), t.split("\n")[0]!);
  const hist = H.filter((h) => h.formation === f || A.some((a) => a.formation === f && a.serial === h.removed_serial)).length;
  const th = ask(`${f}편성 고장 이력`);
  check(`${f}편성 이력 건수`, th.includes(`전체 ${hist}건`), `${hist} vs ${th.split("\n")[0]}`);
}
// 고장 종류
for (const [q, code] of [["절연파괴 몇 건", "FC05"], ["홀더 고장 몇 건", "FC03"], ["물유입 고장 몇 건", "FC02"], ["정기교체 몇 건", "FC00"], ["기타 고장 몇 건", "FC99"], ["브러시 경미 고장 몇 건", "FC01"]]) {
  const n = H.filter((h) => h.fault_code === code).length;
  const t = ask(q!);
  check(`${q} 건수`, t.includes(`전체 ${n}건`), `${n} vs ${t.split("\n")[0]}`);
}
// 외부수선
check("외부수선 건수", ask("외부수선 몇 건").includes(`${E.length}건`), ask("외부수선 몇 건").split("\n")[0]!);
// 연도별
for (const y of ["2023", "2024", "2025", "2026"]) {
  const n = H.filter((h) => h.repair_date.startsWith(y)).length;
  const t = ask(`${y}년 고장 몇 건`);
  check(`${y}년 건수`, t.includes(`${n}건`), `${n} vs ${t.split("\n")[0]}`);
}
// 제조사
for (const m of ["히타치", "현대중공업", "대우중공업", "도시바", "미쓰비시"]) {
  const n = A.filter((a) => a.maker === m).length;
  const t = ask(`${m} 몇 대`);
  check(`${m} 보유`, t.includes(`보유 ${n}대`), `${n} vs ${t.split("\n")[0]}`);
}
// 시리얼 하나하나: 등급·위치가 화면 계산과 같은지
let mism = 0;
for (const a of A) {
  const t = ask(`${a.serial} 상태`);
  const g = computeRisk(a, H).grade;
  if (!t.includes(`등급: ${g}`) || (a.location && !t.includes(a.location))) { mism++; if (mism < 5) bad.push(`✗ ${a.serial}: ${t.split("\n").slice(0, 2).join(" / ")}`); }
}
check("TM 171대 등급·위치", mism === 0, `${mism}대 불일치`);
// 연식
const old = Math.min(...A.filter((a) => a.made_year).map((a) => a.made_year));
check("가장 오래된 연식", ask("가장 오래된 TM").includes(`${old}년`), ask("가장 오래된 TM").split("\n")[1]!);
const y70 = A.filter((a) => a.made_year >= 1970 && a.made_year < 1980).length;
check("1970년대 대수", ask("1970년대 TM 몇 대").includes(`${y70}대`), ask("1970년대 TM 몇 대").split("\n")[0]!);

// 속도 — 504문장 각각
const qs = (await Bun.file(`${S}/q500/q500.txt`).text()).split("\n").filter((l) => l.trim() && !l.startsWith("#"));
const times: number[] = [];
for (const q of qs) { const t0 = performance.now(); ask(q); times.push(performance.now() - t0); }
times.sort((a, b) => a - b);
console.log(`\n속도(ms): 중간 ${times[Math.floor(times.length / 2)]!.toFixed(1)} · 95% ${times[Math.floor(times.length * 0.95)]!.toFixed(1)} · 최대 ${times.at(-1)!.toFixed(1)}`);
const slow = qs.map((q, i) => q).filter((q) => { const t0 = performance.now(); ask(q); return performance.now() - t0 > 30; });
console.log("30ms 넘는 질문:", slow.slice(0, 15).join(" | "));
console.log(`\n불일치 ${bad.length}건`);
console.log(bad.join("\n"));
