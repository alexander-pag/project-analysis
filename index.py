import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from streamlit_option_menu import option_menu
import json
from datetime import datetime
import pandas as pd
import pyautogui as pg
import io

# Se puede modificar los estilos de la pagina desde aquí
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background-color: #FFF6F6;
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
if "graph" not in st.session_state:
    st.session_state["graph"] = False
if "nodes" not in st.session_state:
    st.session_state["nodes"] = []
if "edges" not in st.session_state:
    st.session_state["edges"] = []
if "directed" not in st.session_state:
    st.session_state["directed"] = False
if "weighted" not in st.session_state:
    st.session_state["weighted"] = False
if "name_graph" not in st.session_state:
    st.session_state["name_graph"] = ""


# Crear listas de opciones para las barras de navegación
options_file = ["New Graph", "Open/Close", "Import/Export"]


# Crear las barras de navegación como cajas de selección en la barra lateral
option = st.sidebar.selectbox("File", options_file)

if option == "Open/Close":
    selected = option_menu(
        menu_title=None,
        options=["Open", "Close"],
        default_index=0,
        icons=["list-task", "gear"],
        orientation="horizontal",
        styles={},
    )
    if selected == "Open":
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
    else:
        st.session_state["nodes"] = []
        st.session_state["edges"] = []

elif option == "Import/Export":
    selected = option_menu(
        menu_title=None,
        options=["Export", "Import", "Export to XLSX", "Export to image"],
        default_index=0,
        icons=["list-task", "gear"],
        orientation="horizontal",
        styles={},
    )


elif option == "Save":
    selected = option_menu(
        menu_title=None,
        options=[
            "Save",
            "Save As",
        ],
        default_index=0,
        icons=["list-task", "gear"],
        orientation="horizontal",
        styles={},
    )
else:
    selected = "New Graph"

# Si el usuario selecciona 'New Graph', muestra otro selectbox con las opciones 'Personalizado' y 'Aleatorio'
if selected == "New Graph":
    options_graph = ["Select", "Personalizado", "Aleatorio"]
    graph_option = st.sidebar.selectbox("Choose", options_graph)

    if graph_option == "Personalizado":
        # Crear un expander para el grafo en la barra lateral
        with st.sidebar.expander("Grafo"):
            # Campo de texto para introducir el nombre del grafo
            name = st.text_input("Nombre del grafo")

            # Checkbox para elegir si el grafo es dirigido
            directed = st.checkbox("¿Es dirigido?")

            # Checkbox para elegir si el grafo es ponderado
            weighted = st.checkbox("¿Es ponderado?")

            # Botón para crear el grafo
            create_graph = st.button("Crear grafo")

            if create_graph:
                st.session_state["graph"] = True
                st.session_state["directed"] = directed
                st.session_state["weighted"] = weighted
                st.session_state["name_graph"] = name

        # Si existe un grafo, mostrar los widgets para el nodo
        if st.session_state["graph"]:
            # Crear un expander para el nodo en la barra lateral
            with st.sidebar.expander("Nodo"):
                # Campo de texto para introducir el ID del nodo
                node_id = st.text_input("ID del nodo")

                # Campo de texto para introducir el nombre del nodo
                node_name = st.text_input("Nombre del nodo")

                # Selector de color para elegir el color del nodo
                node_color = st.color_picker("Color del nodo")

                # Selector de forma del nodo, como diccionario
                node_shape = st.selectbox(
                    "Forma del nodo",
                    [
                        "diamond",
                        "dot",
                        "square",
                        "star",
                        "triangle",
                        "triangleDown",
                    ],
                )

                # Botón para agregar el nodo al grafo
                add_node_button = st.button("Agregar nodo")

                if add_node_button:
                    new_node = Node(
                        id=node_id,
                        label=node_name,
                        size=25,
                        shape=node_shape,
                        # image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png",
                        color=node_color,
                    )

                    st.session_state["nodes"].append(new_node)

        if len(st.session_state["nodes"]) > 1:
            # Crear un expander para la arista en la barra lateral
            with st.sidebar.expander("Arista"):
                # Crear un formulario para la arista
                with st.form(key="edge_form"):
                    # Campo de texto para introducir el nodo de inicio de la arista
                    edge_start = st.selectbox(
                        "Nodo de inicio de la arista",
                        [node.id for node in st.session_state["nodes"]],
                    )

                    # Campo de texto para introducir el nodo final de la arista
                    edge_end = st.selectbox(
                        "Nodo final de la arista",
                        [node.id for node in st.session_state["nodes"]],
                    )

                    edge_label = ""
                    if st.session_state["weighted"]:
                        # Campo de texto para introducir la etiqueta de la arista
                        edge_label = st.text_input("Etiqueta de la arista")
                    else:
                        edge_label = ""

                    edge_color = st.color_picker("Color de la arista")

                    # Botón para agregar la arista al grafo
                    add_edge_button = st.form_submit_button(label="Agregar arista")

                    if add_edge_button:
                        if st.session_state["directed"]:
                            new_edge = Edge(
                                source=edge_start,
                                target=edge_end,
                                label=edge_label,
                                color=edge_color,
                            )
                            st.session_state["edges"].append(new_edge)

                        else:
                            new_edge_1 = Edge(
                                source=edge_start,
                                target=edge_end,
                                label=edge_label,
                                color=edge_color,
                            )

                            new_edge_2 = Edge(
                                source=edge_end,
                                target=edge_start,
                                label=edge_label,
                                color=edge_color,
                            )
                            st.session_state["edges"].append(new_edge_1)
                            st.session_state["edges"].append(new_edge_2)

                    st.write(st.session_state["edges"])

    if graph_option == "Aleatorio":
        pass


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

    # Determinar si el grafo es bipartito o no
    is_bipartite = True
    for edge in st.session_state["edges"]:
        if edge.source == edge.to:
            is_bipartite = False
            break

    if is_bipartite:
        st.write("El grafo es bipartito")

