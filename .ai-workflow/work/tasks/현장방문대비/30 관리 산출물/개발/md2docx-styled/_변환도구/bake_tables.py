#!/usr/bin/env python3
"""pandoc 이 만든 docx 의 표·코드 서식을 스타일이 아니라 각 요소에 직접 넣는다.

Google Drive 미리보기 같은 일부 뷰어는 표 스타일(tblStylePr)의 헤더 배경·테두리를 무시한다.
이 스크립트가 같은 모양(A안)을 셀·문단 서식으로 한 번 더 넣어 어디서 열어도 같게 보이게 한다.

usage: bake_tables.py <in.docx | -> <out.docx>   (- 는 표준입력)
"""
import io
import sys
import zipfile
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

HEAD_FILL = "D6E0EB"   # 표 헤더 배경
HEAD_TEXT = "131416"   # 표 헤더 글씨
HEAD_BDR = "90A9C6"    # 표 헤더 테두리
GRID = "CDD1D5"        # 표 격자선
CODE_BG = "F4F5F6"     # 코드 블록 배경
CODE_BAR = "8A949E"    # 코드 블록 왼쪽 선
TEXT_WIDTH = 9638      # A4, 좌우 여백 2cm(1134twip) 기준 본문 폭

RPR_ORDER = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike",
             "outline", "shadow", "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden",
             "color", "spacing", "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect",
             "bdr", "shd", "fitText", "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout",
             "specVanish", "oMath"]


def q(tag):
    return "{%s}%s" % (W, tag)


def el(tag, **attrs):
    e = etree.Element(q(tag))
    for k, v in attrs.items():
        e.set(q(k), str(v))
    return e


def local(e):
    return etree.QName(e).localname


def set_child(parent, child, before=()):
    """같은 이름의 자식을 교체하고, before 에 나열된 형제 앞에 넣는다."""
    for old in parent.findall(q(local(child))):
        parent.remove(old)
    for name in before:
        ref = parent.find(q(name))
        if ref is not None:
            ref.addprevious(child)
            return
    parent.append(child)


def borders(tag, color, sides, sz=4):
    b = el(tag)
    for s in sides:
        b.append(el(s, val="single", sz=sz, space=0, color=color))
    return b


def style_header_runs(tc):
    for r in tc.iter(q("r")):
        rpr = r.find(q("rPr"))
        if rpr is None:
            rpr = el("rPr")
            r.insert(0, rpr)
        for name in ("b", "bCs", "color"):
            for old in rpr.findall(q(name)):
                rpr.remove(old)
        rpr.append(el("b"))
        rpr.append(el("bCs"))
        rpr.append(el("color", val=HEAD_TEXT))
        kids = list(rpr)
        for k in kids:
            rpr.remove(k)
        kids.sort(key=lambda k: RPR_ORDER.index(local(k)) if local(k) in RPR_ORDER else 99)
        for k in kids:
            rpr.append(k)


def bake_table(tbl):
    tblPr = tbl.find(q("tblPr"))
    grid = tbl.find(q("tblGrid"))
    cols = [int(g.get(q("w"))) for g in grid.findall(q("gridCol"))]
    total = sum(cols) or 1
    cols = [max(1, round(c * TEXT_WIDTH / total)) for c in cols]
    cols[-1] += TEXT_WIDTH - sum(cols)
    for g, c in zip(grid.findall(q("gridCol")), cols):
        g.set(q("w"), str(c))

    set_child(tblPr, el("tblW", w=TEXT_WIDTH, type="dxa"), before=("jc", "tblCellSpacing", "tblInd", "tblBorders", "tblLayout", "tblCellMar", "tblLook"))
    set_child(tblPr, borders("tblBorders", GRID, ("top", "left", "bottom", "right", "insideH", "insideV")), before=("shd", "tblLayout", "tblCellMar", "tblLook"))
    mar = el("tblCellMar")
    for side, v in (("top", 50), ("left", 100), ("bottom", 50), ("right", 100)):
        mar.append(el(side, w=v, type="dxa"))
    set_child(tblPr, mar, before=("tblLook",))

    for ri, tr in enumerate(tbl.findall(q("tr"))):
        trPr = tr.find(q("trPr"))
        if trPr is None:
            trPr = el("trPr")
            tr.insert(0, trPr)
        if trPr.find(q("cantSplit")) is None:
            trPr.insert(0, el("cantSplit"))
        header = ri == 0
        for ci, tc in enumerate(tr.findall(q("tc"))):
            tcPr = tc.find(q("tcPr"))
            if tcPr is None:
                tcPr = el("tcPr")
                tc.insert(0, tcPr)
            set_child(tcPr, el("tcW", w=cols[ci] if ci < len(cols) else cols[-1], type="dxa"),
                      before=("gridSpan", "vMerge", "tcBorders", "shd", "vAlign"))
            if header:
                set_child(tcPr, borders("tcBorders", HEAD_BDR, ("top", "left", "bottom", "right")),
                          before=("shd", "noWrap", "tcMar", "vAlign"))
                set_child(tcPr, el("shd", val="clear", color="auto", fill=HEAD_FILL),
                          before=("noWrap", "tcMar", "vAlign"))
                set_child(tcPr, el("vAlign", val="center"))
                style_header_runs(tc)


def bake_code(p):
    pPr = p.find(q("pPr"))
    if pPr is None:
        pPr = el("pPr")
        p.insert(0, pPr)
    bdr = el("pBdr")
    bdr.append(el("left", val="single", sz=18, space=6, color=CODE_BAR))
    shd = el("shd", val="clear", color="auto", fill=CODE_BG)
    after = ("tabs", "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct", "topLinePunct",
             "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind",
             "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
             "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange")
    set_child(pPr, bdr, before=("shd",) + after)
    set_child(pPr, shd, before=after)


def main(src, dst):
    zin = zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read()) if src == "-" else src)
    doc = etree.fromstring(zin.read("word/document.xml"))
    for tbl in doc.iter(q("tbl")):
        bake_table(tbl)
    for p in doc.iter(q("p")):
        ps = p.find("w:pPr/w:pStyle", NS)
        if ps is not None and ps.get(q("val")) == "SourceCode":
            bake_code(p)
    out = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = out if item.filename == "word/document.xml" else zin.read(item.filename)
            zout.writestr(item, data)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
