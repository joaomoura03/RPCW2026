from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError, QueryBadFormed
import socket

GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/musica_portuguesa"
TIMEOUT_SEGUNDOS = 30


def exec_query(query):
    sparql = SPARQLWrapper(GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(TIMEOUT_SEGUNDOS)

    try:
        return sparql.query().convert()
    except QueryBadFormed as e:
        print(f"[SPARQL] Query mal-formada: {e}")
        print(f"[SPARQL] Query problemática:\n{query}\n")
        return None
    except EndPointInternalError as e:
        print(f"[SPARQL] Erro interno do GraphDB: {e}")
        return None
    except socket.timeout:
        print(f"[SPARQL] Timeout ao executar query (>{TIMEOUT_SEGUNDOS}s)")
        return None
    except ConnectionError:
        print(f"[SPARQL] Não foi possível ligar ao GraphDB em {GRAPHDB_ENDPOINT}")
        print(f"[SPARQL] Verifica se o GraphDB está a correr na porta 7200.")
        return None
    except Exception as e:
        # Detectar erros de ligação por mensagem (urllib/requests podem levantar exceptions diferentes consoante a versão)
        msg = str(e).lower()
        if 'connection' in msg or 'refused' in msg or 'resolve' in msg:
            print(f"[SPARQL] Falha de ligação ao GraphDB: {e}")
            print(f"[SPARQL] Verifica se o GraphDB está a correr em {GRAPHDB_ENDPOINT}")
        else:
            print(f"[SPARQL] Erro inesperado: {type(e).__name__}: {e}")
        return None


def exec_update(query):
    sparql = SPARQLWrapper(GRAPHDB_ENDPOINT + "/statements")
    sparql.setQuery(query)
    sparql.setMethod('POST')
    sparql.setTimeout(TIMEOUT_SEGUNDOS)

    try:
        sparql.query()
        return True
    except QueryBadFormed as e:
        print(f"[SPARQL UPDATE] Query mal-formada: {e}")
        print(f"[SPARQL UPDATE] Query problemática:\n{query}\n")
        return False
    except socket.timeout:
        print(f"[SPARQL UPDATE] Timeout (>{TIMEOUT_SEGUNDOS}s)")
        return False
    except Exception as e:
        msg = str(e).lower()
        if 'connection' in msg or 'refused' in msg:
            print(f"[SPARQL UPDATE] Falha de ligação ao GraphDB: {e}")
        else:
            print(f"[SPARQL UPDATE] Erro: {type(e).__name__}: {e}")
        return False