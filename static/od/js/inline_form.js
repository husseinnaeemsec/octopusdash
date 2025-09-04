class InlineForm {
    constructor(triggerId, instance_id) {
        this.trigger = document.getElementById(triggerId);
        if (!this.trigger) throw new Error(`Trigger element with id "${triggerId}" not found.`);
        if (!instance_id) throw new Error("Instance ID is required.");

        this.instance_id = instance_id;
        this.inputs = [];
        this.initialValues = new Map();
        this.isDirty = false;

        this.loadInputs();
        this.bindInputs();
        this.updateTriggerState();
        this.handleInlineForm();
    }

    loadInputs() {
        const formId = this.trigger.dataset.inlineForm;
        this.tr = document.getElementById(formId);

        if (!this.tr) {
            console.error("Inline form not found; skipping");
            return;
        }

        const children = this.tr.querySelectorAll("input, select, textarea");

        children.forEach(child => {
            if (!child.name.startsWith('__')) {
                this.inputs.push(child);
                this.initialValues.set(child, child.value); // save initial value
            }
        });

        if (!this.inputs.length) {
            console.warn("Inline form has no valid children; trigger will remain disabled.");
        }
    }

    bindInputs() {
        this.inputs.forEach(input => {
            input.addEventListener("input", () => {
                this.checkDirty();
            });
        });
    }

    checkDirty() {
        this.isDirty = this.inputs.some(input => input.value !== this.initialValues.get(input));
        this.updateTriggerState();
    }

    updateTriggerState() {
        if (this.isDirty) {
            this.trigger.removeAttribute("disabled");
        } else {
            this.trigger.setAttribute("disabled", true);
        }
    }

    async handleInlineForm() {
        this.trigger.addEventListener("click", async () => {
            if (!this.inputs.length) return;

            const formData = new FormData();
            this.inputs.forEach(input => {
                formData.append(input.name.split("-")[2], input.value);
            });
            formData.append("instance_id", this.instance_id);

            const originalContent = this.trigger.innerHTML;
            this.trigger.innerHTML = `<span class="loading loading-spinner loading-sm text-base-content"></span>`;
            this.trigger.disabled = true;

            try {
                const res = await fetch(window.location.pathname, {
                    method: 'POST',
                    headers: {
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: formData
                });

                const data = await res.json().catch(() => ({}));

                if (res.ok) {
                    new Toast(data.message || 'Operation successful.', 'success');
                    // Update initial values after successful save
                    this.inputs.forEach(input => this.initialValues.set(input, input.value));
                    this.checkDirty();
                } else {
                    new Toast(data.error || 'An error occurred.', 'error');
                }
            } catch (error) {
                console.error('Network error:', error);
                new Toast('A network error occurred.', 'error');
            } finally {
                this.trigger.innerHTML = originalContent;
                this.updateTriggerState();
            }
        });
    }
}
