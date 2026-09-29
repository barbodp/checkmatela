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
    const selection = wearer === 'women'
      ? ['Queen is in development', 'Women’s looks are not available in this preview. Tell us what you would like to see.', 'queen.html']
      : (picks[wearer][occasion] || picks[wearer].default);
    let timing = 'Before you commit, confirm availability, delivery and any alteration time for the exact piece.';
    if (date) {
      const days = Math.ceil((new Date(date + 'T12:00:00') - new Date()) / 86400000);
      if (days < 0) timing = 'That date has passed. Choose a future event date to plan timing.';
      else if (days <= 21) timing = 'Your event is soon. Ask about stock, delivery and fit immediately; no arrival date is guaranteed.';
      else timing = 'You have time to compare styles and measurements, but confirm delivery before relying on it.';
    }
    const enquiryLook = wearer === 'women' ? 'the Queen collection' : selection[0].replace(/^Explore /, '');
    result.innerHTML = `<span class="eyebrow">Your starting point</span><h3>${selection[0]}</h3><p>${selection[1]}</p><p>${timing}</p><div class="look-result__actions"><a class="btn" href="${selection[2]}">Explore styles</a><a class="btn dark-ghost" href="book-a-fitting.html?look=${encodeURIComponent(enquiryLook)}">Ask about fit & timing</a></div>`;
    result.hidden = false;
    result.scrollIntoView({behavior: 'smooth', block: 'nearest'});
  });
})();
