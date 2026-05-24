let cronometro;
let listaNomeCartas = [];
let edicaoSelecionada = "";

function limparFormulario() {
    const inputNome = document.getElementById("nomeCarta");
    inputNome.value = "";
    
    const inputQnt = document.getElementById("qntCarta");
    inputQnt.value = "";
    inputQnt.disabled = true; 

    document.getElementById("sugestoesCartas").innerHTML = "";
    document.getElementById("dropdownEdicoes").innerHTML = "";
    document.getElementById("containerAcabamentos").innerHTML = "";

    edicaoSelecionada = "";
    document.getElementById("btnSalvar").disabled = true;
    
    inputNome.focus(); 
}

function checarFormularioCompleto() {
    const nome = document.getElementById("nomeCarta").value;
    const qnt = document.getElementById("qntCarta").value;
    const acabamento = document.querySelector('input[name="grupoAcabamento"]:checked');
    const botaoSalvar = document.getElementById("btnSalvar");

    if (nome && edicaoSelecionada !== "" && acabamento && qnt > 0) {
        botaoSalvar.disabled = false;
    } else {
        botaoSalvar.disabled = true;
    }
}

function confirmarCarta(cartaEscolhida){
    document.getElementById("qntCarta").disabled = false;

    fetch(`/buscarEdicoes?nome=${encodeURIComponent(cartaEscolhida)}`)
    .then(resposta => resposta.json())
    .then(dadosEdicoes =>{
        montarDropDownEdicoes(dadosEdicoes)
    })
    .catch(erro => console.error(erro));
}

function montarDropDownEdicoes(edicoes) {
    const dropdown = document.getElementById("dropdownEdicoes");
    dropdown.innerHTML = "";

    edicoes.forEach(edicao => {
        const itemOpcao = document.createElement("div");
        itemOpcao.classList.add("opcao-edicao");

        itemOpcao.style.cursor = "pointer";
        itemOpcao.style.padding = "5px";
        itemOpcao.style.borderBottom = "1px solid #ccc";
        itemOpcao.style.transition = "all 0.2s";

        itemOpcao.innerHTML = `
            <img src="${edicao.linkImagem}" alt="${edicao.nome}" width="20" height="20" style="vertical-align: middle;">
            <span style="margin-left: 8px;">${edicao.nome}</span>
        `;

        itemOpcao.addEventListener("click", function() {
            console.log(edicao.nome);
            
            edicaoSelecionada = edicao.codigo;
            checarFormularioCompleto();

            document.querySelectorAll(".opcao-edicao").forEach(div => {
                div.style.border = "none";
                div.style.borderBottom = "1px solid #ccc";
                div.style.backgroundColor = "transparent";
            });

            this.style.border = "2px solid #007BFF";
            this.style.backgroundColor = "#e9ecef";
            this.style.borderRadius = "5px";

            const containerAcabamentos = document.getElementById("containerAcabamentos");
            containerAcabamentos.innerHTML = "";

            if (edicao.acabamentos) {
                const listaAcabamentos = edicao.acabamentos.split(",").map(a => a.trim().toLowerCase());
                const ordem = ["nonfoil", "foil", "etched"];
                
                ordem.forEach(acabamento => {
                    if (listaAcabamentos.includes(acabamento)) {
                        let linkImagemAcabamento = `/static/imagens/${acabamento}.png`;

                        const radio = document.createElement("input");
                        radio.type = "radio";
                        radio.name = "grupoAcabamento";
                        radio.value = acabamento;
                        radio.id = `radio-${acabamento}`;
                        radio.style.display = "none";

                        const label = document.createElement("label");
                        label.htmlFor = radio.id;
                        label.style.cursor = "pointer";
                        label.style.padding = "5px";
                        label.style.borderRadius = "8px";
                        label.style.border = "2px solid transparent";

                        label.innerHTML = `
                            <img src="${linkImagemAcabamento}" alt="${acabamento}" width="40" height="40" title="${gerarTitleCase(acabamento)}">
                        `;

                        radio.addEventListener("change", function() {
                            document.querySelectorAll('label[for^="radio-"]').forEach(lbl => {
                                lbl.style.border = "2px solid transparent";
                                lbl.style.backgroundColor = "transparent";
                            });

                            if (this.checked) {
                                label.style.border = "2px solid #007BFF";
                                label.style.backgroundColor = "#e9ecef";
                            }
                            checarFormularioCompleto();
                        });

                        containerAcabamentos.appendChild(radio);
                        containerAcabamentos.appendChild(label);
                    }
                });
            }
        });

        dropdown.appendChild(itemOpcao);
    });
}

