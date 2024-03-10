import random
import datetime
import json
import streamlit as st
from streamlit_agraph import agraph, Node, Edge
import copy

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
            css = f'<style>{f.read()}</style>'
        return css
    
    def generate_graph_json(self, nodes, edges):
        graph_data = {
            "graph": [
                {
                    "name": (st.session_state["name_graph"] if st.session_state["name_graph"] else "Grafo"),
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
            if selected == "Agregar Nodo":
                node_id = st.text_input("ID del nodo")
                actual_node = None
                index = 0
            elif selected == "Editar Nodo":
                node_id = st.selectbox(
                "Seleccione nodo: ",
                [node.id for node in st.session_state["nodes"]],)
                actual_node = next((node for node in st.session_state["nodes"] if node_id == node.id), None)
                index = list.index(actual_node.shape)

            # Campo de texto para introducir el nombre del nodo
            node_name = st.text_input("Nombre del nodo", actual_node.label if actual_node else '')

            # Selector de color para elegir el color del nodo
            node_color = st.color_picker("Color del nodo", actual_node.color if actual_node else '#ffffff')

            # Selector de forma del nodo, como diccionario
            node_shape = st.selectbox(
                "Forma del nodo",
                list, index = index
            )

            # Botón para agregar el nodo al grafo

            if selected == "Agregar Nodo":
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
                    st.session_state["last_action"] = "New Node"
            elif selected == "Editar Nodo":
                if st.sidebar.button("Cambiar Nodo"):

                    st.session_state["copy_nodes"] = copy.deepcopy(
                        st.session_state["nodes"]
                    )

                    index = st.session_state["nodes"].index(actual_node)

                    st.session_state["nodes"][index].label = node_name
                    st.session_state["nodes"][index].color = node_color
                    st.session_state["nodes"][index].shape = node_shape

                    st.session_state["last_action"] = "Edit Node"
