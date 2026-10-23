const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const S = '/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad';
const D = JSON.parse(fs.readFileSync(S + '/realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(S + '/extra.json', 'utf8'));
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, tm_inspections: [], ...X };
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const [w, h, tag] of [[390, 844, 'm390'], [1280, 900, 'pc']]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: w < 700, hasTouch: w < 700, colorScheme: 'dark', deviceScaleFactor: 1 });
    await ctx.route(/supabase\.co\//, (r) => { const m = r.request().url().match(/rest\/v1\/([a-z_]+)/); return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} }); });
    const pg = await ctx.newPage();
    await pg.goto('http://127.0.0.1:8080/'); await pg.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
    for (const tab of ['status', 'analysis']) {
      await pg.goto(`http://127.0.0.1:8080/dashboard?tab=${tab}`); await pg.waitForTimeout(7000);
      const titles = await pg.evaluate(() => [...document.querySelectorAll('h2, h3')].map((e) => { const r = e.getBoundingClientRect(); return `${Math.round(r.top + window.scrollY)}:${e.textContent.trim().slice(0, 30)}`; }));
      console.log(tag, tab, titles.join(' | '));
      await pg.screenshot({ path: `${S}/ui3/dash_${tag}_${tab}.png`, fullPage: true });
    }
    await ctx.close();
  }
  await b.close();
})();
