from flask import Flask, render_template
from mquery import exec_query
from datetime import datetime


app = Flask(__name__)

data_hora_local = datetime.now()
data_iso = data_hora_local.strftime('%Y-%m-%dT%H:%M:%S')

@app.route("/")
def index():
    q = """
        PREFIX : <http://example.org/biblioteca-temporal#>
        select ?livroID ?titulo ?tipoID ?nomeAutor ?pais where {   
            ?livro a ?tipoLivro .
            FILTER(?tipoLivro in (:LivroHistorico, :LivroFiccional, :LivroParadoxal))
            optional {?livro :titulo ?titulo .}
            ?livro :escritoPor/:nome ?nomeAutor .
            ?livro :escritoPor/:paisOrigem ?pais .
            BIND(STRAFTER(STR(?livro), "#") AS ?livroID)
            BIND(STRAFTER(STR(?tipoLivro), "#") AS ?tipoID)
        }
        ORDER BY ?titulo
    """

    res = exec_query(q)
    livros = []
    for livro in res["results"]["bindings"]:
        l = {
            "id": livro["livroID"]["value"],
            "tipo": livro["tipoID"]["value"],
            "autor": livro["nomeAutor"]["value"],
            "pais": livro["pais"]["value"]
        }
        if "titulo" in livro:
            l["titulo"] = livro["titulo"]["value"]
        livros.append(l)

    return render_template("lista.html", livros = livros)

@app.route("/livro/<id_livro>")
def rota_detalhe(id_livro):
    q = f"""
    PREFIX : <http://example.org/biblioteca-temporal#>
    select ?titulo ?tituloURI ?autor ?linha ?eventoID ?nomEvento ?descricao where {{
        optional {{:{id_livro} :titulo ?titulo.}}
        :{id_livro} a ?tituloURI .
        filter(?tituloURI in (:LivroHistorico, :LivroFiccional, :LivroParadoxal)) .
        :{id_livro} :escritoPor/:nome ?autor .
        :{id_livro} :existeEm ?linha .
        optional {{
            :{id_livro} :refereEvento ?evento .
            ?evento :designacao ?nomEvento .
            ?evento :descricao ?descricao .
            BIND(STRAFTER(STR(?evento), "#") AS ?eventoID)
        }}
    }}
    """
    res = exec_query(q)
    if res is None:
        return render_template("detalhe.html", l={})

    bindings = res["results"]["bindings"]
    if not bindings:
        return render_template("detalhe.html", l={})

    first = bindings[0]
    tipo_uri = first["tituloURI"]["value"]
    tipo_id = tipo_uri.split("#")[-1]

    color_map = {
        "LivroHistorico": "w3-blue",
        "LivroFiccional": "w3-purple",
        "LivroParadoxal": "w3-orange"
    }

    l = {
        "titulo": first.get("titulo", {}).get("value", id_livro),
        "tipo": tipo_id,
        "color": color_map.get(tipo_id, "w3-teal"),
        "autor": first["autor"]["value"],
        "linhas": list({b["linha"]["value"].split("#")[-1] for b in bindings if "linha" in b}),
        "eventos": []
    }

    vistos = set()
    for b in bindings:
        if "eventoID" in b:
            eid = b["eventoID"]["value"]
            if eid not in vistos:
                vistos.add(eid)
                l["eventos"].append({
                    "id": eid,
                    "nome": b.get("nomEvento", {}).get("value", ""),
                    "desc": b.get("descricao", {}).get("value", "")
                })

    return render_template("detalhe.html", l=l)

@app.route("/eventos")
def rota_eventos():
    q = """
        PREFIX : <http://example.org/biblioteca-temporal#>
        SELECT ?eventoID ?nome ?descricao WHERE {
            ?evento a :Evento .
            ?evento :designacao ?nome .
            ?evento :descricao ?descricao .
            BIND(STRAFTER(STR(?evento), "#") AS ?eventoID)
        }
        ORDER BY ?nome
    """
    res = exec_query(q)
    eventos = []
    if res is None:
        return render_template("eventos.html", eventos=eventos)
 
    for ev in res["results"]["bindings"]:
        eventos.append({
            "id": ev["eventoID"]["value"],
            "nome": ev["nome"]["value"],
            "descricao": ev["descricao"]["value"]
        })
 
    return render_template("eventos.html", eventos=eventos)



if __name__ == "__main__":
    app.run(debug=True)