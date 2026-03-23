"""
Script 2: Povoa a ontologia com os doentes a partir do JSON.

Entrada:  med_tratamentos.ttl
          doentes.json

Saída:    med_doentes.ttl
"""

import json
import re
from rdflib import Graph, Namespace, RDF, Literal

BASE   = "http://www.example.org/disease-ontology#"
NS     = Namespace(BASE)

def uri_safe(name: str) -> str:
    return re.sub(r'[\s]+', '_', name.strip()).replace("(", "").replace(")", "")

# ── carregar ontologia com doenças + tratamentos ─────────────────────────────
g = Graph()
g.parse("med_tratamentos.ttl", format="turtle")
g.bind("", NS)
print(f"Ontologia carregada: {len(g)} triplos")

# ── doentes.json ─────────────────────────────────────────────────────────────
print("\nA processar doentes.json...")
with open("doentes.json", encoding='utf-8') as f:
    doentes = json.load(f)

for i, doente in enumerate(doentes, start=1):
    nome     = doente["nome"].strip()
    sintomas = doente["sintomas"]

    patient_uri = NS[f"Patient_{i:04d}"]

    g.add((patient_uri, RDF.type, NS.Patient))
    g.add((patient_uri, NS.name, Literal(nome)))

    for sym_raw in sintomas:
        sym_uri = NS[uri_safe(sym_raw)]

        # criar sintoma se ainda não existir na ontologia
        if (sym_uri, RDF.type, NS.Symptom) not in g:
            g.add((sym_uri, RDF.type, NS.Symptom))
            g.add((sym_uri, NS.name, Literal(sym_raw.strip())))

        g.add((patient_uri, NS.exhibitsSymptom, sym_uri))

# ── gravar ───────────────────────────────────────────────────────────────────
g.serialize(destination="med_doentes.ttl", format="turtle")
print(f"✓ Gravado: med_doentes.ttl  ({len(g)} triplos)")
print(f"  Doentes adicionados: {len(doentes)}")