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
TIME = '11am Sunday'
TIME_TAG = 'TBD, confirming'
ADDR_TAG = 'NEEDED FROM CHURCH: address TBD, 2447 vs 2457 West Point Rd, LaGrange GA 30240'
GIVE_TAG = 'PLACEHOLDER: giving link, pending pastor'

NAV = [('/', 'Home'), ('/visit/', 'Plan Your Visit'), ('/give/', 'Give'), ('/watch/', 'Watch'),
       ('/next-steps/', 'Next Steps'), ('/kids/', 'Kids District'), ('/members/', 'Members Hub'),
       ('/about/', 'About'), ('/privacy/', 'Privacy')]

def page(path, title, body, desc='Refuge City Church in LaGrange, GA. Preview site.'):
    nav = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if h == path else ""}>{n}</a>' for h, n in NAV)
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
  <a class="brand" href="/"><img src="/assets/img/logo.png" alt="Refuge City Church logo">Refuge City</a>
  <details class="nav"><summary class="menu" aria-label="Menu" aria-expanded="false" aria-controls="site-menu"><span></span></summary><button type="button" class="nav-backdrop" tabindex="-1" aria-hidden="true"></button><nav class="panel" id="site-menu">{nav}</nav></details>
</header>
<main id="main">
{body}
</main>
<div class="social">
  <a href="{FB_URL}" aria-label="Facebook">{FB}</a>
  <a href="{IG_URL}" aria-label="Instagram">{IG}</a>
  <a class="ph" href="#" aria-label="YouTube (placeholder)">{YT}</a>
</div>
<p class="soc-note">Facebook: Refuge City Church · Instagram: @refugecity.cc<br>YouTube link: [NEEDED FROM CHURCH: channel URL]</p>
<footer>
  <div class="brand"><img src="/assets/img/logo.png" alt="">Refuge City Church</div>
  <div class="tagline">Energize · Emancipate · Equip · Emerge</div>
  <div><b style="color:#fff">Address:</b> {tag(ADDR_TAG, True)}</div>
  <div><b style="color:#fff">Contact:</b> {tag("NEEDED FROM CHURCH: phone / email", True)}</div>
  <div><b style="color:#fff">Sundays:</b> {TIME} {tag(TIME_TAG, True)}</div>
  <hr>
  <div class="foot-links"><a href="/visit/">Plan a Visit</a><a href="/give/">Give</a><a href="/members/">Members</a><a href="/about/">About</a><a href="/privacy/">Privacy</a></div>
  <div class="fine" style="margin-top:10px">© Refuge City Church · Preview build, not published.</div>
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
    return f'''<div class="hero short"><div class="crumb">{crumb}</div><h1>{h1}</h1>{f'<p>{sub}</p>' if sub else ''}</div>'''

INFO = f'''<div class="info"><b>Sundays:</b> {TIME} {tag(TIME_TAG)}<br><b>Where:</b> {tag(ADDR_TAG)}</div>'''

HUB = f'''<div class="hub">
    <a class="tile" href="#"><div class="ti">{IC_CHECK}</div><div><b>Kids District Check In</b><small>[PLACEHOLDER: check in link]</small></div></a>
    <a class="tile" href="#"><div class="ti">{IC_APP}</div><div><b>Church App</b><small>[PLACEHOLDER: app link]</small></div></a>
    <a class="tile" href="{GROUPS_URL}"><div class="ti">{IC_GROUPS}</div><div><b>Groups</b><small>Church Center Groups [CONFIRM]</small></div></a>
    <a class="tile" href="#"><div class="ti">{IC_CHART}</div><div><b>Giving History</b><small>[{GIVE_TAG}]</small></div></a>
  </div>'''

STEPS = f'''<a class="step" href="/visit/"><div class="n" aria-hidden="true">01</div><div><h3>I'm New</h3><p>[PLACEHOLDER] What a first visit looks like.</p></div><span class="ar" aria-hidden="true">→</span></a>
    <a class="step" href="{GROUPS_URL}"><div class="n" aria-hidden="true">02</div><div><h3>Join a Group</h3><p>Browse groups on Church Center. [CONFIRM]</p></div><span class="ar" aria-hidden="true">→</span></a>
    <a class="step" href="/next-steps/"><div class="n" aria-hidden="true">03</div><div><h3>Serve</h3><p>[NEEDED FROM CHURCH: serve info]</p></div><span class="ar" aria-hidden="true">→</span></a>'''

