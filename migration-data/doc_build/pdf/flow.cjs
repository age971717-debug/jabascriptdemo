const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
(async () => { const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ deviceScaleFactor: 3, viewport: { width: 1000, height: 600 } });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(500);
  await p.locator('.wrap').screenshot({ path: process.argv[3] }); await b.close(); })();
