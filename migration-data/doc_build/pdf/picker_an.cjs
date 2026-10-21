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
  const m = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, colorScheme: 'dark', deviceScaleFactor: 3 });
  await route(m); const p = await m.newPage();
  await p.goto(U + '/'); await p.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await p.goto(U + '/dashboard?tab=analysis'); await wait(p, 9000);
  await p.addStyleTag({ content: '[class*="fixed"],[class*="sticky"]{visibility:hidden !important}' });
  await p.getByRole('button', { name: /위젯 선택/ }).first().tap(); await wait(p, 800);
  const info = await p.evaluate(() => {
    const r = e => { const b = e.getBoundingClientRect(); return [b.left, b.top + scrollY, b.width, b.height]; };
    const btn = [...document.querySelectorAll('button')].find(x => /위젯 선택/.test(x.innerText));
    const tabs = document.querySelector('[aria-label="대시보드 보기"]');
    const labels = [...document.querySelectorAll('label')].filter(l => l.querySelector('input[type=checkbox]'));
    const u = els => { let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9; els.forEach(e=>{const [x,y,w,h]=r(e); x0=Math.min(x0,x); y0=Math.min(y0,y); x1=Math.max(x1,x+w); y1=Math.max(y1,y+h);}); return [x0,y0,x1-x0,y1-y0]; };
    const resets = [...document.querySelectorAll('button')].filter(x => /이 탭 모두 표시|배치 초기화/.test(x.innerText));
    return { tabs: r(tabs), btn: r(btn), labels: u(labels), resets: u(resets), n: labels.length, texts: labels.map(l => l.innerText.trim() + (l.querySelector('input').checked ? '(on)' : '(off)')) };
  });
  console.log(JSON.stringify(info));
  fs.writeFileSync(OUT + '/picker_an.json', JSON.stringify(info));
  await p.screenshot({ path: OUT + '/picker_an_full.png', fullPage: true });
  await b.close();
})();
