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
  const m = await b.newContext({ viewport: { width: 390, height: 1400 }, isMobile: true, hasTouch: true, colorScheme: 'dark', deviceScaleFactor: 3 });
  await route(m); const p = await m.newPage();
  await p.goto(U + '/'); await p.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await p.goto(U + '/repair'); await wait(p, 5000);
  await p.addStyleTag({ content: '[class*="fixed"],[class*="sticky"]{visibility:hidden !important}' });
  await p.addStyleTag({ content: 'select option:checked{background:linear-gradient(#2E75B6,#2E75B6)!important;color:#fff!important}' });
  await p.locator('#repair-detail').fill('주행 중 2,4위 브러쉬홀더 절손 및 용융'); await wait(p, 1500);
  const info = await p.evaluate(() => {
    const sel = [...document.querySelectorAll('select')].find(s => [...s.options].some(o => o.text.startsWith('정기교체')));
    sel.size = sel.options.length; sel.style.height = 'auto'; sel.style.width = '100%'; sel.style.fontSize = '11.5px'; sel.style.letterSpacing = '-0.4px'; sel.style.paddingLeft = '2px'; sel.style.paddingRight = '2px'; sel.style.overflow = 'hidden'; sel.style.paddingTop = '4px'; sel.style.paddingBottom = '4px';
    [...sel.options].forEach(o => { o.style.padding = '6px 5px'; });
    let box = sel.parentElement; while (box && !/^고장코드 자동 분류/.test((box.innerText || '').trim())) box = box.parentElement;
    box.scrollIntoView({ block: 'center' });
    const r = e => { const b = e.getBoundingClientRect(); return [b.left, b.top + scrollY, b.width, b.height]; };
    const detail = document.querySelector('#repair-detail');
    return { box: r(box), sel: r(sel), detail: r(detail) };
  });
  console.log(JSON.stringify(info));
  fs.writeFileSync(OUT + '/fc.json', JSON.stringify(info));
  await wait(p, 600);
  await p.screenshot({ path: OUT + '/fc_full.png', fullPage: true });
  await b.close();
})();
