import re, json, html, pathlib, markdown

ROOT = pathlib.Path(__file__).parent
ORDER = ["code-red", "rotem-algorithm", "code-black", "ed-rsi",
         "difficult-airway", "neck-injury", "one-lung-ventilation",
         "elderly-trauma", "pregnant-trauma", "drowning-hypothermia",
         "rib-fractures", "spinal-cord-injury",
         "vascular-access", "ultrasound", "tag-skillset"]
GROUPS = {
    "resus": "Resuscitation",
    "airway": "Airway",
    "populations": "Special populations",
    "injuries": "Specific injuries",
    "procedures": "Procedures & skills",
}
# names used in the PDFs -> slug in this handbook (None = not in the set)
NAMES = {
    "code red rotem algorithm": "rotem-algorithm",
    "code red cpg": "code-red", "code black cpg": "code-black",
    "emergency department rsi cpg": "ed-rsi",
    "difficult airway & omfs trauma cpg": "difficult-airway",
    "neck injury cpg": "neck-injury", "vascular access cpg": "vascular-access",
    "ultrasound cpg": "ultrasound", "elderly trauma cpg": "elderly-trauma",
    "rib fractures cpg": "rib-fractures", "spinal cord injury cpg": "spinal-cord-injury",
}
SOURCE = {
    "code-red": "Code Red CPG 2025.pdf", "code-black": "Code Black CPG 2025.pdf",
    "ed-rsi": "Emergency Department RSI CPG 2025.pdf",
    "difficult-airway": "Difficult Airway and OMFS Trauma CPG 2025.pdf",
    "neck-injury": "Neck Injury CPG 2025.pdf", "one-lung-ventilation": "One Lung Ventilation CPG 2025.pdf",
    "elderly-trauma": "Elderly Trauma CPG 2025.pdf", "pregnant-trauma": "Pregnant Trauma CPG 2025.pdf",
    "drowning-hypothermia": "Drowning and Hypothermia CPG 2025.pdf", "rib-fractures": "Rib Fractures CPG 2025.pdf",
    "spinal-cord-injury": "Spinal Cord Injury CPG 2025.pdf", "vascular-access": "Vascular Access CPG 2025.pdf",
    "ultrasound": "Ultrasound CPG 2025.pdf", "tag-skillset": "TAG Skills CPG 2025.pdf", "rotem-algorithm": "ROTEM Algorithm 2023.pdf",
}

def link_names(h):
    """Link CPG names in body text (skip inside tags, links and headings)."""
    pat = re.compile(r"(Code Red CPG|Code Black CPG|Emergency Department RSI CPG|Difficult Airway &amp; OMFS Trauma CPG|Neck Injury CPG|Vascular Access CPG|Ultrasound CPG|Elderly Trauma CPG|Rib Fractures CPG|Spinal Cord Injury CPG)")
    out, depth_a = [], 0
    for part in re.split(r"(<[^>]+>)", h):
        if part.startswith("<"):
            if re.match(r"<a[\s>]", part): depth_a += 1
            elif part.startswith("</a"): depth_a -= 1
            out.append(part)
        elif depth_a == 0:
            out.append(pat.sub(lambda m: f'<a class="xref" href="#{NAMES[html.unescape(m.group(1)).lower()]}">{m.group(1)}</a>', part))
        else:
            out.append(part)
    return "".join(out)

from bs4 import BeautifulSoup
KEYLIKE = {"role","gestation","factor","injury","medication","tier","grade","scenario","target","stage","step",""}
def classify(h):
    soup = BeautifulSoup(h, "html.parser")
    for wrap in soup.select("div.tbl"):
        t = wrap.table
        heads = [th.get_text(" ", strip=True) for th in t.select("thead th")]
        first = t.select_one("tr")
        ncols = len(first.find_all(["td","th"])) if first else 0
        if ncols <= 2 and (not heads or heads[0].lower() in KEYLIKE):
            wrap["class"] = ["tbl", "kv"]
        else:
            wrap["class"] = ["tbl", "stack"]
            for tr in t.select("tbody tr"):
                for i, cell in enumerate(tr.find_all(["td","th"])):
                    if i < len(heads) and heads[i]:
                        cell["data-label"] = heads[i]
                    elif i == 0:
                        cell["class"] = cell.get("class", []) + ["rowh"]
    return str(soup)

def build(slug):
    raw = (ROOT / "content" / f"{slug}.md").read_text()
    head, body = raw.split("\n---\n", 1)
    meta = {}
    for line in head.splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    md = markdown.Markdown(extensions=["tables", "sane_lists"])
    h = md.convert(body)
    sections, n = [], 0
    def h2(m):
        nonlocal n
        n += 1
        sid = f"s{n}"
        title = re.sub(r"<[^>]+>", "", m.group(1))
        sections.append({"id": sid, "title": html.unescape(title)})
        return f'</section><section class="sec" id="{slug}.{sid}" data-sid="{sid}"><h2>{m.group(1)}</h2>'
    h = re.sub(r"<h2>(.*?)</h2>", h2, h)
    h = h.replace("</section>", "", 1) + "</section>"
    # figures
    def fig(src, alt):
        alt = html.unescape(alt)
        return (f'<figure><button class="zoom" type="button" data-src="{src}" data-cap="{html.escape(alt)}" aria-label="Enlarge figure: {html.escape(alt)}">'
                f'<img src="{src}" alt="{html.escape(alt)}" loading="lazy"></button>'
                f'<figcaption>{html.escape(alt)}<span>Tap to enlarge</span></figcaption></figure>')
    h = re.sub(r'<p><img alt="([^"]*)" src="([^"]*)" /></p>', lambda m: fig(m.group(2), m.group(1)), h)
    h = re.sub(r"<table>", '<div class="tbl"><table>', h)
    h = re.sub(r"</table>(?!</div>)", "</table></div>", h)
    h = h.replace('<div class="tbl"><div class="tbl"><table>', '<div class="tbl"><table>').replace("</table></div></div>", "</table></div>")
    h = h.replace("<blockquote>", '<aside class="callout">').replace("</blockquote>", "</aside>")
    # drop empty header rows (| | | tables)
    h = re.sub(r"<thead>\s*<tr>\s*(<th></th>\s*)+</tr>\s*</thead>", "", h)
    h = classify(h)
    h = link_names(h)
    h = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', h)
    related = []
    for r in [x.strip() for x in meta.get("related", "").split("|") if x.strip()]:
        related.append({"name": r, "slug": NAMES.get(r.lower())})
    return {
        "slug": slug, "title": meta["title"], "group": meta["group"],
        "version": meta["version"], "effective": meta["effective"], "review": meta["review"],
        "aim": meta.get("aim", ""), "objectives": [o.strip() for o in meta.get("objectives", "").split("|") if o.strip()],
        "footer": meta.get("footer", ""),
        "related": related, "sections": sections, "html": h, "source": SOURCE[slug],
    }

data = [build(s) for s in ORDER]
(ROOT / "data.json").write_text(json.dumps(data, ensure_ascii=False))
tpl = (ROOT / "template.html").read_text()
out = tpl.replace("/*__DATA__*/[]", json.dumps({"groups": GROUPS, "cpgs": data}, ensure_ascii=False).replace("</", "<\\/"))
(ROOT / "site" / "index.html").write_text(out)
print("built", len(data), "CPGs;", sum(len(d["sections"]) for d in data), "sections;", len(out)//1024, "KB")
