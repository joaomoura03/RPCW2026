# Questões SPARQL — Ontologia da Biblioteca Temporal

## Metainformação
- **Título:** Desenvolvimento, povoamento e exploração da ontologia Biblioteca Temporal
- **Data:** 2026-03-9
- **Autor:**
  - **Id:** PG60273
  - **Nome:** João Miguel Mendes Moura

## Resumo

Como base foi-nos dado tinhamos de desenvolver uma ontologia e depois povoa-la com os dois datasets que nos foram fornecidos. Isto foi feito através da função populate.py. Depois disto foi-nos pedido para fazer queries em SPARQL sobre a ontologia.


## Resultados


| Ficheiro | Descrição |
|---|---|
| `biblioteca_temporal.ttl` | Ontologia base em Turtle |
| `dataset_temporal_100.json` | Primeiro dataset de indivíduos |
| `dataset_temporal_v2_100.json` | Segundo dataset de indivíduos |
| `populate.py` | Script de povoamento com rdflib |


### Questão 1 — Livros por linha temporal

Liste todos os livros que existem na **linha temporal original** (`LinhaOriginal`).

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?livro ?linha
WHERE {
    ?livro a :Livro ;
           :existemEm ?linha .
    ?linha a :LinhaOriginal .
}
ORDER BY ?livro
```

---

### Questão 2 — Livros em múltiplas linhas temporais

Identifique os livros que existem em **mais do que uma linha temporal**.

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?livro (COUNT(?linha) AS ?numLinhas)
WHERE {
    ?livro :existemEm ?linha .
}
GROUP BY ?livro
HAVING (COUNT(?linha) > 1)
ORDER BY DESC(?numLinhas)
```

---

### Questão 3 — Livros paradoxais

Liste todos os livros classificados como `LivroParadoxal`.

``` sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?livro
WHERE {
    ?livro a :LivroParadoxal .
}
ORDER BY ?livro
```

---

### Questão 4 — Livros históricos e eventos

Para cada `LivroHistorico`, indique os **eventos históricos** que esse livro refere.

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?livro ?evento
WHERE {
    ?livro a :LivroHistorico ;
           :refere ?evento .
    ?evento a :EventoHistorico .
}
ORDER BY ?livro
```

---

### Questão 5 — Inconsistências semânticas

Identifique livros classificados como `LivroHistorico` que referem **eventos futuros**.

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?livro ?evento
WHERE {
    ?livro a :LivroHistorico ;
           :refere ?evento .
    ?evento a :EventoFuturo .
}
ORDER BY ?livro
```
---

### Questão 6 — Autores mais prolíficos

Liste os autores e o **número de livros** que escreveram, ordenando o resultado por número de livros em
ordem decrescente

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?autor (COUNT(?livro) AS ?numLivros)
WHERE {
    ?autor a :Autor .
    ?livro :saoEscritosPor ?autor .
}
GROUP BY ?autor
ORDER BY DESC(?numLivros)
```

---

### Questão 7 — Autores de livros paradoxais

Identifique os autores que escreveram **pelo menos um livro paradoxal**.

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?autor
WHERE {
    ?livro a :LivroParadoxal ;
           :saoEscritosPor ?autor .
    ?autor a :Autor .
}
ORDER BY ?autor
```

---

### Questão 8 — Livros em linhas alternativas

Liste todos os livros que existem em **pelo menos uma linha temporal alternativa** (`LinhaAlternativa`)

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?livro ?linha
WHERE {
    ?livro :existemEm ?linha .
    ?linha a :LinhaAlternativa .
}
ORDER BY ?livro
```

---

### Questão 9 — Bibliotecários

Indique todos os bibliotecários e a **biblioteca onde trabalham**.

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?bibliotecario ?biblioteca
WHERE {
    ?bibliotecario a :Bibliotecario ;
                   :trabalhaEm ?biblioteca .
    ?biblioteca a :Biblioteca .
}
ORDER BY ?bibliotecario
```

---

### Questão 10 — Livros escritos por Cronos

Liste todos os livros escritos por **Cronos** e indique **em que linhas temporais** esses livros existem.

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?livro ?linha
WHERE {
    ?livro :saoEscritosPor :Cronos ;
           :existemEm ?linha .
}
ORDER BY ?livro
```

---

### Questões Bónus (opcionais)


#### Identifique livros que **não referem nenhum evento**.

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?livro (COUNT(?evt) AS ?total)
WHERE {
    OPTIONAL { ?livro :refere ?evt }
    ?livro a :Livro .
}
GROUP BY ?livro
HAVING (?total = 0)
ORDER BY ?livro
```

---

#### Verifique se existe algum livro **sem linha temporal associada**.

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?livro (COUNT(?lt) AS ?total)
WHERE {
    OPTIONAL { ?livro :existemEm ?lt }
    ?livro a :Livro .
}
GROUP BY ?livro
HAVING (?total = 0)
ORDER BY ?livro
```

---

#### Identifique autores que sejam também leitores (caso essa propriedade esteja modelada).

```sparql
PREFIX : <http://rpcw.di.uminho.pt/2026/biblioteca_temporal/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?pessoa
WHERE {
    ?pessoa a :Autor ;
            a :Leitor .
}
ORDER BY ?pessoa
```