# ---------- HOME ----------
home = f'''<div class="hero">
  <div class="ph-label">PLACEHOLDER PHOTO<small>Family at home / church family moment</small></div>
  <div class="eyebrow">Refuge City Church · LaGrange, GA</div>
  <h1><em>Family.</em> Building. Together.<span class="sub">Starting in your home.</span></h1>
</div>
<div class="ctas">
  <a class="btn primary" href="/visit/">Plan Your Visit <span class="ar">→</span></a>
  <a class="btn dark" href="/give/">Give <span class="ar">→</span></a>
  <a class="btn light" href="/watch/"><span>Watch<span class="soon">COMING SOON</span></span> <span class="ar">→</span></a>
</div>
{INFO}
<p class="quote">“There is more to you and we want to help you discover it.”</p>
<p class="review-note">From Refuge City's Church Center page</p>
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
<section>
  <div class="kids">
    <div class="ph"><span>PLACEHOLDER PHOTO · KIDS</span></div>
    <div class="body">
      <h2>Kids <em>District</em></h2>
      <p>{tag("PLACEHOLDER", True)} Short description of the kids ministry. {tag("NEEDED FROM CHURCH: ages / times", True)}</p>
      <a class="pill" href="/kids/">Learn more →</a>
    </div>
  </div>
</section>
<section>
  <div class="sec-h"><h2>Members Hub</h2><a href="/members/">Open hub&nbsp;→</a></div>
  {HUB}
</section>'''
page('/', 'Home', home)

# ---------- VISIT ----------
visit = subhero('Plan Your Visit', 'We can’t wait to <em>know you!</em>') + f'''
{INFO}
<section>
  <a class="btn primary wide" href="#">Open map <span class="ar">→</span></a>
  <p class="note">{tag("PLACEHOLDER: map link, waiting on confirmed address")}</p>
</section>
<section>
  <div class="sec-h"><h2>What to Expect</h2></div>
  <div class="card prose"><p>{tag("NEEDED FROM CHURCH: parking and where to walk in")}</p><p>{tag("NEEDED FROM CHURCH: what happens for kids on Sunday")}</p><p>{tag("NEEDED FROM CHURCH: how long service runs, what to wear")}</p>
  <p>Look for Reggie! He will help you find us!</p><p class="review-note">From the church’s Church Center page.</p></div>
</section>
<section>
  <div class="sec-h"><h2>Let Us Know</h2>{tag("PREVIEW ONLY")}</div>
  <div class="card">
    <p class="note" style="margin:0 0 6px">This form does not send anything. The real form will be a Planning Center form. {tag("PLACEHOLDER: Planning Center form link, pending pastor")}</p>
    <form class="form" onsubmit="return false" aria-label="Plan your visit (preview, does not submit)">
      <label>First and last name</label><input disabled placeholder="Name">
      <label>Email</label><input disabled placeholder="you@example.com">
      <label>Phone (optional)</label><input disabled placeholder="Phone">
      <label>What Sunday are you coming?</label><input disabled placeholder="Pick a Sunday">
      <label>How many adults? How many kids, and ages?</label><input disabled placeholder="2 adults, 2 kids (5 and 8)">
      <label>Anything we should know?</label><textarea disabled rows="3"></textarea>
      <button class="btn primary wide" type="button" disabled>Send (preview only)</button>
    </form>
  </div>
</section>'''
page('/visit/', 'Plan Your Visit', visit)

# ---------- GIVE ----------
give = subhero('Give', 'Give', tag(GIVE_TAG, True)) + f'''
<section>
  <div class="card prose"><p>{tag("NEEDED FROM CHURCH: short giving message in the pastor’s words")}</p></div>
  <div style="margin-top:14px"><a class="btn primary wide" href="#">Give online <span class="ar">→</span></a></div>
  <p class="note">{tag(GIVE_TAG)} <span class="review-note">The button will link out to the giving tool the pastor keeps. This site never handles payments.</span></p>
</section>
<section>
  <div class="sec-h"><h2>Giving History</h2></div>
  <div class="card prose"><p>Members will see past gifts and year end statements in the giving tool. {tag(GIVE_TAG)}</p></div>
</section>'''
page('/give/', 'Give', give)

# ---------- WATCH ----------
watch = subhero('Watch', 'Watch', '') + f'''
<section>
  <div class="card soon-card"><span class="soon" style="font:700 11px Inter;background:#ffe78a;color:#4a3800;padding:6px 10px;border-radius:999px">COMING SOON</span>
  <div class="big">Live stream</div>
  <p class="prose">The live stream will show up here. {tag("NEEDED FROM CHURCH: stream platform and channel")}</p></div>
  <div class="card prose" style="margin-top:12px"><p>Until then, find us here:</p><div class="social-pills"><a class="pill" href="{FB_URL}">Facebook&nbsp;→</a><a class="pill" href="{IG_URL}">Instagram&nbsp;→</a></div></div>
</section>'''
page('/watch/', 'Watch', watch)

