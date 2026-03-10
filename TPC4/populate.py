import json
from rdflib import Graph, Namespace, RDF, OWL, Literal, URIRef

BASE_URI = "http://rpcw.di.uminho.pt/2026/biblioteca_temporal/"
BT = Namespace(BASE_URI)

g = Graph()
g.parse("biblioteca_temporal.ttl", format="turtle")

with open("dataset_temporal_100.json", encoding="utf-8") as f:
    bd1 = json.load(f)

with open("dataset_temporal_v2_100.json", encoding="utf-8") as f:
    bd2 = json.load(f)

bd = bd1 + bd2

TIPO_CLASSE = {
    "LinhaOriginal":    "LinhaOriginal",
    "LinhaAlternativa": "LinhaAlternativa",
    "Biblioteca":       "Biblioteca",
    "Bibliotecario":    "Bibliotecario",
    "Autor":            "Autor",
    "Leitor":           "Leitor",
    "EventoHistorico":  "EventoHistorico",
    "EventoFuturo":     "EventoFuturo",
    "LivroHistorico":   "LivroHistorico",
    "LivroFiccional":   "LivroFiccional",
    "LivroParadoxal":   "LivroParadoxal",
}

for r in bd:
    owl_class = TIPO_CLASSE.get(r["tipo"], r["tipo"])
    ind = BT[r["id"]]

    g.add((ind, RDF.type, OWL.NamedIndividual))
    g.add((ind, RDF.type, BT[owl_class]))

    if "nome" in r:
        g.add((ind, BT.nome, Literal(r["nome"])))

    if "trabalhaEm" in r:
        g.add((ind, BT.trabalhaEm, BT[r["trabalhaEm"]]))

    if "pertenceA" in r:
        g.add((ind, BT.pertencemA, BT[r["pertenceA"]]))

    if "escritoPor" in r:
        g.add((ind, BT.saoEscritosPor, BT[r["escritoPor"]]))

    if "refereEvento" in r:
        g.add((ind, BT.refere, BT[r["refereEvento"]]))

    if "existeEm" in r:
        linhas = r["existeEm"] if isinstance(r["existeEm"], list) else [r["existeEm"]]
        for linha in linhas:
            g.add((ind, BT.existemEm, BT[linha]))

g.serialize("biblioteca_temporal_populated.ttl", format="turtle")

print("✓ biblioteca_temporal_populated.ttl gerado com sucesso")