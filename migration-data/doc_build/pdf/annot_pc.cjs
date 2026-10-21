// 가이드용 번호 화면: 실제 요소 위치(DOM)로 상자 좌표를 구한다. 화면은 실데이터 사본, 저장 동작 없음.
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const OUT = __dirname + '/a2', U = 'http://127.0.0.1:8080';
fs.mkdirSync(OUT, { recursive: true });
const D = JSON.parse(fs.readFileSync(__dirname + '/../realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(__dirname + '/../extra.json', 'utf8'));
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, ...X };
const route = (ctx) => ctx.route(/supabase\.co\//, (r) => {
  const m = r.request().url().match(/rest\/v1\/([a-z_]+)/);
  if (r.request().method() !== 'GET' && m && m[1] !== 'rpc') return r.fulfill({ status: 403, json: {} });
  return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} });
});
const wait = (p, ms) => p.waitForTimeout(ms);
const HIDE = '[class*="fixed"]:not([role="dialog"]):not([role="dialog"] *):not([data-state]),[class*="sticky"]{visibility:hidden !important}';

// spec: [n, kind, arg...] → 페이지 좌표 상자(여러 요소면 합친 상자)
async function boxes(p, specs, root) {
  return p.evaluate(({ specs, root }) => {
    const R = root ? document.querySelector(root) : document;
    const txt = e => (e.innerText || e.getAttribute('aria-label') || e.placeholder || '').replace(/\s+/g, ' ').trim();
    const vis = e => { const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
    const all = sel => [...R.querySelectorAll(sel)].filter(vis);
    const find = {
      css: (sel) => all(sel).slice(0, 1),
      cssAll: (sel) => all(sel),
      text: (sel, re) => all(sel).filter(e => new RegExp(re).test(txt(e))).slice(0, 1),
      textAll: (sel, re) => all(sel).filter(e => new RegExp(re).test(txt(e))),
      // 글자로 시작하는 가장 작은 덩어리(그 안에 버튼·입력이 있는 것)
      row: (start) => { const c = all('div,section,fieldset,label').filter(e => txt(e).startsWith(start) && e.querySelector('button,a,input,select'));
        c.sort((a, b) => a.getBoundingClientRect().height * a.getBoundingClientRect().width - b.getBoundingClientRect().height * b.getBoundingClientRect().width); return c.slice(0, 1); },
      // h3 제목을 가진 section
      sec: (title) => all('section').filter(s => { const h = s.querySelector('h2,h3,h4'); return h && txt(h).startsWith(title); }).slice(0, 1),
    };
    return specs.map(([n, kind, ...arg]) => {
      const els = find[kind](...arg);
      if (!els.length) return [n, null];
      let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      els.forEach(e => { const b = e.getBoundingClientRect(); x0 = Math.min(x0, b.left); y0 = Math.min(y0, b.top + scrollY); x1 = Math.max(x1, b.right); y1 = Math.max(y1, b.bottom + scrollY); });
      return [n, [x0, y0, x1 - x0, y1 - y0]];
    });
  }, { specs, root });
}
const RES = {};
async function save(p, name, specs, opt = {}) {
  await wait(p, 500);
  const b = await boxes(p, specs, opt.root);
  b.forEach(([n, bx]) => { if (!bx) console.log('  MISSING', name, n); });
  let clip = opt.clip;
  if (opt.rootClip) { clip = await p.evaluate(sel => { const b = document.querySelector(sel).getBoundingClientRect(); return [b.left, b.top + scrollY, b.width, b.height]; }, opt.rootClip); }
  await p.screenshot({ path: `${OUT}/${name}.png`, fullPage: !!opt.full });
  RES[name] = { dpr: 3, boxes: b, clip };
  console.log('shot', name);
}
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const mk = async (h) => { const c = await b.newContext({ viewport: { width: 390, height: h }, isMobile: true, hasTouch: true, colorScheme: 'dark', deviceScaleFactor: 3 });
    await route(c); const p = await c.newPage(); await p.goto(U + '/'); await p.evaluate(() => localStorage.setItem('tm-site-gate', 'granted')); return p; };
  const c = await b.newContext({ viewport: { width: 1280, height: 860 }, colorScheme: 'dark', deviceScaleFactor: 3 });
  await route(c); const p = await c.newPage();
  await p.goto(U + '/'); await p.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await p.goto(U + '/'); await wait(p, 6000);
  await save(p, 'pcnav', [
    [1, 'text', '[data-sidebar="menu-button"]', '^취부현황판'],
    [2, 'text', '[data-sidebar="menu-button"]', '^TM 리포트'],
    [3, 'text', '[data-sidebar="menu-button"]', '^수선의뢰'],
    [4, 'text', '[data-sidebar="menu-button"]', '^고장 이력'],
    [5, 'text', '[data-sidebar="menu-button"]', '^대시보드'],
    [6, 'text', '[data-sidebar="menu-button"]', '^문서'],
    [7, 'text', '[data-sidebar="group-label"]', '^관리'],
  ], { rootClip: '[data-sidebar="sidebar"]' });
  await b.close();
  const old = JSON.parse(fs.readFileSync(OUT + '/boxes.json', 'utf8')); Object.assign(old, RES); fs.writeFileSync(OUT + '/boxes.json', JSON.stringify(old, null, 1));
})();
