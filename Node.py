import streamlit as st
import copy
from Utils import Utils
from streamlit_agraph import Node

U = Utils()


class MyNode:
    # todo: No funciona el color del nodo
    def add_node_to_graph(
        self, selected, graph, nodes, edges, last_action, copy_nodes, copy_edges
    ):
        if selected == "Eliminar Nodo" and graph:
            node_id = st.sidebar.selectbox(
                "Seleccione nodo: ",
                [node.id for node in nodes],
            )

            actual_node = next(
                (node for node in nodes if node.id == node_id),
                None,
            )

            if st.sidebar.button("Eliminar"):

                copy_nodes = copy.deepcopy(nodes)

                copy_edges = copy.deepcopy(edges)

                nodes.remove(actual_node)

                edges_to_remove = [
                    edge
                    for edge in edges
                    if edge.source == actual_node.id or edge.to == actual_node.id
                ]
                edges = [edge for edge in edges if edge not in edges_to_remove]

                last_action = "Delete Node"
                U.posicionate()

            # Retornar los valores actualizados
            return nodes, edges, last_action, copy_nodes, copy_edges

        elif (selected == "Agregar Nodo" or selected == "Editar Nodo") and graph:
            with st.sidebar.expander("Nodo"):
                # Campo de texto para introducir el ID del nodo
                list = [
                    "diamond",
                    "dot",
                    "square",
                    "star",
                    "triangle",
                    "triangleDown",
                    "hexagon",
                ]
                if selected == "Agregar Nodo" and graph:
                    node_id = st.text_input("ID del nodo")
                    actual_node = None
                    index = 0
                elif selected == "Editar Nodo" and graph:
                    node_id = st.selectbox(
                        "Seleccione nodo: ",
                        [node.id for node in nodes],
                    )
                    actual_node = next(
                        (node for node in nodes if node_id == node.id),
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
                        copy_nodes = copy.deepcopy(nodes)
                        new_node = Node(
                            id=node_id,
                            label=node_name,
                            size=15,
                            shape=node_shape,
                            color=node_color,
                            font={"color": "#FFFFFF"},
                        )

                        nodes.append(new_node)
                        last_action = "New Node"
                        U.posicionate()

                    # Retornar los valores actualizados
                    return nodes, edges, last_action, copy_nodes, copy_edges

                elif selected == "Editar Nodo":
                    if st.button("Cambiar Nodo"):

                        copy_nodes = copy.deepcopy(nodes)

                        index = nodes.index(actual_node)

                        nodes[index].label = node_name
                        nodes[index].color = node_color
                        nodes[index].shape = node_shape

                        last_action = "Edit Node"
                        U.posicionate()
                    # Retornar los valores actualizados
                    return nodes, edges, last_action, copy_nodes, copy_edges
