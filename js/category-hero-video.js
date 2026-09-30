/* Category studio films load only when their hero is visible. The poster remains
   available when motion is reduced, playback is blocked, or media cannot load. */
(() => {
  const films = document.querySelectorAll('.cat-hero__film');
  if (!films.length) return;

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  for (const film of films) {
    const video = film.querySelector('video');
    const source = video?.querySelector('source[data-src]');
    const toggle = film.querySelector('.cat-hero__film-toggle');
    if (!video || !source || !toggle) continue;

    const label = toggle.getAttribute('aria-label').replace(/^Play /, '');
    let loaded = false;
    let inView = false;
    let userPaused = false;

    const load = () => {
      if (loaded) return;
      source.src = source.dataset.src;
      source.removeAttribute('data-src');
      video.load();
      loaded = true;
    };

    const pause = () => {
      video.pause();
      film.classList.remove('is-playing');
      toggle.textContent = 'Play film';
      toggle.setAttribute('aria-label', `Play ${label}`);
    };

    const play = async () => {
      load();
      try {
        await video.play();
        toggle.hidden = false;
        film.classList.add('is-playing');
        toggle.textContent = 'Pause film';
        toggle.setAttribute('aria-label', `Pause ${label}`);
      } catch (_) {
        pause();
      }
    };

    toggle.addEventListener('click', () => {
      userPaused = !video.paused;
      if (userPaused) pause();
      else play();
    });
    video.addEventListener('error', () => {
      if (video.readyState === 0) {
        pause();
        toggle.hidden = true;
      }
    });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) pause();
      else if (inView && !userPaused && !reducedMotion.matches) play();
    });

    if (reducedMotion.matches) continue;

    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        for (const entry of entries) {
          inView = entry.isIntersecting;
          if (inView && !document.hidden && !userPaused) play();
          else pause();
        }
      }, { threshold: 0.15, rootMargin: '100px 0px' });
      observer.observe(film);
    } else {
      play();
    }
  }
})();
