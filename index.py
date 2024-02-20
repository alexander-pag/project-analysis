import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json


# Verifica si ya existe un estado de sesión, si no, lo crea
if "nodes" not in st.session_state:
    st.session_state["nodes"] = []
if "edges" not in st.session_state:
    st.session_state["edges"] = []

# Crea un menú desplegable con diferentes opciones
option = st.selectbox(
    "Elige una opción:",
    ("", "Agregar nodo", "Agregar arista", "Leer JSON", "Exportar a JSON"),
)

# Muestra el formulario correspondiente cuando se selecciona una opción
if option == "Agregar nodo":
    node_id = st.text_input("ID del Nodo")
    node_label = st.text_input("Etiqueta del Nodo")
    node_image = st.text_input("URL de la Imagen del Nodo")

    if node_image == "":
        node_image = "https://github.com/github.png?size=460"

    if st.button("Agregar"):
        new_node = Node(
            id=node_id,
            label=node_label,
            size=25,
            shape="circularImage",
            image=node_image,
        )

        st.session_state["nodes"].append(new_node)

elif option == "Agregar arista":
    source = st.selectbox(
        "Nodo de origen", [node.id for node in st.session_state["nodes"]]
    )
    target = st.selectbox(
        "Nodo de destino", [node.id for node in st.session_state["nodes"]]
    )
    edge_label = st.text_input("Etiqueta de la arista")

    if st.button("Agregar"):
        new_edge = Edge(source=source, target=target, label=edge_label)
        st.session_state["edges"].append(new_edge)

elif option == "Leer JSON":

    uploaded_file = st.file_uploader("Elige un archivo JSON", type="json")
    if uploaded_file is not None:
        data = json.load(uploaded_file)

        for graph in data["graph"]:
            for node_data in graph["data"]:
                node = Node(
                    id=node_data["id"],
                    label=node_data["label"],
                    size=node_data["radius"]
                    * 50,  # Ajusta el tamaño según tus necesidades
                    shape="circularImage",
                    image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png",  # Ajusta la imagen según tus necesidades
                )
                st.session_state["nodes"].append(node)

                for linked_node in node_data["linkedTo"]:
                    edge = Edge(
                        source=node.id,
                        target=linked_node["node_id"],
                        label=str(linked_node["weight"]),
                    )
                    st.session_state["edges"].append(edge)

elif option == "Exportar a JSON":
    graph_data = {
        "graph": [
            {
                "name": "G",
                "data": [],
                "generalData1": 100,
                "generalData2": "Alg",
                "generalData3": 300,
            }
        ]
    }

    for node in st.session_state["nodes"]:
        linked_nodes = []
        for edge in st.session_state["edges"]:
            if edge.source == node.id:
                linked_nodes.append({"node_id": edge.to, "weight": int(edge.label)})
        node_data = {
            "id": node.id,
            "label": node.label,
            "data": {},
            "type": "",
            "linkedTo": linked_nodes,
            "radius": node.size / 50,
            "coordinates": {"x": 0, "y": 0},
        }
        graph_data["graph"][0]["data"].append(node_data)

    # Convierte el objeto del grafo a una cadena JSON
    json_str = json.dumps(graph_data)

    # Crea un botón de descarga para el archivo JSON
    st.download_button(
        label="Descargar JSON",
        data=json_str,
        file_name="graph.json",
        mime="application/json",
    )

# Crea tu configuración
config = Config(
    width=750, height=950, directed=False, physics=False, hierarchical=False
)

# Dibuja tu gráfico
return_value = agraph(
    nodes=st.session_state["nodes"], edges=st.session_state["edges"], config=config
)
