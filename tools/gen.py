# Generates the static HTML pages for the Refuge City Church site.
# Run from anywhere:  python3 tools/gen.py
# Writes index.html, 404.html and <page>/index.html into the repo root.
# assets/css/site.css is hand edited and not generated.
#
# Links: internal links and asset paths are written root relative ("/visit/") below,
# then rewritten to RELATIVE paths per page ("../visit/") so the site works both
# locally and under the GitHub Pages project path /Website/.
# 404.html can be served by GitHub Pages at any depth, so it uses SITE_BASE instead.
import re, pathlib
SITE_BASE = '/Website/'   # https://refuge-city-church.github.io/Website/
IC_CHECK = '''<svg viewBox="0 0 24 24"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>'''
IC_APP = '''<svg viewBox="0 0 24 24"><rect x="6" y="2" width="12" height="20" rx="3"/><path d="M11 18h2"/></svg>'''
IC_GROUPS = '''<svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.5"/><path d="M2 20c0-3.5 3-6 7-6s7 2.5 7 6"/><circle cx="17" cy="9" r="2.5"/><path d="M17 14c3 0 5 2 5 5"/></svg>'''
IC_CHART = '''<svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/></svg>'''
FB = '''<svg viewBox="0 0 24 24"><path d="M13.5 22v-8.2h2.8l.4-3.2h-3.2V8.5c0-.9.3-1.6 1.6-1.6h1.7V4.1c-.3 0-1.3-.1-2.5-.1-2.5 0-4.2 1.5-4.2 4.3v2.4H7.3v3.2h2.8V22h3.4z"/></svg>'''
IG = '''<svg viewBox="0 0 24 24"><path d="M12 7.3A4.7 4.7 0 1 0 12 16.7 4.7 4.7 0 0 0 12 7.3zm0 7.7a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm6-7.9a1.1 1.1 0 1 1-2.2 0 1.1 1.1 0 0 1 2.2 0zM21.9 8.1c-.1-1.6-.4-3-1.6-4.2S17.6 2.2 16 2.1c-1.6-.1-6.4-.1-8 0-1.6.1-3 .4-4.2 1.6S2.2 6.4 2.1 8c-.1 1.6-.1 6.4 0 8 .1 1.6.4 3 1.6 4.2s2.6 1.5 4.2 1.6c1.6.1 6.4.1 8 0 1.6-.1 3-.4 4.2-1.6s1.5-2.6 1.6-4.2c.1-1.6.1-6.4 0-7.9zM19.8 18a3.2 3.2 0 0 1-1.8 1.8c-1.3.5-4.3.4-5.9.4s-4.6.1-5.9-.4A3.2 3.2 0 0 1 4.4 18c-.5-1.3-.4-4.3-.4-5.9s-.1-4.6.4-5.9A3.2 3.2 0 0 1 6.2 4.4c1.3-.5 4.3-.4 5.9-.4s4.6-.1 5.9.4a3.2 3.2 0 0 1 1.8 1.8c.5 1.3.4 4.3.4 5.9s.1 4.6-.4 5.9z"/></svg>'''
YT = '''<svg viewBox="0 0 24 24"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2C.5 9.1.5 12 .5 12s0 2.9.5 4.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1c.5-1.9.5-4.8.5-4.8s0-2.9-.5-4.8zM9.7 15.5v-7l6 3.5-6 3.5z"/></svg>'''
FB_URL = 'https://www.facebook.com/p/Refuge-City-Church-61572074312910/'
IG_URL = 'https://www.instagram.com/refugecity.cc/'
GROUPS_URL = 'https://refuge-city-church-507680.churchcenter.com/groups'
OUT = pathlib.Path(__file__).resolve().parent.parent
# Small menu behavior. Without JS the <details> menu still opens and closes, and the icon still becomes an X.
MENU_JS = '''<script>
(function(){
  var nav = document.querySelector('details.nav');
  if (!nav) return;
  var btn = nav.querySelector('summary.menu');
  var panel = nav.querySelector('.panel');
  function el(t){ return t && t.nodeType === 1 ? t : (t && t.parentElement); }
  function sync(focusEl){
    btn.setAttribute('aria-expanded', nav.open ? 'true' : 'false');
    if (focusEl) focusEl.focus();
  }
  nav.addEventListener('toggle', function(){
    if (nav.open) sync(panel.querySelector('a'));
    else sync();
  });
  document.addEventListener('keydown', function(e){
    if ((e.key === 'Escape' || e.key === 'Esc') && nav.open){
      nav.open = false;
      sync(btn);
    }
  });
  document.addEventListener('click', function(e){
    if (!nav.open) return;
    var t = el(e.target);
    if (!t) return;
    if (t.closest('.panel a')){ nav.open = false; sync(); return; }
    if (t.closest('.nav-backdrop') || !nav.contains(t)){ nav.open = false; sync(btn); }
  });
})();
</script>'''

