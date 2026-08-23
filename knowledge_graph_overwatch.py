"""
============================================================
 KNOWLEDGE GRAPH - UNIVERSO OVERWATCH 2
 Trabalho de Estruturas de Dados: Classes, Subclasses, Mapas,
 Nacionalidades, Organizações e Habilidades dos heróis jogáveis.
============================================================

Este programa representa uma base de conhecimento em forma de grafo,
onde cada NÓ é uma entidade (herói, classe, subclasse, mapa,
nacionalidade, organização ou habilidade) e cada ARESTA é um
relacionamento tipado entre duas entidades (ex: "PERTENCE_CLASSE",
"COUNTER", "SINERGIA").

O grafo é implementado com uma lista de adjacência (dicionário de
listas), que é a estrutura mais natural para representar grafos
esparsos como este.
"""

import json


# ============================================================
# 1. ESTRUTURAS BÁSICAS: NÓ E GRAFO
# ============================================================

class No:
    """Representa uma entidade do grafo de conhecimento."""

    def __init__(self, id_no, tipo, nome, propriedades=None):
        self.id = id_no
        self.tipo = tipo                      # ex: "Heroi", "Classe", "Mapa"...
        self.nome = nome
        self.propriedades = propriedades or {}

    def __repr__(self):
        return f"<{self.tipo}: {self.nome}>"


class GrafoConhecimento:
    """
    Grafo de conhecimento implementado como lista de adjacência.

    self.nos:        dicionário  id_no -> objeto No
    self.adjacencia:  dicionário  id_no -> lista de arestas (destino, tipo_relacao, propriedades)
    """

    def __init__(self):
        self.nos = {}
        self.adjacencia = {}

    # ------------------------------------------------------
    # OPERAÇÕES SOBRE NÓS
    # ------------------------------------------------------
    def adicionar_no(self, id_no, tipo, nome, propriedades=None):
        if id_no in self.nos:
            raise ValueError(f"O nó '{id_no}' já existe no grafo.")
        self.nos[id_no] = No(id_no, tipo, nome, propriedades)
        self.adjacencia[id_no] = []

    def remover_no(self, id_no):
        if id_no not in self.nos:
            raise KeyError(f"O nó '{id_no}' não existe no grafo.")
        del self.nos[id_no]
        del self.adjacencia[id_no]
        # Remove também qualquer aresta que outros nós tenham apontando para ele
        for origem in self.adjacencia:
            self.adjacencia[origem] = [
                aresta for aresta in self.adjacencia[origem] if aresta[0] != id_no
            ]

    def consultar_no(self, id_no):
        return self.nos.get(id_no)

    def buscar_por_tipo(self, tipo):
        return [n for n in self.nos.values() if n.tipo == tipo]

    def buscar_por_nome(self, termo):
        termo = termo.lower()
        return [n for n in self.nos.values() if termo in n.nome.lower()]

    # ------------------------------------------------------
    # OPERAÇÕES SOBRE ARESTAS (RELACIONAMENTOS)
    # ------------------------------------------------------
    def adicionar_aresta(self, origem, destino, tipo_relacao, propriedades=None, bidirecional=False):
        if origem not in self.nos or destino not in self.nos:
            raise KeyError("Nó de origem ou destino inexistente.")
        self.adjacencia[origem].append((destino, tipo_relacao, propriedades or {}))
        if bidirecional:
            self.adjacencia[destino].append((origem, tipo_relacao, propriedades or {}))

    def remover_aresta(self, origem, destino, tipo_relacao=None):
        """Remove a aresta origem->destino. Se tipo_relacao for informado,
        remove apenas a aresta daquele tipo específico (pode haver mais de
        uma relação entre os mesmos dois nós, ex: COUNTER e SINERGIA)."""
        antes = len(self.adjacencia.get(origem, []))
        self.adjacencia[origem] = [
            aresta for aresta in self.adjacencia[origem]
            if not (aresta[0] == destino and (tipo_relacao is None or aresta[1] == tipo_relacao))
        ]
        return antes != len(self.adjacencia[origem])

    def consultar_relacionamentos(self, id_no, tipo_relacao=None):
        relacoes = self.adjacencia.get(id_no, [])
        if tipo_relacao:
            relacoes = [r for r in relacoes if r[1] == tipo_relacao]
        return relacoes

    # ------------------------------------------------------
    # CONSULTAS DE DOMÍNIO (específicas do universo Overwatch)
    # ------------------------------------------------------
    def buscar_counters(self, id_heroi):
        """Heróis que o herói `id_heroi` COUNTA (é forte contra)."""
        return self.consultar_relacionamentos(id_heroi, "COUNTER")

    def quem_conta_contra(self, id_heroi):
        """Busca reversa: quais heróis contam CONTRA `id_heroi`."""
        resultado = []
        for origem, arestas in self.adjacencia.items():
            for destino, tipo, props in arestas:
                if destino == id_heroi and tipo == "COUNTER":
                    resultado.append((origem, props))
        return resultado

    def buscar_sinergias(self, id_heroi):
        """Heróis que combinam bem (SINERGIA) com `id_heroi`."""
        return self.consultar_relacionamentos(id_heroi, "SINERGIA")

    def heroes_da_subclasse(self, id_subclasse):
        resultado = []
        for origem, arestas in self.adjacencia.items():
            for destino, tipo, props in arestas:
                if destino == id_subclasse and tipo == "TEM_SUBCLASSE":
                    resultado.append(origem)
        return resultado

    def heroes_da_nacionalidade(self, id_nacionalidade):
        resultado = []
        for origem, arestas in self.adjacencia.items():
            for destino, tipo, props in arestas:
                if destino == id_nacionalidade and tipo == "NACIONALIDADE":
                    resultado.append(origem)
        return resultado

    # ------------------------------------------------------
    # ESTATÍSTICAS GERAIS DO GRAFO
    # ------------------------------------------------------
    def estatisticas(self):
        por_tipo = {}
        for n in self.nos.values():
            por_tipo[n.tipo] = por_tipo.get(n.tipo, 0) + 1
        total_arestas = sum(len(v) for v in self.adjacencia.values())
        return {
            "total_de_nos": len(self.nos),
            "total_de_arestas": total_arestas,
            "nos_por_tipo": por_tipo,
        }

    # ------------------------------------------------------
    # EXPORTAÇÃO (útil para o relatório e para ferramentas externas)
    # ------------------------------------------------------
    def exportar_json(self, caminho):
        dados = {
            "nos": [
                {"id": n.id, "tipo": n.tipo, "nome": n.nome, "propriedades": n.propriedades}
                for n in self.nos.values()
            ],
            "arestas": [
                {"origem": origem, "destino": destino, "tipo": tipo, "propriedades": props}
                for origem, lista in self.adjacencia.items()
                for destino, tipo, props in lista
            ],
        }
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)


