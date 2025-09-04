/**
 * Drag-and-drop style JSON key-value input component.
 *
 * Allows creating multiple key-value pairs dynamically, validates input,
 * and stores data in a Map for easy retrieval.
 *
 * Usage:
 *   new JsonKeyValueInput("containerId", options, initial_cells, newCellBtnId);
 *
 * Options:
 *   - key_placeholder: string, placeholder for key input
 *   - value_placeholder: string, placeholder for value input
 *   - save_text: string, text for the save button
 *   - delete_text: string, HTML string or text for delete button
 *   - key_validator: RegExp, validates key input
 *   - value_validator: RegExp, validates value input
 */

const deleteIcon = `
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
  <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
</svg>
`;

class JsonKeyValueInput {
  /**
   * Constructor
   * @param {string} containerId - Id of the container element
   * @param {Object} options - Customization options
   * @param {number} initial_cells - Number of initial key-value inputs
   * @param {string|null} newCellBtnId - Id of button to add new inputs
   */
  constructor(containerId, options = {}, initial_cells = 1, newCellBtnId = null) {
    this.container = document.getElementById(containerId);
    if (!this.container) throw new Error(`Container with id "${containerId}" not found`);
    
    this.cells_container = this.container.querySelector(".cells-container");
    this.inputs_containers = [];
    this.options = options;
    this.value = new Map();

    // Load default inputs
    Array.from(this.cells_container.children).map((child)=>{
        this.inputs_containers.push(child)
    })
    // Create initial input containers
    for (let i = 0; i < initial_cells; i++) {
      this.createInputContainer();
    }

    this.loadInputs();

    // Bind "add new cell" button if provided
    if (newCellBtnId) {
      const newCellBtn = document.getElementById(newCellBtnId);
      if (newCellBtn) {
        newCellBtn.addEventListener("click", () => {
          this.cells_container.appendChild(this.createInputContainer().container);
        });
      }
    }
  }

  validate(){
    `
    <div class="w-full flex items-center gap-2>
        <input class="input key_input" placeholder="Key" />
        <input class="input value_input" placeholder="Value" />
        <button class="btn save-btn"> Save </button>
        <button class="btn btn-error delete_btn"> Delete </button>
    </div>
    `
  }

  /**
   * Creates a new key-value input container
   * @returns {Object} Elements of the container
   */
  createInputContainer() {
    // Container and elements
    const container = document.createElement("div");
    const keyInput = document.createElement("input");
    const valueInput = document.createElement("input");
    const saveBtn = document.createElement("button");
    const deleteBtn = document.createElement("button");

    // Styling
    container.className = "w-full flex items-center gap-2";
    keyInput.className = "input key_input";
    valueInput.className = "input value_input";
    saveBtn.className = "btn save_btn";
    deleteBtn.className = "btn btn-error delete_btn";

    // Content
    keyInput.placeholder = this.options.key_placeholder || "Key";
    valueInput.placeholder = this.options.value_placeholder || "Value";
    saveBtn.textContent = this.options.save_text || "Save";
    deleteBtn.innerHTML = this.options.delete_text || deleteIcon;

    // Append
    container.append(keyInput, valueInput, saveBtn, deleteBtn);
    this.inputs_containers.push(container);

    return { container, keyInput, valueInput, saveBtn, deleteBtn };
  }

  /**
   * Binds delete button to remove input container and value from Map
   * @param {HTMLElement} btn - Delete button
   * @param {HTMLElement} keyInput - Key input element
   * @param {HTMLElement} container - Container div
   */
  bindDeleteBtn(btn, keyInput, container) {
    btn.addEventListener("click", () => {
      const key = keyInput.value;
      if (key && this.value.has(key)) {
        this.value.delete(key);
      }
      container.remove();
    });
  }

  /**
   * Validates key and value inputs based on options
   * @param {string} key 
   * @param {string} value 
   * @returns {boolean} True if valid
   */
  validateInputs(key, value) {
    let isValid = true;

    if (this.options.key_validator && key && !this.options.key_validator.test(key)) {
      alert("Invalid key");
      isValid = false;
    }

    if (this.options.value_validator && value && !this.options.value_validator.test(value)) {
      alert("Invalid value");
      isValid = false;
    }

    return isValid;
  }

  /**
   * Loads all input containers and binds events
   */
  loadInputs() {
    this.inputs_containers.forEach((container, index) => {
      const keyInput = container.querySelector(".key_input");
      const valueInput = container.querySelector(".value_input");
      const saveBtn = container.querySelector(".save_btn");
      const deleteBtn = container.querySelector(".delete_btn");

      console.log(keyInput,valueInput,saveBtn,deleteBtn)

      if (!keyInput || !valueInput || !saveBtn || !deleteBtn) {
        console.warn("Input container missing elements; skipping.");
        return;
      }

      // Assign unique IDs
      keyInput.id = `id_key_${index}`;
      valueInput.id = `id_value_${index}`;
      keyInput.dataset.valueInput = valueInput.id;
      valueInput.dataset.keyInput = keyInput.id;

      // Bind key/value changes
      const updateValueMap = (keyEl, valueEl) => {
        const k = keyEl.value;
        const v = valueEl.value;

        if (!this.validateInputs(k, v)) return;

        if (k) this.value.set(k, { key: k, value: v });
        else this.value.delete(k); // remove if key empty
      };

      keyInput.addEventListener("change", () => updateValueMap(keyInput, valueInput));
      valueInput.addEventListener("change", () => updateValueMap(keyInput, valueInput));

      // Bind delete button
      this.bindDeleteBtn(deleteBtn, keyInput, container);

      // Append container to DOM if not already
      if (!this.cells_container.contains(container)) {
        this.cells_container.appendChild(container);
      }
    });
  }

  /**
   * Sets a value manually
   * @param {string} key 
   * @param {any} value 
   */
  setValue(key, value) {
    if (key) this.value.set(key, value);
  }
}
