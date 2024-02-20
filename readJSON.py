import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json

# Carga los datos del archivo JSON
with open("read.json", "r") as f:
    data = json.load(f)

# Asegúrate de que los datos estén en el formato correcto
nodes = []
edges = []
for graph in data["graph"]:
    for node_data in graph["data"]:
        node = Node(
            id=node_data["id"],
            label=node_data["label"],
            size=node_data["radius"] * 100,  # Ajusta el tamaño según tus necesidades
            shape="circularImage",
            image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png",  # Ajusta la imagen según tus necesidades
        )
        nodes.append(node)

        for linked_node in node_data["linkedTo"]:
            edge = Edge(
                source=node.id, label="linked_to", target=linked_node["node_id"]
            )
            edges.append(edge)

# Actualiza el estado de la sesión con los nuevos nodos y aristas
st.session_state["nodes"] = nodes
st.session_state["edges"] = edges

# Crea tu configuración
config = Config(width=750, height=950, directed=True, physics=False, hierarchical=False)

# Dibuja tu gráfico
return_value = agraph(
    nodes=st.session_state["nodes"], edges=st.session_state["edges"], config=config
)
