import { answerQuestion } from "/home/user/tm-cbm/src/lib/chatbot";
import { normalizeQuestion, routeQuestion } from "/home/user/tm-cbm/src/lib/chat-router";
const S = "/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad";
const D = await Bun.file(`${S}/realdata.json`).json();
const qs = `116편성 고장 많은 TM
116편성 고장 많아?
116편성 1416호차 2TM 고장 잦아?
부착 TM 시리얼 어디서 봐
편성별 고장 설명해줘
편성 뭐 있어
대시보드 어떻게 봐
AI가 답한 거 맞아?
TM 3개 추천해줘
3월에 교체 몇 대 필요했어
내년에 교체 몇 대 필요해
긴급 빼고 몇 대
정상 아닌 거 목록
111편성 112편성 차이
116편성 1416호차랑 1516호차 비교
테스트 결과 어디서 봐
아니 116편성 말고 115편성
48번
4번
12번 TM
88091 TM 몇 개
296640
편성이 몇 개야
차호 몇 개
리포트 어떻게 뽑아
현황판에서 색깔 뜻
이 앱 장점
예비품 뭐가 좋아
주의 TM 확인하라는데 어디 있어
88091-48 할 일
88091-48 조치 방법
88091-48 정상으로 돌리려면
116편성 비교
고장 많은 편성 비교
올해 고장 몇 건
올해 예산 계획
5개
2025
1999`.split("\n");
for (const q of qs) {
  const nq = normalizeQuestion(q, D.assets);
  const r = routeQuestion(nq, D.assets, D.history, undefined, D.ext);
  const a = answerQuestion(nq, D.assets, D.history, undefined, D.ext);
  console.log(`[${r}/${a.kind ?? "-"}] ${q}\n    → ${a.text.split("\n").filter(Boolean).slice(0, 2).join(" / ").slice(0, 160)}`);
}
