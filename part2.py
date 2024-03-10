import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import networkx as nx

# Crear 5 nodos con id y label
nodes = [
    Node(id="A", label="Node A"),
    Node(id="B", label="Node B"),
    Node(id="C", label="Node C"),
    Node(id="D", label="Node D"),
    Node(id="E", label="Node E"),
]

# Crear 5 aristas con origen, destino y label
edges = [
    Edge(source="A", target="C", label="Edge A-C"),
    Edge(source="B", target="C", label="Edge B-C"),
    Edge(source="A", target="D", label="Edge A-D"),
    Edge(source="B", target="E", label="Edge B-E"),
    Edge(source="A", target="E", label="Edge A-E"),
]

# Crear configuración
config = Config(width=500, height=500, directed=True, physics=False)

# Crear gráfico
st.title("Graph")
agraph(nodes=nodes, edges=edges, config=config)

# Determinar si el grafo corresponde a un grafo bipartito o no
# Crear lista de adyacencia
adj = {node.id: [] for node in nodes}
for edge in edges:
    adj[edge.source].append(edge.to)
    adj[edge.to].append(edge.source)

# Crear lista de nodos visitados
visited = {node.id: False for node in nodes}

# Crear lista de colores
colors = {node.id: -1 for node in nodes}


# Función para determinar si el grafo es bipartito
def is_bipartite(node, color):
    visited[node] = True
    colors[node] = color
    for neighbor in adj[node]:
        if not visited[neighbor]:
            if not is_bipartite(neighbor, 1 - color):
                return False
        elif colors[neighbor] == colors[node]:
            return False
    return True


# Verificar si el grafo es bipartito
bipartite = True
for node in nodes:
    if not visited[node.id]:
        bipartite = is_bipartite(node.id, 0)
        if not bipartite:
            break

# Mostrar resultado
if bipartite:
    st.write("The graph is bipartite")
else:
    st.write("The graph is not bipartite")


# Crear lista de nodos visitados
visited = {node.id: False for node in nodes}

# Crear lista de componentes
components = []


# Función para determinar si el grafo es conexo
def is_connected(node):
    visited[node] = True
    components[-1].append(node)
    for neighbor in adj[node]:
        if not visited[neighbor]:
            is_connected(neighbor)


# Verificar si el grafo es conexo
for node in nodes:
    if not visited[node.id]:
        components.append([])
        is_connected(node.id)

# Mostrar resultado
if len(components) == 1:
    st.write("The graph has only one connected component")
else:
    st.write("The graph has", len(components), "connected components")
    for i, component in enumerate(components):
        st.write("Component", i + 1, ":", component)


# Crear un grafo a partir de los nodos y aristas
G = nx.Graph()
for node in nodes:
    G.add_node(node.id)
for edge in edges:
    G.add_edge(edge.source, edge.to)


# Función para determinar si un grafo es conexo
def is_connected(G):
    return nx.is_connected(G)


# Función para obtener las componentes de un grafo disconexo
def get_components(G):
    return [c for c in nx.connected_components(G)]


# Eliminar una arista
G.remove_edge("A", "C")
G.remove_edge("B", "C")


# Eliminar la misma arista de la lista de aristas
for edge in edges:
    if edge.source == "A" and edge.to == "C":
        edges.remove(edge)
        break
for edge in edges:
    if edge.source == "B" and edge.to == "C":
        edges.remove(edge)
        break

# Crear gráfico después de la eliminación
st.title("Graph after removal")
agraph(nodes=nodes, edges=edges, config=config)

# Verificar si el grafo es conexo
if is_connected(G):
    st.write("El grafo es conexo.")
else:
    st.write("El grafo es disconexo.")
    # Mostrar las componentes del grafo disconexo
    components = get_components(G)
    for i, component in enumerate(components):
        st.write(f"Componente {i+1}: {component}")


"""
# Determinar si el grafo corresponde a un grafo bipartito o no
            # Crear lista de adyacencia
            adj = {node.id: [] for node in st.session_state["nodes"]}
            for edge in st.session_state["edges"]:
                adj[edge.source].append(edge.to)
                adj[edge.to].append(edge.source)

            # Crear lista de nodos visitados
            visited = {node.id: False for node in st.session_state["nodes"]}

            # Crear lista de colores
            colors = {node.id: -1 for node in st.session_state["nodes"]}

            # Función para determinar si el grafo es bipartito
            def is_bipartite(node, color):
                visited[node] = True
                colors[node] = color
                for neighbor in adj[node]:
                    if not visited[neighbor]:
                        if not is_bipartite(neighbor, 1 - color):
                            return False
                    elif colors[neighbor] == colors[node]:
                        return False
                return True

            # Verificar si el grafo es bipartito
            bipartite = True
            for node in st.session_state["nodes"]:
                if not visited[node.id]:
                    bipartite = is_bipartite(node.id, 0)
                    if not bipartite:
                        break

            # Mostrar resultado
            if bipartite:
                st.write("El grafo es bipartito")
            else:
                st.write("El grafo no es bipartito")
"""
