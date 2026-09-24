/* Homepage "chapter" — a cut-out model drifts up past the screen like a balloon as the section scrolls by.
   Progress is scroll-driven but smoothed (lerp), so it lags and floats instead of tracking the scroll 1:1. */
(() => {
  "use strict";
  const sec = document.getElementById('chapter');
  if (!sec) return;
  const fig = sec.querySelector('.balloon__fig');
  if (!fig) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) { sec.classList.add('is-static'); return; }

  const ease = t => (t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);
  let target = 0, cur = 0, running = false, raf = 0, last = 0;

  const measure = () => {
    const r = sec.getBoundingClientRect(), vh = window.innerHeight;
    target = Math.min(1, Math.max(0, (vh - r.top) / (r.height + vh)));
  };

  const frame = now => {
    const dt = Math.min(48, now - last || 16); last = now;
    cur += (target - cur) * Math.min(1, dt * 0.0055);      // frame-rate independent smoothing
    const vh = window.innerHeight, vw = window.innerWidth, h = fig.offsetHeight;
    const y = vh * 1.02 - ease(cur) * (vh * 1.02 + h * 1.2);        // top edge of the figure, in viewport px
    const sway = Math.sin(cur * Math.PI * 3.4) * 2.4;                // vw, side to side
    const rot = -10 + cur * 20 + Math.sin(now / 1700) * 1.6;         // deg, tips one way then the other
    const bob = Math.sin(now / 1100) * 7;                            // px, idle float
    fig.style.transform = `translate3d(calc(-50% + ${sway.toFixed(2)}vw), ${(y + bob).toFixed(1)}px, 0) rotate(${rot.toFixed(2)}deg) scale(${(0.92 + 0.16 * cur).toFixed(3)})`;
    raf = running ? requestAnimationFrame(frame) : 0;
  };

  const start = () => { if (!running) { running = true; last = 0; measure(); raf = requestAnimationFrame(frame); } };
  const stop = () => { running = false; };

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(es => (es[0].isIntersecting ? start() : stop()), { rootMargin: '20% 0px' }).observe(sec);
  } else { start(); }
  window.addEventListener('scroll', measure, { passive: true });
  window.addEventListener('resize', measure);
  measure();
})();