function carregarCartasIniciais(){
    const dadosArmazenados = sessionStorage.getItem("TodasAsCartas");
    let cartasConvertidas = []
    console.log(dadosArmazenados)
    if (dadosArmazenados){
        cartasConvertidas = JSON.parse(dadosArmazenados)
    }
    if (dadosArmazenados && cartasConvertidas.length > 0){
        listaNomeCartas = cartasConvertidas;
    } else {
        fetch("/buscarCartas")
            .then(resposta => resposta.json())
            .then(cartasRecebidas => {
                listaNomeCartas = cartasRecebidas
                sessionStorage.setItem("TodasAsCartas", JSON.stringify(cartasRecebidas));
                console.log(listaNomeCartas)
            })
    }
}

carregarCartasIniciais();

function sugerirCarta() {
    const busca = document.getElementById("nomeCarta").value.toLowerCase();
    const listaHTML = document.getElementById("sugestoesCartas")
    listaHTML.innerHTML = ""
    if (busca.length >= 1){
        const cartasFiltradas = listaNomeCartas.filter(nome => nome.toLowerCase().includes(busca));
        const sugestoes = cartasFiltradas.slice(0, 5)

        sugestoes.forEach(nomeEncontrado => {
            const opcao = document.createElement("option");
            opcao.value = gerarTitleCase(nomeEncontrado);
            listaHTML.appendChild(opcao);
        })
    }
}

document.getElementById("nomeCarta").addEventListener("input", function() {
    clearTimeout(cronometro);
    const valorDigitado = this.value;
    const cartaExiste = listaNomeCartas.find(nome => nome.toLowerCase() === valorDigitado.toLowerCase())
    if (cartaExiste){
        this.value = gerarTitleCase(cartaExiste)
        document.getElementById("sugestoesCartas").innerHTML = "";
        confirmarCarta(cartaExiste)
    } else {
        cronometro = setTimeout(sugerirCarta, 500)
    }
    checarFormularioCompleto();
});

document.getElementById("nomeCarta").addEventListener("keydown", function(evento) {
    if (evento.key === "Enter"){
        evento.preventDefault();
        clearTimeout(cronometro);
        
        const valorDigitado = this.value;
        const cartaExiste = listaNomeCartas.find(nome => nome.toLowerCase() === valorDigitado.toLowerCase());
        
        if (cartaExiste) {
            this.value = gerarTitleCase(cartaExiste);
            document.getElementById("sugestoesCartas").innerHTML = "";
            confirmarCarta(cartaExiste);
        } else {
            sugerirCarta();
        }
        checarFormularioCompleto();
    }
});

document.getElementById("nomeCarta").addEventListener("blur", function() {
    clearTimeout(cronometro);
    sugerirCarta();
    checarFormularioCompleto();
});

document.getElementById("qntCarta").addEventListener("input", function() {
    checarFormularioCompleto();
});

document.getElementById("btnSalvar").addEventListener("click", function() {
    const nomeCarta = document.getElementById("nomeCarta").value;
    const qntCarta = document.getElementById("qntCarta").value;
    const acabamentoCarta = document.querySelector('input[name="grupoAcabamento"]:checked').value;

    fetch("/botaoSalvado", {
        method: "POST",
        headers: {"content-type": "application/json"},
        body: JSON.stringify({
            "nome": nomeCarta,
            "edicao": edicaoSelecionada,
            "acabamento": acabamentoCarta,
            "quantidade": qntCarta
        })
    })
    .then(resposta => resposta.json())
    .then(dados => {
        console.log("Salvo No Banco:", dados)
        alert("Carta Adicionada Com Sucesso")
        limparFormulario()
    })
    .catch(erro => console.error("Erro ao salvar:", erro));
});

function gerarTitleCase(texto){
    return texto
        .split(" ")
        .map(palavra => {
            if (palavra.length === 0) return "";
            return palavra.charAt(0).toUpperCase() + palavra.slice(1).toLowerCase()
        })
        .join(" ")
}