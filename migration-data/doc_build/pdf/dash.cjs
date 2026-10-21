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
  const c = await b.newContext({ viewport: { width: 1280, height: 1000 }, colorScheme: 'dark', deviceScaleFactor: 2 });
  await route(c); const p = await c.newPage();
  await p.goto(U + '/'); await p.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await p.goto(U + '/dashboard'); await wait(p, 9000);
  await p.addStyleTag({ content: '[class*="fixed"]:not(aside):not(aside *),[class*="sticky"]{visibility:hidden !important}' });
  const info = await p.evaluate(() => {
    const r = e => { const b = e.getBoundingClientRect(); return [b.left, b.top + scrollY, b.width, b.height]; };
    const byText = (sel, re) => [...document.querySelectorAll(sel)].filter(e => re.test((e.innerText || '').trim()));
    const smallest = els => els.sort((a, b) => a.getBoundingClientRect().height - b.getBoundingClientRect().height)[0];
    const banner = smallest(byText('div,section', /^지난 확인 이후/).filter(e => e.querySelector('button')));
    const today = smallest(byText('div,section', /^오늘 확인할 것/).filter(e => e.getBoundingClientRect().height > 150));
    const risk = document.querySelector('section[aria-label="조치 필요"]');
    const health = smallest(byText('div,section', /^차량 건강 요약/).filter(e => e.getBoundingClientRect().height > 150));
    const main = document.querySelector('main');
    return { banner: r(banner), today: r(today), risk: r(risk), health: r(health), main: r(main) };
  });
  console.log(JSON.stringify(info));
  fs.writeFileSync(OUT + '/dash.json', JSON.stringify(info));
  await p.screenshot({ path: OUT + '/dash_full.png', fullPage: true });
  await b.close();
})();
