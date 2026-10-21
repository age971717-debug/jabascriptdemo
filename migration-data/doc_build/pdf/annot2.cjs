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
  // 현황판
  let p = await mk(844);
  await p.goto(U + '/'); await wait(p, 6000);
  await save(p, 'board', [
    [1, 'textAll', 'button', '^(전체|긴급|주의|관찰|정상|예비품|불용대기) \\d+$'],
    [2, 'css', 'input[placeholder*="시리얼"]'],
    [3, 'css', '[data-tm-cell]'],
    [4, 'css', 'button[aria-label="TM 챗봇 열기"]'],
    [5, 'css', 'nav[aria-label="주요 화면 바로가기"]'],
    [6, 'css', 'button[aria-label="메뉴 열기"]'],
  ]);
  // TM 상세(긴급 TM)
  p = await mk(1300);
  await p.goto(U + '/'); await wait(p, 6000);
  await p.locator('[data-tm-cell]', { hasText: '88091-48' }).first().tap(); await wait(p, 1800);
  await save(p, 'detail', [
    [1, 'text', 'a,button', '^TM 리포트 열기'],
    [2, 'text', 'a,button', '^이 TM 수선의뢰'],
    [3, 'sec', '기본 정보'],
    [4, 'sec', '위험도 산출 근거'],
    [5, 'sec', '고장 이력'],
  ], { rootClip: '[role="dialog"]' });
  // TM 리포트
  p = await mk(844);
  await p.goto(U + '/asset-report?serial=88091-48'); await wait(p, 6000); await p.addStyleTag({ content: HIDE });
  await save(p, 'report', [
    [1, 'textAll', 'input,button', '^(시리얼 검색|조회)$'],
    [2, 'row', '긴급·주의'],
    [3, 'row', '반복 고장 위치'],
    [4, 'row', '최근 조회'],
    [5, 'textAll', 'button', '^(즐겨찾기|인쇄)$'],
    [6, 'textAll', 'button', '^(PDF|HWP) 다운로드$'],
    [7, 'textAll', 'button', '^(DOCX 다운로드|QR 라벨)$'],
    [8, 'text', 'a,button', '^이 TM 수선의뢰$'],
    [9, 'textAll', 'button', '^(링크로|텍스트 요약으로)$'],
  ], { full: true });
  // 수선의뢰
  p = await mk(844);
  await p.goto(U + '/repair'); await wait(p, 5000);
  await p.locator('#repair-detail').fill('주행 중 2,4위 브러쉬홀더 절손 및 용융'); await wait(p, 1500); await p.addStyleTag({ content: HIDE });
  await save(p, 'repair', [
    [1, 'text', 'a', '^표준 기록지 다운로드'],
    [2, 'text', 'label', '^교체일자'],
    [3, 'text', 'label', '^편성'],
    [4, 'text', 'label', '^취거 TM'],
    [5, 'text', 'label', '^취거품 상태'],
    [6, 'css', '#repair-detail'],
    [7, 'css', 'button[aria-label*="말로"]'],
    [8, 'row', '고장코드'],
    [9, 'row', '관련 수선 절차 보기'],
    [10, 'text', 'label', '^부착 TM'],
    [11, 'textAll', 'button,p', '^(카메라로 찍기|앨범에서 고르기|0/10장)'],
    [12, 'text', 'button', '^수선의뢰 등록$'],
  ], { full: true });
  // 현장 의견
  p = await mk(844);
  await p.goto(U + '/'); await wait(p, 5000);
  await p.getByRole('button', { name: '현장 의견 보내기' }).first().tap(); await wait(p, 1500);
  await save(p, 'feedback', [
    [1, 'textAll', '[role="dialog"] button', '^(불편|개선|오류)$'],
    [2, 'css', '[role="dialog"] button[aria-label*="말로"]'],
    [3, 'css', '[role="dialog"] textarea'],
    [4, 'css', '[role="dialog"] input'],
    [5, 'text', '[role="dialog"] p,[role="dialog"] div', '함께 (보냄|저장)'],
    [6, 'text', '[role="dialog"] button', '^보내기$'],
  ], { rootClip: '[role="dialog"]' });
  await b.close();
  fs.writeFileSync(OUT + '/boxes.json', JSON.stringify(RES, null, 1));
})();
