const S = "/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad";
const D = await Bun.file(`${S}/realdata.json`).json();
const A = D.assets as any[], H = (D.history as any[]).sort((a, b) => a.repair_date.localeCompare(b.repair_date));
const DAY = 86400000, d = (s: string) => new Date(s).getTime();
const F = H.filter((h) => h.is_fault === "Y");
// 1) 고장마다: 같은 시리얼의 이전 고장(5년 안)이 있었나 / 같은 자리의 이전 고장이 있었나
let prevSerial = 0, prevLoc = 0, first = 0;
const gaps: number[] = [];
for (const f of F) {
  const ps = F.filter((x) => x !== f && x.removed_serial === f.removed_serial && d(x.repair_date) < d(f.repair_date) && d(f.repair_date) - d(x.repair_date) <= 5 * 365 * DAY);
  const pl = F.filter((x) => x !== f && x.location === f.location && d(x.repair_date) < d(f.repair_date) && d(f.repair_date) - d(x.repair_date) <= 5 * 365 * DAY);
  if (ps.length) { prevSerial++; gaps.push((d(f.repair_date) - d(ps.at(-1)!.repair_date)) / DAY); }
  if (pl.length) prevLoc++;
  if (!ps.length && !pl.length) first++;
}
console.log(`고장 ${F.length}건 중: 같은 시리얼 이전 고장 있음 ${prevSerial} · 같은 자리 이전 고장 있음 ${prevLoc} · 둘 다 처음 ${first}`);
console.log(`같은 시리얼 재고장 간격(일): ${gaps.sort((a,b)=>a-b).map(Math.round).join(", ")}`);
// 2) 시리얼별 고장 횟수 분포
const cnt: Record<string, number> = {};
for (const f of F) cnt[f.removed_serial] = (cnt[f.removed_serial] ?? 0) + 1;
const dist: Record<number, number> = {};
for (const v of Object.values(cnt)) dist[v] = (dist[v] ?? 0) + 1;
console.log("시리얼당 고장 횟수 분포:", dist, " 고장 난 적 있는 시리얼", Object.keys(cnt).length, "/ 전체", A.length);
// 3) 고장 후 다시 장착되기까지 (떼어낸 TM이 다시 installed 되는 날)
const back: number[] = [];
for (const f of F) {
  const r = H.find((h) => h.installed_serial === f.removed_serial && d(h.repair_date) > d(f.repair_date));
  if (r) back.push((d(r.repair_date) - d(f.repair_date)) / DAY);
}
console.log(`고장으로 떼어낸 뒤 다시 장착된 것 ${back.length}/${F.length}, 걸린 일수 중간값 ${back.sort((a,b)=>a-b)[Math.floor(back.length/2)]}`);
// 4) 연식별 고장률 (현재 TM 기준, 5년 고장 수 / 대수)
const byDec: Record<string, [number, number]> = {};
for (const a of A) { const k = a.made_year ? `${Math.floor(a.made_year / 10) * 10}년대` : "미상"; byDec[k] ??= [0, 0]; byDec[k]![0]++; byDec[k]![1] += cnt[a.serial] ?? 0; }
console.log("연식별 (대수, 고장):", byDec);
const byMk: Record<string, [number, number]> = {};
for (const a of A) { const k = (a.maker ?? "미상").replace(/\(.*\)/, ""); byMk[k] ??= [0, 0]; byMk[k]![0]++; byMk[k]![1] += cnt[a.serial] ?? 0; }
console.log("제조사별 (대수, 고장):", byMk);
// 5) 자리(location) 기준: 과거 고장 있던 자리 vs 없던 자리의 다음 1년 고장률
const locs = [...new Set(A.map((a) => a.location).filter(Boolean))] as string[];
let hiN = 0, hiF = 0, loN = 0, loF = 0;
for (let y = 2022; y <= 2025; y++) {
  const T = d(`${y}-04-01`);
  for (const l of locs) {
    const past = F.some((f) => f.location === l && d(f.repair_date) <= T && T - d(f.repair_date) <= 5 * 365 * DAY);
    const nxt = F.some((f) => f.location === l && d(f.repair_date) > T && d(f.repair_date) <= T + 365 * DAY);
    if (past) { hiN++; if (nxt) hiF++; } else { loN++; if (nxt) loF++; }
  }
}
console.log(`자리 기준(매년 4/1): 과거 고장 있던 자리 ${hiN}건 중 다음 1년 고장 ${hiF} (${(hiF/hiN*100).toFixed(1)}%) vs 없던 자리 ${loN}건 중 ${loF} (${(loF/loN*100).toFixed(1)}%)`);
// 6) 고장 종류별
const fc: Record<string, number> = {};
for (const f of F) fc[f.fault_code] = (fc[f.fault_code] ?? 0) + 1;
console.log("고장코드:", fc);
// 연도별 고장 수
const yr: Record<string, number> = {};
for (const f of F) yr[f.repair_date.slice(0, 4)] = (yr[f.repair_date.slice(0, 4)] ?? 0) + 1;
console.log("연도별 고장:", yr);
