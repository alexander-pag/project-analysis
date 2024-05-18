import streamlit as st
import copy
from Utils import Utils
from streamlit_agraph import Edge

U = Utils()


class MyEdge:
    def add_edge_to_graph(
        self, selected, graph, nodes, edges, last_action, copy_edges, weighted, directed
    ):
        edges = list(filter(lambda e: e.dashes == False, edges))
        if selected == "Agregar Arista" and graph:
            # Crear un expander para la arista en la barra lateral
            with st.sidebar.expander("Arista"):
                # Crear un formulario para la arista
                with st.form(key="edge_form"):
                    # Campo de texto para introducir el nodo de inicio de la arista
                    edge_start = st.selectbox(
                        "Nodo de inicio de la arista",
                        [node.id for node in nodes],
                    )

                    # Campo de texto para introducir el nodo final de la arista
                    edge_end = st.selectbox(
                        "Nodo final de la arista",
                        [node.id for node in nodes],
                    )

                    edge_label = ""
                    if weighted:
                        # Campo de texto para introducir la etiqueta de la arista
                        edge_label = st.text_input("Etiqueta de la arista")
                    else:
                        edge_label = ""

                    edge_color = st.color_picker("Color de la arista")

                    # Botón para agregar la arista al grafo
                    add_edge_button = st.form_submit_button(label="Agregar arista")

                    if add_edge_button:
                        if directed:
                            new_edge = Edge(
                                source=edge_start,
                                target=edge_end,
                                label=edge_label,
                                color=edge_color,
                                dashes=False,
                                width=1,
                            )
                            copy_edges = copy.deepcopy(edges)
                            edges.append(new_edge)

                            for edge in edges:
                                st.write(edge.source, edge.to)

                            U.posicionate()

                        else:
                            b = True
                            for edge in edges:
                                if (
                                    edge_start == edge.to and edge_end == edge.source
                                ) or (
                                    edge_start == edge.source and edge_end == edge.to
                                ):
                                    b = False
                            if b == False:
                                st.warning(
                                    "La arista ingresada ya se encuentra en el grafo."
                                )
                            else:
                                new_edge_1 = Edge(
                                    source=edge_start,
                                    target=edge_end,
                                    label=edge_label,
                                    color=edge_color,
                                    dashes=False,
                                    width=1,
                                )

                                copy_edges = copy.deepcopy(edges)
                                edges.append(new_edge_1)
                                U.posicionate()

                    last_action = "New Edge"
            # Retornar los valores actualizados
            return edges, last_action, copy_edges

        elif selected == "Editar Arista" and graph:
            actual_source = st.sidebar.selectbox(
                "Seleccione arista: ",
                [(edge.source, edge.to) for edge in edges],
            )
            for edge in edges:
                if edge.source == actual_source[0] and edge.to == actual_source[1]:
                    actual_edge = edge

            edge_label = ""
            if weighted:
                # Campo de texto para introducir la etiqueta de la arista
                edge_label = st.sidebar.text_input(
                    "Etiqueta de la arista", actual_edge.label
                )

            edge_color = st.sidebar.color_picker(
                "Color de la arista", actual_edge.color
            )

            if st.sidebar.button("Cambiar Arista"):

                copy_edges = copy.deepcopy(edges)

                index = edges.index(actual_edge)

                if directed:
                    edges[index].label = edge_label
                    edges[index].color = edge_color

                else:
                    edges[index].label = edge_label
                    edges[index].color = edge_color
                U.posicionate()

                last_action = "Edit Edge"

            # Retornar los valores actualizados
            return edges, last_action, copy_edges

        elif selected == "Eliminar Arista" and graph:
            actual_source = st.sidebar.selectbox(
                "Seleccione arista: ",
                [(edge.source, edge.to) for edge in edges],
            )

            actual_edge_2 = None

            if directed:
                actual_edge = next(
                    (
                        edge
                        for edge in edges
                        if edge.source == actual_source[0]
                        and edge.to == actual_source[1]
                    ),
                    None,
                )

            else:
                actual_edge = next(
                    (
                        edge
                        for edge in edges
                        if edge.source == actual_source[0]
                        and edge.to == actual_source[1]
                    ),
                    None,
                )
                actual_edge_2 = next(
                    (
                        edge
                        for edge in edges
                        if edge.source == actual_source[1]
                        and edge.to == actual_source[0]
                    ),
                    None,
                )

            if st.sidebar.button("Eliminar"):
                copy_edges = copy.deepcopy(edges)
                edges.remove(actual_edge)
                if actual_edge_2:
                    edges.remove(actual_edge_2)
                last_action = "Delete Edge"
                self.posicionate()
            """
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
            """

        #   Retornar los valores actualizados
        return edges, last_action, copy_edges
