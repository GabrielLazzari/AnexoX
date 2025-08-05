
CREATE TABLE usuario(
	id integer NOT NULL,  -- Identificador único
	tipo int,  -- Tipo do usuário 0 leitor, 1 autor, 2 editora
	nome varchar(256) NOT NULL,  -- Nome do usuário
	senha varchar(256) NOT NULL,  -- Senha do usuário
	email varchar(100),  -- E-mail
	verificado boolean,  -- Se o usuário foi verificado pela plataforma
	cnpj varchar(14),  -- Cnpj da Editora
	PRIMARY KEY (id)
);

CREATE TABLE livro(
	id integer NOT NULL,  -- Identificador único
	isbn varchar(13),  -- Código do livro
	titulo varchar(1000) NOT NULL,  -- Título do livro
	idAutor integer NOT NULL,  -- Referência para o usuário autor
	idEditora integer NOT NULL,  -- Referência para usuário editora
	dataPublicacao timestamp,  -- Data de publicação
	descricao text,  -- Descrição
	PRIMARY KEY (id),
	FOREIGN KEY (idAutor) REFERENCES usuario (id),
	FOREIGN KEY (idEditora) REFERENCES usuario (id)
);

CREATE TABLE genero_literario(
	id integer NOT NULL,  -- Identificador único
	descricao varchar(100) NOT NULL,  -- Descrição do gênero
	PRIMARY KEY (id)
);

CREATE TABLE preferencia_literaria(
	id integer NOT NULL,  -- Identificador único
	idVinculo integer NOT NULL,  -- Referência para o usuário ou livro
	idGenero integer NOT NULL,  -- Referência ao gênero literário
	PRIMARY KEY (id),
	FOREIGN KEY (idVinculo) REFERENCES usuario (id),
	FOREIGN KEY (idVinculo) REFERENCES livro (id),
	FOREIGN KEY (idGenero) REFERENCES genero_literario (id)
);

CREATE TABLE livro_sugerido(
	id integer NOT NULL,  -- Identificador único
	idUsuario integer NOT NULL,  -- Referência para o usuário
	idLivro integer NOT NULL,  -- Referência para o livro
	dataAdicao timestamp,  -- Data de adicao
	PRIMARY KEY (id),
	FOREIGN KEY (idUsuario) REFERENCES usuario (id),
	FOREIGN KEY (idLivro) REFERENCES livro (id)
);

CREATE TABLE usuario_seguindo(
	id integer NOT NULL,  -- Identificador único
	idUsuario integer NOT NULL,  -- Referência para o usuário
	idUsuarioSeguindo integer NOT NULL,  -- Referência para o usuário seguindo
	dataVinculo timestamp,  -- Data de criação
	PRIMARY KEY (id),
	FOREIGN KEY (idUsuario) REFERENCES usuario (id),
	FOREIGN KEY (idUsuarioSeguindo) REFERENCES usuario (id)
);

CREATE TABLE usuario_seguidores(
	id integer NOT NULL,  -- Identificador único
	idUsuario integer NOT NULL,  -- Referência para o usuário
	idUsuarioSeguidor integer NOT NULL,  -- Referência para o usuário seguidor
	dataVinculo timestamp,  -- Data de criação
	PRIMARY KEY (id),
	FOREIGN KEY (idUsuario) REFERENCES usuario (id),
	FOREIGN KEY (idUsuarioSeguidor) REFERENCES usuario (id)
);

CREATE TABLE listalivro(
	id integer NOT NULL,  -- Identificador único
	nome varchar(100) NOT NULL,  -- Nome da lista
	idUsuario integer NOT NULL,  -- Referência para o usuário
	PRIMARY KEY (id),
	FOREIGN KEY (idUsuario) REFERENCES usuario (id)
);

CREATE TABLE listalivro_livro(
	id integer NOT NULL,  -- Identificador único
	idLivro integer NOT NULL,  -- Referência para o livro
	idListaLivro integer NOT NULL,  -- Referência para a listalivros
	PRIMARY KEY (id),
	FOREIGN KEY (idLivro) REFERENCES livro (id),
	FOREIGN KEY (idListalivros) REFERENCES listalivro (id)
);

CREATE TABLE publicacao(
	id integer NOT NULL,  -- Identificador único
	idUsuario integer NOT NULL,  -- Referência para o usuário
	dataPublicacao timestamp,  -- Data de publicação
	dataEdicao timestamp,  -- Data de edição
	titulo varchar(300) NOT NULL,  -- Título da publicação
	PRIMARY KEY (id),
	FOREIGN KEY (idUsuario) REFERENCES usuario (id)
);

CREATE TABLE publicacao_conteudo(
	id integer NOT NULL,  -- Identificador único
	idPublicacao integer NOT NULL, -- Referência para a publicação
	tipo integer,  -- Tipo do conteúdo: 0 texto, 1 imagem, 2 vídeo
	ordem integer,  -- A ordem em que vai aparecer o conteúdo
	conteudo text NOT NULL,  -- Conteúdo da publicação
	PRIMARY KEY (id),
	FOREIGN KEY (idPublicacao) REFERENCES publicacao (id)
);

-- O comentário é uma publicacao (com img, texto, reacao, etc) vinculado em outra publicacao/livro
CREATE TABLE comentario(
	id integer NOT NULL,  -- Identificador único
	idConteudo integer NOT NULL,  -- Referência para o conteúdo
	idUsuario integer NOT NULL,  -- Referência para o usuário
	idVinculo integer NOT NULL, -- Referência para o livro ou publicação
	PRIMARY KEY (id),
	FOREIGN KEY (idConteudo) REFERENCES publicacao (id),
	FOREIGN KEY (idUsuarioComentou) REFERENCES usuario (id),
	FOREIGN KEY (idVinculo) REFERENCES livro (id),
	FOREIGN KEY (idVinculo) REFERENCES publicacao (id)
);

CREATE TABLE tipo_reacao(
	id integer NOT NULL,  -- Identificador único
	descricao varchar(100) NOT NULL,  -- Descrição da reação
	PRIMARY KEY (id)
);

CREATE TABLE reacao(
	id integer NOT NULL,  -- Identificador único
	idUsuarioReagiu integer NOT NULL,  -- Referência para o usuário
	idVinculo integer NOT NULL,  -- Referência para a publicação ou comentário
	idTipoReacao integer NOT NULL,  -- Tipo da reação
	PRIMARY KEY (id),
	FOREIGN KEY (idUsuarioReagiu) REFERENCES usuario (id),
	FOREIGN KEY (idVinculo) REFERENCES publicacao (id),
	FOREIGN KEY (idTipoReacao) REFERENCES tipo_reacao (id)
);

CREATE TABLE notificacao(
	id integer NOT NULL,  -- Identificador único
	idUsuario integer NOT NULL,  -- Referência para o usuário
	tipo integer NOT NULL,  -- Tipo da notificação: 0 sugestão de livro, 1 convite de chat
	lido boolean,  -- Se a notificação foi lida pelo usuário
	conteudo text NOT NULL,  -- Conteúdo a ser visualizado
	PRIMARY KEY (id),
	FOREIGN KEY (idUsuario) REFERENCES usuario (id)
);


select * from usuario u ;



