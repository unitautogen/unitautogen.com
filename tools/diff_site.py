"""Compare rendered Jekyll pages against the original hand-written pages.
Checks: (1) visible body text identical, (2) every href/src resolves to the same target
(after normalising the base path), (3) head metas match, (4) every local asset exists."""
import re, sys, html, pathlib, difflib
from html.parser import HTMLParser

SRC = pathlib.Path(sys.argv[1]); REN = pathlib.Path(sys.argv[2]); SITE = pathlib.Path(sys.argv[3]); BASE = sys.argv[4] if len(sys.argv)>4 else ""

class Text(HTMLParser):
    def __init__(s): super().__init__(); s.out=[]; s.skip=0; s.links=[]
    def handle_starttag(s, t, a):
        if t in ("style","script","head"): s.skip += 1
        d = dict(a)
        for k in ("href","src"):
            if k in d: s.links.append(d[k])
    def handle_endtag(s, t):
        if t in ("style","script","head"): s.skip -= 1
    def handle_data(s, d):
        if not s.skip: s.out.append(d)
def parse(p):
    t = Text(); t.feed(p.read_text(encoding="utf-8"))
    txt = re.sub(r'\s+', ' ', html.unescape("".join(t.out))).strip()
    return txt, t.links
def metas(p):
    h = p.read_text(encoding="utf-8")
    head = re.search(r'(?s)<head>(.*?)</head>', h).group(1)
    return dict(re.findall(r'<meta (?:name|property)="([^"]+)" content="([^"]*)"', head)) | {"title": re.search(r'<title>(.*?)</title>', head).group(1)}

def norm_src(link, depth):
    if link.startswith(("http","mailto:","#")): return link
    v = link
    if depth: v = "/" + v[3:] if v.startswith("../") else "/blog/" + v
    else: v = "/" + v
    v = v.replace("/index.html", "/")
    if v == "/docs/logo.png": v = "/assets/logo.png"
    return v
def norm_ren(link):
    if link.startswith(("http","mailto:","#")): return link
    assert link.startswith(BASE), f"link without baseurl: {link}"
    v = link[len(BASE):]
    return v.replace("/index.html", "/")

pages = {"index.html":0, "sql-server.html":0, "postgresql.html":0, "blog/index.html":1,
         "blog/rls-is-a-compliance-control.html":1, "blog/most-postgres-rls-ships-untested.html":1,
         "blog/testing-rls-with-jwt-custom-claims-locally.html":1}
ok = True
for name, depth in pages.items():
    st, sl = parse(SRC / name); rt, rl = parse(REN / name)
    if st != rt:
        ok = False; print(f"TEXT DIFF {name}")
        for l in difflib.unified_diff(st.split(". "), rt.split(". "), lineterm="", n=0): print("   ", l[:200])
    a = [norm_src(l, depth) for l in sl]; b = [norm_ren(l) for l in rl]
    # rendered pages add: css link, canonical, feed alternate -> drop those before comparing
    b = [l for l in b if not l.endswith(("/assets/css/site.css", "/feed.xml")) and not l.startswith(("https://unitautogen.github.io","https://unitautogen.com/"))]
    a = [l for l in a if not l.endswith("/feed.xml") and not l.startswith("https://unitautogen.com/")]  # src canonical
    if a != b:
        ok = False; print(f"LINK DIFF {name}\n  src: {a}\n  ren: {b}")
    sm, rm = metas(SRC / name), metas(REN / name)
    for k in ("title","description","og:title","og:description","og:type"):
        if k in sm and html.unescape(sm[k]) != html.unescape(rm.get(k, "")): ok = False; print(f"META DIFF {name} {k}: {sm[k]!r} != {rm.get(k)!r}")
    if "og:image" in sm:
        want = sm["og:image"].replace("https://unitautogen.com", "").lstrip("/")
        if not rm.get("og:image","").endswith(want): ok = False; print(f"META DIFF {name} og:image {rm.get('og:image')}")
    for l in rl:
        if l.startswith(BASE) and not l.endswith("/") and "." in l.rsplit("/",1)[-1]:
            local = SITE / l[len(BASE):].lstrip("/")
            is_post = l[len(BASE):].startswith("/blog/") and (REN / l[len(BASE):].lstrip("/")).exists()  # generated from _posts
            if not local.exists() and not l.endswith("feed.xml") and not is_post: ok = False; print(f"MISSING FILE {name}: {l}")
    print(("OK   " if ok else "CHECK") + f" {name}: {len(rt)} chars, {len(rl)} links")
print("RESULT:", "ALL IDENTICAL" if ok else "DIFFERENCES FOUND")

