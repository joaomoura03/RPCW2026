from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from query import exec_query, exec_update
import re

app = Flask(__name__)
app.secret_key = 'rpcw2026-musica-portuguesa'  # para flash messages

PREFIX = """
PREFIX : <http://rpcw.di.uminho.pt/2026/music-ontology/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
"""


def rows_of(result):
    """Extrai os bindings de um resultado SPARQL com defesa contra None."""
    if not result or "results" not in result:
        return []
    return result["results"].get("bindings", [])

def g(row, key, default=None):
    """Acesso seguro a valores de bindings."""
    return row[key]["value"] if key in row else default

def esc_lit(s):
    """Escapa uma string para ser usada num literal TTL (entre aspas)."""
    if s is None:
        return ""
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')

def esc_id(s):
    """Converte uma string num ID válido para URI (apenas letras, dígitos e _)."""
    if not s:
        return ""
    return re.sub(r'[^\w]', '_', s).strip('_')

def id_unico(base_id):
    if not base_id: return base_id
    q = PREFIX + f"SELECT ?s WHERE {{ :{base_id} ?p ?o }} LIMIT 1"
    res = exec_query(q)
    if not rows_of(res): return base_id
    i = 2
    while i < 100:
        candidate = f"{base_id}_{i}"
        q = PREFIX + f"SELECT ?s WHERE {{ :{candidate} ?p ?o }} LIMIT 1"
        res = exec_query(q)
        if not rows_of(res): return candidate
        i += 1
    return f"{base_id}_{i}"

def generos_list():
    q = PREFIX + """
        SELECT DISTINCT ?id WHERE {
            ?id rdfs:subClassOf* :Genero .
            FILTER(?id != :Genero)
        }
    """
    return sorted([
        {"id": g(r, "id").split('/')[-1], "nome": g(r, "id").split('/')[-1]}
        for r in rows_of(exec_query(q))
    ], key=lambda x: x["nome"])

def editoras_list():
    q = PREFIX + """
        SELECT ?id ?nome 
        WHERE { 
            ?e a :Editora ; 
                :nome ?nome . 
            BIND(STRAFTER(STR(?e), 'music-ontology/') AS ?id) 
        } 
        ORDER BY ?nome"""
    return [{"id": g(r,"id"), "nome": g(r,"nome")} for r in rows_of(exec_query(q))]



@app.route('/')
def index():
    busca         = request.args.get('q', '').strip()
    filtro_genero = request.args.get('genero', '').strip()
    filtro_tipo   = request.args.get('tipo', '').strip()
    filtro_editora= request.args.get('editora', '').strip()
    filtro_ano_de = request.args.get('ano_de', '').strip()
    filtro_ano_ate= request.args.get('ano_ate', '').strip()

    id_re = re.compile(r'^\w+$')
    if filtro_genero and not id_re.match(filtro_genero):
        filtro_genero = ''
    if filtro_editora and not id_re.match(filtro_editora):
        filtro_editora = ''

    filtros = []
    if busca:
        filtros.append(f'FILTER(CONTAINS(LCASE(?nome), LCASE("{esc_lit(busca)}")))')
    if filtro_genero:
        filtros.append(f'?artista :pertenceAoGenero :{filtro_genero} .')
    if filtro_editora:
        filtros.append(f'?artista :pertenceAEditora :{filtro_editora} .')

    if filtro_ano_de and filtro_ano_de.isdigit():
        filtros.append(
            f'OPTIONAL {{ ?artista :anoNascimento ?an_de_n }} '
            f'OPTIONAL {{ ?artista :anoFormacao   ?an_de_f }} '
            f'FILTER('
              f'(BOUND(?an_de_n) && ?an_de_n >= {filtro_ano_de}) || '
              f'(BOUND(?an_de_f) && ?an_de_f >= {filtro_ano_de})'
            f')'
        )
    if filtro_ano_ate and filtro_ano_ate.isdigit():
        filtros.append(
            f'OPTIONAL {{ ?artista :anoNascimento ?an_ate_n }} '
            f'OPTIONAL {{ ?artista :anoFormacao   ?an_ate_f }} '
            f'FILTER('
              f'(BOUND(?an_ate_n) && ?an_ate_n <= {filtro_ano_ate}) || '
              f'(BOUND(?an_ate_f) && ?an_ate_f <= {filtro_ano_ate})'
            f')'
        )

    if filtro_tipo == 'Solo':
        tipo_filter = '{ ?artista a :ArtistaSolo . BIND("Solo" AS ?tipo) }'
    elif filtro_tipo == 'Banda':
        tipo_filter = '{ ?artista a :Banda . BIND("Banda" AS ?tipo) }'
    else:
        tipo_filter = ('{ ?artista a :ArtistaSolo . BIND("Solo" AS ?tipo) }'
                       ' UNION { ?artista a :Banda . BIND("Banda" AS ?tipo) }')

    query = PREFIX + f"""
        SELECT DISTINCT ?artistaID ?nome ?tipo WHERE {{
            {tipo_filter}
            ?artista :nome ?nome .
            {''.join(filtros)}
            BIND(STRAFTER(STR(?artista), "music-ontology/") AS ?artistaID)
        }} ORDER BY ?nome
    """

    artistas = [
        {"id": g(r, "artistaID"), "nome": g(r, "nome"), "tipo": g(r, "tipo")}
        for r in rows_of(exec_query(query))
    ]

    q_stats = PREFIX + """
        SELECT
          (COUNT(DISTINCT ?solo)   AS ?nSolo)
          (COUNT(DISTINCT ?banda)  AS ?nBanda)
          (COUNT(DISTINCT ?album)  AS ?nAlbum)
          (COUNT(DISTINCT ?musica) AS ?nMusica)
          (COUNT(DISTINCT ?premio) AS ?nPremio)
          (COUNT(DISTINCT ?concerto) AS ?nConcerto)
        WHERE {
          { ?solo    a :ArtistaSolo }
          UNION { ?banda   a :Banda }
          UNION { ?album   a :Album }
          UNION { ?musica  a :Musica }
          UNION { ?premio  a :Premio }
          UNION { ?concerto a :Concerto }
        }
    """
    stats_rows = rows_of(exec_query(q_stats))
    stats = {}
    if stats_rows:
        r = stats_rows[0]
        stats = {
            "solos":    g(r, "nSolo",    "0"),
            "bandas":   g(r, "nBanda",   "0"),
            "albuns":   g(r, "nAlbum",   "0"),
            "musicas":  g(r, "nMusica",  "0"),
            "premios":  g(r, "nPremio",  "0"),
            "concertos":g(r, "nConcerto","0"),
        }

    return render_template(
        'lista.html',
        artistas=artistas,
        generos=generos_list(),
        generos_globais=generos_list(), 
        editoras=editoras_list(),
        busca=busca,
        filtro_genero=filtro_genero,
        filtro_tipo=filtro_tipo,
        filtro_editora=filtro_editora,
        filtro_ano_de=filtro_ano_de,
        filtro_ano_ate=filtro_ano_ate,
        stats=stats,
    )



