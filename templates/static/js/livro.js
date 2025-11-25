
function montarGraficoPreco(){
    var graficoPrecoLivro = document.getElementById("graficoPrecoLivro");
    if (!graficoPrecoLivro){
        return;
    }

    var idLivro = document.getElementById('idLivro').innerText;
          
    fetch('/retornarPrecosLivro', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ idLivro: idLivro })
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro != ""){
            toast.erro(retorno.erro);
        }else{
            console.log(retorno)
            const todasDatas = [...new Set(
                Object.values(retorno.dados).flat().map(item => item.data)
            )]
            .sort((a, b) => {
                const [da, ma, ya] = a.split('-');
                const [db, mb, yb] = b.split('-');
                return new Date(`${ya}-${ma}-${da}`) - new Date(`${yb}-${mb}-${db}`);
            });

            // Geração automática de cores
            const cores = [
                'rgb(255, 99, 132)',
                'rgb(54, 162, 235)',
                'rgb(255, 206, 86)',
                'rgb(75, 192, 192)',
                'rgb(153, 102, 255)',
                'rgb(255, 159, 64)'
            ];

            const datasets = [];
            let i = 0;

            for (const [loja, registros] of Object.entries(retorno.dados)) {
                // Criar mapa data -> preço
                const mapa = {};
                registros.forEach(r => mapa[r.data] = r.preco);

                // Montar lista de preços na mesma ordem das datas
                const valores = todasDatas.map(data => mapa[data] ?? null);

                datasets.push({
                    label: loja,
                    data: valores,
                    borderColor: cores[i % cores.length],
                    backgroundColor: cores[i % cores.length].replace('rgb', 'rgba').replace(')', ',0.2)'),
                    tension: 0.3,
                    spanGaps: true
                });
                i++;
            }

            const ctx = document.createElement("canvas");
            graficoPrecoLivro.appendChild(ctx);
            new Chart(ctx, {
                type: 'line',
                    data: {
                    labels: todasDatas,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Histórico de preços por loja'
                        },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => `${ctx.dataset.label}: R$ ${ctx.formattedValue}`
                            }
                        }
                    },
                    scales: {
                        y: {
                        title: { display: true, text: 'Preço (R$)' },
                        beginAtZero: false
                        },
                        x: {
                        title: { display: true, text: 'Data da consulta' }
                        }
                    }
                }
            });
        }
    }).catch(error => { console.error('Erro:', error); });
}

document.addEventListener('DOMContentLoaded', function() {
    
    // Funcionalidade para mostrar/ocultar formulário de comentário
    const btnComentario = document.querySelector('.btn-comentario');
    const novoComentario = document.querySelector('.novo-comentario');
    const btnCancelar = document.querySelector('.btn-cancelar-comentario');
    const btnEnviar = document.querySelector('.btn-enviar-comentario');
    const inputComentario = document.querySelector('.input-comentario');
    
    if (btnComentario) {
        btnComentario.addEventListener('click', function() {
            if (novoComentario){
                const isVisible = novoComentario.style.display !== 'none';
                novoComentario.style.display = isVisible ? 'none' : 'block';
                if (!isVisible) {
                    inputComentario.focus();
                }
            }else{
                toast.erro("Deve estar logado para comentar.");
            }
        });
    }
    
    if (btnCancelar) {
        btnCancelar.addEventListener('click', function() {
            novoComentario.style.display = 'none';
            inputComentario.value = '';
        });
    }
    
    if (btnEnviar) {
        btnEnviar.addEventListener('click', function() {
            const textoComentario = inputComentario.value.trim();
            if (textoComentario) {
                var idLivro = document.getElementById('idLivro').innerText;
                var idComentarioPai = 0;
                var comentario = btnEnviar.closest(".comentario");
                if (comentario){
                    var elResponder = comentario.querySelector("[idcomentariopai]");
                    if (elResponder){
                        idComentarioPai = elResponder.getAttribute("idcomentario");
                    }
                }
                
                var spoiler = document.getElementById("checkSpoilerNovoComentario").checked;
                comentar(document.querySelector('.comentarios'), textoComentario, 'livro', idLivro, spoiler, idComentarioPai)
                
                // Limpar formulário
                inputComentario.value = '';
                novoComentario.style.display = 'none';
            }
        });
    }
    
    // Funcionalidade para reações (emojis)
    const botoesReacao = document.querySelectorAll('.btn-reacao');
    botoesReacao.forEach(btn => {
        btn.addEventListener('click', function() {
            var reacao = this.title;

            if (this.classList.contains("selecionado")){
                this.classList.remove('selecionado');
                reacao = ""
            }else{
                botoesReacao.forEach(b => b.classList.remove('selecionado'));
                this.classList.add('selecionado');
            }
            
            var idLivro = document.getElementById('idLivro').innerText;

            // Aqui você pode adicionar lógica para salvar a reação            
            console.log('Reação selecionada:', reacao);
            fetch('/gravarReacaoLivro', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    idLivro: idLivro,
                    reacao: reacao
                })
            })
            .then(response => response.json())
            .then(retorno => {
                if (retorno.erro){
                    toast.erro(retorno.erro);
                }
            }).catch(error => { console.error('Erro:', error); });
        });
    });
    
    // Validação do formulário de comentário
    if (inputComentario) {
        inputComentario.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (btnEnviar) {
                    btnEnviar.click();
                }
            }
        });
    }

    var idLivro = document.getElementById('idLivro').innerText;
    valoresFiltro = {'telaOrigem': 'livro', 'itemOrigemId': idLivro}
    var areaComentarios = document.getElementById("areaComentarios");
    if (areaComentarios){
        const pag = new Paginacao(areaComentarios, {
            url: '/procurarComentarios',
            filtros: valoresFiltro,
            paginaAtual: valoresFiltro['paginaAtual'] ?? 1,
            qtdTotalElementos: valoresFiltro.qtdItens,
            conteudoHtml: conteudoHtmlComentario,
            flex: false,
            elScroolDeteccao: window,
            qtdElPorPagina: 5,
            logica: function(){
                if (this.paginaAtual == 1 && this.dados.length == 0){
                    this.toggleMsg("Nenhum comentário encontrado para o livro. Seje o primeiro(a) a comentar.");
                }
            }
        });
    }

    montarGraficoPreco();
});