elif selected == "Export":
    graph_data = {
        "graph": [
            {
                "name": (
                    st.session_state["name_graph"]
                    if st.session_state["name_graph"]
                    else "Grafo"
                ),
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
                linked_nodes.append(
                    {"node_id": edge.to, "weight": int(edge.label) if edge.label else 0}
                )
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

    name = ""
    if st.session_state["name_graph"]:
        name = st.session_state["name_graph"]
    else:
        name = "graph"

    st.download_button(
        label="Descargar JSON",
        data=json_str,
        file_name=(name + current_time + ".json"),
        mime="application/json",
    )

elif selected == "Export to image":
    # Definir las coordenadas del área de la captura de pantalla
    x, y, width, height = 580, 320, 1150, 720

    # Tomar la captura de pantalla
    screenshot = pg.screenshot(region=(x, y, width, height))

    # Crear un objeto BytesIO para guardar la imagen
    buf = io.BytesIO()

    # Guardar la captura de pantalla en el objeto BytesIO
    screenshot.save(buf, format="png")

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Crear un botón de descarga para la imagen
    st.download_button(
        label="Descargar captura de pantalla",
        data=buf.getvalue(),
        file_name="graph-" + date + ".png",
        mime="image/png",
    )


elif selected == "Guardar Como":
    graph_data = {
        "graph": [
            {
                "name": (
                    st.session_state["name_graph"]
                    if st.session_state["name_graph"]
                    else "Grafo"
                ),
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
                linked_nodes.append(
                    {"node_id": edge.to, "weight": int(edge.label) if edge.label else 0}
                )
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
    height=600,
    directed=st.session_state["directed"],
    physics=False,
    hierarchical=True,
)

# Dibuja tu gráfico
return_value = agraph(
    nodes=st.session_state["nodes"], edges=st.session_state["edges"], config=config
)
