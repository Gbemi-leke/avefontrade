/* ============================================================
   IZZYMALL.NG — js/main.js
   ============================================================ */

/* ===== MOBILE DRAWER ===== */
(function() {
  const overlay  = document.getElementById('mobOverlay');
  const drawer   = document.getElementById('mobDrawer');
  const closeBtn = document.getElementById('mobClose');
  const ham      = document.getElementById('hamburger');
  const bnavMenu = document.getElementById('bnavMenu');

  function openDrawer()  { drawer?.classList.add('active'); overlay?.classList.add('active'); document.body.style.overflow = 'hidden'; }
  function closeDrawer() { drawer?.classList.remove('active'); overlay?.classList.remove('active'); document.body.style.overflow = ''; }

  ham?.addEventListener('click', openDrawer);
  bnavMenu?.addEventListener('click', openDrawer);
  closeBtn?.addEventListener('click', closeDrawer);
  overlay?.addEventListener('click', closeDrawer);
})();

/* ===== STICKY HEADER ===== */
(function() {
  const header = document.getElementById('siteHeader');
  if (!header) return;
  window.addEventListener('scroll', () => {
    header.style.boxShadow = window.scrollY > 10
      ? '0 2px 16px rgba(0,0,0,0.10)'
      : '';
  }, { passive: true });
})();

/* ===== HERO SLIDER ===== */
(function() {
  const track   = document.getElementById('heroSlides');
  const dotsWrap = document.getElementById('sliderDots');
  const prevBtn = document.getElementById('sliderPrev');
  const nextBtn = document.getElementById('sliderNext');
  if (!track) return;

  const slides = track.querySelectorAll('.hero-slide');
  let current  = 0;
  let timer;

  const dots = [];
  slides.forEach((_, i) => {
    const d = document.createElement('button');
    d.className = 'slider-dot' + (i === 0 ? ' active' : '');
    d.setAttribute('aria-label', 'Slide ' + (i + 1));
    d.addEventListener('click', () => go(i));
    dotsWrap?.appendChild(d);
    dots.push(d);
  });

  function go(n) {
    current = (n + slides.length) % slides.length;
    track.style.transform = `translateX(-${current * 100}%)`;
    dots.forEach((d, i) => d.classList.toggle('active', i === current));
    resetTimer();
  }

  function resetTimer() {
    clearInterval(timer);
    timer = setInterval(() => go(current + 1), 5000);
  }

  prevBtn?.addEventListener('click', () => go(current - 1));
  nextBtn?.addEventListener('click', () => go(current + 1));
  resetTimer();
})();

/* ===== COUNTDOWN TIMER ===== */
(function() {
  const hEl = document.getElementById('cdH');
  const mEl = document.getElementById('cdM');
  const sEl = document.getElementById('cdS');
  if (!hEl) return;

  let total = 9 * 3600 + 47 * 60 + 33;

  setInterval(() => {
    total = total > 0 ? total - 1 : 86399;
    hEl.textContent = String(Math.floor(total / 3600)).padStart(2, '0');
    mEl.textContent = String(Math.floor((total % 3600) / 60)).padStart(2, '0');
    sEl.textContent = String(total % 60).padStart(2, '0');
  }, 1000);
})();

/* ===== COUNTER ANIMATION (stats) ===== */
(function() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  const obs = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const el     = en.target;
      const target = parseInt(el.dataset.count, 10);
      const suffix = el.dataset.suffix || '';
      let current  = 0;
      const inc    = Math.ceil(target / 60);
      const t = setInterval(() => {
        current = Math.min(current + inc, target);
        el.textContent = (current >= 1000 ? (current / 1000).toFixed(current >= 10000 ? 0 : 1) + 'K' : current) + suffix;
        if (current >= target) clearInterval(t);
      }, 28);
      obs.unobserve(el);
    });
  }, { threshold: 0.3 });

  counters.forEach(c => obs.observe(c));
})();

/* ===== CART ===== */
const Cart = {
  get() { try { return JSON.parse(localStorage.getItem('izzy_cart') || '[]'); } catch { return []; } },
  save(c) { try { localStorage.setItem('izzy_cart', JSON.stringify(c)); } catch {} },
  total() { return this.get().reduce((s, i) => s + i.qty, 0); },
  add(id, name, price) {
    const c = this.get();
    const ex = c.find(i => i.id === id);
    ex ? ex.qty++ : c.push({ id, name, price, qty: 1 });
    this.save(c);
    this.updateBadges();
    showToast('Added to cart — ' + name);
  },
  updateBadges() {
    const n = this.total();
    document.querySelectorAll('.cart-badge').forEach(b => {
      b.textContent = n || 0;
      b.style.display = n > 0 ? '' : 'none';
    });
  }
};

Cart.updateBadges();

/* ===== ADD TO CART HANDLERS ===== */
document.addEventListener('click', e => {
  const btn = e.target.closest('[data-add-cart]');
  if (!btn) return;
  e.preventDefault();
  Cart.add(
    btn.dataset.addCart,
    btn.dataset.name || 'Product',
    parseFloat(btn.dataset.price) || 0
  );
});

/* ===== WISHLIST ===== */
document.addEventListener('click', e => {
  const btn = e.target.closest('.product-wishlist');
  if (!btn) return;
  e.preventDefault();
  const active = btn.classList.toggle('active');
  btn.textContent = active ? '❤️' : '🤍';
  showToast(active ? 'Added to wishlist' : 'Removed from wishlist');
});

/* ===== TOAST ===== */
function showToast(msg, type = 'default') {
  let wrap = document.querySelector('.toast-wrap');
  if (!wrap) { wrap = document.createElement('div'); wrap.className = 'toast-wrap'; document.body.appendChild(wrap); }
  const t = document.createElement('div');
  t.className = 'toast' + (type === 'success' ? ' success' : '');
  t.innerHTML = `<span>${type === 'success' ? '✓' : '🛒'}</span> ${msg}`;
  wrap.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(30px)'; t.style.transition = 'all 0.3s'; setTimeout(() => t.remove(), 320); }, 3000);
}

/* ===== NAV DROPDOWN (click toggle) ===== */
(function() {
  const allBtn  = document.getElementById('navAllBtn');
  const allDrop = document.getElementById('navAllDrop');
  const wrap    = document.getElementById('navCatWrap');
  if (!allBtn || !allDrop) return;

  allBtn.addEventListener('click', e => { e.preventDefault(); allDrop.style.display = allDrop.style.display === 'block' ? 'none' : 'block'; });
  document.addEventListener('click', e => { if (wrap && !wrap.contains(e.target)) allDrop.style.display = 'none'; });
})();

/* ===== SEARCH redirect ===== */
document.getElementById('searchSubmit')?.addEventListener('click', () => {
  const q = document.querySelector('.search-input')?.value;
  if (q && q.trim()) window.location.href = 'product-listing.html';
});
