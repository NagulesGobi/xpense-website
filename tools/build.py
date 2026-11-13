#!/usr/bin/env python3
"""Builds the Xpense site: every page shares one head, dock and footer.
Run from the repo root:  python3 tools/build.py
Edit tools/parts/*.html and the PAGES below, never the generated *.html at the root."""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = lambda n: (ROOT / 'tools/parts' / n).read_text()
APPLE = '<svg class="apple" viewBox="0 0 24 24" aria-hidden="true"><path d="M16.4 12.6c0-2.4 2-3.5 2-3.6-1.1-1.6-2.8-1.8-3.4-1.8-1.4-.1-2.8.9-3.5.9s-1.8-.9-3-.8c-1.5 0-3 .9-3.8 2.3-1.6 2.8-.4 7 1.2 9.3.8 1.1 1.7 2.4 2.9 2.3 1.2 0 1.6-.7 3-.7s1.8.7 3 .7c1.3 0 2.1-1.1 2.8-2.3.9-1.3 1.3-2.6 1.3-2.6s-2.5-1-2.5-3.7zM14.1 5.6c.6-.8 1.1-1.9 1-3-.9 0-2.1.6-2.7 1.4-.6.7-1.1 1.8-1 2.9 1 .1 2.1-.5 2.7-1.3z"/></svg>'
NAV = [('index.html', 'Overview'), ('features.html', 'Features'), ('shared.html', 'Shared groups'), ('your-data.html', 'Your data'), ('support.html', 'Support')]

def dock(cur):
    links = ''.join(f'<a href="{h}"{" aria-current=page" if h == cur else ""}>{t}</a>' for h, t in NAV)
    return f'''<header class="dock" data-root="">
  <div class="dock__bar">
    <a class="skip-link" href="#top">Skip to content</a>
    <a class="dock__home" href="https://dotxline.com/" aria-label="Back to dotXline"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg><span>dotXline</span></a>
    <a class="dock__logo" href="index.html"><img src="img/xpense-icon-512.png" alt="">Xpense</a>
    <nav class="dock__links" id="dock-links" aria-label="Main">{links}</nav>
    <button class="icon-btn theme-btn" type="button" aria-label="Switch light and dark"><svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/></svg><svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/></svg></button>
    <button class="icon-btn dock__menu" type="button" aria-expanded="false" aria-controls="dock-links" aria-label="Menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 8h16M4 16h16"/></svg></button>
    <a class="btn btn--primary" href="#get" data-appstore>{APPLE}<span class="lbl-long">Download&nbsp;</span>Xpense</a>
  </div>
</header>'''

def footer():
    f = P('close.html')
    f = f.replace('href="#top"', 'href="index.html"')
    f = re.sub(r'<div class="span-2 start-7 footer__col"><h3>Xpense</h3><ul>.*?</ul></div>',
               '<div class="span-2 start-7 footer__col"><h3>Xpense</h3><ul><li><a href="index.html">Overview</a></li><li><a href="features.html">Features</a></li><li><a href="shared.html">Shared groups</a></li><li><a href="your-data.html">Your data</a></li></ul></div>', f, flags=re.S)
    f = f.replace('<h3>dotXline</h3><ul>', '<h3>dotXline</h3><ul><li><a href="https://dotxline.com/">Back to dotXline</a></li>').replace('<li><a href="https://dotxline.com/">dotxline.com</a></li>', '')
    return f

