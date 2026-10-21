// 표지(머리말·쪽번호 없음) + 본문(머리말·쪽번호) PDF 두 개를 만든다. 합치기는 파이썬에서.
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const [cover, body, out, header] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage();
  await p.goto('file://' + cover); await p.waitForTimeout(400);
  await p.pdf({ path: out + '.cover.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true });
  await p.emulateMedia({ media: 'print' }); await p.goto('file://' + body); await p.waitForTimeout(800);
  console.log(JSON.stringify(await p.evaluate(() => window.__layout)));
  const font = 'font-family:Pretendard,sans-serif;font-size:7.5pt;color:#7a8597;width:100%;';
  await p.pdf({
    path: out + '.body.pdf', format: 'A4', printBackground: true,
    margin: { top: '19mm', bottom: '16mm', left: '17mm', right: '17mm' },
    displayHeaderFooter: true,
    headerTemplate: `<div style="${font}margin:0 17mm;padding-bottom:2mm;border-bottom:0.5pt solid #C5D0E3;display:flex;justify-content:space-between"><span>${header}</span><span>2026. 10.</span></div>`,
    footerTemplate: `<div style="${font}text-align:center">- <span class="pageNumber"></span> -</div>`,
  });
  await b.close();
})();
