// 챗봇 창 크기·글자·터치 영역 측정 (여러 화면 크기)
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const fs = require('fs');
const S = '/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad';
const D = JSON.parse(fs.readFileSync(S + '/realdata.json', 'utf8'));
const X = JSON.parse(fs.readFileSync(S + '/extra.json', 'utf8'));
const map = { tm_assets: D.assets, repair_history: D.history, external_repair_log: D.ext, risk_settings: D.risk, ...X };
const U = 'http://127.0.0.1:8080';
const TAG = process.argv[2] || 'before';
const VP = [
  [360, 640, 'm360', true], [390, 844, 'm390', true], [412, 915, 'm412', true],
  [768, 1024, 't768', true], [1280, 800, 'pc1280', false], [1920, 1080, 'pc1920', false],
];
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const [w, h, tag, mobile] of VP) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: mobile && w < 700, hasTouch: mobile, colorScheme: 'dark', deviceScaleFactor: 2 });
    await ctx.route(/supabase\.co\//, (r) => {
      const m = r.request().url().match(/rest\/v1\/([a-z_]+)/);
      if (r.request().method() !== 'GET' && m && m[1] !== 'rpc') return r.fulfill({ status: 403, json: {} });
      return r.fulfill({ json: m ? (map[m[1]] ?? []) : {} });
    });
    const pg = await ctx.newPage();
    await pg.goto(U + '/');
    await pg.evaluate(() => { localStorage.setItem('tm-site-gate', 'granted'); });
    await pg.goto(U + '/', { waitUntil: 'domcontentloaded' });
    await pg.waitForTimeout(6000);
    await pg.getByRole('button', { name: 'TM 챗봇 열기' }).click();
    await pg.waitForTimeout(800);
    await pg.screenshot({ path: `${S}/chat/sz_${TAG}_${tag}_open.png` });
    for (const q of ['등급표 보여줘', '1416호차 상태']) {
      await pg.getByRole('textbox').last().fill(q);
      await pg.getByRole('button', { name: '질문 보내기' }).click();
      await pg.waitForTimeout(1200);
    }
    await pg.screenshot({ path: `${S}/chat/sz_${TAG}_${tag}_answer.png` });
    const m = await pg.evaluate(() => {
      const input = document.querySelector('#chat-input');
      const panel = input.closest('div.fixed');
      const r = panel.getBoundingClientRect();
      const bubble = [...document.querySelectorAll('[data-chat-bubble="bot"]')].at(-1);
      const fs = getComputedStyle(bubble).fontSize;
      const inFs = getComputedStyle(input).fontSize;
      const btns = [...panel.querySelectorAll('button, a')].filter((e) => e.offsetParent);
      const small = btns.map((e) => e.getBoundingClientRect()).filter((b) => b.height < 40 || b.width < 40).length;
      const hdr = document.querySelector('header')?.getBoundingClientRect();
      const nav = document.querySelector('nav[aria-label="주요 화면 바로가기"]')?.getBoundingClientRect();
      const scroller = panel.querySelector('.overflow-y-auto');
      return {
        panel: `${Math.round(r.left)},${Math.round(r.top)} ${Math.round(r.width)}x${Math.round(r.height)}`,
        viewport: `${innerWidth}x${innerHeight}`,
        coverPct: Math.round((r.width * r.height) / (innerWidth * innerHeight) * 100),
        botFont: fs, inputFont: inFs,
        buttons: btns.length, smallTargets: small,
        overHeader: hdr ? r.top < hdr.bottom : null,
        overNav: nav && nav.height ? r.bottom > nav.top + 1 : null,
        msgArea: Math.round(scroller.getBoundingClientRect().height),
        hOverflow: scroller.scrollWidth > scroller.clientWidth + 1,
      };
    });
    console.log(tag, JSON.stringify(m));
    await ctx.close();
  }
  await b.close();
})();
