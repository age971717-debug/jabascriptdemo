// 실제 챗봇 화면으로 대화 시나리오 실행 — 저장 요청은 403(실데이터 안 바뀜). 시나리오마다 새 창.
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const S = '/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad';
const D = JSON.parse(fs.readFileSync(S + '/realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(S + '/extra.json', 'utf8'));
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, ...X };
const U = 'http://127.0.0.1:8080';
const SCEN = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const errors = [];
  let n = 0;
  for (const [name, steps] of SCEN) {
    n++;
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, colorScheme: 'dark' });
    await ctx.route(/supabase\.co\//, (r) => {
      const m = r.request().url().match(/rest\/v1\/([a-z_]+)/);
      if (r.request().method() !== 'GET' && m && m[1] !== 'rpc') return r.fulfill({ status: 403, json: {} });
      return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} });
    });
    const pg = await ctx.newPage();
    pg.on('pageerror', (e) => errors.push(`${name}: ${String(e).slice(0, 160)}`));
    await pg.goto(U + '/');
    await pg.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
    await pg.goto(U + '/', { waitUntil: 'domcontentloaded' });
    await pg.waitForTimeout(n === 1 ? 8000 : 4000);
    await pg.getByRole('button', { name: 'TM 챗봇 열기' }).click();
    await pg.waitForTimeout(1200);
    console.log(`\n######## ${name}`);
    for (const st of steps) {
      const before = await pg.locator('[data-chat-bubble="bot"]').count();
      if (st.startsWith('chip:')) {
        try {
          await pg.locator('[data-chat-bubble="bot"]').last().getByRole('button', { name: st.slice(5), exact: true }).first().click({ timeout: 3000 });
        } catch { console.log(`> ${st}  (버튼 없음)`); continue; }
      } else {
        await pg.getByRole('textbox').last().fill(st);
        await pg.getByRole('button', { name: '질문 보내기' }).click();
      }
      await pg.waitForTimeout(1300);
      const bots = await pg.locator('[data-chat-bubble="bot"]').allInnerTexts();
      const fresh = bots.slice(before).map((t) => t.replace(/\n+/g, ' / ').slice(0, 260));
      console.log(`> ${st}\n  ${fresh.join('\n  ') || '(새 답 없음)'}`);
    }
    await pg.screenshot({ path: `${S}/chat/flow_${n}.png` });
    await ctx.close();
  }
  console.log('\nerrors', errors);
  await b.close();
})();
