import sys, re, zipfile
src, dst, v161 = sys.argv[1:4]
F = "HY신명조"
NEW = f'w:ascii="Times New Roman" w:eastAsia="{F}" w:hAnsi="Times New Roman" w:cs="Times New Roman"'
SKIP = ("Consolas", "Cambria Math", "Symbol", "Wingdings")
ATTR = re.compile(r'\s+w:(ascii|eastAsia|hAnsi|cs)(Theme)?="[^"]*"')
stats = {}
def fix(xml, name):
    n = 0
    def rep(m):
        nonlocal n
        tag = m.group(0)
        if any(s in tag for s in SKIP): return tag
        rest = ATTR.sub("", tag[len("<w:rFonts"):])
        n += 1
        return f'<w:rFonts {NEW}{rest}'
    xml = re.sub(r'<w:rFonts\b[^>]*>', rep, xml)
    stats[name] = n
    return xml
# HY신명조 entry for fontTable (from v161, without embedded font refs)
with zipfile.ZipFile(v161) as z:
    ft = z.read("word/fontTable.xml").decode()
entry = re.search(r'<w:font w:name="HY신명조">.*?</w:font>', ft, re.S).group(0)
entry = re.sub(r'<w:embed\w+[^>]*/>', '', entry)
targets = re.compile(r'^word/(document|styles|header\d*|footer\d*|footnotes|endnotes|numbering)\.xml$')
with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zi.infolist():
        data = zi.read(info.filename)
        if targets.match(info.filename):
            data = fix(data.decode(), info.filename).encode()
        elif info.filename == "word/fontTable.xml":
            t = data.decode()
            if 'w:name="HY신명조"' not in t:
                t = t.replace("</w:fonts>", entry + "</w:fonts>")
            data = t.encode()
        elif info.filename == "word/settings.xml":
            t = data.decode()
            if "embedTrueTypeFonts" not in t:
                t = re.sub(r'(<w:settings\b[^>]*>)', r'\1<w:embedTrueTypeFonts/>', t, count=1)
            t = re.sub(r'<w:saveSubsetFonts[^>]*/>', '', t)
            data = t.encode()
        zo.writestr(info, data)
print(stats)
