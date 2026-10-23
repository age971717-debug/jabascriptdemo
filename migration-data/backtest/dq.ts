import { runDataChecks } from "/home/user/tm-cbm/src/lib/data-quality";
const D = await Bun.file("/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad/realdata.json").json();
for (const g of runDataChecks(D.assets, D.history)) console.log(g.id, g.items.length, g.items.slice(0, 3).map((i) => `${i.title}: ${i.label}`).join(" | "));
