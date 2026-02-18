# Ontologia de Cinema

## Metainformação
- **Título:** Ontologia de Cinema
- **Data:** 2026-02-09
- **Autor:**
  - **Id:** PG60273
  - **Nome:** João Miguel Mendes Moura

## Resumo

Este trabalho consiste na criação de uma **ontologia OWL** que modela o domínio do cinema, representando filmes, pessoas envolvidas na sua produção, géneros, línguas e países de origem.

A ontologia define **18 classes**, incluindo classes base como **Pessoa**, **Filme**, **Género**, **Lingua**, **Pais**, **Personagem** e **Obra** (com subclasses **Argumento**, **Livro** e **PecaMusical**). Foram também definidas classes derivadas com restrições OWL: **Ator** (pessoa que atuou num filme), **AtorFeminino** e **AtorMasculino** (inferidos pelo sexo), **Escritor** (pessoa que escreveu um argumento ou livro), **Realizador** (pessoa que realizou um filme) e **Músico** (pessoa que compôs uma peça musical). Existem ainda subclasses de Filme baseadas no género: **FilmesAventura**, **FilmesDramaticos**, **FilmesInfantis**, **FilmesRomanticos** e **FilmesThriller**.

Foram definidas **15 object properties**, organizadas em pares inversos: *atuou/temAtor*, *compos/foiComposta*, *escreveu/foiEscrito*, *realizou/foiRealizado* e *representa/ePersonagem*. As restantes propriedades de objeto associam filmes aos seus atributos: *temArgumento*, *temGenero*, *temLingua*, *temPaisOrigem* e *temPecaMusical*. A propriedade *realizou* é funcional (cada realizador realiza um filme). Existem também **4 data properties**: *F_data*, *F_duracao*, *F_titulo* e *temSexo*.

A ontologia instancia **40 indivíduos**: 13 pessoas (atores, realizadores e escritores dos filmes Fight Club, Twilight e Madagascar 2), 2 atores com personagens (Ben Stiller e Chris Rock), 3 filmes, 2 argumentos, 9 géneros, 3 línguas, 4 países e 4 personagens (Alex, Gloria, Marty e Melman).

## Lista de resultados

| Ficheiro | Descrição |
|----------|-----------|
| [cinema.ttl](./cinema.ttl) | Ontologia de cinema em formato Turtle com classes, propriedades e indivíduos |