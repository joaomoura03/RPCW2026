import rdflib

def run_queries():
    # 1. Criar o grafo e carregar a ontologia
    g = rdflib.Graph()
    try:
        g.parse("out.ttl", format="ttl")
    except Exception as e:
        print(f"Erro ao carregar o ficheiro: {e}")
        return

    # Definir o prefixo para as queries
    # O rdflib permite usar o prefixo vazio se definido
    PREFIX = """
    PREFIX : <http://example.org/polvo-filosofico#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    """

    # --- Query 1: Quem foram os clientes? ---
    print("=== 1. Lista de Clientes ===")
    q1 = PREFIX + """
    SELECT DISTINCT ?nome WHERE {
        ?cliente a :Cliente .
        BIND(STRAFTER(STR(?cliente), "#") AS ?nome)
    }
    """
    for row in g.query(q1):
        print(f"- {row.nome}")

    # --- Query 2: Que pratos serve o restaurante? ---
    print("\n=== 2. Pratos servidos no Restaurante ===")
    q2 = PREFIX + """
    SELECT DISTINCT ?nomePrato WHERE {
        ?prato a/rdfs:subClassOf* :Prato .
        # Filtra para garantir que pegamos instÃ¢ncias e nÃ£o as classes
        FILTER NOT EXISTS { ?prato a owl:Class }
        BIND(STRAFTER(STR(?prato), "#") AS ?nomePrato)
    }
    """
    for row in g.query(q2):
        print(f"- {row.nomePrato}")

    # --- Query 3: Quais os ingredientes necessÃ¡rios Ã  confeÃ§Ã£o dos pratos? ---
    print("\n=== 3. Ingredientes por Prato ===")
    q3 = PREFIX + """
    SELECT DISTINCT ?nomePrato ?nomeIngrediente WHERE {
        ?prato :temIngrediente ?ingrediente .
        BIND(STRAFTER(STR(?prato), "#") AS ?nomePrato)
        BIND(STRAFTER(STR(?ingrediente), "#") AS ?nomeIngrediente)
    }
    ORDER BY ?nomePrato
    """
    current_prato = ""
    for row in g.query(q3):
        if row.nomePrato != current_prato:
            print(f"\nPrato: {row.nomePrato}")
            current_prato = row.nomePrato
        print(f"  > {row.nomeIngrediente}")

    # --- Query 4: HÃ¡ funcionÃ¡rios que tambÃ©m sejam clientes? ---
    print("\n=== 4. FuncionÃ¡rios que tambÃ©m sÃ£o Clientes ===")
    q4 = PREFIX + """
    SELECT DISTINCT ?nome WHERE {
        ?pessoa a :Funcionario .
        ?pessoa a :Cliente .
        BIND(STRAFTER(STR(?pessoa), "#") AS ?nome)
    }
    """
    results = g.query(q4)
    if len(results) > 0:
        for row in results:
            print(f"Sim: {row.nome}")
    else:
        print("NÃ£o foram encontrados agentes com ambos os papÃ©is.")

if __name__ == "__main__":
    run_queries()