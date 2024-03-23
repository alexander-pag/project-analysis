from Utils import Utils
import json

U = Utils()


class Graph:
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