def tag(t, dark=False): return f'<span class="tag{" dark" if dark else ""}">[{t}]</span>'
TIME = 'Sundays 11 AM'
ADDR = '2457 West Point Rd, LaGrange, GA 30240'
ADDR_NOTE = 'confirm 2457 is also the physical meeting address'
GIVE_TAG = 'PLACEHOLDER: Church Center giving link, pending Eric'
FORM_TAG = 'PLACEHOLDER: form connects to Planning Center workflow, pending Eric'

NAV = [('/', 'Home'), ('/visit/', 'Plan Your Visit'), ('/give/', 'Give'), ('/watch/', 'Watch'),
       ('/prayer/', 'Prayer'), ('/next-steps/', 'Next Steps'), ('/members/', 'Members Hub'),
       ('/about/', 'About')]

def page(path, title, body, desc='Refuge City Church in LaGrange, GA. Preview site.', social=True):
    nav = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if h == path else ""}>{n}</a>' for h, n in NAV)
    social_block = f'''<div class="social">
  <a href="{FB_URL}" aria-label="Facebook">{FB}</a>
  <a href="{IG_URL}" aria-label="Instagram">{IG}</a>
  <a class="ph" href="#" aria-label="YouTube (placeholder)">{YT}</a>
</div>
<p class="soc-note">YouTube link: [NEEDED FROM CHURCH: channel URL]</p>
''' if social else ''
    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | Refuge City Church</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="/assets/img/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css">
</head><body>
<a class="skip" href="#main">Skip to content</a>
<div class="banner">PREVIEW SITE · Items tagged in yellow are placeholders until confirmed by the church</div>
<header>
  <a class="brand" href="/" aria-label="Refuge City Church, home"><img src="/assets/img/logo.png" alt="">Refuge City</a>
  <details class="nav"><summary class="menu" aria-label="Menu" aria-expanded="false" aria-controls="site-menu"><span></span></summary><button type="button" class="nav-backdrop" tabindex="-1" aria-hidden="true"></button><nav class="panel" id="site-menu">{nav}</nav></details>
</header>
<main id="main">
{body}
</main>
{social_block}<footer>
  <div class="brand"><img src="/assets/img/logo.png" alt="">Refuge City Church</div>
  <div class="tagline">Energize · Emancipate · Equip · Emerge</div>
  <div><b style="color:#fff">Address:</b> {ADDR}<p class="review-note">{ADDR_NOTE}</p></div>
  <div><b style="color:#fff">Contact:</b> {tag("NEEDED FROM CHURCH: phone / email", True)}</div>
  <div><b>{TIME}</b></div>
  <hr>
  <div class="foot-links"><a href="/visit/">Plan Your Visit</a><a href="/give/">Give</a><a href="/watch/">Watch</a><a href="/prayer/">Prayer</a><a href="/members/">Members</a><a href="/about/">About</a></div>
  <div class="fine" style="margin-top:10px">© Refuge City Church · <a class="text-link" href="/privacy/" style="color:#cfcfcf;text-decoration:underline">Privacy</a> · Preview build, not published.</div>