# ============================================================
# 2. CONSTRUÇÃO DA BASE DE CONHECIMENTO (dados do domínio)
# ============================================================
#
# OBS. IMPORTANTE PARA O RELATÓRIO:
# Em fevereiro de 2026 o Overwatch passou a dividir cada classe (Tanque,
# Dano, Suporte) em SUBCLASSES ("sub-roles"), cada uma com uma passiva
# própria (ex.: Bruiser, Vigia/Stalwart, Iniciador para Tanques). Como esse
# sistema é recente e pode ser rebalanceado pela Blizzard, a classificação
# de cada herói abaixo foi construída com base nas fontes oficiais
# disponíveis até a data deste trabalho — vale a pena conferir o patch
# note mais atual antes da entrega final.

def construir_base_conhecimento():
    g = GrafoConhecimento()

    # --------- CLASSES ---------
    g.adicionar_no("classe_tanque", "Classe", "Tanque")
    g.adicionar_no("classe_dano", "Classe", "Dano")
    g.adicionar_no("classe_suporte", "Classe", "Suporte")

    # --------- SUBCLASSES (introduzidas na temporada "Reign of Talon") ---------
    subclasses = [
        ("sub_bruiser", "Bruiser", "classe_tanque",
         "Reduz dano crítico recebido; ganha velocidade em vida crítica"),
        ("sub_stalwart", "Stalwart", "classe_tanque",
         "Reduz efeito de recuo (knockback) e de lentidão sofridos"),
        ("sub_iniciador", "Iniciador", "classe_tanque",
         "Cura leve enquanto está no ar (mobilidade aérea)"),
        ("sub_flanker", "Flanker", "classe_dano",
         "Kits de saúde curam uma quantidade maior de vida"),
        ("sub_specialist", "Specialist", "classe_dano",
         "Recarrega a arma mais rápido logo após um abate"),
        ("sub_sharpshooter", "Sharpshooter", "classe_dano",
         "Acertos críticos reduzem o tempo de recarga de habilidades de movimento"),
        ("sub_recon", "Recon", "classe_dano",
         "Revela inimigos com pouca vida através de paredes após causar dano"),
        ("sub_medic", "Medic", "classe_suporte",
         "Foco em cura direta e sustentação do time"),
        ("sub_tactician", "Tactician", "classe_suporte",
         "Pode acumular carga extra de ultimate, que não se perde ao usá-la"),
        ("sub_survivor", "Survivor", "classe_suporte",
         "Maior capacidade de auto-sustentação em combate corpo a corpo"),
    ]
    for id_sub, nome, id_classe, descricao in subclasses:
        g.adicionar_no(id_sub, "Subclasse", nome, {"passiva": descricao})
        g.adicionar_aresta(id_sub, id_classe, "SUBCLASSE_DE")

    # --------- ORGANIZAÇÕES ---------
    for id_org, nome in [
        ("org_overwatch", "Overwatch"),
        ("org_talon", "Talon"),
        ("org_deadlock", "Deadlock Gang"),
        ("org_shambali", "Ordem Shambali"),
        ("org_nullsector", "Null Sector"),
        ("org_horizon", "Colônia Lunar Horizon"),
    ]:
        g.adicionar_no(id_org, "Organizacao", nome)

    # --------- NACIONALIDADES / ORIGENS ---------
    nacionalidades = [
        "Alemanha", "Holanda", "Nigeria", "Australia", "Coreia do Sul", "Japao",
        "Reino Unido", "Suecia", "China", "Estados Unidos", "Franca", "Egito",
        "Mexico", "Suica", "Haiti", "Irlanda", "Brasil", "Nepal",
    ]
    for nome in nacionalidades:
        id_nac = "nac_" + nome.lower().replace(" ", "_")
        g.adicionar_no(id_nac, "Nacionalidade", nome)

    # --------- MAPAS ---------
    mapas = ["King's Row", "Hanamura", "Numbani", "Route 66", "Ilios", "Eichenwalde"]
    for nome in mapas:
        id_mapa = "mapa_" + nome.lower().replace(" ", "_").replace("'", "")
        g.adicionar_no(id_mapa, "Mapa", nome)

    # --------- HERÓIS + suas habilidades ---------
    # cada tupla: (id_heroi, nome, classe, subclasse, nacionalidade, habilidade_marcante)
    herois = [
        ("heroi_reinhardt", "Reinhardt", "classe_tanque", "sub_stalwart", "nac_alemanha", "Fúria Marcial"),
        ("heroi_sigma", "Sigma", "classe_tanque", "sub_stalwart", "nac_holanda", "Colapso Gravítico"),
        ("heroi_doomfist", "Doomfist", "classe_tanque", "sub_bruiser", "nac_nigeria", "Mão do Destino"),
        ("heroi_roadhog", "Roadhog", "classe_tanque", "sub_bruiser", "nac_australia", "Gancho de Corrente"),
        ("heroi_winston", "Winston", "classe_tanque", "sub_iniciador", "nac_estados_unidos", "Fúria Primata"),
        ("heroi_dva", "D.Va", "classe_tanque", "sub_iniciador", "nac_coreia_do_sul", "Autodestruição do Mech"),

        ("heroi_genji", "Genji", "classe_dano", "sub_flanker", "nac_japao", "Lâmina do Dragão"),
        ("heroi_tracer", "Tracer", "classe_dano", "sub_flanker", "nac_reino_unido", "Bomba Pulsante"),
        ("heroi_torbjorn", "Torbjörn", "classe_dano", "sub_specialist", "nac_suecia", "Torreta Automática"),
        ("heroi_mei", "Mei", "classe_dano", "sub_specialist", "nac_china", "Bloco de Gelo"),
        ("heroi_ashe", "Ashe", "classe_dano", "sub_sharpshooter", "nac_estados_unidos", "B.O.B."),
        ("heroi_widowmaker", "Widowmaker", "classe_dano", "sub_sharpshooter", "nac_franca", "Infra-Visão"),
        ("heroi_pharah", "Pharah", "classe_dano", "sub_recon", "nac_egito", "Barragem de Foguetes"),
        ("heroi_sombra", "Sombra", "classe_dano", "sub_recon", "nac_mexico", "EMP"),

        ("heroi_ana", "Ana", "classe_suporte", "sub_medic", "nac_egito", "Tiro de Bio-Granada"),
        ("heroi_mercy", "Mercy", "classe_suporte", "sub_medic", "nac_suica", "Ressuscitar"),
        ("heroi_zenyatta", "Zenyatta", "classe_suporte", "sub_tactician", "nac_nepal", "Transcendência"),
        ("heroi_baptiste", "Baptiste", "classe_suporte", "sub_tactician", "nac_haiti", "Campo de Imunidade"),
        ("heroi_moira", "Moira", "classe_suporte", "sub_survivor", "nac_irlanda", "Coalescência"),
        ("heroi_lucio", "Lúcio", "classe_suporte", "sub_survivor", "nac_brasil", "Barreira Sonora"),
    ]

    for id_heroi, nome, id_classe, id_sub, id_nac, habilidade in herois:
        g.adicionar_no(id_heroi, "Heroi", nome)
        g.adicionar_aresta(id_heroi, id_classe, "PERTENCE_CLASSE")
        g.adicionar_aresta(id_heroi, id_sub, "TEM_SUBCLASSE")
        g.adicionar_aresta(id_heroi, id_nac, "NACIONALIDADE")

        id_habilidade = f"habilidade_{id_heroi.split('_', 1)[1]}"
        g.adicionar_no(id_habilidade, "Habilidade", habilidade, {"heroi": nome})
        g.adicionar_aresta(id_heroi, id_habilidade, "TEM_HABILIDADE")

    # --------- VÍNCULOS COM ORGANIZAÇÕES ---------
    vinculos_organizacao = [
        ("heroi_reinhardt", "org_overwatch"),
        ("heroi_ana", "org_overwatch"),
        ("heroi_mercy", "org_overwatch"),
        ("heroi_winston", "org_overwatch"),
        ("heroi_tracer", "org_overwatch"),
        ("heroi_widowmaker", "org_talon"),
        ("heroi_sombra", "org_talon"),
        ("heroi_doomfist", "org_talon"),
        ("heroi_ashe", "org_deadlock"),
        ("heroi_zenyatta", "org_shambali"),
        ("heroi_sigma", "org_nullsector"),
        ("heroi_winston", "org_horizon"),
    ]
    for id_heroi, id_org in vinculos_organizacao:
        g.adicionar_aresta(id_heroi, id_org, "MEMBRO_DE")

    # --------- VÍNCULOS COM MAPAS (relação temática/lore) ---------
    vinculos_mapa = [
        ("heroi_genji", "mapa_hanamura"),
        ("heroi_doomfist", "mapa_numbani"),
        ("heroi_ashe", "mapa_route_66"),
        ("heroi_reinhardt", "mapa_eichenwalde"),
        ("heroi_tracer", "mapa_kings_row"),
        ("heroi_zenyatta", "mapa_ilios"),
    ]
    for id_heroi, id_mapa in vinculos_mapa:
        g.adicionar_aresta(id_heroi, id_mapa, "JOGAVEL_EM")

    # --------- RELAÇÕES DE COUNTER (X é forte contra Y) ---------
    counters = [
        ("heroi_winston", "heroi_widowmaker", "Pula na sniper e a força a fugir do campo aberto"),
        ("heroi_winston", "heroi_ashe", "Fecha a distância rapidamente contra heróis de longo alcance"),
        ("heroi_dva", "heroi_widowmaker", "Absorve tiros com Matriz de Defesa e avança sobre a sniper"),
        ("heroi_mei", "heroi_genji", "Parede de gelo interrompe mobilidade e Congelar imobiliza rapidamente"),
        ("heroi_mei", "heroi_tracer", "Congelar anula flankers de curto alcance antes que causem dano"),
        ("heroi_roadhog", "heroi_genji", "Ganchada seguida de dano corpo a corpo elimina alvos frágeis"),
        ("heroi_sombra", "heroi_widowmaker", "Hackear impede o uso da mira e do gancho de fuga"),
        ("heroi_sombra", "heroi_ana", "Hackear bloqueia granadas de cura e dardo de sono"),
        ("heroi_ana", "heroi_genji", "Dardo do Sono neutraliza a Lâmina do Dragão antes que cause dano"),
        ("heroi_reinhardt", "heroi_torbjorn", "Escudo Barreira bloqueia o fogo da torreta"),
        ("heroi_widowmaker", "heroi_roadhog", "Alcance e dano crítico alto puni tanques lentos à distância"),
        ("heroi_widowmaker", "heroi_reinhardt", "Poke de longo alcance sem risco contra tanques que avançam devagar"),
        ("heroi_baptiste", "heroi_dva", "Campo de Imunidade neutraliza mergulhos de mecha"),
        ("heroi_zenyatta", "heroi_roadhog", "Orbe da Discórdia aumenta o dano recebido e acelera o abate"),
        ("heroi_pharah", "heroi_roadhog", "Voo mantém distância seguro de um herói sem alcance vertical"),
        ("heroi_torbjorn", "heroi_genji", "Torreta automática pune flankers que se aproximam sem cobertura"),
    ]
    for id_a, id_b, motivo in counters:
        g.adicionar_aresta(id_a, id_b, "COUNTER", {"motivo": motivo})

    # --------- RELAÇÕES DE SINERGIA (combinam bem em equipe) ---------
    sinergias = [
        ("heroi_reinhardt", "heroi_zenyatta", "Escudo protege o suporte enquanto o Orbe amplifica o dano do time"),
        ("heroi_reinhardt", "heroi_mercy", "Escudo protege o alvo do Feixe de Cura, mantendo o tanque na frente"),
        ("heroi_genji", "heroi_ana", "Nano Boost potencializa o dano da Lâmina do Dragão"),
        ("heroi_genji", "heroi_zenyatta", "Refletir + Orbe da Discórdia formam um combo agressivo de dano"),
        ("heroi_dva", "heroi_moira", "Mergulho da mecha é sustentado pela cura de longo alcance da Moira"),
        ("heroi_lucio", "heroi_doomfist", "Velocidade Amplificada potencializa investidas do Doomfist"),
        ("heroi_sombra", "heroi_doomfist", "Hackear cria abertura para o combo de mobilidade do Doomfist"),
        ("heroi_pharah", "heroi_mercy", "Voo Guiado permite à Mercy amplificar o dano da Pharah no ar (Pharmercy)"),
        ("heroi_widowmaker", "heroi_sombra", "Hackear revela alvos para a sniper eliminar com segurança"),
        ("heroi_torbjorn", "heroi_reinhardt", "Escudo protege a torreta, permitindo dano constante e seguro"),
        ("heroi_baptiste", "heroi_ashe", "Campo de Imunidade protege a sniper contra investidas"),
        ("heroi_ana", "heroi_reinhardt", "Granada de Bio-cura aumenta a cura recebida pelo tanque na frente"),
    ]
    for id_a, id_b, motivo in sinergias:
        g.adicionar_aresta(id_a, id_b, "SINERGIA", {"motivo": motivo})

    return g


