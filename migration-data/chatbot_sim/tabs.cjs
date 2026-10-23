const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const S = '/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad';
const D = JSON.parse(fs.readFileSync(S + '/realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(S + '/extra.json', 'utf8'));
const insp = [{ id: 1, created_at: '2026-10-20', inspected_on: '2026-10-20', serial: '88091-48', location: '111-1511-TM3', insulation_mohm: 4.2, brush_mm: 29, brush_spring_kg: 3.4, bearing_temp_c: 47, abnormal_noise: true, photo_path: null, ai_finding: '주의 — 정류자 표면 일부 흑화로 보임', note: null, nickname: '시험' }];
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, tm_inspections: insp, ...X };
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const [w, h, tag] of [[390, 844, 'm390'], [1280, 900, 'pc']]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: w < 700, hasTouch: w < 700, colorScheme: 'dark', deviceScaleFactor: w < 700 ? 2 : 1 });
    await ctx.route(/supabase\.co\//, (r) => { const m = r.request().url().match(/rest\/v1\/([a-z_]+)/); return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} }); });
    const pg = await ctx.newPage(); const errs = []; pg.on('pageerror', (e) => errs.push(e.message));
    await pg.goto('http://127.0.0.1:8080/'); await pg.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
    for (const t of ['today', 'status', 'analysis']) {
      await pg.goto(`http://127.0.0.1:8080/dashboard?tab=${t}`); await pg.waitForTimeout(6000);
      const hs = await pg.evaluate(() => [...document.querySelectorAll('h2')].map((e) => e.textContent.trim().slice(0, 22)));
      const ph = await pg.evaluate(() => document.documentElement.scrollHeight);
      console.log(tag, t, 'h2:', hs.join(' | '), '| page height', ph);
      await pg.screenshot({ path: `${S}/ui3/tabs_${tag}_${t}.png` });
    }
    await pg.goto('http://127.0.0.1:8080/'); await pg.waitForTimeout(5000);
    await pg.locator('[data-testid="formation-chips"] button', { hasText: '113' }).click(); await pg.waitForTimeout(800);
    console.log(tag, 'formation 113 → sections:', await pg.locator('section[data-formation]').count(), 'cells', await pg.locator('[data-tm-cell]').count());
    await pg.screenshot({ path: `${S}/ui3/tabs_${tag}_form113.png` });
    await pg.goto('http://127.0.0.1:8080/asset-report?serial=88091-48'); await pg.waitForTimeout(6000);
    const titles = await pg.evaluate(() => [...document.querySelectorAll('h3')].map((e) => e.textContent.trim()).filter((t) => /^\d\./.test(t)));
    console.log(tag, 'report sections:', titles.join(' | '));
    const lc = pg.locator('[data-testid="lifecycle"]'); await lc.scrollIntoViewIfNeeded();
    console.log(tag, 'lifecycle:', (await lc.innerText()).replace(/\n/g, ' | ').slice(0, 400));
    await pg.screenshot({ path: `${S}/ui3/tabs_${tag}_life.png` });
    await pg.goto('http://127.0.0.1:8080/asset-report?serial=88091-48&inspect=1'); await pg.waitForTimeout(5000);
    console.log(tag, 'inspect=1 dialog open:', await pg.locator('[data-testid="inspection-form"]').count());
    console.log(tag, 'errors', errs); await ctx.close();
  }
  await b.close();
})();
