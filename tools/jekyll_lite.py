"""Minimal Jekyll emulator, enough to render this site for verification.
Handles: front matter, defaults, layouts (nested), site.posts, permalinks,
relative_url / absolute_url / date filters. NOT a replacement for the real build.

usage: jekyll_lite.py <site_dir> <out_dir>
"""
import sys, re, pathlib, datetime, yaml
from liquid import Environment, FileSystemLoader
from liquid.builtin import register as _reg

SITE = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2])
cfg = yaml.safe_load((SITE / "_config.yml").read_text(encoding="utf-8"))
BASE = cfg.get("baseurl", "") or ""; URL = cfg.get("url", "")

def relative_url(v): return BASE + v if v.startswith("/") else BASE + "/" + v
def absolute_url(v): return URL + relative_url(v)
def jdate(v, fmt):
    if isinstance(v, str): v = datetime.datetime.fromisoformat(v.replace(" +0000", "+00:00"))
    if isinstance(v, datetime.date) and not isinstance(v, datetime.datetime):
        v = datetime.datetime(v.year, v.month, v.day)
    fmt = fmt.replace("%-d", str(v.day))
    return v.strftime(fmt)

env = Environment(loader=FileSystemLoader(str(SITE / "_layouts")))
env.filters["relative_url"] = relative_url
env.filters["absolute_url"] = absolute_url
env.filters["date"] = jdate

def front(text):
    m = re.match(r'(?s)^---\r?\n(.*?)\r?\n---\r?\n?', text)
    if not m: return {}, text
    return (yaml.safe_load(m.group(1)) or {}), text[m.end():]

def apply_defaults(data, typ):
    for d in cfg.get("defaults", []):
        if d["scope"].get("type") == typ:
            for k, v in d["values"].items(): data.setdefault(k, v)
    return data

def render(text, ctx):
    return env.from_string(text).render(**ctx)

def with_layout(content, page, site):
    lay = page.get("layout")
    while lay:
        ldata, ltext = front((SITE / "_layouts" / f"{lay}.html").read_text(encoding="utf-8"))
        content = render(ltext, {"content": content, "page": page, "site": site})
        lay = ldata.get("layout")
    return content

# posts
posts = []
for f in sorted((SITE / "_posts").glob("*.*")):
    data, body = front(f.read_text(encoding="utf-8"))
    apply_defaults(data, "posts")
    m = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.\w+$', f.name)
    slug = m.group(2)
    d = data.get("date") or m.group(1)
    if isinstance(d, str): d = datetime.datetime.fromisoformat(d.replace(" +0000", "+00:00"))
    elif isinstance(d, datetime.date) and not isinstance(d, datetime.datetime): d = datetime.datetime(d.year, d.month, d.day)
    data["date"] = d
    data["url"] = data.get("permalink", "/blog/:title.html").replace(":title", slug)
    data["_body"] = body; data["layout"] = data.get("layout", "post")
    posts.append(data)
posts.sort(key=lambda p: (p["date"], p["url"]), reverse=True)
site = dict(cfg); site["posts"] = posts; site["time"] = datetime.datetime.now()

def emit(url, html):
    p = OUT / url.lstrip("/")
    if url.endswith("/"): p = p / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(html, encoding="utf-8")

for p in posts:
    body = render(p["_body"], {"page": p, "site": site})
    emit(p["url"], with_layout(body, p, site))

for f in list(SITE.glob("*.html")) + list((SITE / "blog").glob("*.html")):
    data, body = front(f.read_text(encoding="utf-8"))
    rel = "/" + f.relative_to(SITE).as_posix()
    data["url"] = rel; data.setdefault("layout", None)
    body = render(body, {"page": data, "site": site})
    emit(rel, with_layout(body, data, site))
print("rendered", sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*.html")))
