// 줄바꿈 검사: 문단·표 칸마다 실제 줄을 나눠 보고, 어색한 곳을 보고
//  ① 줄이 문장부호·기호(. , · ) ⇒ :)로 시작  ② 마지막 줄이 너무 짧음(4글자 이하)  ③ 강조(굵은 글씨·등급 칸)가 두 줄로 쪼개짐
const { chromium } = require('/home/user/tm-cbm/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }); const p = await b.newPage();
  await p.emulateMedia({ media: 'print' }); await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200);
  const out = await p.evaluate(() => {
    const res = [];
    const pages = [...document.querySelectorAll('section.page')];
    document.querySelectorAll('section.page p, .coverwrap p').forEach(el => {
      if (el.classList.contains('h2') || el.closest('.back')) return;
      // 글자마다 위치를 재서 줄로 묶음
      const chars = []; const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let n;
      while ((n = w.nextNode())) {
        if (n.parentElement.closest('.back')) continue;
        for (let i = 0; i < n.nodeValue.length; i++) {
          const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + 1);
          const rc = r.getClientRects()[0]; if (!rc || rc.width === 0) continue;
          chars.push({ c: n.nodeValue[i], top: Math.round(rc.top), node: n.parentElement });
        }
      }
      if (!chars.length) return;
      const lines = []; let cur = [chars[0]];
      for (const ch of chars.slice(1)) { if (Math.abs(ch.top - cur[cur.length - 1].top) > 4) { lines.push(cur); cur = [ch]; } else cur.push(ch); }
      lines.push(cur);
      if (lines.length < 2) return;
      const text = l => l.map(x => x.c).join('').trim();
      const page = pages.indexOf(el.closest('section.page')) + 1;
      const all = text(chars);
      lines.slice(1).forEach(l => { const t = text(l); if (/^[.,·)⇒:%]/.test(t)) res.push([page, '줄 첫 글자가 기호', t.slice(0, 20), all.slice(0, 60)]); });
      const last = text(lines[lines.length - 1]).replace(/\s/g, '');
      if (last.length <= 4) res.push([page, '마지막 줄이 짧음', last, all.slice(0, 60)]);
      // 강조가 쪼개짐: 같은 굵은/등급 요소의 글자가 두 줄에 걸침
      const seen = new Map();
      lines.forEach((l, li) => l.forEach(x => { const e = x.node.closest('b.g, strong, span[style*="font-weight:700"]'); if (!e || e.closest('.more')) return; if (!seen.has(e)) seen.set(e, new Set()); seen.get(e).add(li); }));
      seen.forEach((set, e) => { if (set.size > 1 && e.textContent.trim().length <= 12) res.push([page, '강조가 두 줄로 쪼개짐', e.textContent.trim(), all.slice(0, 60)]); });
    });
    return res;
  });
  out.forEach(x => console.log(JSON.stringify(x)));
  console.log('linebreak check:', out.length ? out.length + ' issues' : 'OK');
  await b.close();
})();
