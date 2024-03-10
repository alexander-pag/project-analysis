import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from streamlit_option_menu import option_menu
import json
from datetime import datetime
import pandas as pd
import pyautogui as pg
import io
from Utils import Utils
import networkx as nx
import copy

U = Utils()

css = U.load_css()
st.markdown(css, unsafe_allow_html=True)

# Verifica si ya existe un estado de sesión, si no, lo crea
default_session_state = {
    "graph": False,
    "nodes": [],
    "copy_nodes": [],
    "edges": [],
    "copy_edges": [],
    "directed": False,
    "weighted": False,
    "conex": False,
    "connected": False,
    "name_graph": "",
    "last_action": "a"
}

for key, value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Crear listas de opciones para las barras de navegación
options_file = ["Archivo", "Editar", "Ejecutar", "Herramientas", "Ayuda"]
# Crear las barras de navegación como cajas de selección en la barra lateral
option = st.sidebar.selectbox("File", options_file)

if option == "Archivo":
    opcionesArchivo = [
        "Nuevo grafo",
        "Open/Close",
        "Guardar Como",
        "Import/Export",
        "Salir",
    ]
    selected = option_menu(
        menu_title=None,
        options=opcionesArchivo,
        default_index=0,
        icons=["plus-circle", "gear", "download", "file-earmark", "x-square"],
        orientation="horizontal",
        styles={},
    )

    if selected == "Guardar Como":
        json_str = U.generate_graph_json(st.session_state["nodes"], st.session_state["edges"])
        U.create_download_button(json_str)

    elif selected == "Open/Close":
        selected1 = option_menu(
            menu_title=None,
            options=["Open", "Close"],
            default_index=0,
            icons=["envelope-open", "x-square"],
            orientation="horizontal",
            styles={},
        )

        if selected1 == "Open":
            uploaded_file = st.sidebar.file_uploader(
                "Elige un archivo JSON", type="json"
            )
            if uploaded_file is not None:
                data = json.load(uploaded_file)

                U.open_json_file(data)

        elif selected1 == "Close":
            st.session_state["nodes"] = []
            st.session_state["edges"] = []

    elif selected == "Import/Export":
        selectedIE = option_menu(
            menu_title=None,
            options=["Export", "Import", "Export to XLSX", "Export to image"],
            default_index=0,
            icons=["list-task", "filetype-txt", "filetype-xlsx", "card-image"],
            orientation="horizontal",
            styles={},
        )

        if selectedIE == "Import":
            uploaded_file = st.sidebar.file_uploader(
                "Elige un archivo JSON", type="json"
            )
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

        elif selectedIE == "Export to image":
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

        elif selectedIE == "Export to XLSX":
            # Crea una lista para almacenar los datos de los nodos
            nodes_data = []

            # Recorre cada nodo y arista en el estado de la sesión
            for node in st.session_state["nodes"]:
                linked_nodes = [
                    {"node_id": edge.to, "weight": edge.label, "color": edge.color}
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
                                f"(node_id: {ln['node_id']}) (weight: {ln['weight']}) (color: {ln['color']})"
                                for ln in linked_nodes
                            ]
                        ),
                        "radius": node.size / 50,
                        "coordinates": {"x": 0, "y": 0},
                    }
                )

            # Crea un DataFrame para los nodos
            nodes_df = pd.DataFrame(nodes_data)

            # Crea un objeto BytesIO para guardar el archivo XLSX
            buf = io.BytesIO()

            # Guarda los datos de los nodos en un archivo XLSX
            nodes_df.to_excel(buf, index=False)

            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Crea un botón de descarga para el archivo XLSX
            st.download_button(
                label="Descargar XLSX",
                data=buf.getvalue(),
                file_name="graph-" + date + ".xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    if selected == "Nuevo grafo":
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
                U.add_node_to_graph("Agregar Nodo")

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

                        st.session_state["last_action"] = "New Node"

        if graph_option == "Aleatorio":
            # Crear un expander para el grafo en la barra lateral
            with st.sidebar.expander("Grafo"):
                with st.form(key="graph_form"):
                    # Campo de texto para introducir el nombre del grafo
                    st.session_state["name_graph"] = st.text_input("Nombre del Grafo")

                    # Checkbox para elegir si el grafo es dirigido
                    st.session_state["directed"] = st.checkbox("¿Es dirigido?")

                    # Checkbox para elegir si el grafo es ponderado
                    st.session_state["weighted"] = st.checkbox("¿Es ponderado?")

                    # Checkbox para elegir si el grafo es completo
                    st.session_state["connected"] = st.checkbox("¿Es completo?")

                    # Checkbox para elegir si el grafo es conexo
                    st.session_state["conex"] = st.checkbox("¿Es conexo?")

                    # Campo de texto para introducir la cantidad de nodos
                    node_qty = st.text_input("Cantidad de nodos")

                    # Botón para generar el grafo
                    generate_graph = st.form_submit_button(label="Generar")

                    if generate_graph:
                        if st.session_state["connected"] and st.session_state["conex"]:
                            # Crear un grafo aleatorio conexo y completo
                            G = nx.connected_watts_strogatz_graph(
                                int(node_qty), int(node_qty) - 1, 0.5, tries=100
                            )
                        elif st.session_state["connected"]:
                            # Crear un grafo aleatorio completo
                            G = nx.complete_graph(int(node_qty))
                        elif st.session_state["conex"]:
                            # Crear un grafo aleatorio conexo
                            G = nx.connected_watts_strogatz_graph(
                                int(node_qty), int(node_qty) // 2, 0.5, tries=100
                            )
                        else:
                            # Crear un grafo aleatorio
                            G = nx.gnp_random_graph(
                                int(node_qty),
                                0.5,
                                directed=st.session_state["directed"],
                            )

                        # Convertir el grafo de networkx a formato agraph
                        nodes = [
                            Node(
                                label="Nodo " + str(n),
                                id=n,
                                color=U.generateColor(),
                                shape=U.generateShape(),
                            )
                            for n in G.nodes()
                        ]
                        if st.session_state["weighted"]:
                            edges = [
                                Edge(
                                    source=e[0],
                                    target=e[1],
                                    label=str(U.generateWeight()),
                                    color=U.generateColor(),
                                )
                                for e in G.edges()
                            ]
                        else:
                            edges = [
                                Edge(
                                    source=e[0],
                                    target=e[1],
                                    color=U.generateColor(),
                                    label="",
                                )
                                for e in G.edges()
                            ]

                        # Guardar los nodos y aristas en el estado de sesión
                        st.session_state["nodes"] = nodes
                        st.session_state["edges"] = edges

                        st.session_state["graph"] = True
                        st.session_state["last_action"] = "New Node"


elif option == "Editar":
    opcionesEditar = [
        "Nodo",
        "Arista",
        "Deshacer",
    ]
    selected = option_menu(
        menu_title=None,
        options=opcionesEditar,
        default_index=0,
        icons=["list-task", "gear", "x-square"],
        orientation="vertical",
        styles={},
    )

    if selected == "Nodo":
        selected = option_menu(
            menu_title=None,
            options=["Agregar Nodo", "Editar Nodo", "Eliminar Nodo"],
            default_index=0,
            icons=["list-task", "gear"],
            orientation="horizontal",
            styles={},
        )
        if selected == "Agregar Nodo":
            U.add_node_to_graph(selected)

        elif selected == "Editar Nodo":
            U.add_node_to_graph(selected)

        elif selected == "Eliminar Nodo":
            node_id = st.sidebar.selectbox(
                "Seleccione nodo: ",
                [node.id for node in st.session_state["nodes"]],
            )

            actual_node = next((node for node in st.session_state["nodes"] if node.id == node_id), None)

            if st.sidebar.button("Eliminar"):

                st.session_state["copy_nodes"] = copy.deepcopy(
                    st.session_state["nodes"]
                )

                st.session_state["nodes"].remove(actual_node)

                st.session_state["last_action"] = "Delete Node"

    elif selected == "Arista":
        selected = option_menu(
            menu_title=None,
            options=["Agregar Arista", "Editar Arista", "Eliminar Arista"],
            default_index=0,
            icons=["list-task", "gear"],
            orientation="horizontal",
            styles={},
        )
        if selected == "Agregar Arista":
            st.session_state["copy_edges"] = copy.deepcopy(st.session_state["edges"])

            source = st.sidebar.selectbox(
                "Nodo de inicio de la arista",
                [node.id for node in st.session_state["nodes"]],
            )
            target = st.sidebar.selectbox(
                "Nodo final de la arista",
                [node.id for node in st.session_state["nodes"]],
            )

            edge_label = ""
            if st.session_state["weighted"]:
                # Campo de texto para introducir la etiqueta de la arista
                edge_label = st.sidebar.text_input("Etiqueta de la arista")
            else:
                edge_label = ""

            edge_color = st.sidebar.color_picker("Color de la arista")

            if st.sidebar.button("Agregar"):
                new_edge = Edge(
                    source=source, target=target, label=edge_label, color=edge_color
                )
                st.session_state["edges"].append(new_edge)
                st.session_state["last_action"] = "New Edge"

        elif selected == "Editar Arista":
            actual_source = st.sidebar.selectbox(
                "Seleccione arista: ",
                [(edge.source, edge.to) for edge in st.session_state["edges"]],
            )

            for edge in st.session_state["edges"]:
                if edge.source == actual_source[0] and edge.to == actual_source[1]:
                    actual_edge = edge

            st.sidebar.write(actual_source)

            edge_label = ""
            if st.session_state["weighted"]:
                # Campo de texto para introducir la etiqueta de la arista
                edge_label = st.sidebar.text_input(
                    "Etiqueta de la arista", actual_edge.label
                )

            edge_color = st.sidebar.color_picker(
                "Color de la arista", actual_edge.color
            )

            if st.sidebar.button("Cambiar Arista"):

                st.session_state["copy_edges"] = copy.deepcopy(
                    st.session_state["edges"]
                )

                index = st.session_state["edges"].index(actual_edge)

                st.session_state["edges"][index].label = edge_label
                st.session_state["edges"][index].color = edge_color

                st.session_state["last_action"] = "Edit Edge"

        elif selected == "Eliminar Arista":
            actual_source = st.sidebar.selectbox(
                "Seleccione arista: ",
                [(edge.source, edge.to) for edge in st.session_state["edges"]],
            )

            actual_edge = next((edge for edge in st.session_state["edges"] if edge.source == actual_source[0] and edge.to == actual_source[1]), None)

            if st.sidebar.button("Eliminar"):

                st.session_state["edges"].remove(actual_edge)
                st.session_state["last_action"] = "Delete Edge"

    elif selected == "Deshacer":
    # Deshacer el último cambio en los nodos o las aristas
        last_action = st.session_state.get("last_action")
        if last_action:
            if last_action in ["New Node", "Delete Node", "Edit Node"]:
                st.session_state["nodes"] = copy.deepcopy(st.session_state["copy_nodes"])
            elif last_action in ["New Edge", "Delete Edge", "Edit Edge"]:
                st.session_state["edges"] = copy.deepcopy(st.session_state["copy_edges"])

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
