const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const S = '/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad';
const D = JSON.parse(fs.readFileSync(S + '/realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(S + '/extra.json', 'utf8'));
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, tm_inspections: [], equipment_type_configs: [], ...X };
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const [w, h, tag] of [[390, 844, 'm390'], [1280, 900, 'pc']]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: w < 700, hasTouch: w < 700, colorScheme: 'dark', deviceScaleFactor: w < 700 ? 2 : 1 });
    await ctx.route(/supabase\.co\//, (r) => { const m = r.request().url().match(/rest\/v1\/([a-z_]+)/); return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} }); });
    const pg = await ctx.newPage(); const errs = []; pg.on('pageerror', (e) => errs.push(e.message));
    await pg.goto('http://127.0.0.1:8080/'); await pg.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
    await pg.goto('http://127.0.0.1:8080/dashboard'); await pg.waitForTimeout(6000);
    const nav = pg.locator('[data-testid="dash-quicknav"]');
    console.log(tag, 'nav:', (await nav.innerText()).replace(/\n/g, ' | '));
    await pg.screenshot({ path: `${S}/ui3/nav_${tag}_top.png` });
    await nav.getByRole('button', { name: '예방정비 임박 TM' }).click(); await pg.waitForTimeout(1200);
    const y = await pg.evaluate(() => { const el = document.querySelector('[data-section="predictive"]'); return el ? Math.round(el.getBoundingClientRect().top) : null; });
    console.log(tag, 'predictive top after jump:', y);
    await pg.screenshot({ path: `${S}/ui3/nav_${tag}_jump.png` });
    if (w < 700) { const btn = pg.locator('[data-section="predictive"] button[aria-label="접기"]'); await btn.click(); await pg.waitForTimeout(400); console.log(tag, 'collapsed h:', await pg.evaluate(() => document.querySelector('[data-section="predictive"]').getBoundingClientRect().height)); await pg.screenshot({ path: `${S}/ui3/nav_${tag}_collapsed.png` }); }
    await pg.goto('http://127.0.0.1:8080/'); await pg.waitForTimeout(4000);
    console.log(tag, 'title:', await pg.title(), '| nav label:', await pg.locator('nav, aside').first().innerText().then((t) => (t.match(/통합현황판|취부현황판/) ?? ['none'])[0]));
    if (w >= 700) { await pg.screenshot({ path: `${S}/ui3/nav_${tag}_home.png` }); }
    await pg.goto('http://127.0.0.1:8080/asset-report?serial=98TWDH393'); await pg.waitForTimeout(5000);
    await pg.getByRole('button', { name: /점검 기록 남기기/ }).first().click(); await pg.waitForTimeout(600);
    console.log(tag, 'form fields:', await pg.locator('[data-testid="inspection-form"] input, [data-testid="inspection-form"] button[role="radio"]').count(), 'more btn:', await pg.getByRole('button', { name: /더 적기/ }).count());
    if (w < 700) await pg.screenshot({ path: `${S}/ui3/nav_${tag}_form.png` });
    console.log(tag, 'errors', errs); await ctx.close();
  }
  await b.close();
})();