@app.route('/artista/<id_artista>')
def detalhe_artista(id_artista):
    if not re.match(r'^\w+$', id_artista):
        return "ID de artista inválido", 400

    query_info = PREFIX + f"""
        SELECT ?nome ?tipo ?anoNasc ?anoForm ?editora ?editoraNome ?bio WHERE {{
            :{id_artista} :nome ?nome .
            OPTIONAL {{ :{id_artista} a :ArtistaSolo . BIND("Solo" AS ?tipo) }}
            OPTIONAL {{ :{id_artista} a :Banda    . BIND("Banda" AS ?tipo) }}
            OPTIONAL {{ :{id_artista} :anoNascimento ?anoNasc }}
            OPTIONAL {{ :{id_artista} :anoFormacao   ?anoForm }}
            OPTIONAL {{ :{id_artista} :pertenceAEditora ?editora .
                        ?editora :nome ?editoraNome }}
            OPTIONAL {{ :{id_artista} :biografia ?bio }}
        }} LIMIT 1
    """
    res = rows_of(exec_query(query_info))
    if not res:
        return "Artista não encontrado", 404

    row = res[0]

    q_generos   = PREFIX + f"SELECT ?nome WHERE {{ :{id_artista} :pertenceAoGenero ?g . BIND(STRAFTER(STR(?g), 'music-ontology/') AS ?nome) }}"
    q_membros   = PREFIX + f"SELECT ?id ?nome WHERE {{ :{id_artista} :temMembro ?m . ?m :nome ?nome . BIND(STRAFTER(STR(?m), 'music-ontology/') AS ?id) }}"
    q_bandas    = PREFIX + f"SELECT ?id ?nome WHERE {{ ?b :temMembro :{id_artista} . ?b :nome ?nome . BIND(STRAFTER(STR(?b), 'music-ontology/') AS ?id) }}"
    q_albuns    = PREFIX + f"SELECT ?id ?nome ?ano WHERE {{ :{id_artista} :lancouAlbum ?a . ?a :nome ?nome . OPTIONAL {{ ?a :anoLancamento ?ano }} BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?id) }} ORDER BY ?ano"
    q_musicas = PREFIX + f"""
        SELECT DISTINCT ?id ?nome ?album ?albumNome WHERE {{
            {{ 
                ?m :interpretadaPor :{id_artista} ; :nome ?nome . 
            }} UNION {{ 
                ?m :temColaboracao :{id_artista} ; :nome ?nome . 
            }}
            BIND(STRAFTER(STR(?m), "music-ontology/") AS ?id)
            OPTIONAL {{ 
                ?m :pertenceAoAlbum ?albumR . 
                ?albumR :nome ?albumNome . 
                BIND(STRAFTER(STR(?albumR), "music-ontology/") AS ?album) 
            }}
        }} ORDER BY ?albumNome ?nome
    """
    q_premios   = PREFIX + f"SELECT ?id ?nome ?cat ?org ?ano WHERE {{ :{id_artista} :recebeuPremio ?p . ?p :nome ?nome . OPTIONAL{{?p :categoria ?cat}} OPTIONAL{{?p :organizacao ?org}} OPTIONAL{{?p :anoPremio ?ano}} BIND(STRAFTER(STR(?p), 'music-ontology/') AS ?id) }} ORDER BY DESC(?ano)"
    q_concertos = PREFIX + f"SELECT ?id ?nome ?local ?data WHERE {{ :{id_artista} :atuouEm ?c . ?c :nome ?nome . OPTIONAL{{?c :local ?local}} OPTIONAL{{?c :data ?data}} BIND(STRAFTER(STR(?c), 'music-ontology/') AS ?id) }} ORDER BY DESC(?data)"
    q_influencias = PREFIX + f"SELECT ?id ?nome WHERE {{ :{id_artista} :influenciadoPor ?a . ?a :nome ?nome . BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?id) }}"
    q_influenciou = PREFIX + f"SELECT ?id ?nome WHERE {{ ?a :influenciadoPor :{id_artista} . ?a :nome ?nome . BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?id) }}"

    artista = {
        "id":         id_artista,
        "nome":       g(row, "nome"),
        "tipo":       g(row, "tipo", "Solo"),
        "anoNasc":    g(row, "anoNasc"),
        "anoForm":    g(row, "anoForm"),
        "editora":    g(row, "editoraNome"),
        "bio":        g(row, "bio"),
        "generos":    [{"nome": r["nome"]["value"]} for r in rows_of(exec_query(q_generos))],
        "membros":    [{"id": g(r,"id"), "nome": g(r,"nome")} for r in rows_of(exec_query(q_membros))],
        "bandas":     [{"id": g(r,"id"), "nome": g(r,"nome")} for r in rows_of(exec_query(q_bandas))],
        "albuns":     [{"id": g(r,"id"), "nome": g(r,"nome"), "ano": g(r,"ano")} for r in rows_of(exec_query(q_albuns))],
        "musicas":    [{"id": g(r,"id"), "nome": g(r,"nome"), "album": g(r,"album"), "albumNome": g(r,"albumNome")} for r in rows_of(exec_query(q_musicas))],
        "premios":    [{"id": g(r,"id"), "nome": g(r,"nome"), "cat": g(r,"cat"), "org": g(r,"org"), "ano": g(r,"ano")} for r in rows_of(exec_query(q_premios))],
        "concertos":  [{"id": g(r,"id"), "nome": g(r,"nome"), "local": g(r,"local"), "data": g(r,"data")} for r in rows_of(exec_query(q_concertos))],
        "influencias": [{"id": g(r,"id"), "nome": g(r,"nome")} for r in rows_of(exec_query(q_influencias))],
        "influenciou": [{"id": g(r,"id"), "nome": g(r,"nome")} for r in rows_of(exec_query(q_influenciou))],
    }

    query_artistas = PREFIX + "SELECT ?id ?nome WHERE { ?id a :Artista ; :nome ?nome . }"
    artistas = [ {'id': g(r, 'id').split('/')[-1], 'nome': g(r, 'nome')} for r in rows_of(exec_query(query_artistas)) ]
    return render_template('detalhe.html', artista=artista, generos_globais=generos_list(), todos_artistas=artistas)



