// 결과보고서용 고화질 화면 — 로컬 개발 서버 + 실제 데이터 사본(읽기 전용), 저장 동작 없음.
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const OUT = __dirname + '/rimg', U = 'http://127.0.0.1:8080';
fs.mkdirSync(OUT, { recursive: true });
const D = JSON.parse(fs.readFileSync(__dirname + '/../realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(__dirname + '/../extra.json', 'utf8'));
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, ...X };
const route = (ctx) => ctx.route(/supabase\.co\//, (r) => {
  const m = r.request().url().match(/rest\/v1\/([a-z_]+)/);
  if (r.request().method() !== 'GET' && m && m[1] !== 'rpc') return r.fulfill({ status: 403, json: {} });
  return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} });
});
const TOP = 46;
const wait = (p, ms) => p.waitForTimeout(ms);
async function el(p, name, loc, pad = 0) {
  const l = loc.first(); await l.scrollIntoViewIfNeeded().catch(() => {}); await wait(p, 700);
  const b = await l.boundingBox(); if (!b) { console.log('no box', name); return; }
  await p.screenshot({ path: `${OUT}/${name}.png`, clip: { x: Math.max(0, b.x - pad), y: Math.max(0, b.y - pad + TOP), width: b.width + 2 * pad, height: b.height + 2 * pad - TOP } });
  console.log('shot', name, Math.round(b.width), Math.round(b.height));
}
async function full(p, name) { await wait(p, 600); await p.screenshot({ path: `${OUT}/${name}.png` }); console.log('shot', name); }
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const m = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, colorScheme: 'dark', deviceScaleFactor: 3 });
  await route(m);
  const p = await m.newPage();
  await p.goto(U + '/'); await p.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await p.goto(U + '/dashboard'); await wait(p, 8000); await p.addStyleTag({ content: '[class*="fixed"],[class*="sticky"]{visibility:hidden !important}' });
  for (const t of ['편성 건강 현황판', '위험도 상위 5대']) {
    const h = p.getByText(t, { exact: true }).first();
    if (await h.count()) await el(p, 'm_w_' + t.replace(/ /g, ''), h.locator('xpath=ancestor::*[contains(@class,"rounded")][1]'), 0);
  }
  await p.goto(U + '/dashboard?tab=analysis'); await wait(p, 9000); await p.addStyleTag({ content: '[class*="fixed"],[class*="sticky"]{visibility:hidden !important}' });
  for (const t of ['제조사별 신뢰도 비교', '제작년도별 고장 현황', '고장유형별 발생 건수']) {
    const h = p.getByText(t, { exact: true }).first();
    if (await h.count()) { await h.scrollIntoViewIfNeeded(); await p.evaluate(() => window.scrollBy(0, -200)); await wait(p, 800);
      await el(p, 'm_w_' + t.replace(/ /g, ''), h.locator('xpath=ancestor::*[contains(@class,"rounded")][1]'), 0); }
  }
  await p.goto(U + '/asset-report?serial=88091-48'); await wait(p, 6000); await p.addStyleTag({ content: '[class*="fixed"],[class*="sticky"]{visibility:hidden !important}' });
  await p.screenshot({ path: OUT + '/m_report_full.png', fullPage: true }); console.log('shot m_report_full');
  await m.close();
  await b.close();
})();
