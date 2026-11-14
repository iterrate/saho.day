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
EMAIL = "hello@saho.day"

NAV = [
    ("./", "Home"),
    ("how-it-works.html", "How it works"),
    ("institutions.html", "For institutions"),
    ("about.html", "About"),
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
  <svg viewBox="0 0 440 356" role="img" aria-label="Four linked places: a village library, a college, a hospital and someone's own Saho. A learner at the library has a dotted link to a circle at the college.">
    <path class="ln sky" pathLength="100" style="--len:100;--d:.1s" d="M188 44H252"/>
    <path class="ln leaf" pathLength="100" style="--len:100;--d:.5s" d="M345 104V262"/>
    <path class="ln earth" pathLength="100" style="--len:100;--d:.9s" d="M252 308H188"/>
    <path class="ln plain" pathLength="100" style="--len:100;--d:1.3s" d="M95 262V104"/>
    <rect class="place sky" x="10" y="20" width="170" height="76" rx="10"/>
    <text class="lbl" x="26" y="50">Village library</text>
    <rect class="place leaf" x="260" y="20" width="170" height="76" rx="10"/>
    <text class="lbl" x="276" y="50">College</text>
    <rect class="place earth" x="260" y="270" width="170" height="76" rx="10"/>
    <text class="lbl" x="276" y="300">Hospital</text>
    <rect class="place plain" x="10" y="270" width="170" height="76" rx="10"/>
    <text class="lbl" x="26" y="300">Your own Saho</text>
    <text class="sub" x="26" y="324">run by one person</text>
    <g class="step s2">
      <path class="dots" d="M176 76H274"/>
      <circle class="ring" cx="286" cy="76" r="9"/>
    </g>
    <circle class="me step s1" cx="160" cy="76" r="9"/>
  </svg>
  <figcaption>Each institution runs its own Saho, and they are all linked. Here, a learner whose home is the village library has joined a circle at the college.</figcaption>
</figure>
"""

FIG_CENTRE = """
<figure class="fig centre">
  <svg viewBox="0 0 520 430" role="img" aria-label="A learner in the centre, with a solid line to their home place, a village library, and a dotted line to a circle at a college. Other places sit around them in a linked ring.">
    <path class="ln plain faint" d="M260 80L440 190L390 370L130 370L80 190Z"/>
    <path class="ln" style="stroke:var(--ink)" d="M260 216V100"/>
    <path class="dots" d="M285 232L420 197"/>
    <circle class="spot sky" cx="260" cy="80" r="17"/><text class="lbl" x="260" y="46" text-anchor="middle">Village library</text>
    <circle class="spot leaf" cx="440" cy="190" r="17"/><text class="lbl" x="452" y="150" text-anchor="middle">College</text>
    <circle class="spot earth" cx="390" cy="370" r="17"/><text class="lbl" x="390" y="414" text-anchor="middle">Hospital</text>
    <circle class="spot plain" cx="130" cy="370" r="17"/><text class="lbl" x="130" y="414" text-anchor="middle">Your own Saho</text>
    <circle class="spot sky" cx="80" cy="190" r="17"/><text class="lbl" x="66" y="124" text-anchor="middle">Panchayat</text><text class="lbl" x="66" y="150" text-anchor="middle">libraries</text>
    <circle class="me" cx="260" cy="240" r="22"/>
    <text class="lbl" x="260" y="298" text-anchor="middle">A learner</text>
    <text class="sub" x="260" y="322" text-anchor="middle">and their record</text>
    <text class="sub" x="272" y="165">home</text>
    <text class="sub" x="330" y="256">a circle</text>
  </svg>
  <figcaption>The learner is at the centre, not a platform. The solid line goes to their home place. The dotted line goes to a circle they joined somewhere else.</figcaption>
</figure>
"""

FIG_CONTRAST = """
<figure class="fig">
  <ul class="panels two">
    <li>
      <h3>The usual way</h3>
      <svg viewBox="0 0 400 300" role="img" aria-label="Many learners all connected to one app in the middle.">
        <g class="dots">
          <path d="M140 125L60 60"/><path d="M140 150L35 150"/><path d="M140 175L60 240"/>
          <path d="M260 125L340 60"/><path d="M260 150L365 150"/><path d="M260 175L340 240"/>
          <path d="M200 115V40"/><path d="M200 185V260"/>
        </g>
        <rect class="place plain" x="140" y="115" width="120" height="70" rx="10"/>
        <text class="lbl" x="200" y="157" text-anchor="middle">One app</text>
        <g class="me"><circle cx="60" cy="60" r="8"/><circle cx="35" cy="150" r="8"/><circle cx="60" cy="240" r="8"/><circle cx="340" cy="60" r="8"/><circle cx="365" cy="150" r="8"/><circle cx="340" cy="240" r="8"/><circle cx="200" cy="40" r="8"/><circle cx="200" cy="260" r="8"/></g>
      </svg>
      <p>Everyone's learning sits with one company.</p>
    </li>
    <li>
      <h3>Saho</h3>
      <svg viewBox="0 0 400 300" role="img" aria-label="Four places, a library, a college, a hospital and someone's own Saho, linked to each other, each with its own learners.">
        <path class="ln plain faint" d="M100 85L300 70M100 85L130 225M300 70L320 215M130 225L320 215"/>
        <circle class="spot sky" cx="100" cy="85" r="20"/><text class="sub" x="100" y="45" text-anchor="middle">Library</text>
        <circle class="spot leaf" cx="300" cy="70" r="20"/><text class="sub" x="300" y="30" text-anchor="middle">College</text>
        <circle class="spot earth" cx="320" cy="215" r="20"/><text class="sub" x="320" y="268" text-anchor="middle">Hospital</text>
        <circle class="spot plain" cx="130" cy="225" r="20"/><text class="sub" x="130" y="278" text-anchor="middle">Your own</text>
        <g class="me"><circle cx="60" cy="110" r="7"/><circle cx="55" cy="70" r="7"/><circle cx="340" cy="55" r="7"/><circle cx="335" cy="100" r="7"/><circle cx="360" cy="195" r="7"/><circle cx="95" cy="245" r="7"/></g>
      </svg>
      <p>Each place is run locally, and they are all linked.</p>
    </li>
  </ul>
</figure>
"""

FIG_STORY = """
<figure class="fig">
  <ol class="panels">
    <li>
      <h3>1 · Join</h3>
      <svg viewBox="0 0 260 190" role="img" aria-label="A learner inside a village library.">
        <rect class="place sky" x="20" y="30" width="220" height="130" rx="10"/>
        <text class="lbl" x="40" y="68">Village library</text>
        <circle class="me" cx="60" cy="120" r="11"/>
      </svg>
      <p>A learner joins at their village library. Their account and record live there.</p>
    </li>
    <li>
      <h3>2 · Learn with others</h3>
      <svg viewBox="0 0 260 190" role="img" aria-label="The learner stays in the library, with a dotted line to a circle at a college.">
        <path class="ln plain" d="M117 70H143"/>
        <rect class="place sky" x="10" y="30" width="105" height="130" rx="10"/>
        <text class="lbl" x="24" y="66">Library</text>
        <rect class="place leaf" x="145" y="30" width="105" height="130" rx="10"/>
        <text class="lbl" x="159" y="66">College</text>
        <path class="dots" d="M52 132C80 182 180 182 205 132"/>
        <circle class="me" cx="40" cy="120" r="11"/>
        <circle class="spot leaf" cx="205" cy="118" r="9" style="stroke-width:3"/>
      </svg>
      <p>They join a circle at a college nearby. Their home doesn't change.</p>
    </li>
    <li>
      <h3>3 · Move, if they want</h3>
      <svg viewBox="0 0 260 190" role="img" aria-label="The learner has moved into the college, with an arrow from the library.">
        <rect class="place sky" x="10" y="30" width="105" height="130" rx="10"/>
        <text class="lbl" x="24" y="66">Library</text>
        <rect class="place leaf" x="145" y="30" width="105" height="130" rx="10"/>
        <text class="lbl" x="159" y="66">College</text>
        <path class="ln plain" d="M60 120H170"/>
        <path class="ln plain" d="M170 120L160 110"/>
        <circle class="me" cx="190" cy="120" r="11"/>
      </svg>
      <p>If they move their home, their record goes with them.</p>
    </li>
  </ol>
</figure>
"""

# ---------------------------------------------------------------- Home
PAGES["index.html"] = ("Saho · Learn on your own terms, together",
"Saho is an open, federated learning platform in Malayalam and English. Any institution can run its own Saho, and learners keep what they learn.",
f"""
<div class="wrap">
  <div class="home-top">
    <div>
      <h1><span class="hero-ml" lang="ml">ഒരുമിച്ച് പഠിക്കാം</span>Learn on your own terms, <em>together</em>.</h1>
      <p class="lede">Saho is a guide and a gathering place for people learning on their own, at any stage of life. It helps you work out what to learn next, and finds you people to learn it with, in Malayalam, English or a mix of both.</p>
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
        <p>Small groups of learners who meet where they are, online or in person. Helpers from the community explain, review and encourage.</p>
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
    <p class="big"><em>For finding your own direction.</em></p>
    <p>Think of a recent graduate doing part-time work, unsure of what comes next. Saho is for exploring your world, your skills and what's possible, at your own pace.</p>
    <p><a href="how-it-works.html">See how it works</a></p>
  </div>
</div>

""")

# ---------------------------------------------------------------- How it works
PAGES["how-it-works.html"] = ("How Saho works",
"How Saho works: a guide, circles and a record you own, across places run by different institutions and linked to each other.",
f"""
<div class="wrap narrow">
  <section class="page-top">
    <span class="mark"></span>
    <h1>How Saho works</h1>
    <p class="lede">Saho gives you three things: a guide to help you plan, a circle of people to learn with, and a record of what you've learned that stays yours. Many institutions run Saho, and their places are linked.</p>
  </section>

  <ol class="steps">
    <li><h2>Talk to the guide</h2><p>The guide is an AI assistant. Tell it what you do, what you enjoy and what you're unsure about. You can read and correct its notes on you.</p></li>
    <li><h2>Get a plan</h2><p>Small steps for this month: something to watch, read or try, and a time to look back on how it went.</p></li>
    <li><h2>Learn with a circle</h2><p>Meet learners at your library or college, or online with people anywhere. Helpers explain and encourage, so the teaching comes from people.</p></li>
    <li><h2>Take it with you</h2><p>Your record belongs to you. Move it to another place, or download it, whenever you choose.</p></li>
  </ol>

  <section>
    <span class="mark sky"></span>
    <h2>Places, not a platform</h2>
    <p>Saho isn't one website. Any institution ({INSTITUTIONS}) can run its own Saho, which we call a <em>place</em>. Places are linked to each other, so a learner at one place can learn with people at another.</p>
    {FIG_CONTRAST.strip()}
    <p>One Saho can serve every library in a panchayat. A single person can also run their own, and join an institution later, or leave it.</p>
  </section>

  <section>
    <span class="mark"></span>
    <h2>One home, many circles</h2>
    <p>Every learner has one home place. Your account, your record and your conversations with the guide are kept there.</p>
    {FIG_CENTRE.strip()}
    <p>You can join circles at other places without leaving home. Each place sees only what you allow, and you can take that back at any time. Other places can't see your conversations with the guide.</p>
  </section>

  <section>
    <span class="mark earth"></span>
    <h2>Moving your home</h2>
    <p>Your home can change. If you start studying at a college, or move to another town, you can move your home place too, and your record goes with you.</p>
    {FIG_STORY.strip()}
    <p>You can also download your record as a file whenever you want.</p>
  </section>
</div>

<div class="wrap">
  <section>
    <span class="mark sky"></span>
    <h2>Three commitments</h2>
    <div class="grid">
      <div class="tile leaf"><h3>Malayalam first</h3><p>Malayalam comes first, including the everyday mix of Malayalam and English. English is something Saho helps with, not a gate to get in. Other languages spoken in Keralam will follow soon.</p></div>
      <div class="tile earth"><h3>AI you can choose</h3><p>The guide runs on AI language models. Each place chooses which one, and can run its own on its own hardware. Nobody has to depend on one company, including us.</p></div>
      <div class="tile sky"><h3>Open source</h3><p>Saho will be released as open-source software, so that anyone can inspect it, run it and improve it.</p></div>
    </div>
  </section>
</div>

<div class="wrap narrow">
  <section>
    <span class="mark"></span>
    <h2>Where it stands</h2>
    <p>Saho is in development, and the first test version is under way. A small pilot with libraries comes next.</p>
    <div class="btns">
      <a class="btn primary" href="institutions.html">Run Saho at your institution</a>
      <a class="btn" href="contact.html">Get in touch</a>
    </div>
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
      <div class="tile leaf"><h2>Colleges</h2><p>Students and alumni keep learning beyond the syllabus. Your college decides how learning works at its place.</p></div>
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
"Write to the people building Saho. Includes our privacy note: no cookies, no analytics.",
f"""
<div class="wrap narrow">
  <section class="page-top">
    <span class="mark sky"></span>
    <h1>Get in touch</h1>
    <p class="lede">Want to try Saho when it's ready, run it at your institution, or help build it? We'd like to hear from you.</p>
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
    <p>This site sets no cookies and uses no analytics or trackers. It is hosted on GitHub Pages, and GitHub logs visitors' IP addresses for security (see <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub's privacy statement</a>). Email to {EMAIL} is forwarded by Cloudflare to our inbox at Zoho Mail.</p>
    <p>If you write to us, we use your email address and what you tell us only to reply. We don't share it with anyone, and we delete it when you ask.</p>
  </section>
</div>
""")

