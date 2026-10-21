// 결과보고서용 고화질 화면 — 로컬 개발 서버 + 실제 데이터 사본(읽기 전용), 저장 동작 없음.
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const OUT = __dirname + '/v12', U = 'http://127.0.0.1:8080';
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
  // PC 리포트 카드(시스템에 보이는 그대로)
  const c = await b.newContext({ viewport: { width: 1100, height: 900 }, colorScheme: 'dark', deviceScaleFactor: 2 });
  await route(c); const q = await c.newPage();
  await q.goto(U + '/'); await q.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await q.goto(U + '/asset-report?serial=88091-48'); await wait(q, 7000);
  await q.addStyleTag({ content: '[class*="fixed"]:not(aside *):not(aside),[class*="sticky"]{visibility:hidden !important}' });
  const info = await q.evaluate(() => {
    const els = [...document.querySelectorAll('div,section,article')].filter(e => /견\s*인\s*전\s*동\s*기\s*고\s*장\s*이\s*력/.test(e.innerText || '') && /관련 정비 문서/.test(e.innerText || ''));
    els.sort((a, b) => a.getBoundingClientRect().height - b.getBoundingClientRect().height);
    const card = els[0], r = card.getBoundingClientRect();
    const hs = [...card.querySelectorAll('h2,h3,h4')].filter(h => /^[1-4]\./.test(h.innerText.trim())).map(h => { const b = h.getBoundingClientRect(); return [h.innerText.trim(), b.left - r.left, b.top - r.top, b.width, b.height]; });
    return { card: [r.left, r.top + scrollY, r.width, r.height], hs };
  });
  console.log(JSON.stringify(info));
  fs.writeFileSync(OUT + '/report_card.json', JSON.stringify(info));
  const [x, y, w, h] = info.card;
  await q.screenshot({ path: OUT + '/report_card.png', fullPage: true, clip: { x, y, width: w, height: h } });
  await c.close();
  // 휴대폰 위젯 추가분
  const m = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, colorScheme: 'dark', deviceScaleFactor: 3 });
  await route(m); const p = await m.newPage();
  await p.goto(U + '/'); await p.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await p.goto(U + '/dashboard'); await wait(p, 8000); await p.addStyleTag({ content: '[class*="fixed"],[class*="sticky"]{visibility:hidden !important}' });
  for (const t of ['반복 고장 위치', '예비품 현황', '예방정비 임박 TM', '편성별 위험 히트맵']) {
    const h = p.getByText(t, { exact: true }).first();
    if (await h.count()) await el(p, 'm_w_' + t.replace(/ /g, ''), h.locator('xpath=ancestor::*[contains(@class,"rounded")][1]'), 0); else console.log('none', t);
  }
  await p.goto(U + '/dashboard?tab=analysis'); await wait(p, 9000); await p.addStyleTag({ content: '[class*="fixed"],[class*="sticky"]{visibility:hidden !important}' });
  for (const t of ['등급별 분포', '월별 수선의뢰 추이']) {
    const h = p.getByText(t, { exact: true }).first();
    if (await h.count()) { await h.scrollIntoViewIfNeeded(); await p.evaluate(() => window.scrollBy(0, -200)); await wait(p, 800);
      await el(p, 'm_w_' + t.replace(/ /g, ''), h.locator('xpath=ancestor::*[contains(@class,"rounded")][1]'), 0); } else console.log('none', t);
  }
  await b.close();
})();
