// 예상 질문 500개 — 경로·필수 문구·오류 문자열 자동 검사 + 전체 답 기록
import { answerQuestion } from "/home/user/tm-cbm/src/lib/chatbot";
import { routeQuestion, normalizeQuestion } from "/home/user/tm-cbm/src/lib/chat-router";
const S = "/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad";
const D = await Bun.file(`${S}/realdata.json`).json();
const A = D.assets as any[], H = D.history as any[], E = D.ext as any[];
const lines = (await Bun.file(`${S}/q500/q500.txt`).text()).split("\n");
let ok: string[] = [], must = "";
const cases: { q: string; ok: string[]; must: string }[] = [];
for (const l of lines) {
  if (l.startsWith("## ")) {
    const [r, m] = l.slice(3).split("|").map((x) => x.trim());
    ok = r!.split(",");
    must = m ?? "";
  } else if (l.trim() && !l.startsWith("#")) cases.push({ q: l.trim(), ok, must });
}
const BAD = /(undefined|NaN|Infinity|\[object|예비품편성|null편성|편성편성|  •|••|\(\)|— —|: ,)/;
const out: string[] = [];
const fails: string[] = [];
for (const c of cases) {
  const q = normalizeQuestion(c.q, A);
  let route = "", text = "";
  try {
    route = routeQuestion(q, A, H, undefined, E);
    const a = answerQuestion(q, A, H, undefined, E);
    text = a.text + (a.chips ? `\n[버튼] ${a.chips.join(" | ")}` : "") + (a.actions ? `\n[바로가기] ${a.actions.map((x) => x.label).join(" | ")}` : "");
  } catch (e) {
    fails.push(`[오류] ${c.q} ${(e as Error).message}`);
    continue;
  }
  const problems: string[] = [];
  if (!c.ok.includes(route)) problems.push(`경로 ${route} (기대 ${c.ok.join("/")})`);
  const needOk =
    !c.must || route === "문서검색" || route === "수선의뢰" || route === "사진"
      ? true
      : c.must === "없어요"
        ? /(없어요|없습니다|않아요|없는)/.test(text)
        : c.must === "보안"
          ? text.includes("보안")
          : c.must === "비교"
            ? text.includes("비교")
            : text.includes(c.must);
  if (!needOk) problems.push(`필수 문구 '${c.must}' 없음`);
  if (BAD.test(text)) problems.push(`이상한 문자열 ${BAD.exec(text)![0]}`);
  if (!text.trim()) problems.push("빈 답");
  if (route !== "문서검색" && route !== "모르는질문" && route !== "수선의뢰" && /질문을 정확히 이해하지 못했어요/.test(text)) problems.push("모름");
  if (problems.length) fails.push(`${c.q}  → ${problems.join(", ")}\n      ${text.split("\n")[0]!.slice(0, 120)}`);
  out.push(`■ ${c.q}  [${route}]\n${text.split("\n").filter(Boolean).slice(0, 4).map((l) => "  " + l.slice(0, 150)).join("\n")}`);
}
await Bun.write(`${S}/q500/answers.txt`, out.join("\n"));
console.log(`질문 ${cases.length}개 · 문제 ${fails.length}개`);
console.log(fails.join("\n"));
