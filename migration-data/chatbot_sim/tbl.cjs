const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const S = '/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad';
const D = JSON.parse(fs.readFileSync(S + '/realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(S + '/extra.json', 'utf8'));
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, ...X };
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const [w,h,tag] of [[360,640,'m360'],[768,1024,'t768']]) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: w<700, hasTouch: true, colorScheme: 'dark', deviceScaleFactor: 2 });
  await ctx.route(/supabase\.co\//, (r) => { const m = r.request().url().match(/rest\/v1\/([a-z_]+)/); return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} }); });
  const pg = await ctx.newPage();
  await pg.goto('http://127.0.0.1:8080/'); await pg.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await pg.goto('http://127.0.0.1:8080/'); await pg.waitForTimeout(6000);
  await pg.getByRole('button', { name: 'TM 챗봇 열기' }).click(); await pg.waitForTimeout(600);
  for (const q of ['88091-48이랑 98TWDH393 비교', '등급표 보여줘']) {
    await pg.getByRole('textbox').last().fill(q); await pg.getByRole('button', { name: '질문 보내기' }).click(); await pg.waitForTimeout(1200);
    const ov = await pg.evaluate(() => { const t=[...document.querySelectorAll('[data-chat-bubble="bot"] table')].at(-1); const p=t.parentElement; return `${Math.round(t.scrollWidth)} / ${Math.round(p.clientWidth)}`; });
    console.log(tag, q, 'table/box', ov);
    await pg.locator('[data-chat-bubble="bot"] table').last().scrollIntoViewIfNeeded();
    await pg.screenshot({ path: `${S}/chat/tbl_${tag}_${q.length}.png` });
  }
  await ctx.close(); }
  await b.close();
})();