@app.route('/album/<id_album>')
def detalhe_album(id_album):
    if not re.match(r'^\w+$', id_album):
        return "ID de álbum inválido", 400

    query_album = PREFIX + f"""
        SELECT ?nome ?ano ?artistaId ?artistaNome WHERE {{
            :{id_album} a :Album ; :nome ?nome .
            OPTIONAL {{ :{id_album} :anoLancamento ?ano }}
            OPTIONAL {{ ?artista :lancouAlbum :{id_album} ; :nome ?artistaNome .
                        BIND(STRAFTER(STR(?artista), "music-ontology/") AS ?artistaId) }}
        }} LIMIT 1
    """
    res = rows_of(exec_query(query_album))
    if not res:
        return "Álbum não encontrado", 404

    row = res[0]
    q_generos = PREFIX + f"SELECT ?nome WHERE {{ :{id_album} :pertenceAoGenero ?g . BIND(STRAFTER(STR(?g), 'music-ontology/') AS ?nome) }}"
    q_musicas = PREFIX + f"SELECT ?id ?nome WHERE {{ ?m :pertenceAoAlbum :{id_album} ; :nome ?nome . BIND(STRAFTER(STR(?m), 'music-ontology/') AS ?id) }} ORDER BY ?nome"

    artista_dados = None
    if g(row, "artistaId"):
        artista_dados = {"id": g(row, "artistaId"), "nome": g(row, "artistaNome")}

    album = {
        "id":      id_album,
        "nome":    g(row, "nome"),
        "ano":     g(row, "ano"),
        "artista": artista_dados,
        "generos": [{"nome": g(r,"nome")} for r in rows_of(exec_query(q_generos))],
        "musicas": [{"id": g(r,"id"), "nome": g(r,"nome")} for r in rows_of(exec_query(q_musicas))],
    }

    return render_template('album.html', album=album, generos_globais=generos_list())



@app.route('/musica/<id_musica>')
def detalhe_musica(id_musica):
    if not re.match(r'^\w+$', id_musica):
        return "ID de música inválido", 400

    query_info = PREFIX + f"""
        SELECT ?nome ?albumId ?albumNome ?ano WHERE {{
            :{id_musica} a :Musica ; :nome ?nome .
            OPTIONAL {{ 
                {{ :{id_musica} :pertenceAoAlbum ?album . }} 
                UNION 
                {{ ?album :contemMusica :{id_musica} . }}
                ?album :nome ?albumNome .
                OPTIONAL {{ ?album :anoLancamento ?ano }}
                BIND(STRAFTER(STR(?album), "music-ontology/") AS ?albumId) 
            }}
        }} LIMIT 1
    """
    res = rows_of(exec_query(query_info))
    if not res:
        return "Música não encontrada", 404

    row = res[0]

    q_int  = PREFIX + f"SELECT ?id ?nome WHERE {{ :{id_musica} :interpretadaPor ?a . ?a :nome ?nome . BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?id) }}"
    q_gen  = PREFIX + f"SELECT ?nome WHERE {{ :{id_musica} :pertenceAoGenero ?g . BIND(STRAFTER(STR(?g), 'music-ontology/') AS ?nome) }}"
    q_feat = PREFIX + f"SELECT ?id ?nome WHERE {{:{id_musica} :temColaboracao ?a . ?a :nome ?nome . BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?id) }}"

    musica = {
        "id":            id_musica,
        "nome":          g(row, "nome"),
        "album":         {"id": g(row,"albumId"), "nome": g(row,"albumNome"), "ano": g(row,"ano")} if g(row,"albumId") else None,
        "interpretes":   [{"id": g(r,"id"), "nome": g(r,"nome")} for r in rows_of(exec_query(q_int))],
        "generos":       [{"nome": g(r,"nome")} for r in rows_of(exec_query(q_gen))],
        "colaboracoes":  [{"id": g(r,"id"), "nome": g(r,"nome")} for r in rows_of(exec_query(q_feat))],
    }

    return render_template('musica.html', musica=musica)



