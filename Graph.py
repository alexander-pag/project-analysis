import json
import streamlit as st
from streamlit_agraph import Edge, Node
import networkx as nx
from Utils import Utils

U = Utils()


class Graph:
    def analyze_graph(self, nodes, edges):
        # Filtro las aristas por la propiedad dashes para saber cuales no han sido eliminadas
        # dashes == False => arista sin eliminar
        # dashes == True => arista eliminada
        edges = list(filter(lambda e: e.dashes == False, edges))
        is_bipartite = st.session_state["G"].check_bipartite(nodes, edges)
        components = st.session_state["G"].find_connected_components(nodes, edges)

        return is_bipartite, components

    def load_from_json(self, filename):
        with open(filename, "r") as file:
            graph_data = json.load(file)

        graph_name = graph_data["graph"][0]["name"]
        node_data_list = graph_data["graph"][0]["data"]

        self.set_name(graph_name)

        for node_data in node_data_list:
            id = node_data["id"]
            label = node_data["label"]
            radius = node_data["radius"]
            coordinates = node_data["coordinates"]
            type = node_data["type"]
            data = node_data["data"]
            linked_to = node_data["linkedTo"]

            self.add_node(id, label, coordinates, radius, type, data)
            self.node_dict[id].adjacent = linked_to

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

    def generate_graph_random(self):
        # Crear un expander para el grafo en la barra lateral
        with st.sidebar.expander("Grafo"):
            with st.form(key="graph_form"):
                nodes = []
                edges = []
                graph = False
                last_action = ""
                # Campo de texto para introducir el nombre del grafo
                name = st.text_input("Nombre del Grafo")

                # Checkbox para elegir si el grafo es dirigido
                directed = st.checkbox("¿Es dirigido?")

                # Checkbox para elegir si el grafo es ponderado
                weighted = st.checkbox("¿Es ponderado?")

                # Checkbox para elegir si el grafo es completo
                connected = st.checkbox("¿Es completo?")

                # Checkbox para elegir si el grafo es conexo
                conex = st.checkbox("¿Es conexo?")

                # Campo de texto para introducir la cantidad de nodos
                node_qty = st.text_input("Cantidad de nodos")

                # Botón para generar el grafo
                generate_graph = st.form_submit_button(label="Generar")

                if generate_graph:
                    if connected and conex:
                        # Crear un grafo aleatorio conexo y completo
                        G = nx.connected_watts_strogatz_graph(
                            int(node_qty), int(node_qty) - 1, 0.5, tries=100
                        )
                    elif connected:
                        # Crear un grafo aleatorio completo
                        G = nx.complete_graph(int(node_qty))
                    elif conex:
                        # Crear un grafo aleatorio conexo
                        G = nx.connected_watts_strogatz_graph(
                            int(node_qty), int(node_qty) // 2, 0.5, tries=100
                        )
                    else:
                        # Crear un grafo aleatorio
                        G = nx.gnp_random_graph(
                            int(node_qty),
                            0.1,
                            directed=directed,
                        )

                    # pos = nx.circular_layout(G)
                    # Convertir el grafo de networkx a formato agraph
                    nodes = [
                        Node(
                            label="Nodo " + str(n),
                            id=n,
                            color=U.generateColor(),
                            shape=U.generateShape(),
                            size=15,
                            font={"color": "#FFFFFF"},
                            physics=True,
                            # x= pos[n][0] * 500, y = pos[n][1] * 500
                        )
                        for n in G.nodes()
                    ]

                    # Inicializar la lista de aristas
                    edges = []

                    # Si el grafo es ponderado, agregar las aristas con pesos
                    if weighted and directed:
                        for e in G.edges():
                            color = U.generateColor()
                            label = str(U.generateWeight())
                            edges.append(
                                Edge(
                                    source=e[0],
                                    target=e[1],
                                    label=label,
                                    color=color,
                                    width=1,
                                    dashes=False,
                                )
                            )

                    elif weighted and not directed:
                        st.write("Ponderado no dirigido")
                        for e in G.edges():
                            color = U.generateColor()
                            label = str(U.generateWeight())
                            edges.append(
                                Edge(
                                    source=e[0],
                                    target=e[1],
                                    label=label,
                                    color=color,
                                    width=1,
                                    dashes=False,
                                )
                            )
                            edges.append(
                                Edge(
                                    source=e[1],
                                    target=e[0],
                                    label=label,
                                    color=color,
                                    width=1,
                                    dashes=False,
                                )
                            )

                    elif not weighted and directed:
                        for e in G.edges():
                            edges.append(
                                Edge(
                                    source=e[0],
                                    target=e[1],
                                    color=U.generateColor(),
                                    width=1,
                                    dashes=False,
                                )
                            )

                    elif not weighted and not directed:
                        for e in G.edges():
                            edges.append(
                                Edge(
                                    source=e[0],
                                    target=e[1],
                                    color=U.generateColor(),
                                    width=1,
                                    dashes=False,
                                )
                            )
                            edges.append(
                                Edge(
                                    source=e[1],
                                    target=e[0],
                                    color=U.generateColor(),
                                    width=1,
                                    dashes=False,
                                )
                            )

                    # Guardar los nodos y aristas en el estado de sesión
                    nodes = nodes
                    edges = edges

                    graph = True
                    last_action = "New Node"

                return nodes, edges, graph, last_action, name

    def create_adjacency_list(self, nodes, edges):
        """
        Crea una lista de adyacencia a partir de los nodos y aristas dados.
        Args:
            nodes (list): Lista de nodos.
            edges (list): Lista de aristas.
        Returns:
            dict: Lista de adyacencia.
        """
        adj = {node.id: [] for node in nodes}
        for edge in edges:
            adj[edge.source].append(edge.to)
            adj[edge.to].append(edge.source)
        return adj

    def is_bipartite(self, node, conjunto, visitados, conjuntos, adj):
        """
        Determina si el grafo es bipartito utilizando búsqueda en profundidad.
        Args:
            node (int): Nodo actual.
            conjunto (int): conjunto del nodo actual (0 o 1).
            visitados (dict): Diccionario de nodos visitados.
            conjuntos (dict): Diccionario de conjuntos de nodos.
            adj (dict): Lista de adyacencia.
        Returns:
            bool: True si el grafo es bipartito, False en caso contrario.
        """
        visitados[node] = True
        conjuntos[node] = conjunto
        for vec in adj[node]:
            if not visitados[vec]:
                if not self.is_bipartite(vec, 1 - conjunto, visitados, conjuntos, adj):
                    return False
            elif conjuntos[vec] == conjuntos[node]:
                return False
        return True

    def check_bipartite(self, nodes, edges):
        """
        Verifica si el grafo es bipartito.
        Args:
            nodes (list): Lista de nodos.
            edges (list): Lista de aristas.
        Returns:
            bool: True si el grafo es bipartito, False en caso contrario.
        """
        adj = self.create_adjacency_list(nodes, edges)
        visitados = {node.id: False for node in nodes}
        conjuntos = {node.id: -1 for node in nodes}
        for node in nodes:
            if not visitados[node.id]:
                if not self.is_bipartite(node.id, 0, visitados, conjuntos, adj):
                    return False
        return True

    def find_connected_components(self, nodes, edges):
        """
        Encuentra los componentes conectados en el grafo y los representa como dos subconjuntos.
        Args:
            nodes (list): Lista de nodos.
            edges (list): Lista de aristas.
        Returns:
            list: Lista de componentes conectados representados como dos subconjuntos.
                Cada componente tiene una tupla de dos listas (lista de nodos de color 0, lista de nodos de color 1).
        """
        adj = self.create_adjacency_list(nodes, edges)
        visitados = {node.id: False for node in nodes}
        componente = []
        for node in nodes:
            if not visitados[node.id]:
                componenteConjuntos = self.componente(node.id, visitados, adj)
                componente.append(componenteConjuntos)
        return componente

    def componente(self, node, visitados, adj):
        """
        Separa las componentes en dos conjuntos
        Args:
            node (int): Nodo actual.
            visited (dict): Diccionario de nodos visitados.
            adj (dict): Lista de adyacencia.
        Returns:
            tuple: Tupla de dos listas (lista de nodos del conjunto 0, lista de nodos del conjunto 1).
        """
        visitados[node] = True
        conjunto1list = []
        conjunto2list = []
        stack = [(node, 0)]
        while stack:
            node, conjunto = stack.pop()
            if conjunto == 0:
                conjunto1list.append(node)
            else:
                conjunto2list.append(node)
            for vec in adj[node]:
                if not visitados[vec]:
                    visitados[vec] = True
                    stack.append((vec, 1 - conjunto))
        return conjunto1list, conjunto2list

    def generate_graph_json(
        self, nodes, edges, graph, directed, weighted, connected, conex
    ):

        graph_data = {
            "graph": [
                {
                    "name": (graph if graph else "Grafo"),
                    "data": [],
                    "generalData1": 100,
                    "generalData2": "Alg",
                    "generalData3": 300,
                    "isDirected": directed,
                    "isWeighted": weighted,
                    "isConnected": connected,
                    "isConex": conex,
                }
            ]
        }

        for node in nodes:
            linked_nodes = []
            # Añadir los nodos que tengan una arista con el nodo actual
            for edge in edges:
                if int(edge.source) == int(node.id):
                    linked_nodes.append(
                        {
                            "node_id": int(edge.to),
                            "weight": (float(edge.label) if weighted else 0.0),
                            "color": edge.color,
                            "width": edge.width,
                            "dashes": edge.dashes,
                        }
                    )

            node_data = {
                "id": int(node.id),
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

    def generarSubGrafoMinimo(self, i, nodes, edges, solucion, listaSolucion, solucionActual, listaSolucionActual, nodedict, numComponentes, memo):
        # Verificar si ya hemos resuelto este subproblema
        estado_actual = (i, tuple(listaSolucion), solucion)
        
        if estado_actual in memo:
            return memo[estado_actual]
        
        # Filtrar las aristas que no están en la lista de soluciones
        copiaEdges = [edge for edge in edges if edge not in listaSolucion]
        componentes = self.find_connected_components(nodes, copiaEdges)
        
        # Si es bipartito y hemos encontrado más componentes
        if len(componentes) == numComponentes + 1:
            if solucion <= solucionActual or solucionActual == -1:
                memo[estado_actual] = (listaSolucion, solucion)
                return listaSolucion, solucion
        
        # Si hemos procesado todos los bordes
        if i >= len(edges):
            return listaSolucionActual, solucionActual
        
        # Si es bipartito y tenemos el mismo número de componentes
        if len(componentes) == numComponentes:
            copynodedict = nodedict.copy()
            copiaSolucion = solucion
            
            if edges[i].to not in nodedict:
                copiaSolucion += float(edges[i].label)
                copynodedict[edges[i].to] = float(edges[i].label)
            else:
                copiaSolucion -= copynodedict[edges[i].to]
                copynodedict[edges[i].to] += float(edges[i].label)
                copiaSolucion += copynodedict[edges[i].to]
            
            copiaListaSolucion = listaSolucion + [edges[i]]
            
            if copiaSolucion <= solucionActual or solucionActual == -1:
                # Explorar la rama sin incluir la arista actual
                listaSolucionActual, solucionActual = self.generarSubGrafoMinimo(
                    i + 1, nodes, edges, solucion, listaSolucion, solucionActual,
                    listaSolucionActual, nodedict, numComponentes, memo
                )
                # Explorar la rama incluyendo la arista actual
                listaSolucionActual, solucionActual = self.generarSubGrafoMinimo(
                    i + 1, nodes, edges, copiaSolucion, copiaListaSolucion, solucionActual,
                    listaSolucionActual, copynodedict, numComponentes, memo
                )
        
        # Memorizar el resultado antes de devolver
        memo[estado_actual] = (listaSolucionActual, solucionActual)
        return listaSolucionActual, solucionActual

    def posicionate(self):
        is_bipartite, components = self.analyze_graph(
            st.session_state["nodes"], st.session_state["edges"]
        )
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
            if len(c) > len(com):
                com = c

            # Convertimos el gráfico a un objeto NetworkX
            g = nx.Graph()

            # Agregamos los nodos al grafo NetworkX
            for node in st.session_state["nodes"]:
                if node.id in c[0] or node.id in c[1]:
                    g.add_node(node.id)

            # Agregamos las conexiones al grafo NetworkX
            for edge in st.session_state["edges"]:
                # edges = list(filter(lambda e: e.dashes == False, st.session_state["edges"]))
                if (edge.source in c[0] or edge.source in c[1]) and (
                    edge.to in c[0] or edge.to in c[1]
                ):
                    g.add_edge(edge.source, edge.to)

            if is_bipartite:
                pos = nx.bipartite_layout(g, c[0])

                colorconjunto1 = U.generateColor()
                colorconjunto2 = U.generateColor()

                for node in st.session_state["nodes"]:
                    if node.id in c[0]:
                        node.color = colorconjunto1
                        node.x, node.y = (
                            pos[node.id][0] * 200 + posnum,
                            pos[node.id][1] * aupos,
                        )

                    elif node.id in c[1]:
                        node.color = colorconjunto2
                        node.x, node.y = (
                            pos[node.id][0] * 200 + posnum,
                            pos[node.id][1] * aupos,
                        )

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
