(() => {
  const toggle = document.querySelector('[data-answer-toggle]');
  if (toggle) toggle.addEventListener('click', () => {
    const hidden = toggle.getAttribute('aria-pressed') !== 'true';
    document.querySelectorAll('.prep-question').forEach(question => { question.open = !hidden; });
    toggle.setAttribute('aria-pressed', String(hidden));
    toggle.textContent = hidden ? '답변 모두 펼쳐보기' : '답변 가리고 연습하기';
  });
  document.querySelectorAll('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));
  let previousOpen = null;
  window.addEventListener('beforeprint', () => {
    const questions = Array.from(document.querySelectorAll('.prep-question'));
    previousOpen = questions.map(question => question.open);
    questions.forEach(question => { question.open = true; });
  });
  window.addEventListener('afterprint', () => {
    if (!previousOpen) return;
    document.querySelectorAll('.prep-question').forEach((question, index) => { question.open = previousOpen[index]; });
    previousOpen = null;
  });
})();
