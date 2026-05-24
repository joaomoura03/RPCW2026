# Arquivo da Música Portuguesa
## Relatório — RPCW 2026

---

## Introdução

O projeto consiste numa aplicação web para explorar e aumentar uma base de conhecimento sobre música portuguesa. A escolha do tema não foi arbitrária, pesquisámos e não encontrámos nenhum recurso público estruturado neste domínio: não existe nenhuma ontologia OWL sobre música portuguesa, nenhum dataset RDF com artistas, álbuns e relações entre eles, nem nenhuma aplicação semântica do género disponível online. Isso tornava o tema simultaneamente desafiante e mais interessante porque tivemos de construir tudo de raiz.

Para além da ontologia, tivemos de criar os dados manualmente. Todos os ficheiros de dataset (artistas, bandas, álbuns, músicas, prémios, concertos, influências) foram escritos totalmente do zero, pelo que não estão completos.

O domínio escolhido é também rico em relações interessantes do ponto de vista semântico: um artista pode ter sido influenciado por outro, uma música pode ter sido composta por uma pessoa e interpretada por outra diferente, uma banda tem membros que também têm carreiras a solo. Este tipo de relações complexas é exatamente onde as tecnologias de Web Semântica brilham face a uma base de dados relacional comum.

O sistema tem três partes que trabalham juntas: uma **ontologia OWL** que define o modelo do conhecimento, os **datasets** que povoam essa ontologia com dados reais, e uma **aplicação Flask** que permite navegar, consultar e adicionar novo conhecimento.

---

## O que é e para que serve o nosso Arquivo
Este projeto consiste num Arquivo da Música Portuguesa, uma plataforma que funciona como uma enciclopédia digital sobre a nossa  história musical.

### Para que vamos usá-lo?
O principal objetivo é reunir e organizar, num só lugar, toda a informação que hoje está espalhada. Em vez de termos dados soltos, criamos uma rede onde tudo está ligado: um artista está ligado aos seus álbuns, que por sua vez ligam às músicas, aos concertos e aos prémios que ganhou.

### A que perguntas responde?
Queremos que qualquer pessoa possa fazer perguntas ao sistema e obter respostas rápidas, como por exemplo:
- "Quais são os artistas que influenciaram o Zeca Afonso?"
- "Que prémios é que uma banda ganhou e em que anos?"
- "Quem participou (como convidado) numa determinada música?"
- "Que artistas pertencem a um género musical específico?"

### Quem vai usar e cuidar disto?
A sustentabilidade e curadoria do arquivo estariam a cargo de uma entidade cultural de referência (ex: Museu da Música ou Ministério da Cultura), assegurando a validação científica dos dados e a sua preservação ao longo do tempo.

---

## A Ontologia

### O que modelámos

O domínio cobre tudo o que rodeia a música portuguesa: os artistas e bandas, os álbuns que lançaram, as músicas que contêm, as editoras a que pertencem, os prémios que ganharam, os concertos que deram, e as relações entre eles: quem influenciou quem, quem colaborou com quem, quem são os membros de uma banda.

As classes principais são:

- **Artista** — superclasse, com duas subclasses disjuntas: `ArtistaSolo` e `Banda`. O facto de serem disjuntas significa que o reasoner deteta automaticamente inconsistências se algo for classificado nas duas ao mesmo tempo.
- **Album**, **Musica** — a discografia.
- **Editora** — a label discográfica do artista.
- **Premio**, **Concerto**, **Tour** — eventos e reconhecimentos.
- **Genero** — uma superclasse com subclasses que funcionam como vocabulário controlado: `Fado`, `Rock`, `Pop`, `HipHop`, `Indie`, `Jazz`, `Metal`, `Blues`, `Folk`, `Pimba`, entre outros. Usar subclasses em vez de strings livres garante consistência, não é possível escrever "rock" e "Rock" como coisas diferentes.

### As relações mais interessantes

A maior parte das propriedades é direta, mas algumas merecem destaque:

**`influenciadoPor` é transitiva.** Declarou-se esta propriedade como `owl:TransitiveProperty`. Isso significa que se afirmarmos que Carminho foi influenciada por Amália Rodrigues, e que Ana Moura também foi influenciada por Amália, o reasoner sabe isso diretamente. Mas se, por exemplo, alguém da nova geração for influenciado por Mariza, e Mariza foi influenciada por Amália, o reasoner infere automaticamente a cadeia toda, sem precisarmos de afirmar explicitamente cada ligação transitiva.

