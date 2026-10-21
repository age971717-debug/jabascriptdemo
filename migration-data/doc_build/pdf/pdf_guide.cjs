// 표지(머리말·쪽번호 없음) + 본문(머리말·쪽번호) PDF 두 개를 만든다. 합치기는 파이썬에서.
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
const [cover, body, out, header] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage();
  await p.emulateMedia({ media: 'print' }); await p.goto('file://' + body); await p.waitForTimeout(800);
  console.log(JSON.stringify(await p.evaluate(() => window.__layout)));
  const secmap = await p.evaluate(() => window.__secmap);
  // 표지: 본문 배치 결과로 쪽 번호 채우기
  const fs = require('fs'); let html = fs.readFileSync(cover, 'utf8');
  html = html.replace(/\{\{p:([^}]+)\}\}/g, (_, k) => secmap[k] ?? '?');
  fs.writeFileSync(cover, html);
  const c = await b.newPage(); await c.goto('file://' + cover); await c.waitForTimeout(400);
  await c.pdf({ path: out + '.cover.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true });
  await p.goto('file://' + body); await p.waitForTimeout(800);
  const font = 'font-family:Pretendard,sans-serif;font-size:7.5pt;color:#7a8597;width:100%;';
  const btn = 'display:inline-block;border:0.6pt solid #8FAAD6;border-radius:6pt;padding:0.4pt 6pt;margin-right:6pt;color:#1F5FBF;font-weight:700;background:#EEF3FB;';
  await p.pdf({
    path: out + '.body.pdf', format: 'A4', printBackground: true,
    margin: { top: '19mm', bottom: '16mm', left: '17mm', right: '17mm' },
    displayHeaderFooter: true,
    headerTemplate: `<div style="${font}margin:0 17mm;padding-bottom:2mm;border-bottom:0.5pt solid #C5D0E3;display:flex;justify-content:space-between"><span>${header}</span><span><span style="${btn}">◀ 뒤로</span><span style="${btn}">⌂ 목차</span>2026. 10.</span></div>`,
    footerTemplate: `<div style="${font}text-align:center">- <span class="pageNumber"></span> -</div>`,
  });
  console.log(JSON.stringify(secmap));
  await b.close();
})();