@app.route('/generos')
def generos():
    query_g = PREFIX + """
        SELECT DISTINCT ?gid WHERE {
            ?gid rdfs:subClassOf* :Genero .
            FILTER(?gid != :Genero)
        }
    """
    gen_list = []
    for r in rows_of(exec_query(query_g)):
        gid = r["gid"]["value"].split('/')[-1]
        q_art = PREFIX + f"""
            SELECT DISTINCT ?id ?nome ?tipo WHERE {{
                {{ ?a a :ArtistaSolo . BIND("Solo" AS ?tipo) }}
                UNION {{ ?a a :Banda . BIND("Banda" AS ?tipo) }}
                {{ 
                    ?a :pertenceAoGenero :{gid} . 
                }}
                UNION 
                {{ 
                    ?m :interpretadaPor ?a ; 
                       :pertenceAoGenero :{gid} . 
                }}
                ?a :nome ?nome .
                BIND(STRAFTER(STR(?a), "music-ontology/") AS ?id)
            }} ORDER BY ?nome
        """
        artistas = [{"id": g(ra,"id"), "nome": g(ra,"nome"), "tipo": g(ra,"tipo")}
                    for ra in rows_of(exec_query(q_art))]
        gen_list.append({"id": gid, "nome": gid, "artistas": artistas, "total": len(artistas)})

    gen_list.sort(key=lambda x: -x["total"])
    return render_template('generos.html', generos=gen_list)



@app.route('/timeline')
def timeline():
    query = PREFIX + """
        SELECT DISTINCT ?id ?nome ?tipo ?ano WHERE {
            { ?a a :ArtistaSolo ; :nome ?nome ; :anoNascimento ?ano . BIND("Nascimento" AS ?tipo) BIND(STRAFTER(STR(?a), "music-ontology/") AS ?id) }
            UNION { ?a a :Banda ; :nome ?nome ; :anoFormacao ?ano . BIND("Formação" AS ?tipo) BIND(STRAFTER(STR(?a), "music-ontology/") AS ?id) }
            UNION { ?a a :Album ; :nome ?nome ; :anoLancamento ?ano . BIND("Álbum" AS ?tipo) BIND(STRAFTER(STR(?a), "music-ontology/") AS ?id) }
            UNION { ?a a :Premio ; :nome ?nome ; :anoPremio ?ano . BIND("Prémio" AS ?tipo) BIND(STRAFTER(STR(?a), "music-ontology/") AS ?id) }
        } ORDER BY ?ano
    """
    eventos_lista = [
        {"id": g(r,"id"), "nome": g(r,"nome"), "tipo": g(r,"tipo"), "ano": g(r,"ano")}
        for r in rows_of(exec_query(query)) if g(r,"ano") and g(r,"ano").isdigit()
    ]
    eventos_por_ano = {}
    for ev in eventos_lista:
        ano = ev["ano"]
        if ano not in eventos_por_ano:
            eventos_por_ano[ano] = []
        eventos_por_ano[ano].append(ev)

    anos_ordenados = sorted(eventos_por_ano.keys())
    eventos_agrupados = [{"ano": ano, "lista": eventos_por_ano[ano]} for ano in anos_ordenados]

    return render_template('timeline.html', eventos_por_ano=eventos_agrupados, total_eventos=len(eventos_lista))



@app.route('/estatisticas')
def estatisticas():
    q_gen = PREFIX + "SELECT ?genero (COUNT(DISTINCT ?a) AS ?total) WHERE { { ?a a :ArtistaSolo } UNION { ?a a :Banda } ?a :pertenceAoGenero ?g . BIND(STRAFTER(STR(?g), 'music-ontology/') AS ?genero) } GROUP BY ?genero ORDER BY DESC(?total)"
    por_genero = [{"genero": g(r,"genero"), "total": int(g(r,"total","0"))} for r in rows_of(exec_query(q_gen))]

    q_edit = PREFIX + "SELECT ?editora (COUNT(DISTINCT ?a) AS ?total) WHERE { { ?a a :ArtistaSolo } UNION { ?a a :Banda } ?a :pertenceAEditora ?e . ?e :nome ?editora . } GROUP BY ?editora ORDER BY DESC(?total)"
    por_editora = [{"editora": g(r,"editora"), "total": int(g(r,"total","0"))} for r in rows_of(exec_query(q_edit))]

    q_dec = PREFIX + "SELECT (FLOOR(?ano / 10) * 10 AS ?decada) (COUNT(?a) AS ?total) WHERE { ?a a :Album ; :anoLancamento ?ano . } GROUP BY (FLOOR(?ano / 10) * 10) ORDER BY ?decada"
    por_decada = [{"decada": str(int(float(g(r,"decada","0"))))+"s", "total": int(g(r,"total","0"))} for r in rows_of(exec_query(q_dec)) if g(r,"decada")]

    q_prem = PREFIX + "SELECT ?org (COUNT(?p) AS ?total) WHERE { ?p a :Premio ; :organizacao ?org . } GROUP BY ?org ORDER BY DESC(?total)"
    por_org = [{"org": g(r,"org"), "total": int(g(r,"total","0"))} for r in rows_of(exec_query(q_prem))]

    q_top = PREFIX + "SELECT ?id ?nome (COUNT(?p) AS ?total) WHERE { { ?a a :ArtistaSolo } UNION { ?a a :Banda } ?a :nome ?nome ; :recebeuPremio ?p . BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?id) } GROUP BY ?id ?nome ORDER BY DESC(?total) LIMIT 10"
    mais_premiados = [{"id": g(r,"id"), "nome": g(r,"nome"), "total": int(g(r,"total","0"))} for r in rows_of(exec_query(q_top))]

    return render_template('estatisticas.html', por_genero=por_genero, por_editora=por_editora, por_decada=por_decada, por_org=por_org, mais_premiados=mais_premiados)


