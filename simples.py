# Logica e base que fiz antes para entender o funcionamento de knowledge graphs, apos isso implementei
# em JS e HTML na D3.js para ficar mais visual e interativo, sem terminal e tal.


import matplotlib.pyplot as plt
import networkx as nx


class OverwatchKnowledgeGraph:
    def __init__(self):
        # Utilizando um Grafo Direcionado (DiGraph) pois relações como "Countera" têm direção.
        self.kg = nx.DiGraph()

    def adicionar_entidade(self, nome, categoria, atributos=None):
        """Adiciona um nó (vértice) ao Knowledge Graph."""
        if atributos is None:
            atributos = {}
        self.kg.add_node(nome, label=categoria, **atributos)

    def adicionar_relacionamento(self, origem, destino, tipo_relacao):
        """Adiciona uma aresta direcionada entre duas entidades."""
        self.kg.add_edge(origem, destino, type=tipo_relacao)

    def consultar_counters(self, heroi):
        """Retorna uma lista de heróis que o herói especificado countera."""
        counters = []
        if heroi in self.kg:
            for vizinho in self.kg.successors(heroi):
                if self.kg.edges[heroi, vizinho]["type"] == "COUNTERA":
                    counters.append(vizinho)
        return counters

    def consultar_sinergias(self, heroi):
        """Retorna com quem o herói tem sinergia."""
        sinergias = []
        if heroi in self.kg:
            for vizinho in self.kg.successors(heroi):
                if self.kg.edges[heroi, vizinho]["type"] == "SINERGIA_COM":
                    sinergias.append(vizinho)
        return sinergias

    def remover_entidade(self, nome):
        """Remove um nó e todas as suas arestas conectadas."""
        if nome in self.kg:
            self.kg.remove_node(nome)

    def info_grafo(self):
        """Imprime a quantidade de nós e arestas."""
        print(f"Total de Nós (Vértices): {self.kg.number_of_nodes()}")
        print(f"Total de Relacionamentos (Arestas): {self.kg.number_of_edges()}")


# Instanciando e Populando o Knowledge Graph
ow_kg = OverwatchKnowledgeGraph()

# 1. CLASSES
classes = ["Tank", "Damage", "Support"]
for c in classes:
    ow_kg.adicionar_entidade(c, "Classe")

# 2. SUBCLASSES E PASSIVAS TÁTICAS
subclasses = [
    "Role Passive Tank (Knockback Resist)",
    "Role Passive DPS (Healing Reduced)",
    "Role Passive Support (Auto-heal)",
    "Dive",
    "Brawl",
    "Poke",
]
for sc in subclasses:
    ow_kg.adicionar_entidade(sc, "Subclasse/Tatica")

# 3. ORGANIZAÇÕES E FACÇÕES
orgs = ["Overwatch", "Talon", "Shimada Clan", "MEKA", "Null Sector"]
for o in orgs:
    ow_kg.adicionar_entidade(o, "Organização")

# 4. NACIONALIDADES
nacionalidades = [
    "South Korea",
    "Germany",
    "UK",
    "Japan",
    "USA",
    "Egypt",
    "Brazil",
    "Switzerland",
    "Mexico",
    "Lunar Colony",
]
for n in nacionalidades:
    ow_kg.adicionar_entidade(n, "Nacionalidade")

# 5. MAPAS
mapas = ["Watchpoint: Gibraltar", "King's Row", "Route 66", "Ilios", "Busan"]
for m in mapas:
    ow_kg.adicionar_entidade(m, "Mapa")

