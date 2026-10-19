const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const OUT = __dirname + '/img', U = 'http://127.0.0.1:8080';
const D = JSON.parse(fs.readFileSync(__dirname + '/../realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(__dirname + '/../extra.json', 'utf8'));
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, ...X };
const route = (ctx) => ctx.route(/supabase\.co\//, (r) => { const m = r.request().url().match(/rest\/v1\/([a-z_]+)/);
  if (r.request().method() !== 'GET' && m && m[1] !== 'rpc') return r.fulfill({ status: 403, json: {} });
  return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} }); });
const BOX = JSON.parse(fs.readFileSync(__dirname + '/boxes.json', 'utf8'));
async function shot(page, name, marks = []) {
  await page.waitForTimeout(600); const boxes = [];
  for (const [label, loc] of marks) { try { const l = loc.first(); if (!(await l.count())) { console.log('no mark', name, label); continue; } const b = await l.boundingBox(); if (b) boxes.push({ label, ...b }); } catch (e) {} }
  await page.screenshot({ path: `${OUT}/${name}.png` }); BOX[name] = { dpr: page.__dpr, boxes }; console.log('shot', name, boxes.length);
}
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const m = await b.newContext({ viewport: { width: 390, height: 760 }, isMobile: true, hasTouch: true, colorScheme: 'dark', deviceScaleFactor: 2 });
  await route(m); const p = await m.newPage(); p.__dpr = 2;
  await p.goto(U + '/'); await p.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await p.goto(U + '/'); await p.waitForTimeout(5000);
  await p.getByRole('button', { name: /긴급/ }).first().tap(); await p.waitForTimeout(1500);
  await shot(p, 'm_board_critical', [['1', p.getByRole('button', { name: /긴급/ })], ['2', p.locator('[data-tm-cell]')]]);
  await m.close();
  const c = await b.newContext({ viewport: { width: 1280, height: 800 }, colorScheme: 'dark', deviceScaleFactor: 1.25 });
  await route(c); const q = await c.newPage(); q.__dpr = 1.25;
  await q.goto(U + '/'); await q.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await q.goto(U + '/'); await q.waitForTimeout(5000);
  await q.getByRole('button', { name: /데이터 내보내기/ }).first().click(); await q.waitForTimeout(1000);
  await shot(q, 'pc_export', [['1', q.getByRole('menu').or(q.getByRole('dialog'))]]);
  await q.keyboard.press('Escape');
  await q.goto(U + '/records'); await q.waitForTimeout(4500);
  const row = q.locator('tbody tr').first(); if (await row.count()) { await row.click(); await q.waitForTimeout(1500); }
  await shot(q, 'pc_record_edit', [['1', q.getByRole('dialog')]]);
  await b.close();
  fs.writeFileSync(__dirname + '/boxes.json', JSON.stringify(BOX, null, 1));
})();
