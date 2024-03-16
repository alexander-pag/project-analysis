import random
import datetime
import json
import streamlit as st
from streamlit_agraph import agraph, Node, Edge
import copy
import pyautogui as pg
import io
from datetime import datetime
import pandas as pd
import networkx as nx


class Utils:
    def createRandomString(self):
        characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        return "".join(random.choice(characters) for i in range(8))

    def createRandomId(self):
        characters = "1234567890"
        return "".join(random.choice(characters) for i in range(4))

    def getDateTime(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generateColor(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def generateDate(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generateShape(self):
        shapes = [
            "dot",
            "star",
            "triangle",
            "triangleDown",
            "hexagon",
            "square",
        ]
        return random.choice(shapes)

    def generateWeight(self):
        return random.randint(1, 100)

    def load_css(self):
        with open("styles.css") as f:
            css = f"<style>{f.read()}</style>"
        return css

    def generate_graph_json(self, nodes, edges):
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
                    "isDirected": st.session_state["directed"],
                    "isWeighted": st.session_state["weighted"],
                    "isConnected": st.session_state["connected"],
                    "isConex": st.session_state["conex"],
                }
            ]
        }

        for node in nodes:
            linked_nodes = []
            # Añadir los nodos que tengan una arista con el nodo actual
            for edge in edges:
                if int(edge.source) == node.id:
                    linked_nodes.append(
                        {
                            "node_id": edge.to,
                            "weight": int(edge.label) if edge.label else 0,
                            "color": edge.color,
                        }
                    )

            node_data = {
                "id": node.id,
                "label": node.label,
                "color": node.color,
                "shape": node.shape,
                "data": {},
                "type": "",
                "linkedTo": linked_nodes,
                "radius": node.size,
                "coordinates": {"x": 0, "y": 0},
            }
            graph_data["graph"][0]["data"].append(node_data)

        # Convierte el objeto del grafo a una cadena JSON
        return json.dumps(graph_data)

    def create_download_button(self, json_str):
        name = st.sidebar.text_input("Nombre del archivo")
        st.sidebar.download_button(
            label="Descargar JSON",
            data=json_str,
            file_name=name + ".json",
            mime="application/json",
        )

    def open_json_file(self, data):
        for graph in data["graph"]:
            for node_data in graph["data"]:
                node = Node(
                    id=node_data["id"],
                    label=node_data["label"],
                    color=node_data["color"],
                    shape=node_data["shape"],
                    size=15,
                )
                st.session_state["nodes"].append(node)

                for linked_node in node_data["linkedTo"]:
                    edge = Edge(
                        source=node.id,
                        target=linked_node["node_id"],
                        color=linked_node["color"],
                        label=(
                            str(linked_node["weight"]) if linked_node["weight"] else ""
                        ),
                    )
                    st.session_state["edges"].append(edge)

    def add_node_to_graph(self, selected):
        if selected == "Eliminar Nodo" and st.session_state["graph"]:
            node_id = st.sidebar.selectbox(
                "Seleccione nodo: ",
                [node.id for node in st.session_state["nodes"]],
            )

            actual_node = next(
                (node for node in st.session_state["nodes"] if node.id == node_id),
                None,
            )

            if st.sidebar.button("Eliminar"):

                st.session_state["copy_nodes"] = copy.deepcopy(
                    st.session_state["nodes"]
                )

                st.session_state["nodes"].remove(actual_node)

                st.session_state["last_action"] = "Delete Node"

        elif selected == "Agregar Nodo" or selected == "Editar Nodo":
            with st.sidebar.expander("Nodo"):
                # Campo de texto para introducir el ID del nodo
                list = [
                    "diamond",
                    "dot",
                    "square",
                    "star",
                    "triangle",
                    "triangleDown",
                ]
                if selected == "Agregar Nodo" and st.session_state["graph"]:
                    node_id = st.text_input("ID del nodo")
                    actual_node = None
                    index = 0
                elif selected == "Editar Nodo":
                    if st.session_state["graph"]:
                        node_id = st.selectbox(
                            "Seleccione nodo: ",
                            [node.id for node in st.session_state["nodes"]],
                        )
                        actual_node = next(
                            (
                                node
                                for node in st.session_state["nodes"]
                                if node_id == node.id
                            ),
                            None,
                        )
                        index = list.index(actual_node.shape)

                        # Campo de texto para introducir el nombre del nodo
                        node_name = st.text_input(
                            "Nombre del nodo", actual_node.label if actual_node else ""
                        )

                        # Selector de color para elegir el color del nodo
                        node_color = st.color_picker(
                            "Color del nodo",
                            actual_node.color if actual_node else "#ffffff",
                        )

                        # Selector de forma del nodo, como diccionario
                        node_shape = st.selectbox("Forma del nodo", list, index=index)

                        # Botón para agregar el nodo al grafo
                        if selected == "Agregar Nodo":
                            add_node_button = st.button("Agregar nodo")

                            if add_node_button:
                                st.session_state["copy_nodes"] = copy.deepcopy(
                                    st.session_state["nodes"]
                                )
                                new_node = Node(
                                    id=node_id,
                                    label=node_name,
                                    size=15,
                                    shape=node_shape,
                                    color=node_color,
                                )

                                st.session_state["nodes"].append(new_node)
                                st.session_state["last_action"] = "New Node"

                        elif selected == "Editar Nodo":
                            if st.button("Cambiar Nodo"):

                                st.session_state["copy_nodes"] = copy.deepcopy(
                                    st.session_state["nodes"]
                                )

                                index = st.session_state["nodes"].index(actual_node)

                                st.session_state["nodes"][index].label = node_name
                                st.session_state["nodes"][index].color = node_color
                                st.session_state["nodes"][index].shape = node_shape

                                st.session_state["last_action"] = "Edit Node"

    def export_to_image(self):
        # Definir las coordenadas del área de la captura de pantalla
        x, y, width, height = 580, 320, 1150, 720

        # Tomar la captura de pantalla
        screenshot = pg.screenshot(region=(x, y, width, height))

        # Crear un objeto BytesIO para guardar la imagen
        buf = io.BytesIO()

        # Guardar la captura de pantalla en el objeto BytesIO
        screenshot.save(buf, format="png")

        date = self.generateDate()

        # Crear un botón de descarga para la imagen
        st.download_button(
            label="Descargar imagen",
            data=buf.getvalue(),
            file_name="graph-" + date + ".png",
            mime="image/png",
        )

    def export_to_xlsx(self, nodes_state, edges_state):
        # Crea una lista para almacenar los datos de los nodos
        nodes_data = []

        # Recorre cada nodo y arista en el estado de la sesión
        for node in nodes_state:
            linked_nodes = [
                {"node_id": edge.to, "weight": edge.label, "color": edge.color}
                for edge in edges_state
                if edge.source == node.id
            ]
            # Agrega los datos del nodo a la lista
            nodes_data.append(
                {
                    "id": node.id,
                    "label": node.label,
                    "color": node.color,
                    "shape": node.shape,
                    "size": node.size,
                    "data": {},
                    "type": "",
                    "linkedTo": ", ".join(
                        [
                            f"(node_id: {ln['node_id']}) (weight: {ln['weight']}) (color: {ln['color']})"
                            for ln in linked_nodes
                        ]
                    ),
                    "radius": node.size / 2,
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

    def generate_graph_personalized(self):
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

            # Si se presiona el botón de crear grafo
            if create_graph:
                return [name, directed, weighted]

    def add_edge_to_graph(self, selected):
        if selected == "Agregar Arista" and st.session_state["graph"]:
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
                            st.session_state["copy_edges"] = copy.deepcopy(
                                st.session_state["edges"]
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
                            st.session_state["copy_edges"] = copy.deepcopy(
                                st.session_state["edges"]
                            )
                            st.session_state["edges"].append(new_edge_1)
                            st.session_state["edges"].append(new_edge_2)

                    st.session_state["last_action"] = "New Edge"

        elif selected == "Editar Arista" and st.session_state["graph"]:
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

        elif selected == "Eliminar Arista" and st.session_state["graph"]:
            actual_source = st.sidebar.selectbox(
                "Seleccione arista: ",
                [(edge.source, edge.to) for edge in st.session_state["edges"]],
            )

            actual_edge = next(
                (
                    edge
                    for edge in st.session_state["edges"]
                    if edge.source == actual_source[0] and edge.to == actual_source[1]
                ),
                None,
            )

            if st.sidebar.button("Eliminar"):

                st.session_state["edges"].remove(actual_edge)
                st.session_state["last_action"] = "Delete Edge"

    def generate_graph_random(self):
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
                            color=self.generateColor(),
                            shape=self.generateShape(),
                            size=15,
                        )
                        for n in G.nodes()
                    ]

                    # Inicializar la lista de aristas
                    edges = []

                    # Si el grafo es ponderado, agregar las aristas con pesos
                    if st.session_state["weighted"] and st.session_state["directed"]:
                        for e in G.edges():
                            color = self.generateColor()
                            label = str(self.generateWeight())
                            edges.append(
                                Edge(
                                    source=e[0],
                                    target=e[1],
                                    label=label,
                                    color=color,
                                    width=1,
                                )
                            )

                    elif (
                        st.session_state["weighted"]
                        and not st.session_state["directed"]
                    ):
                        st.write("Ponderado no dirigido")
                        for e in G.edges():
                            color = self.generateColor()
                            label = str(self.generateWeight())
                            edges.append(
                                Edge(
                                    source=e[0],
                                    target=e[1],
                                    label=label,
                                    color=color,
                                    width=1,
                                )
                            )
                            edges.append(
                                Edge(
                                    source=e[1],
                                    target=e[0],
                                    label=label,
                                    color=color,
                                    width=1,
                                )
                            )

                    elif (
                        not st.session_state["weighted"]
                        and st.session_state["directed"]
                    ):
                        for e in G.edges():
                            edges.append(
                                Edge(
                                    source=e[0],
                                    target=e[1],
                                    color=self.generateColor(),
                                    width=1,
                                )
                            )

                    elif (
                        not st.session_state["weighted"]
                        and not st.session_state["directed"]
                    ):
                        for e in G.edges():
                            edges.append(
                                Edge(
                                    source=e[0],
                                    target=e[1],
                                    color=self.generateColor(),
                                    width=1,
                                )
                            )
                            edges.append(
                                Edge(
                                    source=e[1],
                                    target=e[0],
                                    color=self.generateColor(),
                                    width=1,
                                )
                            )

                    # Guardar los nodos y aristas en el estado de sesión
                    st.session_state["nodes"] = nodes
                    st.session_state["edges"] = edges

                    st.session_state["graph"] = True
                    st.session_state["last_action"] = "New Node"

    def generate_table_data(self):
        # Crear un DataFrame con los datos de los nodos
        nodes_df = pd.DataFrame(
            [
                {
                    "ID": node.id,
                    "Nombre": node.label,
                    "Color": node.color,
                    "Forma": node.shape,
                }
                for node in st.session_state["nodes"]
            ]
        )

        # Crear un DataFrame con los datos de las aristas
        edges_df = pd.DataFrame(
            [
                {
                    "Nodo de inicio": edge.source,
                    "Nodo final": edge.to,
                    "Peso": edge.label,
                    "Color": edge.color,
                }
                for edge in st.session_state["edges"]
            ]
        )
        col1, col2 = st.columns(2)
        col1.markdown("<span id='dataframes'>Nodos</span>", unsafe_allow_html=True)
        col1.dataframe(nodes_df, 600, 500)
        col2.markdown("<span id='dataframes'>Aristas</span>", unsafe_allow_html=True)
        col2.dataframe(edges_df, 600, 500)
