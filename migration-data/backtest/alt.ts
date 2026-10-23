const S = "/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad";
const D = await Bun.file(`${S}/realdata.json`).json();
const A = D.assets as any[], H = D.history as any[];
const DAY = 86400000, d = (s: string) => new Date(s).getTime();
const F = H.filter((h) => h.is_fault === "Y");
const cnt: Record<string, number> = {}; for (const f of F) cnt[f.removed_serial] = (cnt[f.removed_serial] ?? 0) + 1;
const top = Object.entries(cnt).sort((a, b) => b[1] - a[1])[0]!;
console.log("고장 제일 많은 시리얼", top, F.filter((f) => f.removed_serial === top[0]).map((f) => `${f.repair_date} ${f.location} ${f.fault_code}`).join(" | "));
function inService(serial: string, t: string, cur: any) {
  const ev = H.flatMap((h) => [...(h.removed_serial === serial ? [{ d: h.repair_date, k: "off" }] : []), ...(h.installed_serial === serial ? [{ d: h.repair_date, k: "on" }] : [])]).sort((a, b) => a.d.localeCompare(b.d));
  const b = ev.filter((e) => e.d <= t).at(-1); if (b) return b.k === "on";
  const a = ev.find((e) => e.d > t); if (a) return a.k === "off"; return cur.status === "운영중";
}
const test = (name: string, pred: (a: any, T: number) => boolean) => {
  let hn = 0, hf = 0, ln = 0, lf = 0;
  for (let y = 2022; y <= 2025; y++) for (const m of ["01", "04", "07", "10"]) {
    const c = `${y}-${m}-01`, T = d(c); if (T + 365 * DAY > d("2026-04-08")) continue;
    for (const a of A) {
      if (!inService(a.serial, c, a)) continue;
      const nx = F.some((f) => f.removed_serial === a.serial && d(f.repair_date) > T && d(f.repair_date) <= T + 365 * DAY);
      if (pred(a, T)) { hn++; if (nx) hf++; } else { ln++; if (nx) lf++; }
    }
  }
  console.log(`${name}: 해당 ${hn}건 중 ${(hf / hn * 100).toFixed(1)}% vs 나머지 ${ln}건 중 ${(lf / ln * 100).toFixed(1)}% → ${((hf / hn) / (lf / ln)).toFixed(2)}배`);
};
const faultsBefore = (s: string, T: number, win: number) => F.filter((f) => f.removed_serial === s && d(f.repair_date) <= T && T - d(f.repair_date) <= win * DAY).length;
test("최근 1년 안 고장 있음", (a, T) => faultsBefore(a.serial, T, 365) > 0);
test("최근 2년 안 고장 있음", (a, T) => faultsBefore(a.serial, T, 730) > 0);
test("최근 5년 고장 2회 이상", (a, T) => faultsBefore(a.serial, T, 1825) >= 2);
test("최근 5년 고장 1회 이상", (a, T) => faultsBefore(a.serial, T, 1825) >= 1);
test("1970년대 제작", (a) => a.made_year && a.made_year < 1980);
test("1980년대 이전 제작", (a) => a.made_year && a.made_year < 1990);
test("히타치", (a) => /히타치/.test(a.maker ?? ""));
test("대우중공업", (a) => /대우/.test(a.maker ?? ""));
test("고장 많은 시리얼 제외하고 5년 1회 이상", (a, T) => a.serial !== top[0] && faultsBefore(a.serial, T, 1825) >= 1);
