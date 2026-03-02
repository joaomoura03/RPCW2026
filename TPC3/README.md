# Polvo Filosófico GraphDB e SPARQL

## Metainformação
- **Título:** GraphDB e SPARQL da ontologia polvo filosófico
- **Data:** 2026-03-02
- **Autor:**
  - **Id:** PG60273
  - **Nome:** João Miguel Mendes Moura

## Quem foram os clientes?

```sparql
PREFIX : <http://example.org/polvo-filosofico#>

SELECT ?cliente WHERE {
  ?cliente a :Cliente .
}
```
**Resposta:** Ana, Bruno, Carla, Daniel, Eva, Schrodinger


### Quais os ingredientes necessários à confeção dos pratos?

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <http://example.org/polvo-filosofico#>

SELECT ?prato ?ingrediente WHERE {
  ?prato :temIngrediente ?ingrediente .
}
```
**Resposta:**

| Prato | Ingredientes |
|---|---|
| SaladaExistencial | Alface, Tomate |
| TofuMetafisico | Tofu, Cogumelos |
| BifeDeterminista | CarneVaca |
| PeixeDoLivreArbitrio | Peixe |
| PratoDoObservador | Cogumelos, Peixe |
| DilemaDoSer | Tofu, CarneVaca |
| EnsopadoCanibal | IngredientePolvo |
| PratoDoDia | IngredientePolvo |


### Há funcionários que também sejam clientes?

```sparql

PREFIX : <http://example.org/polvo-filosofico#>

SELECT ?pessoa WHERE {
  ?pessoa a :Funcionario .
  ?pessoa a :Cliente .
}
```

**Resposta:** Schrödinger