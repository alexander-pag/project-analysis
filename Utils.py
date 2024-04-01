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
                            "weight": (
                                int(edge.label) if st.session_state["weighted"] else 0
                            ),
                            "color": edge.color,
                            "width": edge.width,
                            "dashes": edge.dashes,
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
                    font={'color': "#FFFFFF"},
                    size=15,
                )
                st.session_state["nodes"].append(node)

                for linked_node in node_data["linkedTo"]:
                    edge = Edge(
                        source=node.id,
                        target=linked_node["node_id"],
                        color=linked_node["color"],
                        width=linked_node["width"],
                        dashes=linked_node["dashes"],
                        label=(
                            str(linked_node["weight"]) if linked_node["weight"] else ""
                        ),
                    )
                    st.session_state["edges"].append(edge)

                    st.session_state["graph"] = True

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

                st.session_state["copy_edges"] = copy.deepcopy(
                    st.session_state["edges"]
                )

                st.session_state["nodes"].remove(actual_node)

                edges_to_remove = [edge for edge in st.session_state["edges"] if edge.source == actual_node.id or edge.to == actual_node.id]
                st.session_state["edges"] = [edge for edge in st.session_state["edges"] if edge not in edges_to_remove]

                st.session_state["last_action"] = "Delete Node"
                self.posicionate()

        elif (selected == "Agregar Nodo" or selected == "Editar Nodo") and st.session_state["graph"]:
            with st.sidebar.expander("Nodo"):
                # Campo de texto para introducir el ID del nodo
                list = [
                    "diamond",
                    "dot",
                    "square",
                    "star",
                    "triangle",
                    "triangleDown",
                    "hexagon"
                ]
                if selected == "Agregar Nodo" and st.session_state["graph"]:
                    node_id = st.text_input("ID del nodo")
                    actual_node = None
                    index = 0
                elif selected == "Editar Nodo"and st.session_state["graph"]:
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
                            font={'color': "#FFFFFF"}
                        )

                        st.session_state["nodes"].append(new_node)
                        st.session_state["last_action"] = "New Node"
                        self.posicionate()

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
                        self.posicionate()

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
                {
                    "node_id": edge.to,
                    "weight": edge.label if st.session_state["weighted"] else 0,
                    "color": edge.color,
                }
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
        edges = list(filter(lambda e: e.dashes == False, st.session_state["edges"]))  
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
                                dashes=False,
                                width = 1
                            )
                            st.session_state["copy_edges"] = copy.deepcopy(
                                st.session_state["edges"]
                            )
                            st.session_state["edges"].append(new_edge)
                            self.posicionate()
                        
                        else:
                            b = True
                            for edge in st.session_state["edges"]:
                                if (edge_start == edge.to and edge_end == edge.source) or (edge_start == edge.source and edge_end == edge.to):
                                    b = False
                            if b == False:
                                st.warning("La arista ingresada ya se encuentra en el grafo.")
                            else:
                                new_edge_1 = Edge(
                                    source=edge_start,
                                    target=edge_end,
                                    label=edge_label,
                                    color=edge_color,
                                    dashes=False,
                                    width = 1
                                )

                                st.session_state["copy_edges"] = copy.deepcopy(
                                    st.session_state["edges"]
                                )
                                st.session_state["edges"].append(new_edge_1)
                                self.posicionate()

                    st.session_state["last_action"] = "New Edge"

        elif selected == "Editar Arista" and st.session_state["graph"]:
            actual_source = st.sidebar.selectbox(
                "Seleccione arista: ",
                [(edge.source, edge.to) for edge in edges],
            )
            for edge in st.session_state["edges"]:
                if edge.source == actual_source[0] and edge.to == actual_source[1]:
                    actual_edge = edge

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

                if st.session_state["directed"]:
                    st.session_state["edges"][index].label = edge_label
                    st.session_state["edges"][index].color = edge_color

                else:
                    st.session_state["edges"][index].label = edge_label
                    st.session_state["edges"][index].color = edge_color
                self.posicionate()

                st.session_state["last_action"] = "Edit Edge"

        elif selected == "Eliminar Arista" and st.session_state["graph"]:
            actual_source = st.sidebar.selectbox(
                "Seleccione arista: ",
                [(edge.source, edge.to) for edge in edges],
            )

            actual_edge_2 = None

            if st.session_state["directed"]:
                actual_edge = next(
                    (
                        edge
                        for edge in st.session_state["edges"]
                        if edge.source == actual_source[0]
                        and edge.to == actual_source[1]
                    ),
                    None,
                )

            else:
                actual_edge = next(
                    (
                        edge
                        for edge in st.session_state["edges"]
                        if edge.source == actual_source[0]
                        and edge.to == actual_source[1]
                    ),
                    None,
                )
                actual_edge_2 = next(
                    (
                        edge
                        for edge in st.session_state["edges"]
                        if edge.source == actual_source[1]
                        and edge.to == actual_source[0]
                    ),
                    None,
                )

            if st.sidebar.button("Eliminar"):
                st.session_state["copy_edges"] = copy.deepcopy(
                    st.session_state["edges"]
                )
                st.session_state["edges"].remove(actual_edge)
                if actual_edge_2:
                    st.session_state["edges"].remove(actual_edge_2)
                st.session_state["last_action"] = "Delete Edge"
                self.posicionate()
            '''
            if st.sidebar.button("Eliminar"):
                st.session_state["copy_edges"] = copy.deepcopy(
                    st.session_state["edges"]
                )
                index1 = st.session_state["edges"].index(actual_edge)
                st.session_state["edges"][index1].width = 5
                st.session_state["edges"][index1].dashes = True
                if actual_edge_2:
                    index2 = st.session_state["edges"].index(actual_edge_2)
                    st.session_state["edges"][index2].width = 5
                    st.session_state["edges"][index2].dashes = True
                st.session_state["last_action"] = "Delete Edge"
                self.posicionate()
            '''
                
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
                            0.1,
                            directed=st.session_state["directed"],
                        )

                    #pos = nx.circular_layout(G)
                    # Convertir el grafo de networkx a formato agraph
                    nodes = [
                        Node(
                            label="Nodo " + str(n),
                            id=n,
                            color=self.generateColor(),
                            shape=self.generateShape(),
                            size=15,
                            font={'color': "#FFFFFF"},
                            physics = True
                            #x= pos[n][0] * 500, y = pos[n][1] * 500
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
                                    dashes=False
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
                                    dashes=False
                                )
                            )
                            edges.append(
                                Edge(
                                    source=e[1],
                                    target=e[0],
                                    label=label,
                                    color=color,
                                    width=1,
                                    dashes=False
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
                                    dashes=False
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
                                    dashes=False
                                )
                            )
                            edges.append(
                                Edge(
                                    source=e[1],
                                    target=e[0],
                                    color=self.generateColor(),
                                    width=1,
                                    dashes=False
                                )
                            )

                    # Guardar los nodos y aristas en el estado de sesión
                    st.session_state["nodes"] = nodes
                    st.session_state["edges"] = edges

                    st.session_state["graph"] = True
                    st.session_state["last_action"] = "New Node"
                    self.posicionate()

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
                    "Peso": int(edge.label) if st.session_state["weighted"] else 0,
                    "Color": edge.color,
                }
                for edge in list(filter(lambda e: e.dashes == False, st.session_state["edges"])) 
            ]
        )
        col1, col2 = st.columns(2)
        col1.markdown("<span id='dataframes'>Nodos</span>", unsafe_allow_html=True)
        col1.dataframe(nodes_df, 600, 500)
        col2.markdown("<span id='dataframes'>Aristas</span>", unsafe_allow_html=True)
        col2.dataframe(edges_df, 600, 500)

    def analyze_graph(self, nodes, edges):   
        # Filtro las aristas por la propiedad dashes para saber cuales no han sido eliminadas
        # dashes == False => arista sin eliminar
        # dashes == True => arista eliminada
        edges = list(filter(lambda e: e.dashes == False, edges))       
        is_bipartite = st.session_state["G"].check_bipartite(nodes, edges)
        components = st.session_state["G"].find_connected_components(nodes, edges)
        
        return is_bipartite, components
    
    def posicionate(self):
        is_bipartite, components = self.analyze_graph(st.session_state["nodes"], st.session_state["edges"])
        # st.sidebar.write(is_bipartite)

        com = []
        posnum = 0
        numNodos = len(st.session_state["nodes"])

        if numNodos > 18:
            aupos = 300 + (numNodos - 18) * 20
            auposx = 100 + (numNodos - 18) * 10
        else:
            aupos = 300
            auposx = 100

        for c in components:
            if len(c) >  len(com):
                com = c

            # Convertimos el gráfico a un objeto NetworkX
            g = nx.Graph()

            # Agregamos los nodos al grafo NetworkX
            for node in st.session_state["nodes"]:
                if node.id in c[0] or node.id in c[1]:
                    g.add_node(node.id)

            # Agregamos las conexiones al grafo NetworkX
            for edge in st.session_state["edges"]:
                #edges = list(filter(lambda e: e.dashes == False, st.session_state["edges"]))  
                if (edge.source in c[0] or edge.source in c[1]) and (edge.to in c[0] or edge.to in c[1]):
                    g.add_edge(edge.source, edge.to)

            if is_bipartite:
                pos = nx.bipartite_layout(g, c[0])

                colorconjunto1 = self.generateColor()
                colorconjunto2 = self.generateColor()

                for node in st.session_state["nodes"]:
                    if node.id in c[0]:
                        node.color = colorconjunto1
                        node.x, node.y = pos[node.id][0] * 200 + posnum, pos[node.id][1] * aupos
                    
                    elif node.id in c[1]:
                        node.color = colorconjunto2
                        node.x, node.y = pos[node.id][0] * 200 + posnum, pos[node.id][1] * aupos
                        
            else:
                g2 = nx.Graph()

                for node in st.session_state["nodes"]:
                        g2.add_node(node.id)

                # Agregamos las conexiones al grafo NetworkX
                for edge in st.session_state["edges"]:
                        g2.add_edge(edge.source, edge.to)

                pos = nx.circular_layout(g2)

                for node in st.session_state["nodes"]:
                    if node.id in c[0] or node.id in c[1]:
                        node.x, node.y = pos[node.id][0] * 500, pos[node.id][1] * 500
                
            posnum += 500