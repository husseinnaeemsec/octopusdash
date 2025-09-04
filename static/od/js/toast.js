class Toast {
    constructor(message,type='success',timeout = 3000) {
        this.message = message;
        this.timeout = timeout;
        this.type = type;
        this.showToast();
    }


    showToast() {
        this.toast = document.createElement("div")
        const content = `
        <div class="toast toast-center w-xl">
            <div class="alert  ${this.type ? 'text-white alert-'+this.type : 'bg-base-300'} ">
                <span> ${this.message} </span>
            </div>
        </div>
        `
        this.toast.innerHTML = content;
        document.body.appendChild(this.toast)
        setTimeout(()=>{
            this.toast.remove();
        },this.timeout)
    }
}