def head(title, desc, path):
    h = P('head.html')
    h = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', h)
    for k in ('name="description"', 'property="og:description"'):
        h = re.sub(rf'<meta {k} content="[^"]*">', f'<meta {k} content="{desc}">', h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">', h)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://xpense.dotxline.com/{"" if path == "index.html" else path}">', h)
    return h

SCRIPTS = '''<script type="module" src="assets/system.js"></script>
<script type="module" src="assets/motion/motion.js"></script>
<script type="module" src="assets/layout/layout.js"></script>
<script src="assets/xp.js" defer></script>'''

def page_head(label, h1, lead, extra=''):
    extra = extra or '<div class="span-4 start-9 xp-head-mark" aria-hidden="true"><img src="img/xpense-mark.svg" alt="" width="260" height="260"></div>'
    return f'''  <section class="page-head" aria-labelledby="ph-h">
    <div class="wrap grid">
      <div class="span-7 stack-4" data-xp-rise>
        <p class="t-label">{label}</p>
        <h1 id="ph-h">{h1}</h1>
        <p class="t-lead measure">{lead}</p>
      </div>
      {extra}
    </div>
  </section>
'''

def write(path, title, desc, body):
    html = f'''{head(title, desc, path)}</head>
<body data-page="{path[:-5]}">
{dock(path)}
<main id="top">
{body}</main>
{footer()}
{SCRIPTS}
</body>
</html>
'''
    (ROOT / path).write_text(html)
    print('built', path)

# ---------- the pages ----------
TOUR = '''  <section class="section" id="tour" aria-labelledby="tour-h">
    <div class="wrap">
      <div class="section-head"><h2 id="tour-h">More of Xpense, page by page</h2><p class="t-lead measure">Budgets and charts, groups that settle up, and what happens to your data.</p></div>
      <div class="tour">
        <a class="tour__card" href="features.html" data-xp-rise>
          <div class="tour__ui" data-ui aria-hidden="true"><div class="budget-row"><div><span>Groceries</span><span>£210 of £300</span></div><i><b data-xp-fill style="--w:70%"></b></i></div><div class="budget-row"><div><span>Food</span><span>£96 of £120</span></div><i><b data-xp-fill style="--w:80%"></b></i></div><div class="budget-row over"><div><span>Fun</span><span>£64 of £60</span></div><i><b data-xp-fill style="--w:100%"></b></i></div></div>
          <h3>Features</h3><p>Budgets per category, History, Analyze, recurring bills and goals.</p><span class="tour__go" aria-hidden="true">→</span>
        </a>
        <a class="tour__card" href="shared.html" data-xp-rise>
          <div class="tour__ui" data-ui aria-hidden="true"><div class="who"><span>You paid</span><b>£120.00</b></div><div class="who"><span>Sam owes you</span><b>£40.00</b></div><div class="who"><span>Alex owes you</span><b>£40.00</b></div></div>
          <h3>Shared groups</h3><p>Flats and trips: who paid, who owes, and settle up in a tap.</p><span class="tour__go" aria-hidden="true">→</span>
        </a>
        <a class="tour__card" href="your-data.html" data-xp-rise>
          <div class="tour__ui tour__ui--csv" data-ui aria-hidden="true"><b>xpense-export.csv</b><span>date,category,amount</span><span>2026-10-30,Food,12.40</span><span>2026-10-30,Transport,8.20</span></div>
          <h3>Your data</h3><p>Receipts stay on your iPhone. Export to CSV, delete any time.</p><span class="tour__go" aria-hidden="true">→</span>
        </a>
      </div>
    </div>
  </section>
'''

DONUT = '<svg class="xp-donut" viewBox="0 0 42 42" aria-hidden="true">' + ''.join(
    f'<circle cx="21" cy="21" r="15.9" fill="none" stroke="{c}" stroke-width="7" pathLength="100" stroke-dasharray="{d} {100-d}" stroke-dashoffset="{-o}" data-xp-seg/>'
    for c, d, o in [('#22C55E', 37, 0), ('#F59E0B', 21, 38), ('#3B82F6', 15, 60), ('#EAB308', 13, 76), ('#EC4899', 9, 90)]) + '</svg>'

FEATURES_TOP = page_head('Features', 'Xpense features, from Quick Add to settle up',
    'Built natively for iPhone with the design of iOS 26. Works offline and syncs when you are back.') + f'''
  <section class="section" id="budgets" aria-labelledby="budgets-h">
    <div class="wrap grid">
      <div class="span-5 stack-4">
        <h2 id="budgets-h">Budgets for the month and each category</h2>
        <p class="t-lead measure">Set one budget for the month and one for each category. What is left stays in plain view, and a category that goes over says so.</p>
      </div>
      <div class="span-7 start-6 xp-panel" data-ui aria-label="Budgets: £1,248.60 spent of £1,600, with Groceries, Food and Fun" role="img">
        <small>Spent in October</small>
        <div class="big"><span data-xp-count="124860">£1,248.60</span></div>
        <span class="ok">£351.40 left of £1,600 budget</span>
        <div class="xp-meter"><b data-xp-fill style="--w:78%"></b></div>
        <div class="budget-list">
          <div class="budget-row"><div><span>Groceries</span><span>£210 of £300</span></div><i><b data-xp-fill style="--w:70%"></b></i></div>
          <div class="budget-row"><div><span>Food</span><span>£96 of £120</span></div><i><b data-xp-fill style="--w:80%"></b></i></div>
          <div class="budget-row"><div><span>Transport</span><span>£58 of £90</span></div><i><b data-xp-fill style="--w:64%"></b></i></div>
          <div class="budget-row over"><div><span>Fun</span><span>£64 of £60</span></div><i><b data-xp-fill style="--w:100%"></b></i></div>
        </div>
      </div>
    </div>
  </section>

  <section class="section ground-surface" id="analyze" aria-labelledby="analyze-h">
    <div class="wrap grid">
      <div class="span-5 stack-4">
        <h2 id="analyze-h">Analyze shows where the month went</h2>
        <p class="t-lead measure">Month totals, a category donut, bar charts and this month against last. Spend less than last month and Xpense says so. Spend more and it stays neutral.</p>
      </div>
      <div class="span-7 start-6 xp-analyze" data-ui role="img" aria-label="Analyze: a category donut and this month against last month">
        <div class="xp-panel">{DONUT}<ul class="xp-legend"><li><i style="--c:#22C55E"></i>Groceries</li><li><i style="--c:#F59E0B"></i>Food</li><li><i style="--c:#3B82F6"></i>Transport</li><li><i style="--c:#EAB308"></i>Bills</li><li><i style="--c:#EC4899"></i>Shopping</li></ul></div>
        <div class="xp-panel">
          <small>October against September</small>
          <div class="xp-vs"><span>September</span><i><b data-xp-fill style="--w:100%" class="last"></b></i><em>£1,260</em></div>
          <div class="xp-vs"><span>October</span><i><b data-xp-fill style="--w:99%"></b></i><em>£1,248</em></div>
          <p class="xp-nice">Nice, £12 less than September.</p>
        </div>
      </div>
    </div>
  </section>
'''

SHARED = page_head('Shared groups', 'Split costs with friends, then settle up',
    'Groups for flats and trips. Xpense tracks who paid and who owes, and settles up in a tap. A group is visible only to its members.') + '''
  <section class="section" id="group" aria-labelledby="group-h">
    <div class="wrap grid">
      <div class="span-5 stack-4">
        <h2 id="group-h">A trip, split three ways</h2>
        <p class="t-lead measure">Add a cost, choose who paid, and Xpense splits it between the group. Try it: the group on the right works.</p>
        <ul class="facts-list">
          <li><b>Who paid, who owes</b><span>Every member sees the same balances.</span></li>
          <li><b>Settle up in a tap</b><span>Mark a debt paid and the balances clear.</span></li>
          <li><b>Report anything wrong</b><span>Use the report option in the app, or email us with the group name. We review reports promptly.</span></li>
        </ul>
      </div>
      <div class="span-7 start-6 xp-group" data-ui data-xp-group role="group" aria-label="Working demo of a shared group">
        <div class="xp-panel">
          <div class="xp-group__top"><div><small>Shared group</small><b class="xp-group__name">Trip</b></div><span class="xp-group__members" aria-hidden="true"><i>Y</i><i>S</i><i>A</i></span></div>
          <ul class="xp-costs" data-costs><li><span><b>Train tickets</b><small>Paid by you</small></span><em>£120.00</em></li></ul>
          <div class="xp-bal" data-bal></div>
          <div class="xp-group__acts">
            <button type="button" class="xp-act" data-add="Dinner,60">Add dinner, £60</button>
            <button type="button" class="xp-act" data-add="Museum,36">Add museum, £36</button>
            <button type="button" class="xp-act xp-act--main" data-settle>Settle up</button>
          </div>
          <p class="xp-group__toast" data-gtoast role="status" aria-live="polite"></p>
        </div>
      </div>
    </div>
  </section>
'''

YOUR_DATA = P('privacy.html').replace('<h2 id="privacy-h">', '<h1 id="privacy-h">').replace('Your expenses stay with you</h2>', 'Your expenses stay with you</h1>').replace('class="section ground-surface" id="privacy"', 'class="section page-first" id="privacy"') + '''
  <section class="section ground-surface" id="export" aria-labelledby="export-h">
    <div class="wrap grid">
      <div class="span-5 stack-4">
        <h2 id="export-h">Export to CSV, delete any time</h2>
        <p class="t-lead measure">Settings, Export downloads your expenses as a CSV file. Settings, Account, Delete Account removes your account and your data from our servers.</p>
        <p><a class="link" href="privacy.html">Read the privacy policy</a></p>
      </div>
      <div class="span-7 start-6 xp-csv" data-ui role="img" aria-label="An exported CSV file of expenses">
        <div class="xp-panel"><b>xpense-export.csv</b><pre data-xp-type>date,category,note,amount
2026-10-30,Food,Lunch,12.40
2026-10-30,Transport,Train to work,8.20
2026-10-29,Groceries,Weekly shop,64.15
2026-10-28,Bills,Phone bill,71.00</pre></div>
      </div>
    </div>
  </section>
'''

FAQ_BLOCK = P('faq.html').replace('<h2 id="faq-h">Xpense details and questions</h2>', '<h2 id="faq-h">Xpense details and questions</h2>')
FAQ_BLOCK = re.sub(r'<img class="faq-icon"[^>]*>', '', FAQ_BLOCK)
CHIPS = '''  <section class="section ground-surface" id="at-a-glance" aria-labelledby="glance-h">
    <div class="wrap grid">
      <div class="span-5 stack-4">
        <h2 id="glance-h" data-xp-rise>Xpense at a glance</h2>
        <p class="t-lead measure" data-xp-rise>Native for iPhone, built with the design of iOS 26. Works offline and syncs when you are back.</p>
      </div>
      <div class="span-7 start-6 xp-stats">
        <div class="xp-panel" data-xp-rise><small>Spent in October</small><b>£1,248.60</b><span>£351.40 left of £1,600</span></div>
        <div class="xp-panel" data-xp-rise><small>This month against last</small><b>−£12</b><span>Nice, £12 less than September.</span></div>
        <div class="xp-panel" data-xp-rise><small>Quick Add tiles</small><b>8</b><span>Food, Transport, Fuel, Subs, Shopping, Groceries, Bills, Fun</span></div>
        <div class="xp-panel" data-xp-rise><small>Price</small><b>Free</b><span>On the App Store, in pounds</span></div>
      </div>
    </div>
  </section>
'''
SUPPORT = page_head('Support', 'Xpense support and questions',
    'We usually reply within 2 business days. Include your iPhone model, iOS version and what happened. Never send passwords.',
    '<div class="span-4 start-9 xp-panel xp-contact" data-xp-rise><small>Email us</small><a class="link" href="mailto:hello@dotxline.com?subject=Xpense%20support">hello@dotxline.com</a><p>dotXline LTD, Cardiff, United Kingdom</p></div>') + P('faq.html')

write('index.html', 'Xpense: an expense tracker for iPhone', 'Log an expense in one tap, keep each category on budget and split costs with friends. Free on the App Store, from dotXline.',
      P('hero.html') + '\n' + P('app.html') + '\n' + P('features.html') + '\n' + P('privacy.html') + '\n' + TOUR)
write('features.html', 'Features: Xpense', 'Quick Add, budgets per category, History, Analyze, recurring bills, savings goals, shared groups, widgets and Siri.',
      FEATURES_TOP + '\n' + P('features.html').replace('<h2 id="features-h">Everything Xpense does, on one iPhone</h2>', '<h2 id="features-h">Everything else Xpense does</h2>') + CHIPS + TOUR)
write('shared.html', 'Shared groups: Xpense', 'Split costs with friends in shared groups for flats and trips, then settle up in a tap.', SHARED + CHIPS + TOUR)
write('your-data.html', 'Your data: Xpense', 'Sign in with Apple or an email code. Receipts stay on your iPhone. Export to CSV and delete your account any time.', YOUR_DATA + FAQ_BLOCK + TOUR)
write('support.html', 'Support: Xpense', 'Help for Xpense: contact, account deletion, export, sync and shared groups.', SUPPORT)

# legal pages: the owner's own text from dotxline.com (privacy.html, terms.html)
SRC = pathlib.Path.home() / 'Apps/dotxline-website'
for name, title, desc in [('privacy', 'Privacy policy: Xpense', 'How Xpense handles your data: what it stores, who can see it, and how to delete it.'),
                          ('terms', 'Terms of use: Xpense', 'The terms for using Xpense and this website.')]:
    body = re.search(r'<main[^>]*>(.*?)</main>', (SRC / f'{name}.html').read_text(), re.S).group(1)
    body = re.sub(r'<p>FreshBit has its own[^\n]*?</p>', '', body).replace('href="xpense.html"', 'href="index.html"')
    write(f'{name}.html', title, desc, f'  <section class="doc-main"><div class="wrap"><article class="doc">{body.strip()}</article></div></section>\n')
