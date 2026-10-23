// 챗봇 질문 묶음 시험: 실제 자료 사본으로 경로·답 첫 줄 확인 (AI·DB 호출 없음)
import { answerQuestion } from "/home/user/tm-cbm/src/lib/chatbot";
import { routeQuestion, normalizeQuestion } from "/home/user/tm-cbm/src/lib/chat-router";
const D = await Bun.file("/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad/realdata.json").json();
const Q: string[] = (await Bun.file(process.argv[2]!).text()).split("\n").map((s) => s.trim()).filter((s) => s && !s.startsWith("#"));
for (const q0 of Q) {
  const q = normalizeQuestion(q0, D.assets);
  const route = routeQuestion(q, D.assets, D.history, undefined, D.ext);
  const a = answerQuestion(q, D.assets, D.history, undefined, D.ext);
  const first = a.text.split("\n").filter(Boolean).slice(0, 3).join(" / ").slice(0, 170);
  console.log(`[${route}] ${q0}\n    → ${first}${a.fallback ? "  (fallback)" : ""}`);
}
