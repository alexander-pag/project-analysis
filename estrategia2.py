import networkx as nx
import itertools
from itertools import product
import streamlit as st
from Utils import Utils
import pandas as pd
import matplotlib.pyplot as plt

U = Utils()

# Crear grafo dirigido
G = nx.DiGraph()

Tres = {
    "A": {
        (0, 0, 0): 1,
        (1, 0, 0): 0,
        (0, 1, 0): 0,
        (1, 1, 0): 0,
        (0, 0, 1): 0,
        (1, 0, 1): 0,
        (0, 1, 1): 0,
        (1, 1, 1): 0,
    },
    "B": {
        (0, 0, 0): 0,
        (1, 0, 0): 0,
        (0, 1, 0): 0,
        (1, 1, 0): 0,
        (0, 0, 1): 0,
        (1, 0, 1): 0,
        (0, 1, 1): 1,
        (1, 1, 1): 0,
    },
    "C": {
        (0, 0, 0): 0,
        (1, 0, 0): 0,
        (0, 1, 0): 0,
        (1, 1, 0): 0,
        (0, 0, 1): 0,
        (1, 0, 1): 1,
        (0, 1, 1): 0,
        (1, 1, 1): 0,
    },
}


# Función para obtener el subconjunto seleccionado
def obtener_subconjunto(selected_subconjunto):
    if selected_subconjunto == "Tres":
        return Tres
    # elif selected_subconjunto == "Cuatro":
    # return Cuatro
    # elif selected_subconjunto == "Cinco":
    # return Cinco


# Interfaz de usuario
selected_subconjunto = st.radio(
    "Selecciona un subconjunto:", ["Tres"]
)  # Agrega más opciones si es necesario

subconjunto_seleccionado = obtener_subconjunto(selected_subconjunto)

resultado, listaNodos = U.generate_state_transitions(subconjunto_seleccionado)
tablacomparativa = U.generarTablaDistribuida(resultado)
df = pd.DataFrame(tablacomparativa[1:], columns=tablacomparativa[0])

cadena = "".join(listaNodos)
st.write(f"## **P({cadena}$^t$ $^+$ $^1$ | {cadena}$^t$)**")
st.dataframe(df)

optionep = []
optionef = []
valorE = ()
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
with col1:
    optionep = st.multiselect("Estados presentes:", listaNodos)
    G.add_nodes_from(optionep, bipartite=0)
with col2:
    optionef = st.multiselect("Estados futuros:", listaNodos)
    # Añadir ' en los nodos futuros
    optioneff = [f"{n}'" for n in optionef]
    G.add_nodes_from(optioneff, bipartite=1)
with col3:
    combinaciones = list(product([0, 1], repeat=len(optionep)))
    valorE = st.selectbox("Selecciona el valor presente: ", combinaciones)
with col4:
    boton = st.button("Generar distribución")

if boton:

    # Crear los arcos
    for nodo in optionep:
        for nodo2 in optioneff:
            if nodo == nodo2[:-1]:
                continue
            G.add_edge(nodo, nodo2, weight=0.0)

    optionep.sort()
    optionef.sort()
    cadena1 = "".join(optionep)
    cadena2 = "".join(optionef)
    st.write(f"## **P({cadena2}$^t$ $^+$ $^1$ | {cadena1}$^t$ = {valorE})**")
    distribucionProbabilidades = U.generarDistribucionProbabilidades(
        subconjunto_seleccionado, optionep, optionef, valorE, listaNodos
    )
    df = pd.DataFrame(
        distribucionProbabilidades[1:], columns=distribucionProbabilidades[0]
    )

    st.dataframe(df)


def find_components(graph):
    # Encontrar todas las componentes débilmente conectadas
    components = list(nx.weakly_connected_components(graph))
    return components


def add_empty_node(graph, component):
    # Encontrar nodos de la parte bipartita 0 en la componente
    bipartite_0_nodes = [
        node for node in component if graph.nodes[node]["bipartite"] == 0
    ]

    # Si no hay nodos de bipartite=0, no es necesario añadir un nodo vacío
    if len(bipartite_0_nodes) == 0:
        return component

    # Si hay nodos de bipartite=0 y solo queda uno en la componente, añadir un nodo vacío
    if len(bipartite_0_nodes) == 1:
        empty_node = ""
        graph.add_node(empty_node, bipartite=0)
        component.add(empty_node)

    return component