# ============================================================
# 3. VISUALIZAÇÃO OPCIONAL DO GRAFO (networkx + matplotlib)
# ============================================================

def visualizar_grafo(g, caminho_saida="grafo_overwatch.png", tipos_relacao=None):
    """Gera uma imagem do grafo. Por padrão desenha apenas COUNTER e
    SINERGIA entre heróis, pois desenhar todos os ~150 relacionamentos
    de uma vez deixaria a imagem ilegível."""
    try:
        import networkx as nx
        import matplotlib.pyplot as plt
    except ImportError:
        print("Bibliotecas networkx/matplotlib não encontradas; pulando visualização.")
        return

    if tipos_relacao is None:
        tipos_relacao = ["COUNTER", "SINERGIA"]

    G = nx.DiGraph()
    for id_heroi in g.buscar_por_tipo("Heroi"):
        G.add_node(id_heroi.id, label=id_heroi.nome)

    cores_aresta = []
    for origem, arestas in g.adjacencia.items():
        for destino, tipo, props in arestas:
            if tipo in tipos_relacao and origem in G.nodes and destino in G.nodes:
                G.add_edge(origem, destino, tipo=tipo)

    plt.figure(figsize=(13, 10))
    pos = nx.spring_layout(G, seed=42, k=0.9)
    labels = {n: g.nos[n].nome for n in G.nodes}

    counter_edges = [(u, v) for u, v, d in G.edges(data=True) if d["tipo"] == "COUNTER"]
    sinergia_edges = [(u, v) for u, v, d in G.edges(data=True) if d["tipo"] == "SINERGIA"]

    nx.draw_networkx_nodes(G, pos, node_color="#f2c14e", node_size=1400, edgecolors="black")
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
    nx.draw_networkx_edges(G, pos, edgelist=counter_edges, edge_color="crimson",
                            connectionstyle="arc3,rad=0.1", arrows=True)
    nx.draw_networkx_edges(G, pos, edgelist=sinergia_edges, edge_color="seagreen",
                            connectionstyle="arc3,rad=0.1", arrows=True)

    plt.title("Knowledge Graph Overwatch 2 - Counters (vermelho) e Sinergias (verde)")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    plt.close()
    print(f"Visualização salva em: {caminho_saida}")


