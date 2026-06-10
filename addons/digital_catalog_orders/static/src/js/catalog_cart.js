document.addEventListener("DOMContentLoaded", function () {
  const cart = [];
  const cartItems = document.getElementById("cart-items");
  const cartDataInput = document.getElementById("cart_data");

  function renderCart() {
    if (!cartItems || !cartDataInput) return;

    cartItems.innerHTML = "";

    cart.forEach(function (item) {
      const div = document.createElement("div");
      div.className = "border rounded p-2 mb-2";
      div.textContent = `${item.name} x ${item.quantity} - $${item.price_unit}`;
      cartItems.appendChild(div);
    });

    cartDataInput.value = JSON.stringify(cart);
  }

  document.querySelectorAll(".add-to-cart").forEach(function (button) {
    button.addEventListener("click", function () {
      const productId = this.dataset.id;
      const name = this.dataset.name;
      const price = parseFloat(this.dataset.price);

      const existing = cart.find((item) => item.product_id === productId);

      if (existing) {
        existing.quantity += 1;
      } else {
        cart.push({
          product_id: productId,
          name: name,
          quantity: 1,
          price_unit: price,
        });
      }

      renderCart();
    });
  });
});
