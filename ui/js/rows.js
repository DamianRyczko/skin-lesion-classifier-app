// Probability rows are real buttons, so keyboard and touch work and each has a role and a name.
export default function (component) {
  const { data, parentElement, setTriggerValue } = component;
  let rows = parentElement.querySelector('.nb-rows');
  if (!rows) {
    rows = document.createElement('div');
    rows.className = 'nb-rows';
    parentElement.appendChild(rows);
    rows.addEventListener('click', (e) => {
      const button = e.target.closest('button[data-code]');
      if (button) rows.trigger('open', button.dataset.code);
    });
  }
  rows.trigger = setTriggerValue;
  if (rows.dataset.signature !== data.signature) {
    rows.dataset.signature = data.signature;
    rows.innerHTML = data.html;
  }
}
