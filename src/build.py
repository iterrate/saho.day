#!/usr/bin/env python3
"""Builds saho.day (../docs/*.html) from the page texts below.

Edit the page bodies here, then run:  python3 src/build.py
Every page gets the same header, navigation and footer. Same build as iterrate.in.
"""
import datetime
import hashlib
import json
import subprocess
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "docs"
BASE = "https://saho.day/"
YEAR = datetime.date.today().year
EMAIL = "contact@iterrate.in"   # until saho.day has its own address

NAV = [
    ("./", "Home"),
    ("how-it-works.html", "How it works"),
    ("institutions.html", "For institutions"),
    ("contact.html", "Contact"),
]

HEAD = """<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Saho">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="en_IN">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#F6F3EA" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#282D2A" media="(prefers-color-scheme: dark)">
<meta name="darkreader-lock">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" href="iterrate-icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preload" href="fonts/crimson-pro-latin.woff2" as="font" type="font/woff2" crossorigin>
{extra_head}
<link rel="stylesheet" href="style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap">
    <a class="wordmark" href="./"><b>saho</b><span class="vh">home</span></a>
    <nav aria-label="Main"><ul class="nav">{nav}</ul></nav>
    <script>(function(){{var n=document.querySelector('.nav'),c=n&&n.querySelector('[aria-current]');if(c&&n.scrollWidth>n.clientWidth)n.scrollLeft=c.offsetLeft-(n.clientWidth-c.offsetWidth)/2;}})();</script>
  </div>
</header>
<main id="main">
"""

FOOT = """</main>
<footer class="site-foot">
  <div class="wrap">
    <picture><source srcset="iterrate-icon-dark.svg" media="(prefers-color-scheme: dark)"><img src="iterrate-icon.svg" alt="" width="44" height="44"></picture>
    <div>
      <p>Saho is built by <a href="https://iterrate.in">Iterrate (OPC) Private Limited</a>, Thiruvananthapuram.</p>
      <p><a href="mailto:{email}">{email}</a></p>
    </div>
    <ul>
      <li><a href="https://iterrate.in/company.html">Company details</a></li>
      <li><a href="contact.html#privacy">Privacy</a></li>
      <li>© {year} Iterrate</li>
    </ul>
  </div>
</footer>
</body>
</html>
"""

PAGES = {}
INSTITUTIONS = "a library, a college, a panchayat, a hospital"

# The federation picture on the home page: four places joined by lines in the logo's style,
# with a gap where each line meets a place. The dot is a learner's record moving from
# their library to a college circle. Lines draw on load (CSS), unless reduced motion is set.
FED = """
<figure class="fed">
  <svg viewBox="0 0 460 390" role="img" aria-labelledby="fed-cap">
    <path class="ln sky" pathLength="100" style="--len:100;--d:.1s" d="M177 64H283"/>
    <path class="ln leaf" pathLength="100" style="--len:100;--d:.5s" d="M365 100V286"/>
    <path class="ln earth" pathLength="100" style="--len:100;--d:.9s" d="M283 322H177"/>
    <path class="ln sky" pathLength="100" style="--len:100;--d:1.3s" d="M95 286V100"/>
    <path class="ln leaf" pathLength="100" style="--len:100;--d:1.7s" d="M177 104L283 282"/>
    <rect class="place sky" x="20" y="30" width="150" height="66" rx="10"/>
    <text class="lbl" x="36" y="58">Village library</text>
    <text class="sub" x="36" y="80">a learner's home place</text>
    <rect class="place leaf" x="290" y="30" width="150" height="66" rx="10"/>
    <text class="lbl" x="306" y="58">College</text>
    <text class="sub" x="306" y="80">a circle they join</text>
    <rect class="place earth" x="290" y="290" width="150" height="66" rx="10"/>
    <text class="lbl" x="306" y="318">Hospital</text>
    <text class="sub" x="306" y="340">Saho for its staff</text>
    <rect class="place sky" x="20" y="290" width="150" height="66" rx="10"/>
    <text class="lbl" x="36" y="318">One person</text>
    <text class="sub" x="36" y="340">their own Saho</text>
    <g class="moving">
      <circle class="me" r="8">
        <animateMotion dur="7s" repeatCount="indefinite" path="M177 64H283" keyPoints="0;0;1;1" keyTimes="0;.35;.65;1" calcMode="linear"/>
      </circle>
    </g>
  </svg>
  <figcaption id="fed-cap">Each institution runs its own Saho, and they talk to each other. A learner's record (the dot) goes with them when they join a circle somewhere else.</figcaption>
</figure>
"""