</footer>
{MENU_JS}
</body></html>
'''
    if path == '/404':
        f, prefix = OUT / '404.html', SITE_BASE
    elif path == '/':
        f, prefix = OUT / 'index.html', './'
    else:
        f = OUT / path.strip('/') / 'index.html'
        prefix = '../' * len(path.strip('/').split('/'))
    html = re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{prefix}', html)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html)

def subhero(crumb, h1, sub=''):
    crumb_html = f'<div class="crumb">{crumb}</div>' if crumb else ''
    return f'''<div class="hero short">{crumb_html}<h1>{h1}</h1>{f'<p>{sub}</p>' if sub else ''}</div>'''

INFO = f'''<div class="info"><b>{TIME}</b><br><b>Where:</b> {ADDR}<p class="review-note">{ADDR_NOTE}</p></div>'''

STEPS = f'''<a class="step" href="/visit/"><div class="n" aria-hidden="true">01</div><div><h3>I'm New</h3><p>[PLACEHOLDER] What a first visit looks like.</p></div><span class="ar" aria-hidden="true">→</span></a>
    <a class="step" href="{GROUPS_URL}"><div class="n" aria-hidden="true">02</div><div><h3>Join a Group</h3><p>Browse groups on Church Center. [CONFIRM]</p></div><span class="ar" aria-hidden="true">→</span></a>
    <a class="step" href="/next-steps/"><div class="n" aria-hidden="true">03</div><div><h3>Serve</h3><p>[NEEDED FROM CHURCH: serve info]</p></div><span class="ar" aria-hidden="true">→</span></a>'''

# ---------- HOME ----------
home = f'''<div class="hero">
  <div class="ph-label">PLACEHOLDER PHOTO<small>Family at home / church family moment</small></div>
  <div class="eyebrow">Refuge City Church · LaGrange, GA</div>
  <h1 class="phrase">There is more to you and we want to help you discover it.</h1>
  <p class="family">Family. Building. Together. Starting in your home.</p>
</div>
<div class="ctas">
  <a class="btn primary" href="/visit/">Plan Your Visit <span class="ar">→</span></a>
  <a class="btn dark" href="/give/">Give <span class="ar">→</span></a>
  <a class="btn light" href="/watch/"><span>Watch<span class="soon">COMING SOON</span></span> <span class="ar">→</span></a>
</div>
{INFO}
<div class="words" aria-label="Energize, Emancipate, Equip, Emerge"><span>Energize</span><span>Emancipate</span><span>Equip</span><span>Emerge</span></div>
<section class="tight"><a class="btn light" href="/prayer/">Prayer request <span class="ar">→</span></a></section>
<section>
  <div class="sec-h"><h2>We Believe</h2><span class="src review-note">From refugecity.cc</span></div>
  <div class="card values">
    <div class="val"><div class="ic">01</div><div><h3>In Jesus and the Bible</h3><p>“The Bible is God’s Word given to man to guide our lives.”</p></div></div>
    <div class="val"><div class="ic">02</div><div><h3>In our City</h3><p>“We love our city.” “We believe that her best days are just ahead.”</p></div></div>
    <div class="val"><div class="ic">03</div><div><h3>In Each Other</h3><p>“At Refuge City, unity is a core value.”</p></div></div>
    <div class="val"><div class="ic">04</div><div><h3>In You</h3><p>“Yes, you heard us. We believe in YOU!”</p></div></div>
  </div>
  <p class="note"><span class="review-note">Excerpts quoted from the church site. </span><a class="text-link" href="/about/" style="color:#167a3c;font-weight:700">Read all of We Believe&nbsp;→</a></p>
</section>
<section>
  <div class="sec-h"><h2>Next Steps</h2><a href="/next-steps/">See all →</a></div>
  <div class="steps">
    {STEPS}
  </div>
