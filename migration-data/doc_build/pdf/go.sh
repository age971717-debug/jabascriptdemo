cd /tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad
python3 -W ignore -c "
import sys,runpy; sys.path.insert(0,'pdfmod'); sys.argv=['g','gcap/annot','pdfout/TM-CBM_사용가이드.pdf']
runpy.run_path('docs_out/guide_pdf.py', run_name='__main__')" > pdfout/layout.txt
head -1 pdfout/layout.txt | python3 -c "
import json,sys; r=json.loads(sys.stdin.read()); print([(x['page'],x['fill'],x['scale'],x['overflow']) for x in r])"
python3 -W ignore -c "
import pymupdf as f
from PIL import Image
d=f.open('pdfout/TM-CBM_사용가이드.pdf'); print('pages',len(d))
for i,p in enumerate(d): p.get_pixmap(dpi=${DPI:-60}).save(f'pdfout/p{i+1:02d}.png')
ims=[Image.open(f'pdfout/p{i+1:02d}.png') for i in range(len(d))]
w,h=ims[0].size; cols=5; rows=(len(ims)+cols-1)//cols
c=Image.new('RGB',(cols*w,rows*h),'#888')
for k,im in enumerate(ims): c.paste(im,((k%cols)*w,(k//cols)*h))
c.save('pdfout/all.png')"
# 글자 깨짐 검사(Chromium 글꼴 묶음 오류로 '비교'→'비W' 같은 깨짐이 생긴 적 있음)
python3 -W ignore -c "
import pymupdf as f, re
d=f.open('pdfout/TM-CBM_사용가이드.pdf'); n=0
for i,p in enumerate(d):
    b=re.findall(r'.{0,8}(?:[\x00-\x08\x0b-\x1f\x7f-\x9f]|[가-힣][A-Za-z](?![A-Za-z])|ç).{0,8}', p.get_text())
    if b: print('BROKEN GLYPHS page', i, b[:5]); n+=1
print('glyph check', 'OK' if not n else f'{n} pages broken')"
# 잘림·튀어나옴 검사(번호 동그라미·사진·표가 칸이나 본문 폭 밖으로 나가면 보고)
node pdfmod/overflow.cjs $PWD/pdfout/TM-CBM_사용가이드_body.html $PWD/pdfout/TM-CBM_사용가이드_cover.html | tail -15