```turtle
:influenciadoPor rdf:type owl:ObjectProperty , owl:TransitiveProperty ;
                 rdfs:domain :Artista ;
                 rdfs:range  :Artista .
```

**`contemMusica` é a inversa de `pertenceAoAlbum`.** Nos dados, sempre que "a música X pertence ao álbum Y" de seguida criamos uma propriedade inversa chamada `contemMusica`. O reasoner materializa automaticamente o sentido contrário ("o álbum Y contém a música X") sem precisarmos de escrever esse triplo. Isto é útil porque a aplicação pode perguntar "que músicas tem este álbum?" sem que o dataset precise de ter essa informação explicitamente.

```turtle
:contemMusica rdf:type owl:ObjectProperty ;
              owl:inverseOf :pertenceAoAlbum .
```

**`pertenceAoGenero` não tem domínio fixo.** A maioria das propriedades tem domínio declarado (por exemplo, `lancouAlbum` só se aplica a artistas). Mas géneros aplicam-se a artistas, a álbuns *e* a músicas. Em vez de criar três propriedades separadas, foi deixada sem domínio fixo.

---

##  O Dataset

### Como foi construído

Como não existia nenhuma fonte de dados estruturada sobre música portuguesa que pudéssemos reutilizar, o dataset foi inteiramente construído do zero. Nomeadamente: anos de nascimento, géneros associados, editoras, relações de influência entre artistas, membros de bandas, e muito mais.

Os dados estão distribuídos por ficheiros JSON separados por entidade: `artistas.json`, `bandas.json`, `albuns.json`, `musicas.json`, etc. Esta separação facilita a manutenção e permite adicionar ou corrigir dados numa área sem tocar nas outras.

O script `populate.py` lê todos estes ficheiros e gera um único ficheiro Turtle (`musica_portuguesa.ttl`) que combina a ontologia base com todos os indivíduos. O resultado final tem cerca de 76 artistas solo, 35 bandas, 54 álbuns, 72 músicas, 10 prémios e 10 concertos históricos.

### Como um artista fica representado em Turtle

Aqui está um exemplo de como o Zeca Afonso fica representado após o processo de geração:

```turtle
:zeca_afonso a :ArtistaSolo ;
    :nome "Zeca Afonso" ;
    :anoNascimento 1929 ;
    :pertenceAEditora :edicoes_orfeu ;
    :biografia "O mais importante cantor de intervenção português, autor de Grândola Vila Morena." ;
    :pertenceAoGenero :Intervencao ;
    :pertenceAoGenero :Folk .

:zeca_afonso :atuouEm :zeca_coliseu_1983 .

:sergio_godinho :influenciadoPor :zeca_afonso .
:adriano_correia :influenciadoPor :zeca_afonso .
```

Note-se que as relações de influência são escritas "do ponto de vista" do influenciado ("Sérgio Godinho foi influenciado por Zeca Afonso") e não ao contrário. Isto é uma escolha de design: qualquer das direções funcionaria, mas esta é mais natural para perguntar "quem influenciou este artista?".

---

## A Aplicação Web

### Arquitetura geral

A aplicação usa Flask como framework web e comunica com o GraphDB através de SPARQL. Existe um módulo auxiliar (`query.py`) que abstrai toda a comunicação com o triplestore, as rotas Flask chamam funções deste módulo e recebem os resultados já em formato Python, sem lidar diretamente com os detalhes do protocolo SPARQL.

```python
def exec_query(query):
    sparql = SPARQLWrapper(GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(30)
    try:
        return sparql.query().convert()
    except QueryBadFormed as e:
        print(f"[SPARQL] Query mal-formada: {e}")
        return None
    except Exception as e:
        # detecta erros de ligação e imprime mensagem útil
        ...
        return None
```

O timeout de 30 segundos e o tratamento de diversos erros (query mal-formada vs. GraphDB em baixo) tornam a aplicação mais robusta e mais fácil de depurar.

### O que é possível fazer

**Navegar e consultar** é o caso de uso principal. A página inicial lista todos os artistas e bandas com filtros por nome, género, tipo (solo ou banda), editora e intervalo de anos. Cada artista tem uma página de perfil que agrega toda a informação: álbuns, músicas, prémios, concertos, membros (no caso de bandas), e a sua genealogia de influências, quem o influenciou e quem ele influenciou.

