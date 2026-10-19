"""hwpx → 대략적인 HTML(쪽 나눔 확인용). 정확한 조판은 한글에서 확인해야 함."""
import base64, re, sys, zipfile
from lxml import etree
NS = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph", "hh": "http://www.hancom.co.kr/hwpml/2011/head",
      "hc": "http://www.hancom.co.kr/hwpml/2011/core"}
src, out = sys.argv[1:3]
z = zipfile.ZipFile(src)
head = etree.fromstring(z.read("Contents/header.xml"))
sec = etree.fromstring(z.read("Contents/section0.xml"))
fonts = [f.get("face") for f in head.find(".//hh:fontface[@lang='HANGUL']", NS).findall("hh:font", NS)]
cs = {}
for c in head.iter("{%s}charPr" % NS["hh"]):
    fr = c.find("hh:fontRef", NS); ra = c.find("hh:ratio", NS)
    cs[c.get("id")] = dict(size=int(c.get("height")) / 100, bold=c.find("hh:bold", NS) is not None,
                           color=c.get("textColor"), font=fonts[int(fr.get("hangul"))] if fr is not None else "",
                           ratio=int(ra.get("hangul")) if ra is not None else 100)
ps = {}
for p in head.iter("{%s}paraPr" % NS["hh"]):
    al = p.find("hh:align", NS); ls = p.find(".//hh:lineSpacing", NS)
    ps[p.get("id")] = dict(align=(al.get("horizontal") if al is not None else "LEFT").lower(), ls=int(ls.get("value")) if ls is not None else 160)
bf = {}
for b in head.iter("{%s}borderFill" % NS["hh"]):
    w = b.find(".//hc:winBrush", NS); bf[b.get("id")] = w.get("faceColor") if w is not None else None
bins = {n.split("/")[-1].split(".")[0]: n for n in z.namelist() if n.startswith("BinData/")}
fam = {"휴먼명조": "serif", "함초롬바탕": "serif"}
def run_html(r):
    s = cs.get(r.get("charPrIDRef"), cs["0"]); o = []
    for ch in r:
        tag = etree.QName(ch).localname
        if tag == "t" and ch.text:
            o.append(f'<span style="font-size:{s["size"]}pt;font-weight:{700 if s["bold"] else 400};color:{s["color"]};font-family:{fam.get(s["font"], "sans-serif")};display:inline-block;transform:scaleX({s["ratio"]/100});transform-origin:left">{ch.text}</span>' if s["ratio"] != 100 and False else
                     f'<span style="font-size:{s["size"]*s["ratio"]/100:.1f}pt;font-weight:{700 if s["bold"] else 400};color:{s["color"]};font-family:{fam.get(s["font"], "sans-serif")}">{ch.text}</span>')
        elif tag == "pic":
            img = ch.find(".//hc:img", NS); sz = ch.find("hp:sz", NS)
            data = z.read(bins[img.get("binaryItemIDRef")])
            o.append(f'<img src="data:image/png;base64,{base64.b64encode(data).decode()}" style="width:{int(sz.get("width"))/283.46:.1f}mm;height:{int(sz.get("height"))/283.46:.1f}mm;vertical-align:bottom">')
        elif tag == "tbl":
            o.append(tbl_html(ch))
    return "".join(o)
def para_html(p):
    pp = ps.get(p.get("paraPrIDRef"), dict(align="left", ls=160))
    br = "page-break-before:always;" if p.get("pageBreak") == "1" else ""
    inner = "".join(run_html(r) for r in p.findall("hp:run", NS)) or "&nbsp;"
    return f'<div style="{br}text-align:{pp["align"]};line-height:{pp["ls"]/100*1.0:.2f};margin:0">{inner}</div>'
def tbl_html(t):
    rows = []
    for tr in t.findall("hp:tr", NS):
        cells = []
        for tc in tr.findall("hp:tc", NS):
            sp = tc.find("hp:cellSpan", NS); sz = tc.find("hp:cellSz", NS)
            bg = bf.get(tc.get("borderFillIDRef"))
            inner = "".join(para_html(p) for p in tc.find("hp:subList", NS).findall("hp:p", NS))
            cells.append(f'<td colspan="{sp.get("colSpan")}" rowspan="{sp.get("rowSpan")}" style="width:{int(sz.get("width"))/283.46:.1f}mm;{"background:"+bg+";" if bg and bg!="none" else ""}border:1px solid #444;padding:0.5mm 1.8mm;vertical-align:middle">{inner}</td>')
        rows.append("<tr style=\"break-inside:avoid\">" + "".join(cells) + "</tr>")
    w = int(t.find("hp:sz", NS).get("width")) / 283.46
    inline = t.find("hp:pos", NS).get("treatAsChar") != "0"
    return f'<table style="border-collapse:collapse;width:{w:.1f}mm;table-layout:fixed;{"break-inside:avoid" if inline else ""}">{"".join(rows)}</table>'
pg = sec.find(".//hp:pagePr", NS); m = pg.find("hp:margin", NS)
mm = lambda v: int(v) / 283.46
body = "".join(para_html(p) for p in sec.findall("hp:p", NS))
open(out, "w").write(f'''<html><head><meta charset="utf-8"><style>@page{{size:A4;margin:{mm(m.get("top"))}mm {mm(m.get("right"))}mm {mm(m.get("bottom"))}mm {mm(m.get("left"))}mm}}
body{{margin:0;font-family:"Noto Sans CJK KR","WenQuanYi Zen Hei",sans-serif;letter-spacing:{__import__("os").environ.get("LSP","0")}em;word-spacing:{__import__("os").environ.get("WSP","0")}em}}</style></head><body>{body}</body></html>''')