</section>
<section id="kids">
  <div class="kids">
    <div class="ph"><span>PLACEHOLDER PHOTO · KIDS</span></div>
    <div class="body">
      <h2>Kids <em>District</em></h2>
      <p>{tag("PLACEHOLDER", True)} Short description of the kids ministry. {tag("NEEDED FROM CHURCH: ages / times", True)}</p>
      <a class="btn primary" href="#">Kids check in <span class="ar">→</span></a>
      <p class="note">{tag("PLACEHOLDER: Kids District check in link")}</p>
    </div>
  </div>
</section>
<section>
  <div class="sec-h"><h2>Members Hub</h2></div>
  <a class="btn primary" href="/resources/">Church family? Open Refuge Resources <span class="ar">→</span></a>
</section>'''
page('/', 'Home', home)

VISIT_JS = r'''<script>
(function(){
  var dates = document.getElementById('visit-dates');
  if (!dates) return;
  var now = new Date();
  var add = (7 - now.getDay()) % 7;
  for (var i = 0; i < 4; i++) {
    var day = new Date(now.getFullYear(), now.getMonth(), now.getDate() + add + i * 7);
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = day.toLocaleDateString('en-US', {month:'short', day:'numeric'});
    b.setAttribute('aria-pressed', 'false');
    dates.appendChild(b);
  }
  function choose(root){
    root.addEventListener('click', function(e){
      var b = e.target.closest('button');
      if (!b || !root.contains(b)) return;
      var all = root.querySelectorAll('button');
      for (var n = 0; n < all.length; n++) all[n].setAttribute('aria-pressed', 'false');
      b.setAttribute('aria-pressed', 'true');
    });
  }
  choose(dates);
  choose(document.getElementById('visit-kidsjoin'));
  choose(document.getElementById('visit-seats'));
  function counter(minusId, plusId, outId){
    var n = outId === 'adults-n' ? 1 : 0;
    var out = document.getElementById(outId);
    document.getElementById(minusId).addEventListener('click', function(){ if (n > 0) { n--; out.textContent = String(n); } });
    document.getElementById(plusId).addEventListener('click', function(){ if (n < 12) { n++; out.textContent = String(n); } });
  }
  counter('adults-minus', 'adults-plus', 'adults-n');
  counter('kids-minus', 'kids-plus', 'kids-n');
  document.getElementById('visit-form').addEventListener('submit', function(e){
    e.preventDefault();
    document.getElementById('visit-form').hidden = true;
    var welcome = document.getElementById('visit-welcome');
    welcome.hidden = false;
    welcome.focus();
  });
})();
</script>'''

# ---------- VISIT ----------
visit = subhero('Plan Your Visit', 'We can’t wait to <em>know you!</em>') + f'''
{INFO}
<section class="tight">
  <p>Every first time guest gets a host who stays with them all Sunday.</p>
</section>
<section>
  <div class="yt-box"><span>Pre-visit video</span></div>
  <p class="note">{tag("NEEDED FROM CHURCH: video: where to park, walking in the door, what to expect")}</p>
</section>
<section>
  <a class="btn primary wide" href="#">Open map <span class="ar">→</span></a>
  <p class="note">{tag("PLACEHOLDER: map link")}</p>
