const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const S = '/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad';
const D = JSON.parse(fs.readFileSync(S + '/realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(S + '/extra.json', 'utf8'));
const insp = [
  { id: 1, created_at: '2026-07-10', inspected_on: '2026-07-10', serial: '88091-48', location: '111-1511-TM3', insulation_mohm: 45, brush_mm: 33, brush_spring_kg: 2.8, bearing_temp_c: 44, abnormal_noise: false, photo_path: null, ai_finding: null, note: null, nickname: '시험' },
  { id: 2, created_at: '2026-10-20', inspected_on: '2026-10-20', serial: '88091-48', location: '111-1511-TM3', insulation_mohm: 4.2, brush_mm: 29, brush_spring_kg: 3.4, bearing_temp_c: 47, abnormal_noise: true, photo_path: null, ai_finding: '주의 — 정류자 표면 일부 흑화로 보임', note: null, nickname: '시험' },
];
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, tm_inspections: insp, ...X };
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, colorScheme: 'dark', deviceScaleFactor: 2 });
  await ctx.route(/supabase\.co\//, (r) => { const req = r.request(); if (req.method() !== 'GET') return r.fulfill({ status: 403, json: { message: 'test: write blocked' } }); const m = req.url().match(/rest\/v1\/([a-z_]+)/); return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} }); });
  const pg = await ctx.newPage(); const errs = []; pg.on('pageerror', (e) => errs.push(e.message));
  await pg.route((u) => /_serverFn/.test(u.href), (r) => { const body = r.request().postData() ?? ''; if (/facts/.test(body)) return r.fulfill({ status: 200, headers: { 'content-type': 'application/json' }, json: { result: { text: '현재 88091-48은 긴급 등급입니다. 최근 5년 고장 교체 3회와 절연저항 4.2㏁(기준 5㏁ 미만)이 근거입니다. 다음 점검 때 절연저항을 다시 재고 교체를 검토하시기 바랍니다.' } } }); return r.continue(); });
  await pg.goto('http://127.0.0.1:8080/'); await pg.evaluate(() => localStorage.setItem('tm-site-gate', 'granted'));
  // 1) dashboard today item
  await pg.goto('http://127.0.0.1:8080/dashboard'); await pg.waitForTimeout(6000);
  const today = await pg.evaluate(() => [...document.querySelectorAll('h2')].find((h) => /오늘 확인할 것/.test(h.textContent))?.closest('section, div')?.innerText.slice(0, 600));
  console.log('TODAY:', (today ?? '').replace(/\n/g, ' | ').slice(0, 500));
  await pg.screenshot({ path: `${S}/ui3/flow_today.png` });
  // 2) report opinion card
  await pg.goto('http://127.0.0.1:8080/asset-report?serial=88091-48'); await pg.waitForTimeout(6000);
  const card = pg.locator('[data-testid="opinion-card"]'); await card.scrollIntoViewIfNeeded();
  await pg.getByRole('button', { name: 'AI 소견 보기' }).click(); await pg.waitForTimeout(1500);
  console.log('OPINION:', (await card.innerText()).replace(/\n/g, ' | ').slice(0, 300));
  await pg.screenshot({ path: `${S}/ui3/flow_opinion.png` });
  // 3) repeat banner
  await pg.goto('http://127.0.0.1:8080/?repeat=true'); await pg.waitForTimeout(5000);
  console.log('BANNER:', (await pg.locator('[data-testid="repeat-filter-banner"]').innerText()).replace(/\n/g, ' | '));
  await pg.screenshot({ path: `${S}/ui3/flow_banner.png` });
  // 4) chatbot: inspection by text → confirm → 저장 → password prompt; then 점검 기록 조회; then AI 소견
  await pg.goto('http://127.0.0.1:8080/'); await pg.waitForTimeout(5000);
  await pg.getByRole('button', { name: 'TM 챗봇 열기' }).click(); await pg.waitForTimeout(600);
  const say = async (q) => { await pg.getByRole('textbox').last().fill(q); await pg.getByRole('button', { name: '질문 보내기' }).click(); await pg.waitForTimeout(1500); return (await pg.locator('[data-chat-bubble="bot"]').last().innerText()).replace(/\n/g, ' | ').slice(0, 260); };
  console.log('C1:', await say('88091-48 절연저항 120 브러시 33 이음 없음'));
  await pg.screenshot({ path: `${S}/ui3/flow_chat1.png` });
  console.log('C2:', await say('저장'));
  console.log('C3:', await say('취소'));
  console.log('C4:', await say('88091-48 점검 기록 보여줘'));
  await pg.screenshot({ path: `${S}/ui3/flow_chat2.png` });
  console.log('C5:', await say('88091-48 AI 소견'));
  await pg.waitForTimeout(1500); console.log('C5b:', (await pg.locator('[data-chat-bubble="bot"]').last().innerText()).replace(/\n/g, ' | ').slice(0, 300));
  console.log('C6:', await say('이번 달 요약'));
  await pg.screenshot({ path: `${S}/ui3/flow_chat3.png` });
  console.log('errors', errs);
  await b.close();
})();
