import { answerQuestion } from "/home/user/tm-cbm/src/lib/chatbot";
import { normalizeQuestion } from "/home/user/tm-cbm/src/lib/chat-router";
const S = "/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad";
const D = await Bun.file(`${S}/realdata.json`).json();
for (const q of process.argv.slice(2)) {
  const a = answerQuestion(normalizeQuestion(q, D.assets), D.assets, D.history, undefined, D.ext);
  console.log(`■ ${q} [${a.kind}]\n${a.text}\n${a.chips ? "[버튼] " + a.chips.join(" | ") : ""}\n`);
}