# ---------- NEXT STEPS ----------
ns = subhero('Next Steps', 'Next <em>Steps</em>') + f'''
<section><div class="list">
  <div class="card"><h3>I'm New</h3><p>{tag("PLACEHOLDER")} What a first visit looks like. {tag("NEEDED FROM CHURCH: what “starting in your home” means")}</p><div style="margin-top:12px"><a class="pill" href="/visit/">Plan your visit →</a></div></div>
  <div class="card"><h3>Join a Group</h3><p>Groups are listed on the church’s Church Center page. {tag("CONFIRM")}</p><div style="margin-top:12px"><a class="pill" href="{GROUPS_URL}">Browse groups →</a></div></div>
  <div class="card"><h3>Serve</h3><p>{tag("NEEDED FROM CHURCH: serve info")}</p><div style="margin-top:12px"><a class="pill" href="#">Serve signup →</a></div><p class="note">{tag("PLACEHOLDER: serve link")}</p></div>
</div></section>'''
page('/next-steps/', 'Next Steps', ns)

# ---------- KIDS ----------
kids = '''<div class="hero short" style="background:radial-gradient(circle at 25% 40%,#ffd36b 0,transparent 30%),radial-gradient(circle at 75% 60%,#5fd38d 0,transparent 35%),radial-gradient(circle at 55% 25%,#6bb8ff 0,transparent 28%),#20302a"><div class="ph-label">PLACEHOLDER PHOTO<small>Kids photo needs church permission</small></div><div class="crumb">Kids District</div><h1>Kids <em>District</em></h1></div>''' + f'''
<section><div class="list">
  <div class="card"><h3>Ages</h3><p>{tag("NEEDED FROM CHURCH: ages")}</p></div>
  <div class="card"><h3>Times</h3><p>{tag("NEEDED FROM CHURCH: kids times")}</p></div>
  <div class="card"><h3>What to expect</h3><p>{tag("NEEDED FROM CHURCH: check in steps, safety, what kids do")}</p></div>
</div>
<div style="margin-top:14px"><a class="btn primary wide" href="#">Kids check in <span class="ar">→</span></a></div>
<p class="note">{tag("PLACEHOLDER: Kids District check in link")}</p></section>'''
page('/kids/', 'Kids District', kids)

# ---------- MEMBERS ----------
mem = subhero('Members Hub', 'Members <em>Hub</em>', 'Everything for church family in one place.') + f'''
<section>
  {HUB}
  <p class="note">Links open the church’s own tools. {tag("NEEDED FROM CHURCH: confirm each link")}</p>
</section>
<section>
  <div class="sec-h"><h2>More</h2></div>
  <div class="list">
    <a class="btn light" href="/next-steps/">Next Steps <span class="ar">→</span></a>
    <a class="btn light" href="/kids/">Kids District <span class="ar">→</span></a>
    <a class="btn light" href="/give/">Give <span class="ar">→</span></a>
  </div>
</section>'''
page('/members/', 'Members Hub', mem)

# ---------- ABOUT ----------
BEL = [
 ('In Jesus and the Bible', 'Jesus is the Son of God who died on a cross to pardon the sins of anyone who would accept Him. The Bible is God’s Word given to man to guide our lives. Our full doctrinal statement is available upon request.'),
 ('In our City', 'We love our city. Is she perfect? No, but we love her anyway! We believe that her best days are just ahead. That is why we serve our community every chance we get. LaGrange has a history of leading the way in offering hope and help to those in need. We are going to take our city back to those roots. God did command us to love our neighbor as ourselves.'),
 ('In Each Other', 'At Refuge City, unity is a core value. Being unified in the vision and mission makes us one. Every human being is uniquely gifted. When our gifts are aligned in Christ to work together we are unstoppable. We don’t expect perfection from each other but we do expect progress. We believe there is more in each of us and we provoke each other to do more!'),
 ('In You', 'Yes, you heard us. We believe in YOU! We believe that there is more to you. Maybe you have never been to church, or maybe you think that you are too far gone for God to do anything in your life. Are you a discouraged, disenchanted, depleted, and/or defeated Christian? We believe in you. Maybe you have a dream that keeps nagging at the back of your mind. You don’t believe it can happen. We love dreamers, and we believe in you!'),
]
about = subhero('About', 'About <em>Us</em>') + f'''
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
  <div class="sec-h"><h2>Our Pastor</h2></div>
  <div class="card prose"><p>{tag("NEEDED FROM CHURCH: pastor name, photo and short bio")}</p></div>
</section>'''
page('/about/', 'About', about)

# ---------- PRIVACY ----------
priv = subhero('Privacy', 'Privacy') + f'''
<section><div class="card prose">
  <p>{tag("PLACEHOLDER: draft privacy text, needs church review")}</p>
  <p>This website does not collect or store form entries or payments itself. Forms and giving open the church’s own tools, which have their own privacy policies.</p>
  <p>Questions: {tag("NEEDED FROM CHURCH: contact email")}</p>
</div></section>'''
page('/privacy/', 'Privacy', priv)

page('/404', 'Page not found', subhero('404', 'Page not <em>found</em>') + '<section><a class="btn primary wide" href="/">Back home <span class="ar">→</span></a></section>')
print('ok')
