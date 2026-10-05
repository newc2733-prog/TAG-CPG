"""Package the built handbook (site/index.html) as a standalone, installable web app in app/handbook/.
Run build.py first. Output is plain static files: upload the handbook folder to any web host."""
import re, json, shutil, pathlib, datetime

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "site"
OUT = ROOT / "app" / "handbook"
STAMP = datetime.datetime.now()
VERSION = STAMP.strftime("%Y%m%d-%H%M")
BUILD_LABEL = STAMP.strftime("%-d %b %Y")

if OUT.exists(): shutil.rmtree(OUT)
(OUT / "fonts").mkdir(parents=True); (OUT / "icons").mkdir()
shutil.copytree(SRC / "fig", OUT / "fig")

# fonts and icons are kept beside this script
for f in ["lexend-latin-wght-normal.woff2", "lexend-latin-ext-wght-normal.woff2"]:
    shutil.copy(ROOT / "fonts" / f, OUT / "fonts" / f)
for f in (ROOT / "icons").iterdir():
    shutil.copy(f, OUT / "icons" / f.name)

page = (SRC / "index.html").read_text()
# local font instead of Google Fonts
page = re.sub(r'<link rel="preconnect"[^>]*>\n', "", page)
page = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n', "", page)
page = re.sub(r"<title>.*?</title>\n", "", page, count=1)
page = re.sub(r'<meta name="description"[^>]*>\n', "", page, count=1)
FONT_CSS = """@font-face{font-family:"Lexend";font-style:normal;font-display:swap;font-weight:100 900;src:url(fonts/lexend-latin-ext-wght-normal.woff2) format("woff2");unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF}
@font-face{font-family:"Lexend";font-style:normal;font-display:swap;font-weight:100 900;src:url(fonts/lexend-latin-wght-normal.woff2) format("woff2");unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
html{-webkit-text-size-adjust:100%}body{margin:0}img{max-width:100%}[hidden]{display:none!important}
:root{padding-bottom:env(safe-area-inset-bottom,0px)}
.update{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(env(safe-area-inset-bottom,0px) + 16px);z-index:50;background:#111;color:#FBFAF6;border:0;border-radius:999px;padding:12px 20px;font:700 1rem "Lexend",Arial,sans-serif;box-shadow:0 6px 20px rgba(0,0,0,.3);cursor:pointer}
.install{max-width:44rem;margin-top:16px;font-size:.95rem;color:#5A5A5A}
"""
page = page.replace("<style>\n", "<style>\n" + FONT_CSS, 1)
# build date + install hint on the home page; update prompt; offline support
page = page.replace("are shown without a link.</p>`;",
    "are shown without a link.</p>`;\n  h += `<p class=\"install\">Handbook updated " + BUILD_LABEL + ".${standalone ? \"\" : \" To keep it on your phone, use your browser’s Share or menu button and choose Add to Home Screen.\"}</p>`;", 1)
assert "Handbook updated" in page
APP_JS = """
const standalone = (window.matchMedia && matchMedia("(display-mode: standalone)").matches) || navigator.standalone === true;
if ("serviceWorker" in navigator) {
  const hadController = !!navigator.serviceWorker.controller;
  navigator.serviceWorker.register("sw.js").then(reg => {
    const check = () => reg.update().catch(() => {});
    document.addEventListener("visibilitychange", () => { if (!document.hidden) check(); });
    setInterval(check, 60 * 60 * 1000);
  }).catch(() => {});
  let prompted = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (!hadController || prompted) return;   // first install: nothing to announce
    prompted = true;
    const b = document.createElement("button");
    b.className = "update"; b.type = "button"; b.textContent = "New version ready. Tap to update";
    b.addEventListener("click", () => location.reload());
    document.body.append(b);
  });
}
"""
page = page.replace("<script>\nconst DATA", "<script>" + APP_JS + "const DATA", 1)
assert "const standalone" in page
HEAD = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>TAG Trauma Handbook</title>
<meta name="description" content="Trauma Anaesthesia Group clinical practice guidelines, Royal London Hospital.">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#FBFAF6">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="TAG Handbook">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<!-- build {VERSION} -->
"""
style_end = page.index("</style>") + len("</style>")
html_out = HEAD + page[:style_end] + "\n</head>\n<body>\n" + page[style_end:] + "\n</body>\n</html>\n"
(OUT / "index.html").write_text(html_out)

(OUT / "manifest.webmanifest").write_text(json.dumps({
    "name": "TAG Trauma Handbook", "short_name": "TAG Handbook",
    "description": "Trauma Anaesthesia Group clinical practice guidelines, Royal London Hospital.",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#FBFAF6", "theme_color": "#FBFAF6",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ]}, indent=2))
(OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")

files = ["./", "index.html", "manifest.webmanifest"] + sorted(
    str(p.relative_to(OUT)) for d in ("fonts", "icons", "fig") for p in (OUT / d).iterdir())
(OUT / "sw.js").write_text("""// Offline support. A new build changes VERSION, which makes phones fetch the new files.
const VERSION = "%s";
const CACHE = "tag-handbook-" + VERSION;
const FILES = %s;
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES.map(f => new Request(f, {cache: "reload"})))).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith("tag-handbook-") && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  const req = e.request.mode === "navigate" ? "index.html" : e.request;
  e.respondWith(caches.open(CACHE).then(c => c.match(req, {ignoreSearch: true})).then(hit => hit || fetch(e.request)));
});
""" % (VERSION, json.dumps(files, indent=2)))

size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
print("packaged", VERSION, len(files), "cached files,", round(size / 1e6, 1), "MB ->", OUT)
