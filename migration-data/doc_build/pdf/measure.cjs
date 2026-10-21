// 덩어리마다 높이(mm)와 그 안 그림 높이 합(mm)을 잰다
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage(); await p.emulateMedia({ media: 'print' });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(500);
  const r = await p.evaluate(() => { const MM = 96 / 25.4;
    return [...document.querySelectorAll('.blk')].map(el => [el.getBoundingClientRect().height / MM,
      [...el.querySelectorAll('img.sc')].reduce((a, i) => a + i.getBoundingClientRect().height / MM, 0) / Math.max(1, [...el.querySelectorAll('tr')].filter(tr => tr.querySelector('img.sc')).length ? 1 : 1)]); });
  // 같은 줄에 나란히 있는 그림은 높이를 한 번만 셈
  const r2 = await p.evaluate(() => { const MM = 96 / 25.4;
    return [...document.querySelectorAll('.blk')].map(el => { let ih = 0;
      el.querySelectorAll('tr').forEach(tr => { const hs = [...tr.querySelectorAll('img.sc')].map(i => i.getBoundingClientRect().height / MM); if (hs.length) ih += Math.max(...hs); });
      return [el.getBoundingClientRect().height / MM, ih]; }); });
  console.log(JSON.stringify(r2)); await b.close();
})();
