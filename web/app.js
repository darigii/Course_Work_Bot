let tg = window.Telegram.WebApp;
tg.expand();


const categoryOrder = ["Еда", "Сладости и снеки", "Напитки", "Косметика", "Одежда", "Альбомы", "Прочее"];
let cart = JSON.parse(localStorage.getItem("cart")) || [];

// Показываем/скрываем кнопку корзины
function toggleCartButton(show) {
  const btn = document.getElementById("basket-btn");
  if (!btn) return;
  btn.style.display = show ? "block" : "none";
}

// Обновляем UI карточек по текущей корзине
function updateCartUI() {
  cart.forEach(item => {
    const card = document.querySelector(`.product-card[data-id="${item.id}"]`);
    if (card) {
      card.querySelector('.add-btn')?.classList.add('hidden');
      card.querySelector('.counter')?.classList.remove('hidden');
      card.querySelector('.count').textContent = item.count;
    }
  });
  toggleCartButton(cart.length > 0);
}

// Получение товаров
fetch("https://darigii.pythonanywhere.com/products?nocache=" + Date.now())
  .then(res => res.ok ? res.json() : Promise.reject(`HTTP ${res.status}`))
  .then(data => {
    const container = document.getElementById("product-container");

    categoryOrder.forEach(mainCategory => {
      const subcats = data[mainCategory];
      if (!subcats) return;

      const hasItems = Object.values(subcats).some(items => items?.length > 0);
      if (!hasItems) return;

      const mainTitle = document.createElement("h2");
      mainTitle.textContent = mainCategory;
      mainTitle.className = "main-category-title";
      container.appendChild(mainTitle);

      for (const [subCategory, items] of Object.entries(subcats)) {
        if (!items || items.length === 0) continue;

        const section = document.createElement("section");
        section.className = "category-section";
        section.setAttribute("data-category", mainCategory);

        const subTitle = document.createElement("h3");
        subTitle.textContent = subCategory;
        section.appendChild(subTitle);

        const grid = document.createElement("div");
        grid.className = "products-grid";

        items.forEach(p => {
          const id = p.name + "_" + mainCategory;
          const card = document.createElement("div");
          card.className = "product-card";
          card.dataset.id = id;
          card.innerHTML = `
            <img src="${p.image_url}" alt="${p.name}" />
            <h3>${p.name}</h3>
            <p>${p.price}₽</p>
            <div class="product-controls">
              <button class="add-btn">Добавить</button>
              <div class="counter hidden">
                <button class="minus">−</button>
                <span class="count">1</span>
                <button class="plus">+</button>
              </div>
            </div>
          `;
          grid.appendChild(card);
        });

        section.appendChild(grid);
        container.appendChild(section);
      }

      updateCartUI();
    });
  })
  .catch(err => {
    console.error("Ошибка загрузки каталога:", err);
    document.getElementById("product-container").innerHTML =
      "<p>⚠️ Не удалось загрузить каталог.</p>";
  });

// Логика добавления, увеличения и уменьшения
document.addEventListener("click", e => {
  const card = e.target.closest(".product-card");
  if (!card) return;
  const id = card.dataset.id;
  const name = card.querySelector("h3").textContent;
  const price = parseInt(card.querySelector("p").textContent);
  const img = card.querySelector("img").src;

  if (e.target.classList.contains("add-btn")) {
    cart.push({ id, name, price, img, count: 1 });
    localStorage.setItem("cart", JSON.stringify(cart));
    updateCartUI();
  }

  if (e.target.classList.contains("plus")) {
    const item = cart.find(p => p.id === id);
    if (item) {
      item.count++;
      card.querySelector(".count").textContent = item.count;
      localStorage.setItem("cart", JSON.stringify(cart));
    }
  }

  if (e.target.classList.contains("minus")) {
    const item = cart.find(p => p.id === id);
    if (item) {
      item.count--;
      if (item.count <= 0) {
        cart = cart.filter(p => p.id !== id);
        card.querySelector(".add-btn").classList.remove("hidden");
        card.querySelector(".counter").classList.add("hidden");
      } else {
        card.querySelector(".count").textContent = item.count;
      }
      localStorage.setItem("cart", JSON.stringify(cart));
      toggleCartButton(cart.length > 0);
    }
  }
});

document.body.insertAdjacentHTML("beforeend", `
  <a href="basket.html" id="basket-btn" class="cart-button hidden">
     Корзина
  </a>
`);














