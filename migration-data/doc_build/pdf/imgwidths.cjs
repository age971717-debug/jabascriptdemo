// 배치가 끝난 본문에서 사진마다 실제 인쇄 폭(mm) → JSON (사진 속 번호 크기를 종이 위 같은 크기로 맞추는 데 씀)
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }); const p = await b.newPage();
  await p.emulateMedia({ media: 'print' }); await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200);
  console.log(JSON.stringify(await p.evaluate(() => { const o = {}; document.querySelectorAll('img.sc[data-name]').forEach(i => { if (i.dataset.name) o[i.dataset.name] = +(i.getBoundingClientRect().width / (96 / 25.4)).toFixed(2); }); return o; })));
  await b.close();
})();
