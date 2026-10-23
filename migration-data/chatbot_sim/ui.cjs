const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const S = '/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad';
const D = JSON.parse(fs.readFileSync(S + '/realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(S + '/extra.json', 'utf8'));
const insp = [
  { id: 1, created_at: '2026-04-01', inspected_on: '2026-04-01', serial: '88091-48', location: '111-1511-TM3', insulation_mohm: 120, brush_mm: 38, bearing_temp_c: 41, abnormal_noise: false, note: null, nickname: '시험', brush_spring_kg: 2.9, photo_path: null, ai_finding: null },
  { id: 2, created_at: '2026-07-10', inspected_on: '2026-07-10', serial: '88091-48', location: '111-1511-TM3', insulation_mohm: 45, brush_mm: 33, bearing_temp_c: 44, abnormal_noise: false, note: '정류자 그을림 약간', nickname: '시험', brush_spring_kg: 2.8, photo_path: null, ai_finding: null },
  { id: 3, created_at: '2026-10-20', inspected_on: '2026-10-20', serial: '88091-48', location: '111-1511-TM3', insulation_mohm: 4.2, brush_mm: 29, bearing_temp_c: 47, abnormal_noise: true, note: null, nickname: '시험', brush_spring_kg: 3.4, photo_path: null, ai_finding: '주의 — 정류자 표면 일부 흑화로 보임' },
];
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, tm_inspections: insp, ...X };
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const [w, h, tag] of [[390, 844, 'm390'], [1280, 900, 'pc']]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: w < 700, hasTouch: w < 700, colorScheme: 'dark', deviceScaleFactor: w < 700 ? 2 : 1 });
    await ctx.route(/supabase\.co\//, (r) => { const req = r.request(); if (req.method() !== 'GET') return r.fulfill({ status: 403, json: {} }); const m = req.url().match(/rest\/v1\/([a-z_]+)/); return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} }); });
    const pg = await ctx.newPage();
    const errs = []; pg.on('pageerror', (e) => errs.push(e.message));
    await pg.goto('http://127.0.0.1:8080/'); await pg.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
    await pg.goto('http://127.0.0.1:8080/asset-report?serial=98TWDH393'); await pg.waitForTimeout(6000); await pg.locator('[data-testid="inspections"]').scrollIntoViewIfNeeded(); await pg.screenshot({ path: `${S}/ui3/${tag}_empty.png` });
    await pg.goto('http://127.0.0.1:8080/asset-report?serial=88091-48'); await pg.waitForTimeout(6000);
    const sec = pg.locator('[data-testid="inspections"]');
    await sec.scrollIntoViewIfNeeded();
    console.log(tag, 'report flags:', (await sec.innerText()).split('\n').slice(0, 8).join(' | '));
    const ov = await sec.evaluate((el) => [el.scrollWidth, el.clientWidth, document.documentElement.scrollWidth, window.innerWidth]);
    console.log(tag, 'overflow sec/page', ov);
    await pg.screenshot({ path: `${S}/ui3/${tag}_report.png`, fullPage: false });
    pg.on('request', (q) => { if (q.method() === 'POST' && !/supabase/.test(q.url())) console.log(tag, 'POST', q.url().slice(0, 120)); });
    await pg.route((u) => /_server|serverFn/i.test(u.href) && !/supabase/.test(u.href), (r) => r.fulfill({ status: 200, headers: { 'content-type': 'application/json' }, json: { result: { state: '주의', summary: '정류자 표면 일부 흑화·브러시 편마모로 보임' } } }));
    await pg.getByRole('button', { name: /점검 기록 남기기/ }).first().click(); await pg.waitForTimeout(600); await pg.screenshot({ path: `${S}/ui3/${tag}_dialog0.png` }); await pg.getByRole('button', { name: /더 적기/ }).click(); await pg.waitForTimeout(300);
    const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAD0lEQVQImWNgYGD4z8DAAAAEAQH+ZGl5AAAAAElFTkSuQmCC', 'base64');
    await pg.locator('[data-testid="inspection-photo-input"]').setInputFiles({ name: 'tm.png', mimeType: 'image/png', buffer: png }); await pg.waitForTimeout(3500);
    console.log(tag, 'photo finding:', await pg.locator('[data-testid="inspections"] textarea').inputValue().catch(() => 'no textarea'));
    await pg.waitForTimeout(300);
    await pg.screenshot({ path: `${S}/ui3/${tag}_form.png` }); await pg.keyboard.press('Escape'); await pg.waitForTimeout(400);
    await pg.unrouteAll({ behavior: 'ignoreErrors' }); await ctx.route(/supabase\.co\//, (r) => { const req = r.request(); if (req.method() !== 'GET') return r.fulfill({ status: 403, json: {} }); const m = req.url().match(/rest\/v1\/([a-z_]+)/); return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} }); });
    await pg.goto('http://127.0.0.1:8080/repair'); await pg.waitForTimeout(5000);
    await pg.locator('textarea').first().fill('주행 중 GR 점등 및 절연페인트 박리'); await pg.waitForTimeout(400);
    const ai = pg.getByRole('button', { name: 'AI 의견 보기' });
    await ai.scrollIntoViewIfNeeded(); await ai.click(); await pg.waitForTimeout(4000);
    await pg.screenshot({ path: `${S}/ui3/${tag}_repair.png` });
    console.log(tag, 'repair ai box:', (await pg.locator('text=AI는 참고 의견').locator('..').innerText()).replace(/\n/g, ' | '));
    await pg.goto('http://127.0.0.1:8080/data-management'); await pg.waitForTimeout(5000);
    const t = pg.getByRole('tab', { name: /데이터 점검/ }); if (await t.count()) await t.first().click(); await pg.waitForTimeout(1500);
    const card = pg.locator('[data-testid="fault-accuracy"]');
    if (await card.count()) { await card.scrollIntoViewIfNeeded(); console.log(tag, 'accuracy:', (await card.innerText()).replace(/\n/g, ' | ').slice(0, 300)); await pg.screenshot({ path: `${S}/ui3/${tag}_acc.png` }); }
    else console.log(tag, 'no accuracy card; tabs:', await pg.getByRole('tab').allInnerTexts());
    const lst = pg.locator('[data-check="faultNoSerial"]'); console.log(tag, 'faultNoSerial count', await lst.getAttribute('data-count').catch(() => 'none'));
    console.log(tag, 'errors', errs);
    await ctx.close();
  }
  await b.close();
})();
