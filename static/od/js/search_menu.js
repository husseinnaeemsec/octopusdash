class SearchMenu {
  constructor(inputEl, options = {}) {
    this.inputEl = inputEl;
    this.data = options.data || [
      "تفاحة", "موز", "برتقال", "مانجو", "أناناس", "فراولة", "عنب", "رمان"
    ];

    // Create menu
    this.menuEl = document.createElement("div");
    this.menuEl.className = `
      fixed hidden bg-base-100 rounded-lg shadow-lg 
      max-h-60 overflow-y-auto z-50
    `;
    document.body.appendChild(this.menuEl);

    this.attachEvents();
  }

  attachEvents() {
    this.inputEl.addEventListener("focus", () => this.showMenu());
    this.inputEl.addEventListener("blur", () => setTimeout(() => this.hideMenu(), 150));
    this.inputEl.addEventListener("input", () => this.updateMenu());
  }

  updateMenu() {
    const query = this.inputEl.value.toLowerCase();
    const filtered = this.data.filter(item => item.toLowerCase().includes(query));
    this.renderList(filtered);
  }

  renderList(items) {
    if (!items.length) {
      this.menuEl.innerHTML = `<div class="p-2 text-gray-500 text-sm">لا توجد نتائج</div>`;
      return;
    }

    this.menuEl.innerHTML = `
      <ul class="divide-y divide-gray-100">
        ${items.map(i => `
          <li class="p-2 cursor-pointer hover:bg-base-300">${i}</li>
        `).join("")}
      </ul>
    `;
  }

  showMenu() {
    this.updateMenu();
    this.menuEl.classList.remove("hidden");
    this.positionMenu();
  }

  hideMenu() {
    this.menuEl.classList.add("hidden");
  }

  positionMenu() {
    const rect = this.inputEl.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;

    const spaceBelow = viewportHeight - rect.bottom;
    const spaceAbove = rect.top;
    const spaceRight = viewportWidth - rect.right;
    const spaceLeft = rect.left;

    this.menuEl.style.width = rect.width + "px";

    if (spaceBelow > 150) {
      // below
      this.menuEl.style.top = rect.bottom + 10 + "px";
      this.menuEl.style.left = rect.left + "px";
    } else if (spaceAbove > 150) {
      // above
      this.menuEl.style.top = (rect.top - this.menuEl.offsetHeight) + "px";
      this.menuEl.style.left = rect.left + "px";
    } else if (spaceRight > 200) {
      // right
      this.menuEl.style.top = rect.top + "px";
      this.menuEl.style.left = rect.right + "px";
    } else {
      // left
      this.menuEl.style.top = rect.top + "px";
      this.menuEl.style.left = (rect.left - 200) + "px";
    }
  }
}