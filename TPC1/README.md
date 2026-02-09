# TPC1: Ontologia da História

## Metainformação
- **Título:** TPC1 - Ontologia da História
- **Data:** 09/02/2026
- **Autor:**
  - **Id:** PG60273
  - **Nome:** João Miguel Mendes Moura

## Resumo

Este trabalho consiste na criação de uma **ontologia OWL** baseada na história do estudante Eduardo e os seus amigos na Universidade do Minho.

A ontologia modela o domínio do ensino de línguas através de nove classes: **Pessoa** (com subclasses **Estudante** e **Professor**), **Universidade**, **Escola**, **CentroLinguas**, **Curso**, **Lingua** e **Cidade**. Foram definidas quatro propriedades de dados (*nome*, *temIdade*, *nacionalidade*, *diaDaSemana*) e treze propriedades de objetos que estabelecem relações semânticas entre indivíduos. As principais relações incluem *falaLingua* e *aprendeLingua* (distinguem línguas já faladas de línguas em aprendizagem), *frequenta* e *leciona* (conectam pessoas a cursos), *estudaEm* e *docenteDe* (associam pessoas a instituições), *oriundoDe* (indica proveniência geográfica), e as propriedades simétricas *amigoDe* e *parceiroLinguisticoDe*.

A ontologia instancia **14 indivíduos**: cinco pessoas (Eduardo, Ana, Carlos, Hanna e Helmut Ratz), quatro línguas (Português, Espanhol, Inglês e Alemão), dois cursos (Alemão e Biotecnologia), duas instituições (Universidade do Minho, Escola de Letras Artes e Ciências Humanas), um centro de línguas e uma cidade (Porto).

A informação representada permite responder às seguintes questões:

1. **Quantas línguas fala o Eduardo?** — 4 (Português, Espanhol, Inglês + Alemão em aprendizagem)
2. **Quem se inscreveu no curso de alemão?** — Eduardo, Carlos e Ana
3. **Quantos indivíduos existem na ontologia?** — 14
4. **Quem é Hanna?** — Uma estudante alemã de biotecnologia na Universidade do Minho, parceira linguística do Eduardo

## Lista de resultados

| Ficheiro | Descrição |
|----------|-----------|
| [historia.ttl](./historia.ttl) | Ontologia completa da história em formato Turtle |