
function abrirModalRAG() {
    fetch('/rag')
    .then(res => res.text())
    .then(data => {
        console.log(data);
        document.getElementById('ragContent').textContent = data;
        document.getElementById('ragModal').style.display = 'block';
    });
}

// function abrirModalRAG() {
//     document.getElementById('ragContent').textContent = 'Meu deus do céu';
// }

function abrirModalJuiz() {
    fetch('/api/juiz')
    .then(res => res.json())
    .then(data => {
        document.getElementById('juizContent').textContent = data.resultado;
        document.getElementById('juizModal').style.display = 'block';
    });
}

function fecharModal(id) {
    document.getElementById(id).style.display = 'none';
}