let selected;
const result = document.querySelector('#result');
const submit = document.querySelector('#submit');
const money = cents => new Intl.NumberFormat('en-GB', {style:'currency', currency:'GBP'}).format(cents / 100);
async function loadProducts() {
  try {
    const response = await fetch('/api/products');
    if (!response.ok) throw new Error('Catalog unavailable');
    const products = await response.json();
    for (const product of products) {
      const button = document.createElement('button');
      button.className = 'product';
      button.type = 'button';
      button.setAttribute('aria-pressed', 'false');
      const name = document.createElement('strong');
      name.textContent = product.name;
      button.append(name, document.createTextNode(money(product.price_cents)));
      button.onclick = () => {
        selected = product.id;
        document.querySelectorAll('.product').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
        submit.disabled = false;
      };
      document.querySelector('#products').append(button);
    }
    console.info('Catalog loaded', {products: products.length});
  } catch (error) {
    result.textContent = 'Could not load products. Reload the page to try again.';
    console.error('Catalog request failed', error);
  }
}
document.querySelector('#checkout').onsubmit = async event => {
  event.preventDefault();
  submit.disabled = true;
  result.textContent = 'Placing your demo order…';
  try {
    const response = await fetch('/api/checkout', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({product_id:selected, quantity:Number(document.querySelector('#quantity').value), scenario:document.querySelector('#scenario').value})});
    const body = await response.json();
    result.textContent = response.ok ? `Order placed. Total ${money(body.total_cents)}.` : body.error;
    console.info('Checkout completed', {status:response.status});
  } catch (error) {
    result.textContent = 'Could not place the order. Try again.';
    console.error('Checkout request failed', error);
  } finally { submit.disabled = false; }
};
loadProducts();