</section>
<section>
  <div class="sec-h"><h2>Let us know</h2></div>
  <p class="note">{tag(FORM_TAG)}</p>
  <form id="visit-form" class="form" action="#" method="post" aria-label="Plan your visit (preview, does not send)">
    <fieldset>
      <legend>What Sunday are you coming?</legend>
      <div class="choices" id="visit-dates"></div>
    </fieldset>
    <label for="visit-from">Where are you coming from?</label>
    <input id="visit-from" name="from" autocomplete="off" maxlength="80">
    <p class="count-label" id="adults-label">Adults</p>
    <div class="counter"><button type="button" id="adults-minus" aria-label="Fewer adults">−</button><span class="n" id="adults-n">1</span><button type="button" id="adults-plus" aria-label="More adults">+</button></div>
    <p class="count-label" id="kids-label">Kids</p>
    <div class="counter"><button type="button" id="kids-minus" aria-label="Fewer kids">−</button><span class="n" id="kids-n">0</span><button type="button" id="kids-plus" aria-label="More kids">+</button></div>
    <fieldset>
      <legend>Will your kids join Kids District?</legend>
      <div class="choices" id="visit-kidsjoin">
        <button type="button" aria-pressed="false">Yes</button>
        <button type="button" aria-pressed="false">No</button>
        <button type="button" aria-pressed="false">No kids</button>
      </div>
    </fieldset>
    <fieldset>
      <legend>Where would you like to sit?</legend>
      <p class="note">We ask because we'll save your seats.</p>
      <div class="choices" id="visit-seats">
        <button type="button" aria-pressed="false">Front</button>
        <button type="button" aria-pressed="false">Middle</button>
        <button type="button" aria-pressed="false">Back</button>
      </div>
    </fieldset>
    <label for="visit-name">Name</label>
    <input id="visit-name" name="name" autocomplete="name">
    <label for="visit-phone">Phone</label>
    <input id="visit-phone" name="phone" autocomplete="tel" inputmode="tel">
    <label for="visit-email">Email</label>
    <input id="visit-email" name="email" autocomplete="email" inputmode="email">
    <label for="visit-note">Anything else? (optional)</label>
    <textarea id="visit-note" name="note" rows="3"></textarea>
    <button class="btn primary wide" type="submit">Send</button>
  </form>
  <div id="visit-welcome" class="card welcome" tabindex="-1" hidden>
    <h2>We're so glad you're coming.</h2>
    <p>We look forward to meeting you.</p>
    <p>A host will reach out before Sunday.</p>
    <p class="note">{tag(FORM_TAG)}</p>
  </div>
</section>
{VISIT_JS}'''
page('/visit/', 'Plan Your Visit', visit)

PRAYER_JS = r'''<script>
(function(){
  var form = document.getElementById('prayer-form');
  if (!form) return;
  var choices = document.getElementById('prayer-share');
  choices.addEventListener('click', function(e){
    var b = e.target.closest('button');
    if (!b) return;
    var all = choices.querySelectorAll('button');
    for (var i = 0; i < all.length; i++) all[i].setAttribute('aria-pressed', 'false');
    b.setAttribute('aria-pressed', 'true');
  });
  form.addEventListener('submit', function(e){
    e.preventDefault();
    form.hidden = true;
    var done = document.getElementById('prayer-done');
    done.hidden = false;
    done.focus();
  });
})();
</script>'''

prayer = subhero('', 'Prayer') + f'''
<section>
  <p class="note">{tag(FORM_TAG)}</p>
  <form id="prayer-form" class="form" action="#" method="post" aria-label="Prayer request (preview, does not send)">
    <label for="prayer-name">Name (optional)</label>
    <input id="prayer-name" name="name" autocomplete="name">
    <label for="prayer-request">Request</label>
    <textarea id="prayer-request" name="request" rows="4"></textarea>
    <label for="prayer-contact">Phone or email (optional)</label>
    <input id="prayer-contact" name="contact" autocomplete="on">
    <fieldset>
      <legend>Share with prayer team?</legend>
      <div class="choices" id="prayer-share">
        <button type="button" aria-pressed="false">Yes</button>
        <button type="button" aria-pressed="false">No</button>
      </div>
    </fieldset>
    <button class="btn primary wide" type="submit">Send</button>
  </form>
  <div id="prayer-done" class="card welcome" tabindex="-1" hidden>
    <p>Nothing was sent. This is a preview.</p>
    <p class="note">{tag(FORM_TAG)}</p>
  </div>
