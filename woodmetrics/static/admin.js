document.querySelectorAll('form[data-confirm]').forEach(form => form.addEventListener('submit', event => {
  if (!window.confirm(form.dataset.confirm)) event.preventDefault();
}));
const category = document.getElementById('category_id');
const type = document.getElementById('type_id');
if (category && type) {
  const options = Array.from(type.options).slice(1).map(option => option.cloneNode(true));
  const filterTypes = () => {
    const selected = type.value;
    type.replaceChildren(new Option('Selecciona un tipo de tablero', ''));
    options.filter(option => option.dataset.category === category.value).forEach(option => type.add(option.cloneNode(true)));
    type.value = Array.from(type.options).some(option => option.value === selected) ? selected : '';
    type.disabled = !category.value;
  };
  category.addEventListener('change', filterTypes);
  filterTypes();
}
const search = document.getElementById('table-search');
if (search) search.addEventListener('input', () => {
  let visible = 0;
  document.querySelectorAll('#records-table tbody tr').forEach(row => {
    row.hidden = !row.textContent.toLocaleLowerCase().includes(search.value.toLocaleLowerCase());
    if (!row.hidden) visible++;
  });
  document.getElementById('no-matches').hidden = visible > 0;
});
