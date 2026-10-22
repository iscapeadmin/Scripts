// iScape landing page: reveals, the cyclone-season check, and the map at three distances.

// Stagger the hero's parts and each section's parts.
document.querySelectorAll('.nav > *, .hero-title, .hero-support span').forEach((el, i) => el.style.setProperty('--i', i));
document.querySelectorAll('.intro .thumb').forEach((el, i) => el.style.setProperty('--d', i + 1));
document.querySelectorAll('.check-form, .faq-list, .about-text').forEach((el) => el.style.setProperty('--d', 1));

// The hero drawing opens on load: a fully clipped element never reports as intersecting.
requestAnimationFrame(() => requestAnimationFrame(() => document.querySelector('.hero-art')?.classList.add('is-in')));

// Fit the footer name to the content width, margin to margin.
(() => {
  const name = document.querySelector('.footer-name');
  if (!name) return;
  const fit = () => {
    name.style.fontSize = '100px';
    const pad = parseFloat(getComputedStyle(name).paddingLeft);
    const box = name.parentElement.clientWidth - 2 * pad;
    name.style.fontSize = `${(100 * box) / (name.getBoundingClientRect().width - pad) * 0.99}px`;
  };
  fit();
  document.fonts?.ready.then(fit);
  addEventListener('resize', fit);
})();

// Reveal once on entering the viewport; never leaves anything hidden.
(() => {
  const targets = document.querySelectorAll('[data-reveal]:not(.hero-art), .intro');
  if (!('IntersectionObserver' in window)) { targets.forEach((el) => el.classList.add('is-in')); return; }
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });
  targets.forEach((el) => io.observe(el));
  addEventListener('load', () => setTimeout(() => {
    targets.forEach((el) => { const r = el.getBoundingClientRect(); if (r.top < innerHeight && r.bottom > 0) el.classList.add('is-in'); });
  }, 2500));
})();

// Countdown to the cyclone season (1 November to 30 April), on Mackay's clock.
(() => {
  const out = document.getElementById('countdown');
  if (!out) return;
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-AU', { timeZone: 'Australia/Brisbane', year: 'numeric', month: 'numeric', day: 'numeric' })
    .formatToParts(new Date()).filter((p) => p.type !== 'literal').map((p) => [p.type, Number(p.value)]));
  const today = Date.UTC(parts.year, parts.month - 1, parts.day);
  const day = 86400000;
  const inSeason = parts.month >= 11 || parts.month <= 4;
  if (inSeason) {
    const startYear = parts.month >= 11 ? parts.year : parts.year - 1;
    const start = Date.UTC(startYear, 10, 1);
    const end = Date.UTC(startYear + 1, 3, 30);
    const n = Math.round((today - start) / day) + 1;
    const total = Math.round((end - start) / day) + 1;
    out.textContent = `Cyclone season: day ${n} of ${total}.`;
  } else {
    const n = Math.round((Date.UTC(parts.year, 10, 1) - today) / day);
    out.textContent = n === 1 ? 'Cyclone season starts tomorrow.' : `${n} days until cyclone season.`;
  }
})();

// The check: count the answers, say where the office stands, and carry the answers into the email.
(() => {
  const form = document.getElementById('check-form');
  const verdict = document.getElementById('verdict');
  const send = document.getElementById('check-send');
  if (!form || !verdict || !send) return;
  const questions = [...form.querySelectorAll('.q')].map((q) => ({ name: q.querySelector('input').name, text: q.querySelector('.q-text').textContent }));
  const update = () => {
    const answers = questions.map((q) => ({ ...q, value: form.elements[q.name].value }));
    const answered = answers.filter((a) => a.value);
    const yes = answered.filter((a) => a.value === 'yes').length;
    const gaps = answered.length - yes;
    if (answered.length < questions.length) {
      verdict.textContent = `${answered.length} of 5 answered${answered.length ? `, ${yes} ready` : ''}.`;
    } else if (gaps === 0) {
      verdict.textContent = "Ready. We'd still test the restore.";
    } else if (gaps <= 2) {
      verdict.textContent = `Close: ${gaps} ${gaps === 1 ? 'thing' : 'things'} to fix before the first watch.`;
    } else {
      verdict.textContent = "Not yet. Let's fix it before November.";
    }
    const body = ['Our answers to the cyclone season check:', '', ...answers.map((a) => `${a.text} ${a.value ? a.value.toUpperCase() : '(not answered)'}`), '', 'Business name:', 'Best number to call:'].join('\n');
    send.href = `mailto:hello@iscape.com.au?subject=${encodeURIComponent('Cyclone season review')}&body=${encodeURIComponent(body)}`;
  };
  form.addEventListener('change', update);
  form.addEventListener('submit', (e) => { e.preventDefault(); location.href = send.href; });
})();

// The map at three distances: switch stage as each marker passes the middle of the screen.
(() => {
  const reach = document.querySelector('.reach');
  if (!reach) return;
  reach.dataset.at = '1';
  if (!('IntersectionObserver' in window)) { reach.dataset.at = '3'; return; }
  const marks = [...reach.querySelectorAll('.reach-mark')];
  const io = new IntersectionObserver(() => {
    let at = 1;
    for (const m of marks) if (m.getBoundingClientRect().top < innerHeight * 0.5) at = Number(m.dataset.stage);
    reach.dataset.at = String(at);
  }, { rootMargin: '0px 0px -50% 0px', threshold: 0 });
  marks.forEach((m) => io.observe(m));
})();