# ============================================================
# 4. DEMONSTRAÇÃO DE USO
# ============================================================

if __name__ == "__main__":
    grafo = construir_base_conhecimento()

    print("=" * 60)
    print("ESTATÍSTICAS GERAIS DO GRAFO")
    print("=" * 60)
    stats = grafo.estatisticas()
    print(f"Total de nós: {stats['total_de_nos']}")
    print(f"Total de arestas: {stats['total_de_arestas']}")
    for tipo, qtd in stats["nos_por_tipo"].items():
        print(f"  - {tipo}: {qtd}")

    print("\n" + "=" * 60)
    print("CONSULTA: quem Genji COUNTA e quem COUNTA contra Genji")
    print("=" * 60)
    for destino, tipo, props in grafo.buscar_counters("heroi_genji"):
        print(f"Genji conta contra {grafo.nos[destino].nome}: {props['motivo']}")
    for origem, props in grafo.quem_conta_contra("heroi_genji"):
        print(f"{grafo.nos[origem].nome} conta contra Genji: {props['motivo']}")

    print("\n" + "=" * 60)
    print("CONSULTA: sinergias do Reinhardt")
    print("=" * 60)
    for destino, tipo, props in grafo.buscar_sinergias("heroi_reinhardt"):
        print(f"Reinhardt + {grafo.nos[destino].nome}: {props['motivo']}")

    print("\n" + "=" * 60)
    print("CONSULTA: heróis da subclasse Flanker")
    print("=" * 60)
    for id_heroi in grafo.heroes_da_subclasse("sub_flanker"):
        print(f"- {grafo.nos[id_heroi].nome}")

    print("\n" + "=" * 60)
    print("CONSULTA: heróis egípcios (mesma nacionalidade)")
    print("=" * 60)
    for id_heroi in grafo.heroes_da_nacionalidade("nac_egito"):
        print(f"- {grafo.nos[id_heroi].nome}")

    print("\n" + "=" * 60)
    print("DEMONSTRAÇÃO: adicionar, consultar e remover um nó")
    print("=" * 60)
    grafo.adicionar_no("heroi_wuyang", "Heroi", "Wuyang")
    grafo.adicionar_aresta("heroi_wuyang", "classe_dano", "PERTENCE_CLASSE")
    print("Nó adicionado:", grafo.consultar_no("heroi_wuyang"))
    print("Relacionamentos do Wuyang:", grafo.consultar_relacionamentos("heroi_wuyang"))
    grafo.remover_no("heroi_wuyang")
    print("Wuyang removido. Consulta agora retorna:", grafo.consultar_no("heroi_wuyang"))

    # Exporta a base para JSON (útil para anexar ao relatório)
    grafo.exportar_json("/mnt/user-data/outputs/grafo_overwatch.json")
    print("\nBase de conhecimento exportada para grafo_overwatch.json")

    # Gera a visualização (opcional)
    visualizar_grafo(grafo, "/mnt/user-data/outputs/grafo_overwatch.png")