# ---------------------------------------------------------------- About
PAGES["about.html"] = ("About Saho",
"Why Saho is being built, who builds it, and where its name comes from.",
f"""
<div class="wrap narrow">
  <section class="page-top">
    <span class="mark"></span>
    <h1>About Saho</h1>
    <p class="lede">Saho is a learning platform for Keralam, run by the institutions that use it. It is in development now, and will be released as open-source software.</p>
  </section>

  <section>
    <span class="mark sky"></span>
    <h2>Why we're building it</h2>
    <p>Keralam aims to be a knowledge society. AI is changing what knowledge work looks like, and we want people here to learn how to use these tools in their work and lives on their own terms, without handing that over to a few distant platforms.</p>
  </section>

  <section>
    <span class="mark"></span>
    <h2>Who builds it</h2>
    <p>Saho is built by <a href="https://iterrate.in">Iterrate (OPC) Private Limited</a>, founded by Sangeeth. It is a one-person company for now. You can read more about Sangeeth at <a href="https://sangeethvarma.com">sangeethvarma.com</a>.</p>
    <p>If you'd like to help build Saho, <a href="contact.html">write to us</a>.</p>
  </section>

  <section>
    <span class="mark earth"></span>
    <h2>The name</h2>
    <p><em>Saho</em> is a call to work together, named for Sahodaran Ayyappan and his ideals of fraternity and equality. <em>saho.day</em> reads as <em>sahoday</em>: rising together.</p>
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
