/**
 * OctopusDash DragDropFileInput
 * -----------------------------
 * Usage:
 *   new DragDropFileInput('#my-dropzone', {
 *     inputName: 'attachments',
 *     multiple: true,
 *     maxSizeMB: 10,
 *     accept: ['image/png', 'image/jpeg', 'application/pdf'],
 *     onChange(files) { console.log('files', files); },
 *     onError(msg) { console.warn(msg); }
 *   });
 */

class DragDropFileInput {
  constructor(selector, options = {}) {
    this.el = document.querySelector(selector);
    if (!this.el) throw new Error(`Dropzone ${selector} not found`);

    this.opts = Object.assign(
      {
        inputName: 'files',
        multiple: true,
        maxSizeMB: null,
        accept: [],
        onChange: () => {},
        onError: () => {},
      },
      options
    );

    this.init();
  }

  init() {
    // create hidden input
    this.input = document.createElement('input');
    this.input.type = 'file';
    this.input.name = this.opts.inputName;
    this.input.multiple = this.opts.multiple;
    this.input.classList.add('hidden');
    if (this.opts.accept.length) this.input.accept = this.opts.accept.join(',');
    this.el.appendChild(this.input);

    // create inner UI
    this.el.classList.add(
      'file-drop',
      'rounded-2xl',
      'border',
      'border-dashed',
      'border-base-300',
      'bg-base-100',
      'hover:bg-base-200',
      'cursor-pointer',
      'p-6',
      'text-center'
    );

    this.el.innerHTML = `
      <div class="flex flex-col items-center gap-3 pointer-events-none">
        <svg xmlns="http://www.w3.org/2000/svg" class="size-10 opacity-70" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M3 15.75V18a3 3 0 003 3h12a3 3 0 003-3v-2.25M16.5 9L12 4.5 7.5 9M12 4.5V15" />
        </svg>
        <p class="text-base font-semibold">Drag & drop files here</p>
        <button type="button" class="btn btn-primary btn-sm mt-2">Choose files</button>
        <p class="text-xs text-base-content/60">PNG, JPG, PDF up to ${this.opts.maxSizeMB ?? '∞'}MB</p>
      </div>
      <div class="file-list mt-4 hidden rounded-xl border border-base-300 bg-base-100">
        <ul class="divide-y divide-dashed divide-base-300"></ul>
      </div>
    `;

    this.chooseBtn = this.el.querySelector('button');
    this.fileListWrap = this.el.querySelector('.file-list');
    this.fileList = this.fileListWrap.querySelector('ul');

    this.bindEvents();
  }

  bindEvents() {
    this.chooseBtn.addEventListener('click', () => this.input.click());
    this.el.addEventListener('click', (e) => {
      if (e.target === this.el) this.input.click();
    });

    this.input.addEventListener('change', (e) => this.handleChosen(e.target.files));

    ['dragenter', 'dragover'].forEach((t) =>
      this.el.addEventListener(t, (e) => {
        e.preventDefault();
        this.el.classList.add('ring-2', 'ring-primary');
      })
    );

    ['dragleave', 'dragend', 'drop'].forEach((t) =>
      this.el.addEventListener(t, (e) => {
        e.preventDefault();
        this.el.classList.remove('ring-2', 'ring-primary');
      })
    );

    this.el.addEventListener('drop', (e) => {
      if (!e.dataTransfer) return;
      this.handleChosen(e.dataTransfer.files);
    });

    this.fileList.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-remove]');
      if (!btn) return;
      const idx = Number(btn.dataset.remove);
      const arr = Array.from(this.input.files);
      arr.splice(idx, 1);
      this.setFiles(arr);
    });
  }

  formatBytes(b) {
    if (b === 0) return '0 B';
    const k = 1024,
      sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(b) / Math.log(k));
    return (b / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i];
  }

  validate(files) {
    const errs = [];
    for (const f of files) {
      if (this.opts.maxSizeMB && f.size > this.opts.maxSizeMB * 1024 * 1024) {
        errs.push(`“${f.name}” exceeds ${this.opts.maxSizeMB}MB (${this.formatBytes(f.size)})`);
      }
      if (this.opts.accept.length && !this.opts.accept.includes(f.type)) {
        errs.push(`“${f.name}” type not allowed (${f.type || 'unknown'})`);
      }
    }
    return errs;
  }

  handleChosen(fileList) {
    const files = Array.from(fileList);
    const errs = this.validate(files);
    if (errs.length) {
      this.opts.onError(errs[0]);
      return;
    }
    this.setFiles(files);
    this.opts.onChange(files);
  }

  setFiles(files) {
    const dt = new DataTransfer();
    files.forEach((f) => dt.items.add(f));
    this.input.files = dt.files;
    this.renderList(files);
  }

  renderList(files) {
    if (!files.length) {
      this.fileListWrap.classList.add('hidden');
      this.fileList.innerHTML = '';
      return;
    }
    this.fileListWrap.classList.remove('hidden');
    this.fileList.innerHTML = files
      .map(
        (f, idx) => `
      <li class="px-3 py-2 flex items-center gap-3 text-sm">
        <div class="avatar placeholder">
          <div class="bg-base-300 text-base-content/70 rounded w-8 h-8 flex items-center justify-center">
            <span class="text-xs">${(f.name.split('.').pop() || '').slice(0, 3).toUpperCase()}</span>
          </div>
        </div>
        <div class="flex-1 overflow-hidden">
          <div class="truncate font-medium">${f.name}</div>
          <div class="text-xs text-base-content/60">${this.formatBytes(f.size)}</div>
        </div>
        <button class="btn btn-ghost btn-xs" data-remove="${idx}">Remove</button>
      </li>`
      )
      .join('');
  }
}
