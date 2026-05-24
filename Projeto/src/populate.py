import json

ONTOLOGIA = 'music.ttl'
DATASETS  = 'datasets/'
OUTPUT    = 'musica_portuguesa.ttl'


def esc(s):
    if not s:
        return ""
    if isinstance(s, int):
        return s
    return str(s).replace('\\', '\\\\').replace('\"', '\\\"').replace('\n', ' ')

def carregar(ficheiro):
    with open(DATASETS + ficheiro, encoding='utf-8') as f:
        return json.load(f)

def secao(titulo):
    return (
        "\n#################################################################\n"
        f"#    {titulo}\n"
        "#################################################################\n\n"
    )



def gerar_editora(e):
    linhas = [f":{e['id']} a :Editora"]
    linhas.append(f':nome "{esc(e["nome"])}"')
    return ' ;\n    '.join(linhas) + ' .\n\n'

def gerar_artista_solo(a, mapa_premios, mapa_concertos, mapa_influencias):
    linhas = [f":{a['id']} a :ArtistaSolo"]
    linhas.append(f':nome "{esc(a["nome"])}"')
    if 'anoNascimento' in a:
        linhas.append(f':anoNascimento {a["anoNascimento"]}')
    if 'pertenceAEditora' in a:
        linhas.append(f':pertenceAEditora :{a["pertenceAEditora"]}')
    elif 'editora' in a:
        linhas.append(f':pertenceAEditora :{a["editora"]}')
        
    if 'biografia' in a:
        linhas.append(f':biografia "{esc(a["biografia"])}"')
    elif 'descricao' in a:
        linhas.append(f':biografia "{esc(a["descricao"])}"')
        
    for g in a.get('generos', []):
        linhas.append(f':pertenceAoGenero :{g}')
        
    bloco = ' ;\n    '.join(linhas) + ' .\n'
    
    for pr_id in mapa_premios.get(a['id'], []):
        bloco += f":{a['id']} :recebeuPremio :{pr_id} .\n"
        
    for cc_id in mapa_concertos.get(a['id'], []):
        bloco += f":{a['id']} :atuouEm :{cc_id} .\n"

    for inf_id in mapa_influencias.get(a['id'], []):
        bloco += f":{a['id']} :influenciadoPor :{inf_id} .\n"
        
    return bloco + '\n'

def gerar_banda(b, mapa_premios, mapa_concertos, mapa_influencias):
    linhas = [f":{b['id']} a :Banda"]
    linhas.append(f':nome "{esc(b["nome"])}"')
    if 'anoFormacao' in b:
        linhas.append(f':anoFormacao {b["anoFormacao"]}')
    if 'pertenceAEditora' in b:
        linhas.append(f':pertenceAEditora :{b["pertenceAEditora"]}')
    elif 'editora' in b:
        linhas.append(f':pertenceAEditora :{b["editora"]}')
        
    if 'biografia' in b:
        linhas.append(f':biografia "{esc(b["biografia"])}"')
    elif 'descricao' in b:
        linhas.append(f':biografia "{esc(b["descricao"])}"')
        
    for g in b.get('generos', []):
        linhas.append(f':pertenceAoGenero :{g}')
    for m in b.get('temMembro', b.get('membros', [])):
        linhas.append(f':temMembro :{m}')
        
    bloco = ' ;\n    '.join(linhas) + ' .\n'
    
    for pr_id in mapa_premios.get(b['id'], []):
        bloco += f":{b['id']} :recebeuPremio :{pr_id} .\n"
        
    for cc_id in mapa_concertos.get(b['id'], []):
        bloco += f":{b['id']} :atuouEm :{cc_id} .\n"

    for inf_id in mapa_influencias.get(b['id'], []):
        bloco += f":{b['id']} :influenciadoPor :{inf_id} .\n"
        
    return bloco + '\n'

def gerar_album(a):
    linhas = [f":{a['id']} a :Album"]
    linhas.append(f':nome "{esc(a["nome"])}"')
    if 'anoLancamento' in a:
        linhas.append(f':anoLancamento {a["anoLancamento"]}')
    for g in a.get('generos', []):
        linhas.append(f':pertenceAoGenero :{g}')
        
    bloco = ' ;\n    '.join(linhas) + ' .\n'
    if 'lancadoPor' in a:
        bloco += f":{a['lancadoPor']} :lancouAlbum :{a['id']} .\n"
    elif 'artista' in a:
        bloco += f":{a['artista']} :lancouAlbum :{a['id']} .\n"
    return bloco + '\n'

def gerar_musica(m, mapa_colaboracoes):
    linhas = [f":{m['id']} a :Musica"]
    linhas.append(f':nome "{esc(m["nome"])}"')
    
    for ip in m.get('interpretadaPor', []):
        linhas.append(f':interpretadaPor :{ip}')
    if 'artista' in m and not m.get('interpretadaPor'):
        linhas.append(f':interpretadaPor :{m["artista"]}')
        
    for cp in m.get('compostaPor', []):
        linhas.append(f':compostaPor :{cp}')
    for ep in m.get('escritaPor', []):
        linhas.append(f':escritaPor :{ep}')
        
    if 'pertenceAoAlbum' in m:
        linhas.append(f':pertenceAoAlbum :{m["pertenceAoAlbum"]}')
    elif 'album' in m:
        linhas.append(f':pertenceAoAlbum :{m["album"]}')
        
    for g in m.get('generos', []):
        linhas.append(f':pertenceAoGenero :{g}')
        
    bloco = ' ;\n    '.join(linhas) + ' .\n'
    
    for colab_artista in mapa_colaboracoes.get(m['id'], []):
        bloco += f":{m['id']} :temColaboracao :{colab_artista} .\n"
        
    return bloco + '\n'