# 6. HERÓIS JOGÁVEIS
herois = {
    "Winston": {
        "classe": "Tank",
        "nacionalidade": "Lunar Colony",
        "org": "Overwatch",
        "tatica": "Dive",
    },
    "D.Va": {
        "classe": "Tank",
        "nacionalidade": "South Korea",
        "org": "MEKA",
        "tatica": "Dive",
    },
    "Reinhardt": {
        "classe": "Tank",
        "nacionalidade": "Germany",
        "org": "Overwatch",
        "tatica": "Brawl",
    },
    "Tracer": {
        "classe": "Damage",
        "nacionalidade": "UK",
        "org": "Overwatch",
        "tatica": "Dive",
    },
    "Genji": {
        "classe": "Damage",
        "nacionalidade": "Japan",
        "org": "Shimada Clan",
        "tatica": "Dive",
    },
    "Cassidy": {
        "classe": "Damage",
        "nacionalidade": "USA",
        "org": "Overwatch",
        "tatica": "Brawl",
    },
    "Pharah": {
        "classe": "Damage",
        "nacionalidade": "Egypt",
        "org": "Overwatch",
        "tatica": "Poke",
    },
    "Sombra": {
        "classe": "Damage",
        "nacionalidade": "Mexico",
        "org": "Talon",
        "tatica": "Dive",
    },
    "Ana": {
        "classe": "Support",
        "nacionalidade": "Egypt",
        "org": "Overwatch",
        "tatica": "Dive",
    },
    "Lucio": {
        "classe": "Support",
        "nacionalidade": "Brazil",
        "org": "Overwatch",
        "tatica": "Brawl",
    },
    "Mercy": {
        "classe": "Support",
        "nacionalidade": "Switzerland",
        "org": "Overwatch",
        "tatica": "Poke",
    },
    "Kiriko": {
        "classe": "Support",
        "nacionalidade": "Japan",
        "org": "N/A",
        "tatica": "Brawl",
    },
}

for h, atributos in herois.items():
    ow_kg.adicionar_entidade(h, "Heroi")
    # Conectando Herói aos seus atributos base (relacionamentos estruturais)
    ow_kg.adicionar_relacionamento(h, atributos["classe"], "PERTENCE_A_CLASSE")
    ow_kg.adicionar_relacionamento(h, atributos["tatica"], "ESTILO_DE_JOGO")
    if atributos["org"] != "N/A":
        ow_kg.adicionar_relacionamento(h, atributos["org"], "MEMBRO_DA")
    ow_kg.adicionar_relacionamento(h, atributos["nacionalidade"], "ORIGEM")

# 7. RELACIONAMENTOS TÁTICOS (Counters e Sinergias)
relacoes_taticas = [
    # Counters (Quem ganha vantagem sobre quem)
    ("Winston", "Genji", "COUNTERA"),
    (
        "Winston",
        "Widowmaker",
        "COUNTERA",
    ),  # Widow nao ta na lista mas pode ser adicionada
    ("Sombra", "Winston", "COUNTERA"),
    ("Cassidy", "Tracer", "COUNTERA"),
    ("Ana", "Reinhardt", "COUNTERA"),
    ("Pharah", "Reinhardt", "COUNTERA"),
    # Sinergias (Combos famosos)
    ("Winston", "Tracer", "SINERGIA_COM"),
    ("Winston", "Genji", "SINERGIA_COM"),
    ("Pharah", "Mercy", "SINERGIA_COM"),  # Pharmercy
    ("Reinhardt", "Lucio", "SINERGIA_COM"),  # Rush
    ("Genji", "Ana", "SINERGIA_COM"),  # Nano-blade
]

for origem, destino, tipo in relacoes_taticas:
    # Garante que o destino existe antes de criar a aresta (caso de Widowmaker)
    if destino not in ow_kg.kg.nodes:
        ow_kg.adicionar_entidade(destino, "Heroi")
    ow_kg.adicionar_relacionamento(origem, destino, tipo)

# Testando as Consultas no Grafo
print("--- Análise do Knowledge Graph de Overwatch 2 ---")
ow_kg.info_grafo()

print("\n[Consulta] Quem Winston countera?")
print(ow_kg.consultar_counters("Winston"))

print("\n[Consulta] Com quem Pharah tem sinergia?")
print(ow_kg.consultar_sinergias("Pharah"))
