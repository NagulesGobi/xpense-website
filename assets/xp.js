/* Xpense site behaviour: the glass dock, the theme switch, the tally-up motion and the working
   app demos. The kit's system.js, motion.js and layout.js run everything else. */
(function () {
  'use strict';
  // The one place for the App Store link. Replace it with the real link when Apple gives it
  // (apps.apple.com/...); every [data-appstore] link on every page uses it.
  var APP_STORE_URL = 'https://apps.apple.com/app/id6829723496';
  var d = document, root = d.documentElement;
  var RM = matchMedia('(prefers-reduced-motion: reduce)');
  var clamp = function (v) { return Math.max(0, Math.min(1, v)); };
  if (APP_STORE_URL) d.querySelectorAll('a[data-appstore]').forEach(function (a) { a.href = APP_STORE_URL; a.target = '_blank'; a.rel = 'noopener'; });

  // theme: the new look grows out of the button
  function dark() { var t = root.getAttribute('data-theme'); return t ? t === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; }
  d.querySelectorAll('.theme-btn').forEach(function (b) {
    b.addEventListener('click', function () {
      var next = dark() ? 'light' : 'dark';
      var apply = function () { root.setAttribute('data-theme', next); try { localStorage.setItem('xp-theme', next); } catch (e) {} };
      if (!d.startViewTransition || RM.matches) return apply();
      var r = b.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
      var end = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
      d.startViewTransition(apply).ready.then(function () {
        root.animate({ clipPath: ['circle(0px at ' + x + 'px ' + y + 'px)', 'circle(' + end + 'px at ' + x + 'px ' + y + 'px)'] },
          { duration: 750, easing: 'cubic-bezier(.76,0,.24,1)', pseudoElement: '::view-transition-new(root)' });
      }).catch(function () {});
    });
  });

  // the dock: a glass pill that tucks into the Xpense mark when you scroll down
  var dock = d.querySelector('.dock'), links = d.getElementById('dock-links'), menu = d.querySelector('.dock__menu');
  if (menu && links) {
    menu.addEventListener('click', function () { var o = links.classList.toggle('open'); menu.setAttribute('aria-expanded', String(o)); });
    links.addEventListener('click', function (e) { if (e.target.closest('a')) { links.classList.remove('open'); menu.setAttribute('aria-expanded', 'false'); } });
  }
  if (dock) (function () {
    var bar = dock.querySelector('.dock__bar');
    var dot = d.createElement('button');
    dot.className = 'dock-dot'; dot.type = 'button'; dot.tabIndex = -1; dot.setAttribute('aria-label', 'Open the menu'); dot.setAttribute('aria-expanded', 'false');
    dot.innerHTML = '<img src="' + (dock.getAttribute('data-root') || '') + 'img/xpense-icon-512.png" alt="">';
    bar.appendChild(dot);
    function measure() { if (dock.classList.contains('collapsed')) return; var pad = parseFloat(getComputedStyle(dock).paddingLeft) || 0; bar.style.setProperty('--pw', Math.min(1180, dock.clientWidth - pad * 2) + 'px'); dock.classList.add('ready'); }
    function set(c) {
      if (c === dock.classList.contains('collapsed')) return;
      dock.classList.toggle('collapsed', c); dot.setAttribute('aria-expanded', String(!c)); dot.tabIndex = c ? 0 : -1;
      [].forEach.call(bar.children, function (k) { if (k !== dot) { if (c) k.setAttribute('inert', ''); else k.removeAttribute('inert'); } });
    }
    var lastY = scrollY, hold = 0, tick = false;
    addEventListener('scroll', function () {
      if (tick) return; tick = true;
      requestAnimationFrame(function () {
        tick = false; var y = scrollY, dy = y - lastY, open = links && links.classList.contains('open');
        if (y < 70) set(false); else if (dy > 6 && y > 180 && !open && Date.now() > hold) set(true); else if (dy < -6) set(false);
        if (Math.abs(dy) > 6) lastY = y;
      });
    }, { passive: true });
    dot.addEventListener('click', function () { hold = Date.now() + 2500; lastY = scrollY; set(false); });
    dock.addEventListener('focusin', function () { set(false); });
    measure(); addEventListener('resize', measure); if (d.fonts) d.fonts.ready.then(measure);
  })();

  var money = function (p) { return '£' + (p / 100).toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };

  // working demo 1: the Overview. A Quick Add tile logs that category's usual amount.
  d.querySelectorAll('[data-overview]').forEach(function (ph) {
    var spent = 124860, budget = 160000;
    var total = ph.querySelector('[data-total]'), left = ph.querySelector('[data-left]'), bar = ph.querySelector('[data-bar]'),
        used = ph.querySelector('[data-used]'), recent = ph.querySelector('[data-recent]'), toast = ph.querySelector('[data-toast]'), t;
    function draw() {
      total.textContent = money(spent);
      var l = budget - spent;
      left.textContent = l >= 0 ? money(l) + ' left of ' + money(budget).replace('.00', '') + ' budget' : money(-l) + ' over your budget';
      var pct = Math.round(spent / budget * 100); bar.style.setProperty('--w', Math.min(100, pct) + '%'); used.textContent = pct + '% used';
    }
    ph.querySelectorAll('.xp-tile').forEach(function (tile) {
      tile.addEventListener('click', function () {
        var p = Math.round(parseFloat(tile.getAttribute('data-amt')) * 100), name = tile.getAttribute('data-cat');
        spent += p; draw();
        var li = d.createElement('li'); li.className = 'new';
        li.innerHTML = '<i style="--c:' + tile.style.getPropertyValue('--c') + '"></i><span><b>' + name + '</b><small>' + name + ' · Just now</small></span><em>' + money(p) + '</em>';
        recent.insertBefore(li, recent.firstChild); while (recent.children.length > 3) recent.removeChild(recent.lastChild);
        toast.textContent = money(p) + ' logged to ' + name + '.'; toast.classList.add('on');
        clearTimeout(t); t = setTimeout(function () { toast.classList.remove('on'); }, 1800);
      });
    });
    draw();
  });

  // working demo 2: New expense. Pick a category, key in an amount, save.
  d.querySelectorAll('[data-keypad]').forEach(function (ph) {
    var q = function (s) { return ph.querySelector(s); };
    var amt = q('.kp-amt'), save = q('.kp-save'), chips = [].slice.call(ph.querySelectorAll('.kp-chip')), pence = 0, cat = '';
    function refresh() { amt.textContent = money(pence); save.disabled = !(pence > 0 && cat); }
    function press(k) { if (k === 'del') pence = Math.floor(pence / 10); else if (k === '00') pence = Math.min(pence * 100, 9999999); else pence = Math.min(pence * 10 + (+k), 9999999); refresh(); }
    ph.querySelectorAll('.kp-key').forEach(function (b) { b.addEventListener('click', function () { press(b.getAttribute('data-k')); }); });
    chips.forEach(function (c) { c.addEventListener('click', function () { cat = c.getAttribute('data-cat'); chips.forEach(function (x) { x.setAttribute('aria-pressed', String(x === c)); }); refresh(); }); });
    ph.addEventListener('keydown', function (e) { if (/^\d$/.test(e.key)) press(e.key); else if (e.key === 'Backspace') press('del'); });
    var LAST = 24000, SO_FAR = 15000;
    save.addEventListener('click', function () {
      var tot = SO_FAR + pence, diff = Math.abs(LAST - tot);
      q('.kp-form').hidden = true; var done = q('.kp-done'); done.hidden = false;
      q('.kp-log').textContent = money(pence) + ' logged to ' + cat + '.';
      q('.kp-msg').textContent = tot <= LAST ? 'Nice, ' + money(diff).replace('.00', '') + ' less than last month so far.' : money(diff).replace('.00', '') + ' more than last month so far.';
      var max = Math.max(LAST, tot), bl = q('.kp-bars .last b'), bt = q('.kp-bars .this b');
      bl.style.width = '0'; bt.style.width = '0';
      setTimeout(function () { bl.style.width = (LAST / max * 100) + '%'; bt.style.width = (tot / max * 100) + '%'; }, 30);
      q('.kp-again').focus({ preventScroll: true });
    });
    q('.kp-again').addEventListener('click', function () { pence = 0; cat = ''; chips.forEach(function (x) { x.setAttribute('aria-pressed', 'false'); }); refresh(); q('.kp-done').hidden = true; q('.kp-form').hidden = false; });
    refresh();
  });

  // Xpense motion: things tally up as they come into view (bars fill, the donut draws, money counts)
  var seen = function (el) {
    el.classList.add('in');
    if (el.hasAttribute('data-xp-track')) el.querySelectorAll('[data-xp-fill]').forEach(function (b) { b.classList.add('in'); });
    var c = el.getAttribute('data-xp-count');
    if (c && !RM.matches) { var to = +c, t0 = performance.now(); (function f(now) { var k = Math.min(1, (now - t0) / 1200), e = 1 - Math.pow(1 - k, 3); el.textContent = money(Math.round(to * e)); if (k < 1) requestAnimationFrame(f); })(t0); }
    if (el.hasAttribute('data-xp-type') && !RM.matches) {
      var full = el.textContent, i = 0; el.textContent = ''; el.classList.add('typing');
      (function step() { i += 3; el.textContent = full.slice(0, i); if (i < full.length) setTimeout(step, 22); else el.classList.remove('typing'); })();
    }
  };
  // a bar starts at zero width, so watch its track and fill every bar inside it
  d.querySelectorAll('[data-xp-fill]').forEach(function (b) { b.parentElement.setAttribute('data-xp-track', ''); });
  var targets = d.querySelectorAll('[data-xp-rise], [data-xp-track], .xp-donut, [data-xp-count], [data-xp-type]');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { seen(e.target); io.unobserve(e.target); } }); }, { threshold: .25 });
    targets.forEach(function (el) { io.observe(el); });
  } else targets.forEach(seen);

  // working demo 3: a shared group. Add a cost paid by you, split three ways, then settle up.
  d.querySelectorAll('[data-xp-group]').forEach(function (g) {
    var costs = g.querySelector('[data-costs]'), bal = g.querySelector('[data-bal]'), toast = g.querySelector('[data-gtoast]');
    var paid = 12000, settled = false;
    function draw() {
      var each = Math.round(paid / 3);
      bal.innerHTML = settled ? '<div><span>Everyone is square</span><b>£0.00</b></div>'
        : '<div><span>Sam owes you</span><b>' + money(each) + '</b></div><div><span>Alex owes you</span><b>' + money(each) + '</b></div>';
    }
    g.querySelectorAll('[data-add]').forEach(function (b) {
      b.addEventListener('click', function () {
        var p = b.getAttribute('data-add').split(','), amt = Math.round(+p[1] * 100);
        if (settled) { settled = false; paid = 0; }
        paid += amt;
        var li = d.createElement('li'); li.className = 'new';
        li.innerHTML = '<span><b>' + p[0] + '</b><small>Paid by you · split 3 ways</small></span><em>' + money(amt) + '</em>';
        costs.insertBefore(li, costs.firstChild); while (costs.children.length > 3) costs.removeChild(costs.lastChild);
        toast.textContent = p[0] + ' added. ' + money(Math.round(amt / 3)) + ' each.'; draw();
      });
    });
    g.querySelector('[data-settle]').addEventListener('click', function () { settled = true; draw(); toast.textContent = 'Settled up. Sam and Alex paid you back.'; });
    draw();
  });
})();
