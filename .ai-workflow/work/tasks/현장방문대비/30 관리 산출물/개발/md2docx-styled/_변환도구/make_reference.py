import re, shutil, zipfile, sys, os
import os
HC=os.environ.get("HC","1F3A5F"); HEADFILL=os.environ.get("HEADFILL","1F3A5F"); HEADTXT=os.environ.get("HEADTXT","FFFFFF"); HEADBDR=os.environ.get("HEADBDR","1F3A5F"); GRID=os.environ.get("GRID","B8C0CC"); CODEBG=os.environ.get("CODEBG","F3F4F6"); BAR=os.environ.get("BAR","8A96A6")
src, out = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(src)
files = {n: z.read(n) for n in z.namelist()}
s = files['word/styles.xml'].decode('utf8')

def sub_style(sid, new):
    global s
    pat = re.compile(r'<w:style [^>]*w:styleId="%s".*?</w:style>' % sid, re.S)
    if pat.search(s): s = pat.sub(lambda m: new, s, count=1)
    else: s = s.replace('</w:styles>', new + '</w:styles>')

FONT = '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="맑은 고딕" w:cs="Calibri"/>'
MONO = '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:eastAsia="맑은 고딕" w:cs="Consolas"/>'

# defaults: 10pt, Korean-aware fonts, tighter spacing
s = re.sub(r'<w:rPrDefault>.*?</w:rPrDefault>',
  '<w:rPrDefault><w:rPr>%s<w:sz w:val="20"/><w:szCs w:val="20"/><w:lang w:val="ko-KR" w:eastAsia="ko-KR" w:bidi="ar-SA"/></w:rPr></w:rPrDefault>' % FONT, s, flags=re.S)
s = re.sub(r'<w:pPrDefault>.*?</w:pPrDefault>',
  '<w:pPrDefault><w:pPr><w:spacing w:after="100" w:line="288" w:lineRule="auto"/></w:pPr></w:pPrDefault>', s, flags=re.S)

def heading(n, sz, before, after, border):
    bdr = '<w:pBdr><w:bottom w:val="single" w:sz="8" w:space="3" w:color="%s"/></w:pBdr>' % HC if border else ''
    return ('<w:style w:type="paragraph" w:styleId="Heading%d"><w:name w:val="heading %d"/><w:basedOn w:val="Normal"/><w:next w:val="BodyText"/>'
            '<w:link w:val="Heading%dChar"/><w:uiPriority w:val="9"/><w:qFormat/><w:pPr><w:keepNext/><w:keepLines/>%s'
            '<w:spacing w:before="%d" w:after="%d"/><w:outlineLvl w:val="%d"/></w:pPr>'
            '<w:rPr>%s<w:b/><w:bCs/><w:color w:val="%s"/><w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr></w:style>'
            % (n, n, n, bdr, before, after, n-1, FONT, HC, sz, sz))
sub_style('Heading1', heading(1, 36, 120, 160, False))
sub_style('Heading2', heading(2, 28, 320, 120, True))
sub_style('Heading3', heading(3, 24, 220, 80, False))
# heading char styles keep default; body spacing
sub_style('BodyText', '<w:style w:type="paragraph" w:styleId="BodyText"><w:name w:val="Body Text"/><w:basedOn w:val="Normal"/><w:link w:val="BodyTextChar"/><w:qFormat/><w:pPr><w:spacing w:before="60" w:after="100"/></w:pPr></w:style>')
sub_style('Compact', '<w:style w:type="paragraph" w:customStyle="1" w:styleId="Compact"><w:name w:val="Compact"/><w:basedOn w:val="BodyText"/><w:qFormat/><w:pPr><w:spacing w:before="30" w:after="30"/></w:pPr></w:style>')

# table: grid, navy header row with white bold text
sub_style('Table', (
 '<w:style w:type="table" w:default="1" w:styleId="Table"><w:name w:val="Table"/><w:basedOn w:val="TableNormal"/><w:semiHidden/><w:unhideWhenUsed/><w:qFormat/>'
 '<w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblBorders>'
 + ''.join('<w:%s w:val="single" w:sz="4" w:space="0" w:color="%s"/>' % (e, GRID) for e in ('top','left','bottom','right','insideH','insideV'))
 + '</w:tblBorders><w:tblCellMar><w:top w:w="50" w:type="dxa"/><w:left w:w="100" w:type="dxa"/><w:bottom w:w="50" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr>'
 '<w:tblStylePr w:type="firstRow"><w:rPr><w:b/><w:bCs/><w:color w:val="'+HEADTXT+'"/></w:rPr><w:tcPr><w:tcBorders>'
 + ''.join('<w:%s w:val="single" w:sz="4" w:space="0" w:color="%s"/>' % (e, HEADBDR) for e in ('top','left','bottom','right'))
 + '</w:tcBorders><w:shd w:val="clear" w:color="auto" w:fill="%s"/><w:vAlign w:val="center"/></w:tcPr></w:tblStylePr></w:style>' % HEADFILL))

# code: shaded block with left bar; inline code shaded mono
sub_style('SourceCode', ('<w:style w:type="paragraph" w:customStyle="1" w:styleId="SourceCode"><w:name w:val="Source Code"/><w:basedOn w:val="Normal"/><w:link w:val="VerbatimChar"/>'
 '<w:pPr><w:keepLines/><w:pBdr><w:left w:val="single" w:sz="18" w:space="6" w:color="%s"/></w:pBdr><w:shd w:val="clear" w:color="auto" w:fill="%s"/>'
 '<w:spacing w:before="0" w:after="0" w:line="264" w:lineRule="auto"/><w:ind w:left="200" w:right="100"/></w:pPr><w:rPr>%s<w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr></w:style>') % (BAR, CODEBG, MONO))
sub_style('VerbatimChar', ('<w:style w:type="character" w:customStyle="1" w:styleId="VerbatimChar"><w:name w:val="Verbatim Char"/><w:basedOn w:val="BodyTextChar"/>'
 '<w:rPr>%s<w:sz w:val="18"/><w:szCs w:val="18"/><w:shd w:val="clear" w:color="auto" w:fill="%s"/></w:rPr></w:style>') % (MONO, CODEBG))
files['word/styles.xml'] = s.encode('utf8')

# A4 + 2cm margins
d = files['word/document.xml'].decode('utf8')
d = re.sub(r'<w:sectPr>(.*?)</w:sectPr>', lambda m: '<w:sectPr>%s<w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="709" w:footer="709" w:gutter="0"/></w:sectPr>' % m.group(1), d, count=1, flags=re.S)
files['word/document.xml'] = d.encode('utf8')

with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as o:
    for n, b in files.items(): o.writestr(n, b)
print('wrote', out)
