// 사용 가이드용 화면 캡처 — 로컬 개발 서버 + 실제 데이터 사본(읽기 전용), 저장 동작 없음.
// 화면마다 표시할 요소의 위치(boxes)를 함께 기록해 번호 표시(①②③)에 쓴다.
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const OUT = __dirname + '/img', U = 'http://127.0.0.1:8080';
fs.mkdirSync(OUT, { recursive: true });
const D = JSON.parse(fs.readFileSync(__dirname + '/../realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(__dirname + '/../extra.json', 'utf8'));
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, ...X };
const route = (ctx) => ctx.route(/supabase\.co\//, (r) => {
  const m = r.request().url().match(/rest\/v1\/([a-z_]+)/);
  if (r.request().method() !== 'GET' && m && m[1] !== 'rpc') return r.fulfill({ status: 403, json: {} });
  return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} });
});
const BOX = {};
async function shot(page, name, marks = [], full = false) {
  await page.waitForTimeout(600);
  const boxes = [];
  for (const [label, loc] of marks) {
    try {
      const l = loc.first(); if (!(await l.count())) { console.log('  no mark', name, label); continue; }
      const b = await l.boundingBox(); if (b) boxes.push({ label, ...b });
    } catch (e) { console.log('  mark err', name, label, e.message.split('\n')[0]); }
  }
  const sy = await page.evaluate(() => window.scrollY);
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: full });
  BOX[name] = { dpr: page.__dpr, scrollY: full ? 0 : 0, boxes: boxes.map(b => ({ ...b, y: full ? b.y + sy : b.y })) };
  console.log('shot', name, boxes.length);
}
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  // ---------------- 휴대폰 ----------------
  const m = await b.newContext({ viewport: { width: 390, height: 760 }, isMobile: true, hasTouch: true, colorScheme: 'dark', deviceScaleFactor: 2 });
  await route(m);
  const p = await m.newPage(); p.__dpr = 2;
  await p.goto(U + '/'); await p.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await p.goto(U + '/'); await p.waitForTimeout(5000);
  await shot(p, 'm_board', [
    ['1', p.getByRole('button', { name: /긴급/ })],
    ['2', p.getByPlaceholder(/시리얼/)],
    ['3', p.locator('[data-tm-cell]')],
    ['4', p.getByRole('button', { name: /챗봇|도우미|질문/ }).last()],
    ['5', p.locator('nav').last()],
    ['6', p.getByRole('button', { name: /데이터 내보내기/ })],
  ]);
  const cell = p.locator('[data-tm-cell]').first();
  await cell.tap(); await p.waitForTimeout(1500);
  await shot(p, 'm_detail', [
    ['1', p.getByRole('button', { name: /TM 리포트 열기/ }).or(p.getByRole('link', { name: /TM 리포트 열기/ }))],
    ['2', p.getByRole('button', { name: /이 TM 수선의뢰/ }).or(p.getByRole('link', { name: /이 TM 수선의뢰/ }))],
    ['3', p.getByText('위험도 산출 근거')],
  ]);
  await p.keyboard.press('Escape');
  // 리포트
  await p.goto(U + '/asset-report?serial=88091-48'); await p.waitForTimeout(5000);
  await shot(p, 'm_report', [
    ['1', p.getByRole('textbox').first()],
    ['2', p.getByText(/긴급·주의/).first()],
    ['3', p.getByText(/반복 고장 위치/).first()],
    ['4', p.getByRole('button', { name: /PDF/ })],
  ], true);
  // 수선의뢰 (입력만, 저장 안 함)
  await p.goto(U + '/repair'); await p.waitForTimeout(4500);
  const det = p.locator('#repair-detail');
  if (await det.count()) { await det.fill('주행 중 2,4위 브러쉬홀더 절손 및 용융'); await p.waitForTimeout(1500); }
  await shot(p, 'm_repair', [
    ['1', p.getByText(/표준 기록지/).first()],
    ['2', p.getByText('교체일자').first()],
    ['3', p.getByText(/취거 TM/).first()],
    ['4', p.locator('#repair-detail')],
    ['5', p.getByRole('button', { name: /음성으로 입력|마이크/ })],
    ['6', p.getByText(/고장코드 자동 분류/).first()],
    ['7', p.getByText(/관련 수선 절차/).first()],
  ], true);
  // 챗봇
  await p.goto(U + '/'); await p.waitForTimeout(4000);
  await p.getByRole('button', { name: /챗봇|도우미|질문/ }).last().tap(); await p.waitForTimeout(2000);
  await shot(p, 'm_chat', [
    ['1', p.getByText('현황 조회').first()],
    ['2', p.getByText('문서 검색').first()],
    ['3', p.locator('#chat-input')],
  ]);
  await p.getByRole('button', { name: '오늘 뭐부터 점검해야 돼?' }).first().tap().catch(() => {});
  await p.waitForTimeout(2500);
  await shot(p, 'm_chat_answer');
  await p.locator('#chat-input').fill('왜 긴급인지 알려줘'); await p.keyboard.press('Enter'); await p.waitForTimeout(2500);
  await shot(p, 'm_chat_reason');
  await p.locator('#chat-input').fill('116편성 1416호차 2TM 고장났어, 절연파괴야'); await p.keyboard.press('Enter'); await p.waitForTimeout(3000);
  await shot(p, 'm_chat_repair');
  // 현장 의견
  await p.goto(U + '/'); await p.waitForTimeout(4000);
  await p.getByRole('button', { name: '현장 의견 보내기' }).first().tap().catch(() => {}); await p.waitForTimeout(1200);
  await shot(p, 'm_feedback');
  await p.keyboard.press('Escape');
  // 휴대폰 이력·대시보드
  await p.goto(U + '/records'); await p.waitForTimeout(4500); await shot(p, 'm_records');
  await p.goto(U + '/dashboard'); await p.waitForTimeout(6000); await shot(p, 'm_dash');
  await m.close();

  // ---------------- PC ----------------
  const c = await b.newContext({ viewport: { width: 1280, height: 800 }, colorScheme: 'dark', deviceScaleFactor: 1.25 });
  await route(c);
  const q = await c.newPage(); q.__dpr = 1.25;
  await q.goto(U + '/'); await q.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  await q.goto(U + '/'); await q.waitForTimeout(5000);
  await q.locator('[data-tm-cell]').nth(2).click(); await q.waitForTimeout(1500);
  await shot(q, 'pc_board', [['1', q.locator('aside').first()], ['2', q.locator('[data-tm-cell]').nth(2)], ['3', q.getByText('위험도 산출 근거')], ['4', q.getByRole('button', { name: /현장 의견/ })], ['5', q.getByRole('button', { name: /스냅샷 저장/ })]]);
  for (const [name, url, wait, marks, full] of [
    ['pc_records', '/records', 4500, (pg) => [['1', pg.getByRole('tab').first()], ['2', pg.getByRole('combobox').first()]], false],
    ['pc_external', '/records?tab=external', 4500, () => [], false],
    ['pc_outsourcing', '/records?tab=outsourcing', 4500, () => [], false],
    ['pc_report', '/asset-report?serial=88091-48', 5000, (pg) => [['1', pg.getByRole('button', { name: /PDF/ })], ['2', pg.getByRole('button', { name: /QR 라벨/ })], ['3', pg.getByRole('button', { name: /인쇄/ })]], true],
    ['pc_dash', '/dashboard', 7000, (pg) => [['1', pg.getByRole('tab', { name: '현황' }).or(pg.getByText('현황', { exact: true }))], ['2', pg.getByRole('button', { name: /위젯 선택/ })]], true],
    ['pc_analysis', '/dashboard?tab=analysis', 8000, () => [], true],
    ['pc_docs', '/documents', 4000, () => [], false],
    ['pc_dm_manage', '/data-management?tab=manage', 4500, () => [], false],
    ['pc_check', '/data-management?tab=check', 4500, () => [], false],
    ['pc_changes', '/data-management?tab=changes', 4500, () => [], false],
    ['pc_dm_feedback', '/data-management?tab=feedback', 4500, () => [], false],
    ['pc_raw', '/raw-data', 4500, () => [], false],
    ['pc_integrity', '/integrity', 5000, () => [], false],
    ['pc_grade', '/grade-standards', 4500, () => [], true],
    ['pc_grade_settings', '/grade-standards?tab=settings', 4500, () => [], false],
    ['pc_expansion', '/expansion-settings', 4500, () => [], false],
    ['pc_help', '/help', 4500, () => [], false],
  ]) {
    await q.goto(U + url); await q.waitForTimeout(wait);
    if (full) { for (let i = 0; i < 8; i++) { await q.mouse.wheel(0, 500); await q.waitForTimeout(300); } await q.evaluate(() => window.scrollTo(0, 0)); await q.waitForTimeout(1500); }
    await shot(q, name, marks(q), full);
  }
  await q.goto(U + '/dashboard'); await q.waitForTimeout(6000);
  await q.getByRole('button', { name: /위젯 선택/ }).first().click(); await q.waitForTimeout(1000);
  await shot(q, 'pc_picker');
  await b.close();
  fs.writeFileSync(__dirname + '/boxes.json', JSON.stringify(BOX, null, 1));
})();