@app.route('/colaboracoes')
def colaboracoes():
    q_inf = PREFIX + "SELECT ?aId ?aNome ?bId ?bNome WHERE { ?a :influenciadoPor ?b . ?a :nome ?aNome . ?b :nome ?bNome . BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?aId) BIND(STRAFTER(STR(?b), 'music-ontology/') AS ?bId) }"
    influencias = [{"source": g(r,"bId"), "sourceNome": g(r,"bNome"), "target": g(r,"aId"), "targetNome": g(r,"aNome")} for r in rows_of(exec_query(q_inf))]

    q_feat = PREFIX + "SELECT ?mId ?mNome ?aId ?aNome ?bId ?bNome WHERE { ?m a :Musica ; :nome ?mNome ; :interpretadaPor ?a ; :temColaboracao ?b . ?a :nome ?aNome . ?b :nome ?bNome . BIND(STRAFTER(STR(?m), 'music-ontology/') AS ?mId) BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?aId) BIND(STRAFTER(STR(?b), 'music-ontology/') AS ?bId) }"
    feats = [{"musica": g(r,"mNome"), "musicaId": g(r,"mId"), "artista": g(r,"aNome"), "artistaId": g(r,"aId"), "feat": g(r,"bNome"), "featId": g(r,"bId")} for r in rows_of(exec_query(q_feat))]

    return render_template('colaboracoes.html', influencias=influencias, feats=feats)


@app.route('/premios')
def premios():
    q = PREFIX + """
    SELECT ?pId ?pNome ?cat ?org ?ano ?aId ?aNome 
    WHERE { 
        ?p a :Premio ; 
                :nome ?pNome . 
        OPTIONAL { ?p :categoria ?cat } 
        OPTIONAL { ?p :organizacao ?org } 
        OPTIONAL { ?p :anoPremio ?ano } 
        OPTIONAL { 
            ?a :recebeuPremio ?p ; 
                :nome ?aNome . 
            BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?aId) 
        } 
        BIND(STRAFTER(STR(?p), 'music-ontology/') AS ?pId) 
    } 
    ORDER BY DESC(?ano) ?org
    """
    lista = [{"id": g(r,"pId"), "nome": g(r,"pNome"), "cat": g(r,"cat"), "org": g(r,"org"), "ano": g(r,"ano"), "artistaId": g(r,"aId"), "artistaNome": g(r,"aNome")} for r in rows_of(exec_query(q))]

    q_artistas = PREFIX + "SELECT DISTINCT ?id ?nome WHERE { { ?a a :ArtistaSolo } UNION { ?a a :Banda } ?a :nome ?nome . BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?id) } ORDER BY ?nome"
    lista_artistas = [{"id": g(r,"id"), "nome": g(r,"nome")} for r in rows_of(exec_query(q_artistas))]

    return render_template('premios.html', premios=lista, artistas=lista_artistas)



@app.route('/concertos')
def concertos():
    q = PREFIX + """
    SELECT ?cId ?cNome ?local ?data 
    WHERE { 
        ?c a :Concerto ; 
            :nome ?cNome . 
        OPTIONAL { ?c :local ?local } 
        OPTIONAL { ?c :data ?data } 
        BIND(STRAFTER(STR(?c), 'music-ontology/') AS ?cId) 
    } 
    ORDER BY DESC(?data)
    """
    concertos_list = []
    for r in rows_of(exec_query(q)):
        cid = g(r, "cId")
        q_art = PREFIX + f"SELECT ?id ?nome WHERE {{ ?a :atuouEm :{cid} ; :nome ?nome . BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?id) }}"
        artistas_concerto = [{"id": g(ra,"id"), "nome": g(ra,"nome")} for ra in rows_of(exec_query(q_art))]
        concertos_list.append({"id": cid, "nome": g(r,"cNome"), "local": g(r,"local"), "data": g(r,"data"), "artistas": artistas_concerto})

    q_todos_artistas = PREFIX + "SELECT DISTINCT ?id ?nome WHERE { { ?a a :ArtistaSolo } UNION { ?a a :Banda } ?a :nome ?nome . BIND(STRAFTER(STR(?a), 'music-ontology/') AS ?id) } ORDER BY ?nome"
    lista_artistas = [{"id": g(r,"id"), "nome": g(r,"nome")} for r in rows_of(exec_query(q_todos_artistas))]

    return render_template('concertos.html', concertos=concertos_list, artistas=lista_artistas)


