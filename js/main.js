(() => {
  "use strict";

  /* ---------------- Header solid-on-scroll ---------------- */
  const header = document.getElementById('siteHeader');
  const onScrollHeader = () => {
    if (!header) return;
    header.classList.toggle('solid', window.scrollY > 40);
  };
  document.addEventListener('scroll', onScrollHeader, { passive: true });
  onScrollHeader();

  /* ---------------- Mobile nav ---------------- */
  const navToggle = document.getElementById('navToggle');
  const mainNav = document.getElementById('mainNav');
  if (navToggle && mainNav) {
    navToggle.addEventListener('click', () => {
      const open = mainNav.classList.toggle('open');
      navToggle.classList.toggle('open', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
    mainNav.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        mainNav.classList.remove('open');
        navToggle.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  /* ---------------- Scroll reveal ---------------- */
  const revealTargets = document.querySelectorAll('[data-reveal], [data-reveal-group]');
  if ('IntersectionObserver' in window && revealTargets.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
    revealTargets.forEach(el => io.observe(el));
  } else {
    revealTargets.forEach(el => el.classList.add('in'));
  }

  /* ---------------- Exploding suit diagram (triggers once on view) ---------------- */
  const explodeStage = document.getElementById('explodeStage');
  if (explodeStage) {
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            explodeStage.classList.add('exploded');
            io.unobserve(entry.target);
          }
        });
      }, { threshold: 0.4 });
      io.observe(explodeStage);
    } else {
      explodeStage.classList.add('exploded');
    }
  }

  /* ---------------- Newsletter / waitlist forms ---------------- */
  document.querySelectorAll('.newsletter-form').forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (form.classList.contains('sent')) return;
      form.classList.add('sent');
    });
  });

  /* ---------------- Product quick-view stub ---------------- */
  document.querySelectorAll('.product-card__quick .btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
    });
  });

  /* ---------------- Style subcategory jump (e.g. Pawn styles) ---------------- */
  document.querySelectorAll('.style-select').forEach(sel => {
    sel.addEventListener('change', () => {
      const id = sel.value;
      if (!id) return;
      const target = document.getElementById(id);
      if (!target) return;
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      target.classList.add('is-highlighted');
      setTimeout(() => target.classList.remove('is-highlighted'), 1600);
    });
  });
})();