def separate_bipartite_components(graph, component):
    # Inicializar conjuntos de nodos de bipartite=0 y bipartite=1
    bipartite_0_set = set()
    bipartite_1_set = set()

    # Separar la componente en conjuntos de nodos de bipartite=0 y bipartite=1
    for node in component:
        if graph.nodes[node]["bipartite"] == 0:
            bipartite_0_set.add(node)
        else:
            bipartite_1_set.add(node)

    # Si no hay nodos de bipartite=1 en la componente, agregar un nodo vacío
    if not bipartite_1_set:
        bipartite_1_set.add("")

    # Remover el nodo vacío del conjunto de bipartite=0 si existe
    bipartite_0_set.discard("")

    return bipartite_0_set, bipartite_1_set


def remove_edges_and_check_components(graph, state_values):
    # Crear una copia del grafo original
    graph_copy = graph.copy()

    # Inicializar la lista de aristas eliminadas
    removed_edges = []

    # Obtener nodos de bipartite=0
    bipartite_0_nodes = [
        node for node, attr in graph.nodes(data=True) if attr["bipartite"] == 0
    ]

    # Recorrer los nodos de bipartite=0
    for node in bipartite_0_nodes:
        # Obtener las aristas del nodo
        node_edges = list(graph.edges(node))
        for edge in node_edges:
            # Eliminar una arista
            graph_temp = graph_copy.copy()
            graph_temp.remove_edge(*edge)

            # Verificar si se generan dos componentes
            if nx.number_weakly_connected_components(graph_temp) == 2:
                # Llamar a la función para encontrar todas las componentes
                components = find_components(graph_temp)
                for component in components:
                    # Añadir nodo vacío si es necesario
                    component_with_empty_node = add_empty_node(graph_temp, component)
                    print("After removing edge", edge)
                    print("Component:", component_with_empty_node)
                    # Separar la componente en conjuntos de bipartite=0 y bipartite=1
                    bipartite_0_set, bipartite_1_set = separate_bipartite_components(
                        graph_temp, component_with_empty_node
                    )

                    # Obtener valores de los estados presentes para bipartite=0
                    bipartite_0_values = tuple(
                        state_values[bipartite_0_nodes.index(node)]
                        for node in bipartite_0_set
                    )
                    print("Bipartite=0 nodes:", bipartite_0_set, bipartite_0_values)
                    print("Bipartite=1 nodes:", bipartite_1_set)

                    # Llamar a la función para calcular la tabla de distribución
                print("-------------------")
                break  # Detener el bucle si se encontraron dos componentes
        else:
            # Si no se generaron dos componentes, agregar la arista a removed_edges
            removed_edges.append(node_edges[0])

    # Si no se generaron dos componentes eliminando una arista por nodo, probar combinaciones de dos aristas
    for combination in itertools.combinations(removed_edges, 2):
        graph_temp = graph_copy.copy()
        graph_temp.remove_edges_from(combination)
        if nx.number_weakly_connected_components(graph_temp) == 2:
            components = find_components(graph_temp)
            for component in components:
                # Añadir nodo vacío si es necesario
                component_with_empty_node = add_empty_node(graph_temp, component)
                print("After removing edges", combination)
                print("Component:", component_with_empty_node)
                # Separar la componente en conjuntos de bipartite=0 y bipartite=1
                bipartite_0_set, bipartite_1_set = separate_bipartite_components(
                    graph_temp, component_with_empty_node
                )

                # Obtener valores de los estados presentes para bipartite=0
                bipartite_0_values = tuple(
                    state_values[bipartite_0_nodes.index(node)]
                    for node in bipartite_0_set
                )
                print("Bipartite=0 nodes:", bipartite_0_set, bipartite_0_values)
                print("Bipartite=1 nodes:", bipartite_1_set)

                # Llamar a la función para calcular la tabla de distribución
            print("-------------------")


# Uso de la función
remove_edges_and_check_components(G, (0, 1, 0))