@app.route('/pesquisa')
def pesquisa():
    q       = request.args.get('q', '').strip()
    genero  = request.args.get('genero', '').strip()
    ano_de  = request.args.get('ano_de', '').strip()
    ano_ate = request.args.get('ano_ate', '').strip()
    editora = request.args.get('editora', '').strip()

    id_re = re.compile(r'^\w+$')
    if genero and not id_re.match(genero):
        genero = ''
    if editora and not id_re.match(editora):
        editora = ''

    filtros_art = []
    if genero:
        filtros_art.append(f'?e :pertenceAoGenero :{genero} .')
    if editora:
        filtros_art.append(f'?e :pertenceAEditora :{editora} .')

    resultados = []
    if q or genero or editora or ano_de or ano_ate:
        filtro_nome = f'FILTER(CONTAINS(LCASE(?nome), LCASE("{esc_lit(q)}")))' if q else ''

        query = PREFIX + f"""
            SELECT DISTINCT ?id ?nome ?tipo WHERE {{
                {{ {{ ?e a :ArtistaSolo . BIND("Artista" AS ?tipo) }}
                  UNION {{ ?e a :Banda . BIND("Banda" AS ?tipo) }}
                  ?e :nome ?nome . {filtro_nome} {''.join(filtros_art)}
                  BIND(CONCAT("/artista/", STRAFTER(STR(?e), "music-ontology/")) AS ?id) }}
                UNION {{ ?e a :Album ; :nome ?nome . {filtro_nome}
                        BIND("Álbum" AS ?tipo)
                        BIND(CONCAT("/album/", STRAFTER(STR(?e), "music-ontology/")) AS ?id) }}
                UNION {{ ?e a :Musica ; :nome ?nome . {filtro_nome}
                        BIND("Música" AS ?tipo)
                        BIND(CONCAT("/musica/", STRAFTER(STR(?e), "music-ontology/")) AS ?id) }}
            }} ORDER BY ?tipo ?nome LIMIT 80
        """
        resultados = [{"id": g(r,"id"), "nome": g(r,"nome"), "tipo": g(r,"tipo")} for r in rows_of(exec_query(query))]

    return render_template('pesquisa.html', resultados=resultados, busca=q, generos=generos_list(), editoras=editoras_list(), filtro_genero=genero, filtro_editora=editora, ano_de=ano_de, ano_ate=ano_ate)



@app.route('/api/stats/generos')
def api_stats_generos():
    q = PREFIX + """
    SELECT ?genero (COUNT(DISTINCT ?a) AS ?total) 
    WHERE { 
        { ?a a :ArtistaSolo } 
        UNION 
        { ?a a :Banda } 
        ?a :pertenceAoGenero ?g . 
        BIND(STRAFTER(STR(?g), 'music-ontology/') AS ?genero) 
    } 
    GROUP BY ?genero 
    ORDER BY DESC(?total)
    """
    return jsonify([{"genero": g(r,"genero"), "total": int(g(r,"total","0"))} for r in rows_of(exec_query(q))])

@app.route('/api/stats/decadas')
def api_stats_decadas():
    q = PREFIX + """
    SELECT (FLOOR(?ano / 10) * 10 AS ?decada) (COUNT(?a) AS ?total) 
    WHERE { 
        ?a a :Album ; 
            :anoLancamento ?ano . 
    } 
    GROUP BY (FLOOR(?ano / 10) * 10) 
    ORDER BY ?decada
    """
    return jsonify([{"decada": str(int(float(g(r,"decada","0"))))+"s", "total": int(g(r,"total","0"))} for r in rows_of(exec_query(q)) if g(r,"decada")])



TIPOS_ARTISTA_VALIDOS = {'ArtistaSolo', 'Banda'}

@app.route('/artista/adicionar', methods=['POST'])
def adicionar_artista():
    nome    = request.form.get('nome', '').strip()
    tipo    = request.form.get('tipo', 'ArtistaSolo')
    ano     = request.form.get('ano', '').strip()
    generos = request.form.getlist('genero')
    editora = request.form.get('editora', '').strip()

    if not nome:
        flash("Nome obrigatório.", "error")
        return redirect(url_for('index'))

    if tipo not in TIPOS_ARTISTA_VALIDOS:
        tipo = 'ArtistaSolo'

    ids_generos_validos = {g_['id'] for g_ in generos_list()}
    generos = [g_ for g_ in generos if g_.strip() and g_.strip() in ids_generos_validos]

    if editora:
        ids_editoras_validas = {e['id'] for e in editoras_list()}
        if editora not in ids_editoras_validas:
            editora = ''

    base_id = esc_id(nome)
    if not base_id:
        flash("Nome inválido.", "error")
        return redirect(url_for('index'))
    new_id = id_unico(base_id)

    prop_ano = ":anoNascimento" if tipo == 'ArtistaSolo' else ":anoFormacao"

    triplos = [
        f':{new_id} a :{tipo} .',
        f':{new_id} :nome "{esc_lit(nome)}"^^xsd:string .',
    ]
    if ano and ano.isdigit():
        triplos.append(f':{new_id} {prop_ano} {int(ano)} .')
    for gen in generos:
        triplos.append(f':{new_id} :pertenceAoGenero :{gen} .')
    if editora:
        triplos.append(f':{new_id} :pertenceAEditora :{editora} .')

    ok = exec_update(PREFIX + "INSERT DATA {\n  " + "\n  ".join(triplos) + "\n}")
    if not ok:
        flash("Erro a inserir no triplestore. Verifica se o GraphDB está a correr.", "error")
        return redirect(url_for('index'))

    return redirect(url_for('detalhe_artista', id_artista=new_id))


