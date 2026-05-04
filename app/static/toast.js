function mostrarAviso(mensagem, tipo = "sucesso") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast-aviso ${tipo}`;
    toast.textContent = mensagem;

    const barra = document.createElement("div");
    barra.className = "toast-barra";
    
    toast.appendChild(barra);
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = "sumirToast 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards";
        setTimeout(() => toast.remove(), 400); 
    }, 5000);
}