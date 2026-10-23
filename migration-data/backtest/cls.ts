import { classifyFault } from "/home/user/tm-cbm/src/lib/tm";
const D = await Bun.file("/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad/realdata.json").json();
const H = D.history as any[];
let ok = 0, n = 0; const bad: string[] = []; const conf: Record<string, number> = {};
for (const h of H) {
  if (!h.detail?.trim()) continue;
  n++;
  const g = classifyFault(h.detail).code;
  if (g === h.fault_code) ok++; else { bad.push(`${h.fault_code}→${g} | ${h.detail} | type=${h.fault_type}`); conf[`${h.fault_code}→${g}`] = (conf[`${h.fault_code}→${g}`] ?? 0) + 1; }
}
console.log(`내용 있는 기록 ${n}건 / 전체 ${H.length} · 키워드 분류 일치 ${ok} (${(ok / n * 100).toFixed(1)}%)`);
console.log(conf); console.log(bad.join("\n"));
console.log("\n내용 없는 기록:", H.filter((h) => !h.detail?.trim()).map((h) => h.fault_code).join(","));
console.log("\n예시 30개:\n" + H.slice(0, 30).map((h) => `${h.fault_code} | ${h.fault_type} | ${h.detail}`).join("\n"));
