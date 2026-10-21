// 덩어리마다 [배율1 높이, 최소 배율 높이, 최대 배율 높이](mm)
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage(); await p.emulateMedia({ media: 'print' });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(600);
  const r = await p.evaluate(() => { const MM = 96 / 25.4;
    return [...document.querySelectorAll('.blk')].map(el => { const imgs = [...el.querySelectorAll('img.sc')];
      const h = sc => { setScale(imgs, sc); return el.getBoundingClientRect().height / MM; };
      const a = h(1), lo = h(0.72), hi = h(1.25); setScale(imgs, 1); return [a, lo, hi]; }); });
  console.log(JSON.stringify(r)); await b.close();
})();
