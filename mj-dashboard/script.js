(() => {
  'use strict';
  const dialog = document.querySelector('.image-dialog');
  const expanded = document.querySelector('#expanded-image');
  const caption = document.querySelector('#image-caption');
  const closeButton = dialog?.querySelector('.dialog-close');
  let opener = null;

  if (dialog && expanded && caption && closeButton && typeof dialog.showModal === 'function') {
    document.querySelectorAll('[data-lightbox]').forEach(button => {
      button.addEventListener('click', () => {
        const source = button.querySelector('img');
        if (!source) return;
        opener = button;
        expanded.src = source.currentSrc || source.src;
        expanded.alt = source.alt;
        caption.textContent = button.dataset.caption || source.alt;
        dialog.classList.toggle('is-portrait', source.naturalHeight > source.naturalWidth);
        dialog.showModal();
        document.body.classList.add('dialog-open');
        closeButton.focus();
      });
    });
    closeButton.addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      const bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
    });
    dialog.addEventListener('close', () => {
      document.body.classList.remove('dialog-open');
      expanded.removeAttribute('src');
      opener?.focus({ preventScroll: true });
      opener = null;
    });
  }

  const tocLinks = [...document.querySelectorAll('.chapter-nav a')];
  const chapters = tocLinks.map(link => document.querySelector(link.getAttribute('href'))).filter(Boolean);
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const active = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!active) return;
      tocLinks.forEach(link => {
        if (link.getAttribute('href') === `#${active.target.id}`) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
    }, { rootMargin: '-15% 0px -65% 0px', threshold: 0 });
    chapters.forEach(chapter => observer.observe(chapter));
  }

  let previouslyOpen = [];
  window.addEventListener('beforeprint', () => {
    previouslyOpen = [...document.querySelectorAll('details')].filter(detail => detail.open);
    document.querySelectorAll('details').forEach(detail => { detail.open = true; });
  });
  window.addEventListener('afterprint', () => {
    document.querySelectorAll('details').forEach(detail => { detail.open = previouslyOpen.includes(detail); });
  });
})();