@app.route('/album/adicionar', methods=['POST'])
def adicionar_album():
    nome       = request.form.get('nome', '').strip()
    ano        = request.form.get('ano', '').strip()
    artista_id = request.form.get('artista_id', '').strip()
    generos    = request.form.getlist('genero')

    if not nome or not artista_id:
        flash("Nome do álbum e artista são obrigatórios.", "error")
        if artista_id and re.match(r'^\w+$', artista_id):
            return redirect(url_for('detalhe_artista', id_artista=artista_id))
        return redirect(url_for('index'))

    if not re.match(r'^\w+$', artista_id):
        flash("ID de artista inválido.", "error")
        return redirect(url_for('index'))

    ids_generos_validos = {g_['id'] for g_ in generos_list()}
    generos = [g_ for g_ in generos if g_.strip() and g_.strip() in ids_generos_validos]

    base_id = esc_id(nome) + '_alb'
    new_id = id_unico(base_id)

    triplos = [
        f':{new_id} a :Album .',
        f':{new_id} :nome "{esc_lit(nome)}"^^xsd:string .',
    ]
    if ano and ano.isdigit():
        triplos.append(f':{new_id} :anoLancamento {int(ano)} .')
    for gen in generos:
        triplos.append(f':{new_id} :pertenceAoGenero :{gen} .')
    triplos.append(f':{artista_id} :lancouAlbum :{new_id} .')

    ok = exec_update(PREFIX + "INSERT DATA {\n  " + "\n  ".join(triplos) + "\n}")
    if not ok:
        flash("Erro a inserir no triplestore.", "error")
        return redirect(url_for('detalhe_artista', id_artista=artista_id))

    return redirect(url_for('detalhe_album', id_album=new_id))


@app.route('/musica/adicionar', methods=['POST'])
def adicionar_musica():
    nome = request.form.get('nome', '').strip()
    artista_id = request.form.get('artista_id', '').strip()
    album_id = request.form.get('album_id', '').strip()
    feat_id = request.form.get('feat_id', '').strip()
    generos_ids = request.form.getlist('genero')
    
    if not nome or not artista_id:
        flash("Erro: Nome da música e artista são obrigatórios.", "error")
        return redirect(url_for('detalhe_artista', id_artista=artista_id))

    base_id = esc_id(nome) + '_musica'
    new_id = id_unico(base_id)

    triplos = [
        f':{new_id} a :Musica .',
        f':{new_id} :nome "{esc_lit(nome)}"^^xsd:string .',
        f':{new_id} :interpretadaPor :{artista_id} .'
    ]
    if feat_id:
        triplos.append(f':{new_id} :temColaboracao :{feat_id} .')
    if album_id:
        triplos.append(f':{new_id} :pertenceAoAlbum :{album_id} .')
    for g_id in generos_ids:
        triplos.append(f':{new_id} :pertenceAoGenero :{g_id} .')

    ok = exec_update(PREFIX + "INSERT DATA {\n  " + "\n  ".join(triplos) + "\n}")
    if not ok:
        flash("Erro a inserir a música.", "error")
    else:
        flash(f"Música '{nome}' registada com sucesso!", "success")

    return redirect(url_for('detalhe_artista', id_artista=artista_id))



@app.route('/genero/adicionar', methods=['POST'])
def adicionar_genero():
    nome = request.form.get('nome', '').strip()

    if not nome:
        flash("Nome do género obrigatório.", "error")
        return redirect(url_for('generos'))

    base_id = esc_id(nome)
    if not base_id:
        flash("Nome de género inválido.", "error")
        return redirect(url_for('generos'))
    q_existe = PREFIX + f"SELECT ?s WHERE {{ :{base_id} rdfs:subClassOf :Genero }} LIMIT 1"
    res = exec_query(q_existe)
    
    if len(rows_of(res)) > 0:
        flash(f"O género '{nome}' já existe.", "error")
        return redirect(url_for('generos'))

    triplos = [
        f':{base_id} a owl:Class .',
        f':{base_id} rdfs:subClassOf :Genero .',
        f':{base_id} rdfs:label "{esc_lit(nome)}"^^xsd:string .',
    ]

    ok = exec_update(PREFIX + "INSERT DATA {\n  " + "\n  ".join(triplos) + "\n}")
    if not ok:
        flash("Erro a inserir o género no triplestore.", "error")
    else:
        flash(f"Género '{nome}' adicionado com sucesso!", "success")

    return redirect(url_for('generos'))


@app.route('/premio/adicionar', methods=['POST'])
def adicionar_premio():
    nome       = request.form.get('nome', '').strip()
    categoria  = request.form.get('categoria', '').strip()
    organizacao= request.form.get('organizacao', '').strip()
    ano        = request.form.get('ano', '').strip()
    artista_id = request.form.get('artista_id', '').strip()

    if not nome:
        flash("Nome do prémio obrigatório.", "error")
        return redirect(url_for('premios'))

    base_id = esc_id(nome) + '_premio'
    new_id = id_unico(base_id)

    triplos = [
        f':{new_id} a :Premio .',
        f':{new_id} :nome "{esc_lit(nome)}"^^xsd:string .',
    ]
    if categoria:
        triplos.append(f':{new_id} :categoria "{esc_lit(categoria)}"^^xsd:string .')
    if organizacao:
        triplos.append(f':{new_id} :organizacao "{esc_lit(organizacao)}"^^xsd:string .')
    if ano and ano.isdigit():
        triplos.append(f':{new_id} :anoPremio {int(ano)} .')

    if artista_id and re.match(r'^\w+$', artista_id):
        triplos.append(f':{artista_id} :recebeuPremio :{new_id} .')

    ok = exec_update(PREFIX + "INSERT DATA {\n  " + "\n  ".join(triplos) + "\n}")
    if not ok:
        flash("Erro a inserir o prémio no triplestore.", "error")
    else:
        flash(f"Prémio '{nome}' registado com sucesso!", "success")

    return redirect(url_for('premios'))