# ---------------------------------------------------------------- Home
PAGES["index.html"] = ("Saho · Learn at your own pace, with people near you",
"Saho is an open, federated learning platform in Malayalam and English. Any institution can run its own Saho, and learners keep what they learn.",
f"""
<div class="wrap">
  <div class="home-top">
    <div>
      <h1><span class="hero-ml" lang="ml">ഒരുമിച്ച് പഠിക്കാം</span>Learn at your own pace, with people <em>near you</em>.</h1>
      <p class="lede">Saho is a guide and a circle for people learning on their own, at any stage of life. It helps you work out what to learn next, and finds you people to learn it with, in Malayalam, English or a mix of both.</p>
      <div class="btns">
        <a class="btn primary" href="how-it-works.html">How it works</a>
        <a class="btn" href="institutions.html">For institutions</a>
      </div>
    </div>
    {FED.strip()}
  </div>

  <section aria-label="What Saho does">
    <div class="grid">
      <div class="tile leaf">
        <h2>A guide</h2>
        <p>Talk things through in the language you think in. The guide suggests next steps and resources, including books on your library's shelf. It doesn't lecture.</p>
      </div>
      <div class="tile sky">
        <h2>Circles</h2>
        <p>Small groups of learners who meet where they are, online and in person. Helpers from the community explain, review and encourage.</p>
      </div>
      <div class="tile earth">
        <h2>Your record</h2>
        <p>What you learn and what you say belong to you. Places see only what you allow, and you can take it with you.</p>
      </div>
    </div>
  </section>
</div>

<div class="band">
  <div class="wrap">
    <p class="big"><em>For finding a direction, not cramming for one exam.</em></p>
    <p>Think of a recent graduate doing part-time work, unsure of what comes next. Saho is for exploring your world, your skills and what's possible, at your own pace.</p>
    <p><a href="how-it-works.html">See how it works</a></p>
  </div>
</div>

<div class="wrap narrow">
  <section class="name">
    <span class="mark earth"></span>
    <h2>The name</h2>
    <p><em>Saho</em> is a call to work together, named for Sahodaran Ayyappan and his ideals of fraternity and equality.</p>
    <p><em>saho.day</em> reads as <em>sahoday</em>: rising together.</p>
  </section>
</div>
""")

# ---------------------------------------------------------------- How it works
PAGES["how-it-works.html"] = ("How Saho works",
"How Saho works: a guide, circles, shared learning paths and a record you own, across places run by different institutions.",
f"""
<div class="wrap narrow">
  <section class="page-top">
    <span class="mark"></span>
    <h1>How Saho works</h1>
    <p class="lede">You talk to a guide, learn with a circle, and keep a record of what you've learned. Different institutions run Saho, and they are all connected.</p>
  </section>

  <ol class="principles">
    <li><h2>Start with a conversation</h2><p>Tell the guide what you do now, what you enjoy and what you're unsure about, in Malayalam, English or a mix of both. It notes what you already know and what you're curious about, and you correct it when it gets you wrong.</p></li>
    <li><h2>Get a plan for this month</h2><p>Small steps you can take: something to watch, something to read (often from your library's shelf), something to try in your own work, and a time to look back on how it went.</p></li>
    <li><h2>Learn with a circle</h2><p>Meet other learners at your library or college, in person and online. Helpers explain, review and encourage, and you can thank them.</p></li>
    <li><h2>Take it with you</h2><p>Your record of what you've learned belongs to you. Move it to another place, or download it, whenever you choose.</p></li>
  </ol>

  <section>
    <span class="mark sky"></span>
    <h2>Places, not a platform</h2>
    <p>Saho isn't one website. Any institution ({INSTITUTIONS}) can run its own Saho, which we call a <em>place</em>. Places talk to each other, so a learner at a village library can join a circle at a college nearby.</p>
    <p>Every learner has one home place for their account and record. They decide what each place can see, and they can take that back. Private conversations with the guide stay in their home place.</p>
    <p>One Saho can serve every library in a panchayat. A single person can also run their own, and join an institution later, or leave it.</p>
  </section>

  <section>
    <span class="mark"></span>
    <h2>Malayalam first</h2>
    <p>Malayalam comes first, including the everyday mix of Malayalam and English, not as an afterthought. English is something Saho helps with, not a gate to get in. Other languages spoken in Keralam will follow soon.</p>
  </section>

  <section>
    <span class="mark earth"></span>
    <h2>AI you can choose</h2>
    <p>The guide uses AI language models. Each place chooses which one, and can run its own on its own hardware. Nobody has to depend on one company, including us.</p>
    <p>The AI helps you think and find your way. People do the teaching and the encouraging.</p>
  </section>

  <section>
    <span class="mark"></span>
    <h2>Open source</h2>
    <p>Saho will be released as open-source software, so that anyone can inspect it, run it and improve it.</p>
  </section>
</div>
""")

