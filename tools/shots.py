"""Local check: serves the repo under /website/ (like GitHub Pages), takes 390x844 @2x
screenshots of every page and checks that internal links and assets resolve.

  pip install playwright && python -m playwright install chromium
  python3 tools/shots.py [output_dir]     (default: ./shots, git ignored)

Set CHROME=/path/to/chrome to use an installed Chrome instead of Playwright's Chromium.
"""
import os, sys, socket, tempfile, threading, functools, urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urljoin, urlparse
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'shots'); OUT.mkdir(parents=True, exist_ok=True)
PAGES = {'home': '', 'visit': 'visit/', 'give': 'give/', 'watch': 'watch/', 'next-steps': 'next-steps/',
         'kids': 'kids/', 'members': 'members/', 'about': 'about/', 'privacy': 'privacy/',
         '404': 'some/missing/page/'}

tmp = tempfile.mkdtemp(); os.symlink(ROOT, os.path.join(tmp, 'website'))

class H(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def send_error(self, code, *a, **k):  # mimic GitHub Pages: serve /website/404.html for missing files
        if code == 404:
            body = (ROOT / '404.html').read_bytes()
            self.send_response(404); self.send_header('Content-Type', 'text/html'); self.end_headers(); self.wfile.write(body)
        else: super().send_error(code, *a, **k)

s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
srv = ThreadingHTTPServer(('127.0.0.1', port), functools.partial(H, directory=tmp))
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{port}/website/'

seen, bad, problems = set(), [], []
with sync_playwright() as p:
    kw = {'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {}
    b = p.chromium.launch(args=['--no-sandbox'], **kw)
    pg = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True).new_page()
    failed = []
    pg.on('requestfailed', lambda r: failed.append(r.url))
    pg.on('response', lambda r: failed.append(f'{r.status} {r.url}') if r.status >= 400 and urlparse(r.url).netloc == urlparse(base).netloc and '/missing/' not in r.url else None)
    for name, path in PAGES.items():
        pg.goto(base + path, wait_until='networkidle'); pg.wait_for_timeout(300)
        if pg.evaluate('document.documentElement.scrollWidth') > 390: problems.append(f'{name}: horizontal overflow')
        if not pg.evaluate('!!document.querySelector("link[rel=stylesheet][href*=site]") && getComputedStyle(document.body).backgroundColor !== "rgba(0, 0, 0, 0)"'):
            problems.append(f'{name}: stylesheet not applied')
        robots = pg.evaluate('document.querySelector("meta[name=robots]")?.content')
        if robots != 'noindex, nofollow': problems.append(f'{name}: robots meta = {robots}')
        pg.screenshot(path=str(OUT / f'{name}-full.png'), full_page=True)
        if name in ('home', 'members'): pg.screenshot(path=str(OUT / f'{name}-hero.png'))
        for h in pg.eval_on_selector_all('a[href],link[href],img[src]', 'els=>els.map(e=>e.getAttribute("href")||e.getAttribute("src"))'):
            full = urljoin(pg.url, h).split('#')[0]
            if urlparse(full).netloc == urlparse(base).netloc and '/missing/' not in full:
                if not urlparse(full).path.startswith('/website/'): bad.append((name, h, 'outside /website/'))
                seen.add(full)
    b.close()
for u in sorted(seen):
    try: urllib.request.urlopen(u)
    except Exception as e: bad.append((u, getattr(e, 'code', e)))
srv.shutdown()
print(f'checked {len(seen)} internal URLs; broken: {bad or "none"}')
print('asset/request errors:', sorted(set(failed)) or 'none')
print('problems:', problems or 'none')
print('screenshots in', OUT)
sys.exit(1 if bad or problems or failed else 0)