@app.route('/concerto/adicionar', methods=['POST'])
def adicionar_concerto():
    nome       = request.form.get('nome', '').strip()
    local      = request.form.get('local', '').strip()
    data       = request.form.get('data', '').strip()
    artista_id = request.form.get('artista_id', '').strip()

    if not nome:
        flash("Nome do concerto obrigatório.", "error")
        return redirect(url_for('concertos'))

    base_id = esc_id(nome) + '_conc'
    new_id = id_unico(base_id)

    triplos = [
        f':{new_id} a :Concerto .',
        f':{new_id} :nome "{esc_lit(nome)}"^^xsd:string .',
    ]
    if local:
        triplos.append(f':{new_id} :local "{esc_lit(local)}"^^xsd:string .')
    if data:
        triplos.append(f':{new_id} :data "{esc_lit(data)}"^^xsd:string .')

    if artista_id and re.match(r'^\w+$', artista_id):
        triplos.append(f':{artista_id} :atuouEm :{new_id} .')

    ok = exec_update(PREFIX + "INSERT DATA {\n  " + "\n  ".join(triplos) + "\n}")
    if not ok:
        flash("Erro a inserir o concerto no triplestore.", "error")
    else:
        flash(f"Concerto '{nome}' registado com sucesso!", "success")

    return redirect(url_for('concertos'))



def remover_individuo(id_individuo):
    if not re.match(r'^\w+$', id_individuo):
        return False
    q1 = PREFIX + f"DELETE WHERE {{ :{id_individuo} ?p ?o }}"
    q2 = PREFIX + f"DELETE WHERE {{ ?s ?p :{id_individuo} }}"
    return exec_update(q1) and exec_update(q2)


@app.route('/artista/<id_artista>/remover', methods=['POST'])
def remover_artista(id_artista):
    if not re.match(r'^\w+$', id_artista):
        flash("ID de artista inválido.", "error")
        return redirect(url_for('index'))
    q_nome = PREFIX + f"SELECT ?n WHERE {{ :{id_artista} :nome ?n }} LIMIT 1"
    rs = rows_of(exec_query(q_nome))
    nome = g(rs[0], "n") if rs else id_artista
    if remover_individuo(id_artista):
        flash(f'Artista "{nome}" removido com sucesso.', "success")
    else:
        flash("Erro ao remover o artista. Verifica se o GraphDB está a correr.", "error")
    return redirect(url_for('index'))


@app.route('/album/<id_album>/remover', methods=['POST'])
def remover_album(id_album):
    if not re.match(r'^\w+$', id_album):
        flash("ID de álbum inválido.", "error")
        return redirect(url_for('index'))
    q = PREFIX + f"""
        SELECT ?nome ?artistaId WHERE {{
            :{id_album} :nome ?nome .
            OPTIONAL {{ ?a :lancouAlbum :{id_album} .
                        BIND(STRAFTER(STR(?a), "music-ontology/") AS ?artistaId) }}
        }} LIMIT 1
    """
    rs = rows_of(exec_query(q))
    nome = g(rs[0], "nome") if rs else id_album
    artista_id = g(rs[0], "artistaId") if rs else None
    if remover_individuo(id_album):
        flash(f'Álbum "{nome}" removido com sucesso.', "success")
    else:
        flash("Erro ao remover o álbum.", "error")
    if artista_id and re.match(r'^\w+$', artista_id):
        return redirect(url_for('detalhe_artista', id_artista=artista_id))
    return redirect(url_for('index'))


@app.route('/musica/<id_musica>/remover', methods=['POST'])
def remover_musica(id_musica):
    if not re.match(r'^\w+$', id_musica):
        flash("ID de música inválido.", "error")
        return redirect(url_for('index'))
    q = PREFIX + f"""
        SELECT ?nome ?albumId ?artistaId WHERE {{
            :{id_musica} :nome ?nome .
            OPTIONAL {{ :{id_musica} :pertenceAoAlbum ?album .
                        BIND(STRAFTER(STR(?album), "music-ontology/") AS ?albumId) }}
            OPTIONAL {{ :{id_musica} :interpretadaPor ?a .
                        BIND(STRAFTER(STR(?a), "music-ontology/") AS ?artistaId) }}
        }} LIMIT 1
    """
    rs = rows_of(exec_query(q))
    nome = g(rs[0], "nome") if rs else id_musica
    album_id = g(rs[0], "albumId") if rs else None
    artista_id = g(rs[0], "artistaId") if rs else None
    if remover_individuo(id_musica):
        flash(f'Música "{nome}" removida com sucesso.', "success")
    else:
        flash("Erro ao remover a música.", "error")
    if album_id and re.match(r'^\w+$', album_id):
        return redirect(url_for('detalhe_album', id_album=album_id))
    if artista_id and re.match(r'^\w+$', artista_id):
        return redirect(url_for('detalhe_artista', id_artista=artista_id))
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', codigo=404, mensagem="Página não encontrada"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', codigo=500, mensagem="Erro interno do servidor. Verifica se o GraphDB está a correr."), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)