Há também vistas temáticas: uma linha do tempo cronológica que agrega nascimentos, formações de bandas, lançamentos de álbuns e prémios; uma página de conexões que mostra o grafo de influências e os feats entre artistas; estatísticas com gráficos de distribuição por género e editora; e uma pesquisa global que cobre artistas, álbuns e músicas ao mesmo tempo.

**Inserir novo conhecimento** é possível adicionar diretamente pela interface, sem acesso ao triplestore. A aplicação tem formulários para adicionar artistas, álbuns, músicas, géneros, prémios e concertos. Por baixo, cada submissão gera uma query `INSERT DATA` em SPARQL:

```python
triplos = [
    f':{new_id} a :{tipo} .',
    f':{new_id} :nome "{esc_lit(nome)}"^^xsd:string .',
]
if ano and ano.isdigit():
    triplos.append(f':{new_id} {prop_ano} "{int(ano)}"^^xsd:integer .')
for gen in generos:
    triplos.append(f':{new_id} :pertenceAoGenero :{gen} .')

exec_update(PREFIX + "INSERT DATA {\n  " + "\n  ".join(triplos) + "\n}")
```

Antes de inserir, o código verifica se o ID gerado já existe no triplestore (função `id_unico`) e sanitiza todos os inputs para evitar injeção em queries SPARQL (funções `esc_lit` e `esc_id`).

**Remoção de dados** uma vez que a aplicação disponibiliza funcionalidades de remoção para as entidades: artistas, álbuns e músicas. Dada a natureza de um grafo,implementámos uma função, `remover_individuo`, que assegura a integridade:

```python
def remover_individuo(id_individuo):
    if not re.match(r'^\w+$', id_individuo):
        return False
    q1 = PREFIX + f"DELETE WHERE {{ :{id_individuo} ?p ?o }}"
    q2 = PREFIX + f"DELETE WHERE {{ ?s ?p :{id_individuo} }}"
    return exec_update(q1) and exec_update(q2)
```

### Um exemplo de query da aplicação

Quando se carrega a página de um artista, a aplicação faz várias queries em paralelo para agregar toda a informação. Uma delas busca as influências:

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/music-ontology/>

SELECT ?id ?nome WHERE {
    ?a :influenciadoPor :amalia_rodrigues .
    ?a :nome ?nome .
    BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?id)
}
```

Graças à transitividade declarada na ontologia e ao reasoner do GraphDB, esta query devolve não só os artistas que foram diretamente influenciados por Amália, mas também os que foram influenciados por esses artistas, toda a cadeia, sem necessidade de recursão explícita na query.

---

## O papel do Reasoner

Um ponto importante a sublinhar é que a aplicação depende do reasoner do GraphDB estar ativo. Sem ele:

- A propriedade `contemMusica` não existe na prática (não é materializada), por isso a listagem de músicas de um álbum fica vazia em certas queries que a usam pelo sentido inverso.
- A transitividade de `influenciadoPor` não é inferida, por isso o grafo de influências fica incompleto.
- A disjunção entre `ArtistaSolo` e `Banda` não é verificada automaticamente.


---

## Conclusão

A escolha de Web Semântica para este domínio revelou-se acertada. Num modelo relacional tradicional, modelar algo como "influências transitivas" implicaria escrever queries recursivas ou guardar cálculos pré-computados. Aqui, basta declarar a propriedade como transitiva e o reasoner trata do resto.

Ainda com algumas dificuldades no que toca à base de dados para o povoamento da ontologia, conseguimos ter datasets bastante completos e com vários casos de estudo interessantes.

Da mesma forma, a capacidade de fazer perguntas como "quem escreveu letras mas nunca interpretou músicas?" ou "pares de artistas que partilham a mesma editora?" em SPARQL, com uma sintaxe declarativa, é muito mais expressiva do que o equivalente em SQL, especialmente quando as relações são complexas e cruzadas.

O projeto cumpre os três requisitos do enunciado: a ontologia está especificada e justificada, a aplicação web permite navegar e consultar a base de conhecimento e é possível aumentar essa base de conhecimento diretamente pela interface.

---

*Projeto RPCW 2026 — Universidade do Minho*