# ---------------------------------------------------------------- For institutions
PAGES["institutions.html"] = ("Run Saho at your institution",
"Any institution can run its own Saho for its learners or staff. Iterrate sets it up, hosts it and supports it. Free for learners.",
f"""
<div class="wrap narrow">
  <section class="page-top">
    <span class="mark leaf"></span>
    <h1>Run Saho at your institution</h1>
    <p class="lede">Any institution ({INSTITUTIONS}) can run its own Saho, for the people it serves or for its own staff.</p>
  </section>

  <section>
    <div class="grid two">
      <div class="tile sky"><h2>Libraries</h2><p>A reading room becomes a place to learn with others. Saho points learners to books on your own shelves.</p></div>
      <div class="tile earth"><h2>Panchayats</h2><p>One Saho can serve every library in a panchayat, with local resources and local priorities.</p></div>
      <div class="tile leaf"><h2>Colleges</h2><p>Students and alumni keep learning beyond the syllabus. Your college decides how learning works on its place.</p></div>
      <div class="tile sky"><h2>Any organisation</h2><p>A hospital could run Saho to help its staff keep learning. So could a cooperative, a club or a company.</p></div>
    </div>
  </section>

  <section>
    <span class="mark"></span>
    <h2>Your place, your rules</h2>
    <p>You decide who can join, which AI model the guide uses, and how learning works at your place. You stay connected to every other Saho place, and you can move your place to other hosting at any time.</p>
  </section>

  <section>
    <span class="mark earth"></span>
    <h2>What it costs</h2>
    <p>The basic platform is free for learners. Institutions pay Iterrate for a licence, setup, hosting and support, or run Saho themselves.</p>
    <p>An institution can add its own courses or fees, and learners can pay for premium features beyond what their institution covers.</p>
  </section>

  <section>
    <span class="mark sky"></span>
    <h2>Where it stands</h2>
    <p>Saho is in development, and the first test version is under way. A small pilot with libraries comes next.</p>
    <p>If your institution would like to take part, <a href="contact.html">write to us</a>.</p>
  </section>
</div>
""")

# ---------------------------------------------------------------- Contact
PAGES["contact.html"] = ("Contact · Saho",
"Write to the people building Saho, in Malayalam or English. Includes our privacy note: no cookies, no analytics.",
f"""
<div class="wrap narrow">
  <section class="page-top">
    <span class="mark sky"></span>
    <h1>Get in touch</h1>
    <p class="lede">Want to try Saho, run it at your institution, or help build it? We'd like to hear from you.</p>
  </section>

  <section>
    <div class="card">
      <h2>Email</h2>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p class="small">Saho is built by Iterrate. Its address, phone number and company details are on <a href="https://iterrate.in/contact.html">iterrate.in</a>.</p>
    </div>
  </section>

  <section id="privacy">
    <span class="mark earth"></span>
    <h2>Privacy</h2>
    <p>This site sets no cookies and uses no analytics or trackers. It is hosted on GitHub Pages, and GitHub logs visitors' IP addresses for security (see <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub's privacy statement</a>). Our email is handled by Zoho Mail.</p>
    <p>If you write to us, we use your email address and what you tell us only to reply. We don't share it with anyone, and we delete it when you ask.</p>
  </section>
</div>
""")

