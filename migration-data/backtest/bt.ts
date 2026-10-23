// 등급 판정 검증: 과거 시점 T의 등급(그때까지 기록만) → T 이후 1년 안에 실제 고장 교체가 났나
import { computeRisk } from "/home/user/tm-cbm/src/lib/tm";
const S = "/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad";
const D = await Bun.file(`${S}/realdata.json`).json();
const A = D.assets as any[], H = D.history as any[];
const DAY = 86400000;
const dates = H.map((h) => h.repair_date).sort();
console.log(`자료: TM ${A.length}대, 이력 ${H.length}건 (${dates[0]} ~ ${dates.at(-1)}), 고장 ${H.filter((h) => h.is_fault === "Y").length}건`);
const last = new Date(dates.at(-1)!);
// T 시점에 차량에 붙어 있었나
function inService(serial: string, T: Date, cur: any): boolean {
  const ev = H.flatMap((h) => [
    ...(h.removed_serial === serial ? [{ d: h.repair_date, k: "off" }] : []),
    ...(h.installed_serial === serial ? [{ d: h.repair_date, k: "on" }] : []),
  ]).sort((a, b) => a.d.localeCompare(b.d));
  const t = T.toISOString().slice(0, 10);
  const before = ev.filter((e) => e.d <= t).at(-1);
  if (before) return before.k === "on";
  const after = ev.find((e) => e.d > t);
  if (after) return after.k === "off";
  return cur.status === "운영중";
}
const cut: string[] = [];
for (let y = 2022; y <= 2025; y++) for (const m of ["01", "04", "07", "10"]) cut.push(`${y}-${m}-01`);
const rows: { T: string; g: string; fail: boolean; serial: string }[] = [];
for (const c of cut) {
  const T = new Date(`${c}T12:00:00`);
  if (T.getTime() + 365 * DAY > last.getTime() + DAY) continue;
  const past = H.filter((h) => h.repair_date <= c);
  for (const a of A) {
    if (!inService(a.serial, T, a)) continue;
    const g = computeRisk({ ...a, status: "운영중" }, past, T).grade;
    const end = new Date(T.getTime() + 365 * DAY).toISOString().slice(0, 10);
    const fail = H.some((h) => h.removed_serial === a.serial && h.is_fault === "Y" && h.repair_date > c && h.repair_date <= end);
    rows.push({ T: c, g, fail, serial: a.serial });
  }
}
const tab = (rs: typeof rows) => {
  const out: Record<string, [number, number]> = {};
  for (const r of rs) { const k = r.g; out[k] ??= [0, 0]; out[k]![0]++; if (r.fail) out[k]![1]++; }
  return out;
};
const show = (title: string, rs: typeof rows) => {
  console.log(`\n${title} (TM×시점 ${rs.length}건)`);
  const t = tab(rs);
  for (const g of ["긴급", "주의", "관찰", "정상"]) if (t[g]) console.log(`  ${g}: ${t[g]![0]}건 중 다음 1년 고장 ${t[g]![1]}건 = ${((t[g]![1] / t[g]![0]) * 100).toFixed(1)}%`);
  const hi = rs.filter((r) => r.g === "긴급" || r.g === "주의"), lo = rs.filter((r) => r.g === "정상" || r.g === "관찰");
  const hr = hi.filter((r) => r.fail).length / hi.length, lr = lo.filter((r) => r.fail).length / lo.length;
  console.log(`  긴급+주의 ${(hr * 100).toFixed(1)}% vs 관찰+정상 ${(lr * 100).toFixed(1)}% → ${(hr / lr).toFixed(1)}배`);
  const failAll = rs.filter((r) => r.fail).length, caught = hi.filter((r) => r.fail).length;
  console.log(`  실제 고장 ${failAll}건 중 미리 긴급·주의였던 것 ${caught}건 (${((caught / failAll) * 100).toFixed(0)}%) · 긴급·주의 비율 ${((hi.length / rs.length) * 100).toFixed(0)}%`);
};
show("전체 시점 합계", rows);
for (const y of ["2022", "2023", "2024", "2025"]) show(`${y}년 시점`, rows.filter((r) => r.T.startsWith(y)));
// 한 해 한 번(4월 1일) 기준 — 같은 TM 중복 줄인 값
show("매년 4월 1일 기준만", rows.filter((r) => r.T.endsWith("-04-01")));
