/* Homepage "The Board" index — hovering a title / numeral previews that collection and lights up its numeral. */
(() => {
  "use strict";
  const root = document.getElementById('index');
  if (!root) return;
  const links = [...root.querySelectorAll('.index__list a, .index__nums a')];
  const imgs = [...root.querySelectorAll('.index__preview img')];
  const soon = root.querySelector('.index__soon');
  const set = k => {
    root.dataset.active = k;
    links.forEach(a => a.classList.toggle('is-on', a.dataset.k === k));
    imgs.forEach(i => i.classList.toggle('is-on', i.dataset.k === k));
    if (soon) soon.classList.toggle('is-on', soon.dataset.k === k);
  };
  links.forEach(a => {
    a.addEventListener('mouseenter', () => set(a.dataset.k));
    a.addEventListener('focus', () => set(a.dataset.k));
  });
  set('0');
})();