</section>
{PRAYER_JS}'''
page('/prayer/', 'Prayer', prayer)

# ---------- GIVE ----------
give = subhero('', 'Give', tag(GIVE_TAG, True)) + f'''
<section>
  <div class="card prose"><p>{tag("NEEDED FROM CHURCH: short giving message in the pastor’s words")}</p></div>
  <div style="margin-top:14px"><a class="btn primary wide" href="#">Planning Center Giving <span class="ar">→</span></a></div>
  <p class="note">{tag(GIVE_TAG)} <span class="review-note">This site never handles payments.</span></p>
</section>
<section>
  <div class="sec-h"><h2>Giving History</h2></div>
  <div class="card prose"><p>Members will see past gifts and year end statements in the giving tool. {tag(GIVE_TAG)}</p></div>
</section>'''
page('/give/', 'Give', give)

# ---------- WATCH ----------
watch = subhero('', 'Watch', '') + f'''
<section>
  <div class="yt-box"><span>Live stream coming soon, streaming on YouTube</span></div>
  <p class="note">{tag("NEEDED FROM CHURCH: YouTube channel or live URL")}</p>
  <div class="social-pills"><a class="pill" href="{FB_URL}">Facebook&nbsp;→</a><a class="pill" href="{IG_URL}">Instagram&nbsp;→</a></div>
</section>'''
page('/watch/', 'Watch', watch, social=False)

# ---------- NEXT STEPS ----------
ns = subhero('', 'Next <em>Steps</em>') + f'''
<section><div class="list">
  <div class="card"><h3>I'm New</h3><p>{tag("PLACEHOLDER")} What a first visit looks like. {tag("NEEDED FROM CHURCH: what “starting in your home” means")}</p><div style="margin-top:12px"><a class="pill" href="/visit/">Plan your visit →</a></div></div>
  <div class="card"><h3>Join a Group</h3><p>Groups are listed on the church’s Church Center page. {tag("CONFIRM")}</p><div style="margin-top:12px"><a class="pill" href="{GROUPS_URL}">Browse groups →</a></div></div>
  <div class="card"><h3>Serve</h3><p>{tag("NEEDED FROM CHURCH: serve info")}</p><div style="margin-top:12px"><a class="pill" href="#">Serve signup →</a></div><p class="note">{tag("PLACEHOLDER: serve link")}</p></div>
</div></section>'''
page('/next-steps/', 'Next Steps', ns)

# ---------- KIDS (old links redirect home) ----------
kids_dir = OUT / 'kids'
kids_dir.mkdir(parents=True, exist_ok=True)
(kids_dir / 'index.html').write_text('''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta http-equiv="refresh" content="0; url=../#kids">
<title>Kids District | Refuge City Church</title>
<link rel="icon" href="../assets/img/logo.png">
</head><body>
<p><a href="../#kids">Kids District is on the home page.</a></p>
</body></html>
''')

# ---------- MEMBERS ----------
mem = subhero('', 'Members <em>Hub</em>') + f'''
<section>
  <a class="btn primary" href="/resources/">Church family? Open Refuge Resources <span class="ar">→</span></a>
</section>
<section>
  <div class="sec-h"><h2>More</h2></div>
  <div class="list">
    <a class="btn light" href="/next-steps/">Next Steps <span class="ar">→</span></a>
    <a class="btn light" href="/#kids">Kids District <span class="ar">→</span></a>
    <a class="btn light" href="/give/">Give <span class="ar">→</span></a>
  </div>
