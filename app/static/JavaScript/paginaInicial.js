let cronometro;
let listaNomeCartas = []

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
        const sugestoes = cartasFiltradas.slice(0, 10)

        sugestoes.forEach(nomeEncontrado => {
            const opcao = document.createElement("option");
            opcao.value = nomeEncontrado;
            listaHTML.appendChild(opcao);
        })
    }
}

document.getElementById("nomeCarta").addEventListener("input", function() {
    clearTimeout(cronometro);
    cronometro = setTimeout(sugerirCarta, 500)
});

document.getElementById("nomeCarta").addEventListener("keydown", function(evento) {
    if (evento.key === "Enter"){
        evento.preventDefault();
        clearTimeout(cronometro)
        sugerirCarta();
    }
    clearTimeout(cronometro);
    cronometro = setTimeout(sugerirCarta, 500)
});

document.getElementById("nomeCarta").addEventListener("blur", function() {
    clearTimeout(cronometro);
    sugerirCarta()
});

document.getElementById("btn-helloWorld").addEventListener("click", function() {
    const nomeCarta = document.getElementById("nomeCarta").value;
    const edicaoCarta = document.getElementById("edicaoCarta").value;
    const acabamentoCarta = document.getElementById("acabamentoCarta").value;
    const qntCarta = document.getElementById("qntCarta").value;

    fetch("/botaoClicado", {
        method: "POST",
        headers: {"content-type": "application/json"},
        body: JSON.stringify({
            "nome": nomeCarta,
            "edicao": edicaoCarta,
            "acabamento": acabamentoCarta,
            "quantidade": qntCarta
        })
    })
    .then(resposta => resposta.json())
    .then(dados => console.log(dados))
})