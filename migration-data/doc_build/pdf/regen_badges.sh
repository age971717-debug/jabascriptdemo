# 사진 번호 크기 맞추기: 그림 다시 그림 → 가이드 배치 → 실제 인쇄 폭 재기 (폭이 안 바뀔 때까지)
cd /tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad
for i in 1 2 3; do
  (cd gcap && python3 draw2.py >/dev/null && python3 draw_dash.py >/dev/null && python3 draw_card.py >/dev/null && python3 draw_docs.py >/dev/null && python3 draw_pc.py >/dev/null && python3 draw_navphone.py >/dev/null)
  bash pdfout/go.sh >/dev/null 2>&1
  node pdfmod/imgwidths.cjs $PWD/pdfout/TM-CBM_사용가이드_body.html > gcap/printed_new.json
  if cmp -s gcap/printed_new.json gcap/printed_mm.json; then echo "stable after $i"; break; fi
  mv gcap/printed_new.json gcap/printed_mm.json; echo "round $i changed"
done
