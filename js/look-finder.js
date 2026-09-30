(() => {
  const form = document.querySelector('#lookFinder');
  const result = document.querySelector('#lookResult');
  if (!form || !result) return;
  const picks = {
    men: {
      'black-tie': ['Explore men’s tuxedos', 'A tuxedo is the clearest starting point for a black-tie invitation.', 'king.html'],
      prom: ['Explore men’s formal wear', 'Start with a tuxedo or a statement suit, then match the venue and dress code.', 'king.html'],
      default: ['Explore men’s suits', 'Compare two- and three-piece looks, then finish with shoes and accessories.', 'king.html']
    },
    kids: {
      'black-tie': ['Explore kids’ tuxedos', 'A tuxedo gives a formal invitation a clear direction.', 'pawn-tuxedo.html'],
      prom: ['Explore kids’ tuxedos', 'Start with a formal look, then check the measurements and event date.', 'pawn-tuxedo.html'],
      family: ['Explore kids’ vest sets', 'A vest set gives a dressed-up look without a jacket.', 'pawn-suit-vest-set.html'],
      default: ['Explore kids’ suits', 'Compare colorways and the four Pawn styles before choosing a size.', 'pawn.html']
    }
  };
  form.addEventListener('submit', event => {
    event.preventDefault();
    const data = new FormData(form);
    const wearer = data.get('wearer');
    const occasion = data.get('occasion');
    const date = data.get('eventDate');
    const hasChest = Boolean(data.get('chest'));
    const hasWaist = Boolean(data.get('waist'));
    const selection = wearer === 'women'
      ? ['Queen is in development', 'Women’s looks are not available in this preview. Tell us what you would like to see.', 'queen.html']
      : (picks[wearer][occasion] || picks[wearer].default);
    let timing = 'Add your event date, then confirm availability, delivery and any alteration time for the exact piece before ordering.';
    if (date) {
      const today = new Date();
      const todayUTC = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
      const days = Math.round((Date.parse(date + 'T00:00:00Z') - todayUTC) / 86400000);
      if (days < 0) timing = 'That date has passed. Choose a future event date to plan timing.';
      else if (days <= 21) timing = 'Your event is soon. Ask about stock, delivery and alteration time before choosing a look. An arrival date has not been confirmed.';
      else timing = 'There is time to compare looks, but confirm stock, delivery and alteration time for your choice before relying on it.';
    }
    const fit = hasChest && hasWaist
      ? 'You have both key measurements. Compare them with the size guide, then check the measurements for the specific garment before choosing a size.'
      : hasChest || hasWaist
        ? 'You have one key measurement. Take the other, compare both with the size guide, and confirm the garment measurements before choosing.'
        : 'Take your chest and waist measurements, compare them with the size guide, and check the specific garment before choosing a size.';
    const enquiryLook = wearer === 'women' ? 'the Queen collection' : selection[0].replace(/^Explore /, '');
    result.innerHTML = `<span class="eyebrow">Your fit & timing plan</span><h3>${selection[0]}</h3><div class="look-result__grid"><div><strong>01 / Style</strong><p>${selection[1]}</p></div><div><strong>02 / Fit</strong><p>${fit}</p></div><div><strong>03 / Timing</strong><p>${timing}</p></div></div><div class="look-result__actions"><a class="btn" href="${selection[2]}">Explore styles</a><a class="btn dark-ghost" href="size-guide.html">Open size guide</a><a class="btn dark-ghost" href="book-a-fitting.html?look=${encodeURIComponent(enquiryLook)}">Ask about fit & timing</a></div>`;
    result.hidden = false;
    result.scrollIntoView({behavior: 'smooth', block: 'nearest'});
  });
})();
