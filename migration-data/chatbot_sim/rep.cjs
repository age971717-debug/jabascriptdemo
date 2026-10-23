const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const S = '/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad';
const D = JSON.parse(fs.readFileSync(S + '/realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(S + '/extra.json', 'utf8'));
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, tm_inspections: [], ...X };
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const [w, h, tag] of [[390, 844, 'm390'], [1280, 900, 'pc']]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: w < 700, hasTouch: w < 700, colorScheme: 'dark', deviceScaleFactor: w < 700 ? 2 : 1 });
    await ctx.route(/supabase\.co\//, (r) => { const m = r.request().url().match(/rest\/v1\/([a-z_]+)/); return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} }); });
    const pg = await ctx.newPage(); const errs = []; pg.on('pageerror', (e) => errs.push(e.message));
    await pg.goto('http://127.0.0.1:8080/'); await pg.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
    await pg.goto('http://127.0.0.1:8080/?repeat=true'); await pg.waitForTimeout(6000);
    const banner = pg.locator('[data-testid="repeat-filter-banner"]');
    console.log(tag, 'banner:', (await banner.innerText()).replace(/\n/g, ' | '));
    const cells = await pg.locator('[data-tm-cell]').count(); const cars = await pg.locator('section[data-formation] .grid > div').count();
    console.log(tag, 'cells', cells, 'car boxes', cars);
    await pg.screenshot({ path: `${S}/ui3/${tag}_repeat.png` });
    await pg.getByRole('link', { name: '전체 보기' }).click(); await pg.waitForTimeout(1500);
    console.log(tag, 'after clear cells', await pg.locator('[data-tm-cell]').count(), 'url', pg.url());
    console.log(tag, 'errors', errs); await ctx.close();
  }
  await b.close();
})();
