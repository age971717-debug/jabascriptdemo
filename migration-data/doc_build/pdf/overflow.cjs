// 잘림·튀어나옴 검사: 번호 동그라미가 자기 칸(이름표·표 칸) 밖으로, 사진이 칸 밖으로, 무엇이든 본문 폭 밖으로 나가면 보고
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const out = [];
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage(); await p.emulateMedia({ media: 'print' }); await p.goto('file://' + f); await p.waitForTimeout(1200);
    out.push(...await p.evaluate((name) => {
      const bad = [], T = 0.6;
      const txt = e => (e.closest('p,td')?.innerText || '').replace(/\s+/g, ' ').slice(0, 50);
      const boxOf = e => { let a = e.parentElement; while (a && a !== document.body) { const cs = getComputedStyle(a);
        if ((cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent') || a.tagName === 'TD') return a; a = a.parentElement; } return null; };
      const roots = [...document.querySelectorAll('section.page, .coverwrap, body.cover')];
      document.querySelectorAll('b.cn, img, table, p, span').forEach(e => {
        const r = e.getBoundingClientRect(); if (!r.width || !r.height) return;
        if (e.matches('b.cn')) { const box = boxOf(e); if (box) { const q = box.getBoundingClientRect();
          if (r.left < q.left - T || r.right > q.right + T || r.top < q.top - T || r.bottom > q.bottom + T) bad.push([name, '번호가 칸 밖', e.dataset.n, txt(e)]); } }
        if (e.tagName === 'IMG') { const td = e.closest('td'); if (td) { const q = td.getBoundingClientRect();
          if (r.left < q.left - T || r.right > q.right + T) bad.push([name, '사진이 칸 밖', e.alt || '', txt(td)]); } }
        const root = e.closest('section.page') || e.closest('.coverwrap');
        if (root) { const q = root.getBoundingClientRect(); if (r.left < q.left - T || r.right > q.right + T) bad.push([name, '본문 폭 밖', e.tagName, txt(e)]); }
      });
      const hit = (a, b) => a.left < b.right - T && b.left < a.right - T && a.top < b.bottom - T && b.top < a.bottom - T;
      // ① 글자가 칸·상자를 넘침(가로 스크롤이 생기면 잘린 것)
      document.querySelectorAll('section.page td, section.page p, .coverwrap td, .coverwrap p, p.lab span, .more, .back').forEach(e => {
        if (e.scrollWidth > e.clientWidth + 1 && e.clientWidth > 0) bad.push([name, '글자가 칸을 넘침', e.tagName, txt(e)]);
        const cs = getComputedStyle(e);
        if (cs.overflow === 'hidden' && e.scrollHeight > e.clientHeight + 1 && e.clientHeight > 0) bad.push([name, '글자가 아래로 잘림', e.tagName, txt(e)]);
      });
      // ② 번호 동그라미가 다른 글자와 겹침(자기 숫자를 뺀 같은 문단의 모든 글자 상자와 비교)
      document.querySelectorAll('b.cn').forEach(c => {
        const p = c.closest('p, td'); if (!p) return;
        const cr = c.getBoundingClientRect();
        const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT); let n, found = false;
        while (!found && (n = w.nextNode())) {
          if (c.contains(n) || !n.nodeValue.trim()) continue;
          const rng = document.createRange(); rng.selectNodeContents(n);
          for (const r of rng.getClientRects()) if (r.width > 1 && hit(cr, r)) { found = true; break; }
        }
        if (found) bad.push([name, '번호가 글자와 겹침', c.dataset.n, txt(c)]);
      });
      // ③ 돌아가기·자세히 버튼이 제목·이름표 글자를 가림
      document.querySelectorAll('.back').forEach(b => {
        const br = b.getBoundingClientRect(); const host = b.parentElement;
        [...host.querySelectorAll('.ht, .hs, span')].filter(x => x !== b && !b.contains(x) && !x.contains(b)).forEach(x => {
          if (hit(br, x.getBoundingClientRect())) bad.push([name, '버튼이 글자를 가림', '', txt(host)]); });
      });
      return bad;
    }, f.split('/').pop()));
  }
  const seen = new Set(); out.forEach(x => { const k = JSON.stringify(x); if (!seen.has(k)) { seen.add(k); console.log(k); } });
  console.log('overflow check:', seen.size ? seen.size + ' problems' : 'OK');
  await b.close();
})();
