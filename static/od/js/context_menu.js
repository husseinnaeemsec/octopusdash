class ContextMenu {
    static openMenus = new Set(); // track all open menus

    /**
     * @param {HTMLElement} container - The container element for context menu
     * @param {HTMLElement|null} trigger - Optional trigger element
     * @param {Array<{label: string, action: Function}>} items - Menu items
     */
    constructor({ container, trigger = null, items = [] }) {
        this.container = container;
        this.trigger = trigger;
        this.items = items;
        this.menu = null;
        this.isOpen = false;

        this.init();
    }

    init() {
        this.createMenu();
        this.addEventListeners();
    }

    createMenu() {
        this.menu = document.createElement("div");
        this.menu.className = `
            absolute z-50 hidden w-48  bg-base-100 border border-base-content rounded-md shadow-lg 
            overflow-hidden divide-y divide-gray-100 
        `;
        document.body.appendChild(this.menu);

        this.items.forEach(item => {
            const el = document.createElement("div");
            el.className = `
                px-4 py-2 text-sm hover:bg-base-300 cursor-pointer
                transition-colors
            `;
            el.innerHTML = item.label;
            el.addEventListener("click", e => {
                item.action(e);
                this.closeMenu();
            });
            this.menu.appendChild(el);
        });
    }

    addEventListeners() {
        // Trigger click
        if (this.trigger) {
            this.trigger.addEventListener("click", e => {
                e.preventDefault();
                this.toggleMenuAtTrigger();
            });
        }

        // Container right-click
        this.container.addEventListener("contextmenu", e => {
            e.preventDefault();
            this.openMenu(e.clientX, e.clientY);
        });

        // Close on outside click
        document.addEventListener("click", e => {
            if (this.isOpen && !this.menu.contains(e.target) &&
                (!this.trigger || !this.trigger.contains(e.target))) {
                this.closeMenu();
            }
        });

        // Escape key
        document.addEventListener("keydown", e => {
            if (this.isOpen && e.key === "Escape") {
                this.closeMenu();
            }
        });

        // Resize
        window.addEventListener("resize", () => {
            if (this.isOpen) this.adjustPosition();
        });
    }

    toggleMenuAtTrigger() {
        const rect = this.trigger.getBoundingClientRect();
        const x = rect.left;
        const y = rect.bottom;

        if (this.isOpen) {
            this.closeMenu();
        } else {
            this.openMenu(x, y);
        }
    }

    openMenu(x, y) {
        // Close all other menus first
        ContextMenu.openMenus.forEach(menu => menu.closeMenu());
        ContextMenu.openMenus.add(this);

        this.menu.style.display = "block";
        this.isOpen = true;

        // Set temporary position for size calculation
        this.menu.style.left = `${x}px`;
        this.menu.style.top = `${y}px`;
        this.adjustPosition();
    }

    adjustPosition() {
        const rect = this.menu.getBoundingClientRect();
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        const padding = 8;

        let left = rect.left;
        let top = rect.top;

        // Horizontal position
        if (left + rect.width + padding > vw) {
            // not enough space on right, move left
            left = vw - rect.width - padding;
        }
        if (left < padding) left = padding;

        // Vertical position
        if (top + rect.height + padding > vh) {
            // not enough space at bottom, move above
            top = vh - rect.height - padding;
        }
        if (top < padding) top = padding;

        this.menu.style.left = `${left}px`;
        this.menu.style.top = `${top}px`;
    }

    closeMenu() {
        this.menu.style.display = "none";
        this.isOpen = false;
        ContextMenu.openMenus.delete(this);
    }
}
