import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from streamlit_option_menu import option_menu
import json
from datetime import datetime
import pandas as pd

# Se puede modificar los estilos de la pagina desde aquí
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background-color: #e5e5f7;
opacity: 0.8;
background-size: 20px 20px;
}
[data-testid='stHeader']{
display: none !important;
}
[data-testid = 'stAppViewBlockContainer']{
    max-width: 1200px;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# Verifica si ya existe un estado de sesión, si no, lo crea
if "nodes" not in st.session_state:
    st.session_state["nodes"] = []
if "edges" not in st.session_state:
    st.session_state["edges"] = []
directed = False

# Crear listas de opciones para las barras de navegación
options_file = [
    "New Graph",
    "Open/Close",
    "Import/Export"
]


# Crear las barras de navegación como cajas de selección en la barra lateral
option = st.sidebar.selectbox("File", options_file)

if (option == "Open/Close"):
    selected = option_menu(
        menu_title=None,
        options= ["Open", "Close"],
        default_index=0,
        icons=["list-task", 'gear'],
        orientation = "horizontal",
        styles= {
        
        }   
    )
elif (option == "Import/Export"):
    selected = option_menu(
        menu_title=None,
        options= ["Export", "Import", "Export to XLSX"],
        default_index=0,
        icons=["list-task", 'gear'],
        orientation = "horizontal",
        styles= {
        
        }   
    )
elif (option == "Save"):
    selected = option_menu(
        menu_title=None,
        options= ["Save", "Save As",],
        default_index=0,
        icons=["list-task", 'gear'],
        orientation = "horizontal",
        styles= {
        
        }   
    )
else:
    selected = "New Graph"

# Si el usuario selecciona 'New Graph', muestra otro selectbox con las opciones 'Personalizado' y 'Aleatorio'
if selected == "New Graph":
    options_graph = ["Select", "Personalizado", "Aleatorio"]
    graph_option = st.sidebar.selectbox("Choose", options_graph)

    if graph_option == "Personalizado":
        directed = st.checkbox("Dirigido", value=False)
        directed = st.checkbox("Ponderado", value=False)
        if directed == "Dirigido":
            directed = True


# Muestra el formulario correspondiente cuando se selecciona una opción
if selected == "Agregar nodo":
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

elif selected == "Agregar arista":
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

elif selected == "Import":
    uploaded_file = st.sidebar.file_uploader("Elige un archivo JSON", type="json")
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

elif selected == "Export":
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

    # Obtener la hora actual
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    st.download_button(
        label="Descargar JSON",
        data=json_str,
        file_name="graph-" + current_time + ".json",
        mime="application/json",
    )

elif selected == "Guardar Como":
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
    name = st.text_input("Nombre del archivo")

    st.download_button(
        label="Descargar JSON",
        data=json_str,
        file_name=name + ".json",
        mime="application/json",
    )


elif selected == "Export to XLSX":
    # Crea una lista para almacenar los datos de los nodos
    nodes_data = []

    # Recorre cada nodo y arista en el estado de la sesión
    for node in st.session_state["nodes"]:
        linked_nodes = [
            {"node_id": edge.to, "weight": edge.label}
            for edge in st.session_state["edges"]
            if edge.source == node.id
        ]
        # Agrega los datos del nodo a la lista
        nodes_data.append(
            {
                "id": node.id,
                "label": node.label,
                "data": {},
                "type": "",
                "linkedTo": ", ".join(
                    [
                        f"(node_id: {ln['node_id']}) (weight: {ln['weight']})"
                        for ln in linked_nodes
                    ]
                ),
                "radius": node.size / 50,
                "coordinates": {"x": 0, "y": 0},
            }
        )

    # Crea un DataFrame para los nodos
    nodes_df = pd.DataFrame(nodes_data)

    # Escribe el DataFrame a un archivo de Excel
    nodes_df.to_excel("graph.xlsx", index=False)


# Crea tu configuración
config = Config(
    width="100%",
    height=950,
    directed=directed,
    physics=False,
    hierarchical=True,
)

# Dibuja tu gráfico
return_value = agraph(
    nodes=st.session_state["nodes"], edges=st.session_state["edges"], config=config
)
