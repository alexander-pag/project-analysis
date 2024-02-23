import networkx as nx
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# Crear un grafo conexo aleatorio con networkx
G = nx.connected_watts_strogatz_graph(n=5, k=2, p=0.1)

# Convertir el grafo de networkx a formato agraph
nodes = [Node(str(n)) for n in G.nodes()]
edges = [Edge(str(u), str(v)) for u, v in G.edges()]

# Configuración del grafo para la visualización
config = Config(width=500, height=500, directed=False, physics=False)

# Visualizar el grafo en Streamlit
agraph(nodes=nodes, edges=edges, config=config)
