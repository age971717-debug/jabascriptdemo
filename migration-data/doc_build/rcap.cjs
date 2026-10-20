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
const wait = (p, ms) => p.waitForTimeout(ms);
async function el(p, name, loc, pad = 0) {
  const l = loc.first(); await l.scrollIntoViewIfNeeded().catch(() => {}); await wait(p, 700);
  const b = await l.boundingBox(); if (!b) { console.log('no box', name); return; }
  await p.screenshot({ path: `${OUT}/${name}.png`, clip: { x: Math.max(0, b.x - pad), y: Math.max(0, b.y - pad), width: b.width + 2 * pad, height: b.height + 2 * pad } });
  console.log('shot', name, Math.round(b.width), Math.round(b.height));
}
async function full(p, name) { await wait(p, 600); await p.screenshot({ path: `${OUT}/${name}.png` }); console.log('shot', name); }
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  // ---------- 휴대폰 (DPR 3) ----------
  const m = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, colorScheme: 'dark', deviceScaleFactor: 3 });
  await route(m);
  const p = await m.newPage();
  await p.goto(U + '/'); await p.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await p.goto(U + '/'); await wait(p, 6000);
  await full(p, 'm_board');
  const cell = p.locator('[data-tm-cell]', { hasText: '88091-48' });
  if (await cell.count()) { await cell.first().scrollIntoViewIfNeeded(); await wait(p, 500); await full(p, 'm_board_88091'); await cell.first().tap(); await wait(p, 1800); await full(p, 'm_detail'); }
  await p.keyboard.press('Escape'); await wait(p, 500);
  // 대시보드 오늘 확인할 것
  await p.goto(U + '/dashboard'); await wait(p, 7000);
  await el(p, 'm_today', p.locator('section,div').filter({ has: p.getByText('오늘 확인할 것', { exact: true }) }).filter({ hasText: '리포트 확인' }).last(), 0);
  await full(p, 'm_dash');
  // 수선의뢰: 세부 고장내용 → 자동 분류·관련 절차
  await p.goto(U + '/repair'); await wait(p, 5000);
  const det = p.locator('#repair-detail');
  if (await det.count()) { await det.fill('주행 중 2,4위 브러쉬홀더 절손 및 용융'); await wait(p, 1500); await det.scrollIntoViewIfNeeded(); await p.evaluate(() => window.scrollBy(0, -120)); await wait(p, 600); await full(p, 'm_repair'); }
  // 챗봇
  await p.goto(U + '/'); await wait(p, 5000);
  await p.getByRole('button', { name: /챗봇|도우미|질문/ }).last().tap(); await wait(p, 2000);
  await full(p, 'm_chat');
  await p.locator('#chat-input').fill('116편성 1416호차 2TM 고장났어, 절연파괴야'); await p.keyboard.press('Enter'); await wait(p, 3500);
  await full(p, 'm_chat_repair');
  await m.close();
  // ---------- PC (DPR 2) ----------
  const c = await b.newContext({ viewport: { width: 1280, height: 900 }, colorScheme: 'dark', deviceScaleFactor: 2 });
  await route(c);
  const q = await c.newPage();
  await q.goto(U + '/'); await q.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await q.goto(U + '/'); await wait(q, 6000); await full(q, 'pc_board');
  await q.goto(U + '/dashboard'); await wait(q, 8000);
  for (const t of ['편성 건강 현황판', '위험도 상위 5대', '최근 12개월 고장 추이']) {
    const h = q.getByText(t, { exact: true }).first();
    if (await h.count()) await el(q, 'pc_w_' + t.replace(/ /g, ''), h.locator('xpath=ancestor::*[contains(@class,"rounded")][1]'), 0);
  }
  await full(q, 'pc_dash');
  await q.goto(U + '/dashboard?tab=analysis'); await wait(q, 9000);
  for (const t of ['제조사별 신뢰도 비교', '제작년도별 고장 현황', '고장유형별 발생 건수', '등급별 분포']) {
    const h = q.getByText(t, { exact: true }).first();
    if (await h.count()) await el(q, 'pc_w_' + t.replace(/ /g, ''), h.locator('xpath=ancestor::*[contains(@class,"rounded")][1]'), 0);
  }
  await q.goto(U + '/asset-report?serial=88091-48'); await wait(q, 6000); await full(q, 'pc_report');
  await b.close();
})();