def gerar_tour(t):
    t_id = t['id']
    linhas = [f":{t_id} a :Tour"]
    linhas.append(f':nome "{esc(t.get("nome", "Tour"))}"')
    bloco = ' ;\n    '.join(linhas) + ' .\n'

    art_id = t.get('artista')
    if art_id:
        bloco += f":{art_id} :realizouTour :{t_id} .\n"

    return bloco + '\n'


def main():
    print(f"A ler a ontologia base ({ONTOLOGIA})...")
    with open(ONTOLOGIA, encoding='utf-8') as f:
        ontologia = f.read()

    marcador = "###  Generated by the OWL API"
    if marcador in ontologia:
        ontologia = ontologia[:ontologia.index(marcador)].rstrip() + '\n'

    print("A carregar todos os ficheiros JSON...")
    editoras  = carregar('editoras.json')['editoras']
    artistas  = carregar('artistas.json')['artistasSolo']
    bandas    = carregar('bandas.json')['bandas']
    albuns    = carregar('albuns.json')['albuns']
    musicas   = carregar('musicas.json')['musicas']
    
    premios_json      = carregar('premios.json')['premios']
    concertos_json    = carregar('concertos.json')['concertos']
    tours_json        = carregar('tours.json')['tours']
    influencias_json  = carregar('influencias.json')['influencias']
    colaboracoes_json = carregar('colaboracoes.json')['colaboracoes']

    abox = secao("INDIVÍDUOS INTEGRADOS E MAPEADOS")

    abox += secao("Editoras")
    for e in editoras:
        abox += gerar_editora(e)

    abox += secao("Prémios")
    mapa_premios = {}
    for pr in premios_json:
        pr_id = pr['id']
        art_id = pr.get('ganhadoPor')
        if art_id:
            if art_id not in mapa_premios:
                mapa_premios[art_id] = []
            mapa_premios[art_id].append(pr_id)
        
        linhas_pr = [f":{pr_id} a :Premio"]
        linhas_pr.append(f'    :nome "{esc(pr.get("nome", "Prémio"))}"')
        if 'categoriaPremio' in pr:
            linhas_pr.append(f'    :categoria "{esc(pr["categoriaPremio"])}"')
        if 'entidadePremio' in pr:
            linhas_pr.append(f'    :organizacao "{esc(pr["entidadePremio"])}"')
        if 'anoPremio' in pr:
            linhas_pr.append(f'    :anoPremio {pr["anoPremio"]}')
        abox += ' ;\n'.join(linhas_pr) + ' .\n\n'

    abox += secao("Concertos")
    mapa_concertos = {}
    for cc in concertos_json:
        cc_id = cc['id']
        art_id = cc.get('artista')
        if art_id:
            if art_id not in mapa_concertos:
                mapa_concertos[art_id] = []
            mapa_concertos[art_id].append(cc_id)
            
        linhas_cc = [f":{cc_id} a :Concerto"]
        linhas_cc.append(f'    :nome "{esc(cc.get("nome", "Concerto"))}"')
        if 'localConcerto' in cc:
            linhas_cc.append(f'    :local "{esc(cc["localConcerto"])}"')
        if 'dataConcerto' in cc:
            linhas_cc.append(f'    :data "{esc(cc["dataConcerto"])}"')
        abox += ' ;\n'.join(linhas_cc) + ' .\n\n'

    abox += secao("Tours")
    for t in tours_json:
        abox += gerar_tour(t)

    mapa_influencias = {}
    for inf in influencias_json:
        origo = inf['influenciado']
        dest = inf['influenciador']
        if origo not in mapa_influencias:
            mapa_influencias[origo] = []
        mapa_influencias[origo].append(dest)

    # 5. Mapear Colaborações (Música -> Artista Secundário)
    mapa_colaboracoes = {}
    for colab in colaboracoes_json:
        m_id = colab.get('musica')
        art2 = colab.get('artista2')
        if m_id and art2:
            if m_id not in mapa_colaboracoes:
                mapa_colaboracoes[m_id] = []
            mapa_colaboracoes[m_id].append(art2)

    # 6. Gerar os indivíduos estruturais cruzados
    abox += secao("Artistas Solo")
    for a in artistas:
        abox += gerar_artista_solo(a, mapa_premios, mapa_concertos, mapa_influencias)

    abox += secao("Bandas")
    for b in bandas:
        abox += gerar_banda(b, mapa_premios, mapa_concertos, mapa_influencias)

    abox += secao("Álbuns")
    for al in albuns:
        abox += gerar_album(al)

    abox += secao("Músicas")
    for m in musicas:
        abox += gerar_musica(m, mapa_colaboracoes)

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(ontologia)
        f.write(abox)

    print(f"\n✓ Sucesso total! {OUTPUT} sincronizado e povoado com todas as relações.")


if __name__ == "__main__":
    main()