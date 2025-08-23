// Funcionalidades para a página de detalhes do livro

document.addEventListener('DOMContentLoaded', function() {
    
    // Funcionalidade para mostrar/ocultar formulário de comentário
    const btnComentario = document.querySelector('.btn-comentario');
    const novoComentario = document.querySelector('.novo-comentario');
    const btnCancelar = document.querySelector('.btn-cancelar-comentario');
    const btnEnviar = document.querySelector('.btn-enviar-comentario');
    const inputComentario = document.querySelector('.input-comentario');
    
    if (btnComentario) {
        btnComentario.addEventListener('click', function() {
            const isVisible = novoComentario.style.display !== 'none';
            novoComentario.style.display = isVisible ? 'none' : 'block';
            if (!isVisible) {
                inputComentario.focus();
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
                // Aqui você pode adicionar a lógica para enviar o comentário ao servidor
                console.log('Enviando comentário:', textoComentario);
                
                // Simular adição do comentário na lista
                adicionarComentario({
                    usuario: { nome: 'Você', avatar: 'default.jpg' },
                    texto: textoComentario,
                    id: Date.now()
                });
                
                // Limpar formulário
                inputComentario.value = '';
                novoComentario.style.display = 'none';
            }
        });
    }
    
    // Funcionalidade para spoiler
    const spoilers = document.querySelectorAll('.spoiler');
    spoilers.forEach(spoiler => {
        spoiler.addEventListener('click', function() {
            this.classList.toggle('revelado');
            if (this.classList.contains('revelado')) {
                this.style.cursor = 'default';
            } else {
                this.style.cursor = 'pointer';
            }
        });
    });
    
    // Funcionalidade para reações (emojis)
    const botoesReacao = document.querySelectorAll('.btn-reacao');
    botoesReacao.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove seleção anterior
            botoesReacao.forEach(b => b.classList.remove('selecionado'));
            // Adiciona seleção atual
            this.classList.add('selecionado');
            
            // Aqui você pode adicionar lógica para salvar a reação
            const reacao = this.textContent;
            console.log('Reação selecionada:', reacao);
        });
    });
    
    // Funcionalidade para curtir comentários
    const botoesReagir = document.querySelectorAll('.btn-reagir');
    botoesReagir.forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.toggle('curtido');
            const icon = this.querySelector('img');
            if (this.classList.contains('curtido')) {
                // Trocar para ícone preenchido se disponível
                icon.src = icon.src.replace('heart-outline', 'heart');
            } else {
                // Voltar para ícone outline
                icon.src = icon.src.replace('heart.svg', 'heart-outline.svg');
            }
        });
    });
    
    // Funcionalidade para favoritar livro
    const btnFavoritar = document.querySelector('.btn-acao[title="Favoritar"]');
    if (btnFavoritar) {
        btnFavoritar.addEventListener('click', function() {
            this.classList.toggle('favoritado');
            const icon = this.querySelector('img');
            if (this.classList.contains('favoritado')) {
                // Trocar para ícone preenchido se disponível
                icon.src = icon.src.replace('bookmark-outline', 'bookmark');
                console.log('Livro favoritado');
            } else {
                // Voltar para ícone outline
                icon.src = icon.src.replace('bookmark.svg', 'bookmark-outline.svg');
                console.log('Livro removido dos favoritos');
            }
        });
    }
    
    // Funcionalidade para compartilhar
    const btnCompartilhar = document.querySelector('.btn-acao[title="Compartilhar"]');
    if (btnCompartilhar) {
        btnCompartilhar.addEventListener('click', function() {
            // Implementar funcionalidade de compartilhamento
            if (navigator.share) {
                navigator.share({
                    title: document.querySelector('.livro-titulo').textContent,
                    text: 'Confira este livro incrível!',
                    url: window.location.href
                });
            } else {
                // Fallback para navegadores que não suportam Web Share API
                navigator.clipboard.writeText(window.location.href).then(() => {
                    alert('Link copiado para a área de transferência!');
                });
            }
        });
    }
    
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
});

// Função para adicionar comentário dinamicamente
function adicionarComentario(comentario) {
    const comentariosLista = document.querySelector('.comentarios-lista');
    if (!comentariosLista) return;
    
    const novoComentarioHTML = `
        <div class="comentario">
            <div class="usuario-avatar">
                <img src="static/imagens/usuarios/${comentario.usuario.avatar}" alt="${comentario.usuario.nome}" class="avatar-pequeno">
            </div>
            <div class="comentario-conteudo">
                <div class="comentario-cabecalho">
                    <div class="usuario-nome">${comentario.usuario.nome}</div>
                    <div class="comentario-opcoes">
                        <button class="btn-opcoes" title="Mais opções">
                            <img src="static/css/icones/ellipsis-vertical-outline.svg" class="svg-sm">
                        </button>
                    </div>
                </div>
                <div class="comentario-texto">
                    ${comentario.texto}
                </div>
                <div class="comentario-acoes">
                    <button class="btn-reagir" title="Curtir">
                        <img src="static/icones/heart-outline.svg" class="svg-sm">
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Adicionar no início da lista
    comentariosLista.insertAdjacentHTML('afterbegin', novoComentarioHTML);
    
    // Adicionar event listeners aos novos botões
    const novoComentarioElement = comentariosLista.firstElementChild;
    const btnReagir = novoComentarioElement.querySelector('.btn-reagir');
    if (btnReagir) {
        btnReagir.addEventListener('click', function() {
            this.classList.toggle('curtido');
            const icon = this.querySelector('img');
            if (this.classList.contains('curtido')) {
                icon.src = icon.src.replace('heart-outline', 'heart');
            } else {
                icon.src = icon.src.replace('heart.svg', 'heart-outline.svg');
            }
        });
    }
}

// Função para animação suave ao rolar para comentários
function rolarParaComentarios() {
    const comentariosSecao = document.querySelector('.comentarios-secao');
    if (comentariosSecao) {
        comentariosSecao.scrollIntoView({ behavior: 'smooth' });
    }
}
