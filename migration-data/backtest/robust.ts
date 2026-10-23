// 장착 여부 판단을 빼고, 연 1회(4/1)만, 고장 집계가 많은 2022~2023 시점만 — 결과가 방법 탓인지 확인
const S = "/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad";
const D = await Bun.file(`${S}/realdata.json`).json();
const A = D.assets as any[], H = D.history as any[];
const DAY = 86400000, d = (s: string) => new Date(s).getTime();
const F = H.filter((h) => h.is_fault === "Y" && h.removed_serial);
console.log("시리얼 없는 고장 기록", H.filter((h) => h.is_fault === "Y" && !h.removed_serial).length, "건");
for (const years of [[2022, 2023], [2022, 2023, 2024, 2025]]) {
  let hn = 0, hf = 0, ln = 0, lf = 0;
  for (const y of years) {
    const T = d(`${y}-04-01`);
    for (const a of A) {
      const past = F.filter((f) => f.removed_serial === a.serial && d(f.repair_date) <= T && T - d(f.repair_date) <= 1825 * DAY).length;
      const nx = F.some((f) => f.removed_serial === a.serial && d(f.repair_date) > T && d(f.repair_date) <= T + 365 * DAY);
      if (past) { hn++; if (nx) hf++; } else { ln++; if (nx) lf++; }
    }
  }
  console.log(`${years.join("·")} (장착 판단 없이 전체 TM): 과거 고장 있음 ${hn}건 ${(hf / hn * 100).toFixed(1)}% vs 없음 ${ln}건 ${(lf / ln * 100).toFixed(1)}%`);
}
// 2년 내다보기
{
  let hn = 0, hf = 0, ln = 0, lf = 0;
  for (const y of [2022, 2023, 2024]) {
    const T = d(`${y}-04-01`);
    for (const a of A) {
      const past = F.filter((f) => f.removed_serial === a.serial && d(f.repair_date) <= T).length;
      const nx = F.some((f) => f.removed_serial === a.serial && d(f.repair_date) > T && d(f.repair_date) <= T + 730 * DAY);
      if (past) { hn++; if (nx) hf++; } else { ln++; if (nx) lf++; }
    }
  }
  console.log(`다음 2년 기준: 과거 고장 있음 ${hn}건 ${(hf / hn * 100).toFixed(1)}% vs 없음 ${ln}건 ${(lf / ln * 100).toFixed(1)}%`);
}