# ---------------------------------------------------------------- 404
PAGES["404.html"] = ("Page not found · Saho",
"This page doesn't exist.",
"""
<div class="wrap narrow">
  <section class="page-top">
    <span class="mark sky"></span>
    <h1>Page not found</h1>
    <p class="lede">There's nothing at this address. It may have moved, or the link may have a typo.</p>
    <div class="btns">
      <a class="btn primary" href="./">Go to the home page</a>
      <a class="btn" href="contact.html">Contact us</a>
    </div>
  </section>
</div>
""")

# Structured data for search engines (schema.org).
APP = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Saho",
    "url": BASE,
    "applicationCategory": "EducationalApplication",
    "inLanguage": ["ml", "en"],
    "publisher": {"@type": "Organization", "name": "Iterrate (OPC) Private Limited", "url": "https://iterrate.in/"},
}
EXTRA_HEAD = {
    "index.html": '<link rel="preload" href="fonts/crimson-pro-italic-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
                  '<script type="application/ld+json">' + json.dumps(APP, ensure_ascii=False) + '</script>\n',
}


def asset(name):
    """Link to a file with a short content hash, so browsers fetch it again after each change."""
    h = hashlib.sha1((SITE / name).read_bytes()).hexdigest()[:8]
    return f"{name}?v={h}"


def typography(html):
    """Curly quotes and apostrophes in the visible text, so they can be typed straight here.
    Tags, attributes, scripts and styles are left alone."""
    out = []
    for part in re.split(r"(<script.*?</script>|<style.*?</style>|<[^>]+>)", html, flags=re.S):
        if part.startswith("<"):
            out.append(part)
            continue
        part = re.sub(r"(?<=\w)'(?=\w)", "\u2019", part)          # it's, don't
        part = re.sub(r"(^|[\s(\[\u2014-])'", "\\1\u2018", part)   # opening single
        part = part.replace("'", "\u2019")                          # closing single
        part = re.sub(r'(^|[\s(\[\u2014-])"', "\\1\u201c", part)   # opening double
        part = part.replace('"', "\u201d")                          # closing double
        out.append(part)
    return "".join(out)


def plain(text):
    """The same curly quotes for titles and descriptions (which sit inside attributes)."""
    return typography(text).replace('"', "&quot;")


def last_changed(fname, changed_now):
    """The date a page last really changed: today if this build changed it, otherwise the date
    of the last git commit that touched it (so unchanged pages keep their old date)."""
    if not changed_now:
        try:
            out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", f"{SITE.name}/{fname}"],
                                 cwd=SITE.parent, capture_output=True, text=True).stdout.strip()
            if out:
                return out
        except OSError:
            pass
    return datetime.date.today().isoformat()


def build():
    pages = []
    changed = {}
    for fname, (title, desc, body) in PAGES.items():
        nav = "".join(
            f'<li><a href="{href}"{" aria-current=\"page\"" if href == fname or (href == "./" and fname == "index.html") else ""}>{label}</a></li>'
            for href, label in NAV
        )
        url = BASE if fname == "index.html" else BASE + fname
        head = HEAD.replace('href="style.css"', f'href="{asset("style.css")}"').format(
            title=plain(title), desc=plain(desc), nav=nav, url=url,
            extra_head=EXTRA_HEAD.get(fname, ""))
        if fname == "404.html":
            # GitHub serves this page at any missing address, so links must start from the site root.
            head = head.replace("<head>\n", '<head>\n<base href="/">\n', 1).replace(
                f'<link rel="canonical" href="{BASE}404.html">\n', "")
            head = head.replace('<meta name="description"', '<meta name="robots" content="noindex">\n<meta name="description"', 1)
        else:
            pages.append((url, fname))
        foot = FOOT.format(year=YEAR, email=EMAIL)
        html = head + typography(body) + typography(foot)
        changed[fname] = not (SITE / fname).exists() or (SITE / fname).read_text(encoding="utf-8") != html
        (SITE / fname).write_text(html, encoding="utf-8")
        print("wrote", fname)

    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{last_changed(f, changed[f])}</lastmod></url>\n" for u, f in pages)
        + "</urlset>\n", encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8")
    print("wrote sitemap.xml, robots.txt")


if __name__ == "__main__":
    build()