</section>'''
page('/members/', 'Members Hub', mem)

# ---------- RESOURCES (unlisted) ----------
resources = subhero('', 'Refuge <em>Resources</em>') + f'''
<section>
  <p>This page is for our church family.</p>
  <div class="hub">
    <a class="tile" href="#"><div class="ti">{IC_APP}</div><div><b>Right Now Media</b><small>[PLACEHOLDER: Right Now Media link]</small></div><span class="ar" aria-hidden="true">↗</span></a>
    <a class="tile" href="#"><div class="ti">{IC_CHECK}</div><div><b>Kids District Check In</b><small>[PLACEHOLDER: Kids District check in link]</small></div><span class="ar" aria-hidden="true">↗</span></a>
    <a class="tile" href="#"><div class="ti">{IC_APP}</div><div><b>Church App</b><small>[PLACEHOLDER: app link]</small></div><span class="ar" aria-hidden="true">↗</span></a>
    <a class="tile" href="#"><div class="ti">{IC_GROUPS}</div><div><b>Groups</b><small>[PLACEHOLDER: groups link]</small></div><span class="ar" aria-hidden="true">↗</span></a>
    <a class="tile" href="#"><div class="ti">{IC_CHART}</div><div><b>City Resources</b><small>Coming soon</small><small>[PLACEHOLDER: City Resources link]</small></div><span class="ar" aria-hidden="true">↗</span></a>
  </div>
</section>'''
page('/resources/', 'Refuge Resources', resources)

# ---------- ABOUT ----------
BEL = [
 ('In Jesus and the Bible', 'Jesus is the Son of God who died on a cross to pardon the sins of anyone who would accept Him. The Bible is God’s Word given to man to guide our lives. Our full doctrinal statement is available upon request.'),
 ('In our City', 'We love our city. Is she perfect? No, but we love her anyway! We believe that her best days are just ahead. That is why we serve our community every chance we get. LaGrange has a history of leading the way in offering hope and help to those in need. We are going to take our city back to those roots. God did command us to love our neighbor as ourselves.'),
 ('In Each Other', 'At Refuge City, unity is a core value. Being unified in the vision and mission makes us one. Every human being is uniquely gifted. When our gifts are aligned in Christ to work together we are unstoppable. We don’t expect perfection from each other but we do expect progress. We believe there is more in each of us and we provoke each other to do more!'),
 ('In You', 'Yes, you heard us. We believe in YOU! We believe that there is more to you. Maybe you have never been to church, or maybe you think that you are too far gone for God to do anything in your life. Are you a discouraged, disenchanted, depleted, and/or defeated Christian? We believe in you. Maybe you have a dream that keeps nagging at the back of your mind. You don’t believe it can happen. We love dreamers, and we believe in you!'),
]
about = subhero('', 'About <em>Us</em>') + f'''
<section>
  <div class="sec-h"><h2>Our Mission</h2><span class="src review-note">From refugecity.cc</span></div>
  <div class="card prose"><p>We exist to engage our community with the life changing love of Jesus for the purpose of seeing them energized, emancipated, and equipped to emerge as who God created them to be.</p></div>
</section>
<section>
  <div class="sec-h"><h2>We Believe</h2><span class="src review-note">From refugecity.cc</span></div>
  <div class="list">{''.join(f'<div class="card"><h3>{h}</h3><p>{t}</p></div>' for h, t in BEL)}</div>
  <p class="note review-note">Text copied from the church’s current site.</p>
</section>
<section>
  <div class="sec-h"><h2>Sundays</h2></div>
  <div class="card prose"><p><b>{TIME}</b></p><p><b>Address:</b> {ADDR}</p><p class="review-note">{ADDR_NOTE}</p></div>
</section>
<section>
  <div class="sec-h"><h2>Our Pastor</h2></div>
  <div class="card prose"><p>{tag("NEEDED FROM CHURCH: pastor name, photo and short bio")}</p></div>
</section>'''
page('/about/', 'About', about)

# ---------- PRIVACY ----------
priv = subhero('', 'Privacy') + f'''
<section><div class="card prose">
  <p>{tag("PLACEHOLDER: draft privacy text, needs church review")}</p>
  <p>This website does not collect or store form entries or payments itself. Forms and giving open the church’s own tools, which have their own privacy policies.</p>
  <p>Questions: {tag("NEEDED FROM CHURCH: contact email")}</p>
</div></section>'''
page('/privacy/', 'Privacy', priv)

page('/404', 'Page not found', subhero('404', 'Page not <em>found</em>') + '<section><a class="btn primary wide" href="/">Back home <span class="ar">→</span></a></section>')
print('ok')
