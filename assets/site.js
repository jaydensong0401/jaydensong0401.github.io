(() => {
  const dialog = document.getElementById('image-dialog');
  if (dialog) {
    const image = document.getElementById('enlarged-image');
    const title = document.getElementById('image-dialog-title');
    document.querySelectorAll('[data-enlarge]').forEach(button => button.addEventListener('click', () => {
      const source = button.querySelector('img');
      if (!source) return;
      image.src = source.currentSrc || source.src;
      image.alt = source.alt;
      title.textContent = source.alt;
      dialog.showModal();
    }));
    document.getElementById('close-image').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const r = dialog.getBoundingClientRect();
      if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
    });
  }
  const printButton = document.getElementById('print-case');
  if (printButton) printButton.addEventListener('click', () => window.print());
  const progress = document.getElementById('reading-progress');
  const sectionLinks = Array.from(document.querySelectorAll('.nav a[href^="#"]'));
  let pending = false;
  function update() {
    const max = document.documentElement.scrollHeight - innerHeight;
    if (progress) progress.style.width = (max > 0 ? Math.min(100, scrollY / max * 100) : 0) + '%';
    let selected = null;
    sectionLinks.forEach(link => {
      const section = document.getElementById(link.getAttribute('href').slice(1));
      if (section && section.getBoundingClientRect().top <= 150) selected = link;
    });
    sectionLinks.forEach(link => { if (link === selected) link.setAttribute('aria-current', 'true'); else link.removeAttribute('aria-current'); });
    pending = false;
  }
  addEventListener('scroll', () => { if (!pending) { pending = true; requestAnimationFrame(update); } }, { passive:true });
  addEventListener('resize', update);
  update();
})();
