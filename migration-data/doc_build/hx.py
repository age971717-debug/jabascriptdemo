"""hwpx 작성 도우미 — 표 셀 안 문단 서식·그림·병합까지(문서 3종 공용)."""
import io
from PIL import Image
from hwpx import HwpxDocument

MM = 7200 / 25.4


class Doc:
    def __init__(self, margins=(20, 20, 15, 15)):
        self.d = HwpxDocument.new()
        l, r, t, b = margins
        self.d.set_page_setup(paper_size="A4", orientation="PORTRAIT",
                              margins_mm={"left": l, "right": r, "top": t, "bottom": b})
        self._pp = {}

    # 글자·문단 서식 id
    def cs(self, **kw):
        return self.d.ensure_run_style(**kw)

    def pp(self, **fmt):
        """문단 서식 id — 임시 문단에 서식을 걸어 id만 얻고 지운다(셀 안 문단에 재사용)."""
        key = tuple(sorted(fmt.items()))
        if key not in self._pp:
            p = self.d.add_paragraph("")
            self.d.set_paragraph_format(paragraph_index=len(self.d.paragraphs) - 1, **fmt)
            self._pp[key] = p.para_pr_id_ref
            p.remove()
        return self._pp[key]

    # 본문 문단: **굵게** 구간 지원
    def para(self, text, cs, bold_cs=None, target=None, **fmt):
        ppid = self.pp(**fmt) if fmt else None
        if target is None:
            p = self.d.add_paragraph("", para_pr_id_ref=ppid, char_pr_id_ref=cs, include_run=False)
        else:
            p = target.add_paragraph("", para_pr_id_ref=ppid, char_pr_id_ref=cs)
            for r in list(p.runs):
                r.remove() if hasattr(r, "remove") else None
        for i, part in enumerate(text.split("**")):
            if part:
                p.add_run(part, char_pr_id_ref=(bold_cs if (i % 2 and bold_cs) else cs))
        return p

    def image(self, path, width_mm, box=None, target=None, ppid=None, max_h_mm=None):
        im = Image.open(path).convert("RGB")
        if box:
            im = im.crop(box)
        b = io.BytesIO(); im.save(b, "PNG", optimize=True)
        item = self.d.add_image(b.getvalue(), "png")
        w, h = im.size
        W = round(width_mm * MM); H = round(W * h / w)
        if max_h_mm and H > max_h_mm * MM:
            H = round(max_h_mm * MM); W = round(H * w / h)
        if target is None:
            p = self.d.add_paragraph("", para_pr_id_ref=ppid, include_run=False)
        else:
            p = target.add_paragraph("", para_pr_id_ref=ppid)
        p.add_picture(item, width=W, height=H, treat_as_char=True)
        return p

    def table(self, rows, cols, widths, width_mm=None):
        kw = {}
        if width_mm:
            kw["width"] = round(width_mm * MM)
        t = self.d.add_table(rows=rows, cols=cols, **kw)
        t.set_column_widths(widths)
        return t

    def cell(self, t, r, c, lines, cs, bold_cs=None, shade=None, **fmt):
        """셀 내용을 문단 여러 개로 채운다. lines: str 또는 (text, cs, fmt) 목록."""
        cell = t.cell(r, c)
        first = True
        for ln in ([lines] if isinstance(lines, str) else lines):
            text, lcs, lfmt = (ln, cs, fmt) if isinstance(ln, str) else (ln[0], ln[1], {**fmt, **(ln[2] if len(ln) > 2 else {})})
            if first:
                p0 = cell.paragraphs[0]
                p0.para_pr_id_ref = self.pp(**lfmt) if lfmt else p0.para_pr_id_ref
                for run in list(p0.runs):
                    run.remove()
                for i, part in enumerate(text.split("**")):
                    if part:
                        p0.add_run(part, char_pr_id_ref=(bold_cs if (i % 2 and bold_cs) else lcs))
                first = False
            else:
                self.para(text, lcs, bold_cs, target=cell, **lfmt)
        if shade:
            t.set_cell_shading(r, c, shade)
        return cell

    def save(self, path):
        self.d.save_to_path(path)
        from hwpx import validate_editor_open_safety
        r = validate_editor_open_safety(path)
        return r.reopen_ok, r.blocking_package_errors


def _png(path, box):
    im = Image.open(path).convert("RGB")
    if box:
        im = im.crop(box)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    return b.getvalue(), im.size


def cell_pics(D, t, r, c, items, height_mm, ppid=None, gap=" "):
    """셀 첫 문단에 그림 여러 장을 같은 높이로 나란히. items: (path, box)."""
    cell = t.cell(r, c)
    p = cell.paragraphs[0]
    for run in list(p.runs):
        run.remove()
    if ppid:
        p.para_pr_id_ref = ppid
    for k, (path, box) in enumerate(items):
        data, (w, h) = _png(path, box)
        item = D.d.add_image(data, "png")
        H = round(height_mm * MM); W = round(H * w / h)
        p.add_picture(item, width=W, height=H, treat_as_char=True)
        if k < len(items) - 1:
            p.add_run(gap)
    return cell
