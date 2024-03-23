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

    def is_bipartite(self, node, color, visited, colors, adj):
        """
        Determina si el grafo es bipartito utilizando búsqueda en profundidad.
        Args:
            node (int): Nodo actual.
            color (int): Color del nodo actual (0 o 1).
            visited (dict): Diccionario de nodos visitados.
            colors (dict): Diccionario de colores de nodos.
            adj (dict): Lista de adyacencia.
        Returns:
            bool: True si el grafo es bipartito, False en caso contrario.
        """
        visited[node] = True
        colors[node] = color
        for neighbor in adj[node]:
            if not visited[neighbor]:
                if not self.is_bipartite(neighbor, 1 - color, visited, colors, adj):
                    return False
            elif colors[neighbor] == colors[node]:
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
        visited = {node.id: False for node in nodes}
        colors = {node.id: -1 for node in nodes}
        for node in nodes:
            if not visited[node.id]:
                if not self.is_bipartite(node.id, 0, visited, colors, adj):
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
        visited = {node.id: False for node in nodes}
        components = []
        for node in nodes:
            if not visited[node.id]:
                component_coloring = self.color_component(node.id, visited, adj)
                components.append(component_coloring)
        return components

    def color_component(self, node, visited, adj):
        """
        Colorea un componente conexo del grafo.
        Args:
            node (int): Nodo actual.
            visited (dict): Diccionario de nodos visitados.
            adj (dict): Lista de adyacencia.
        Returns:
            tuple: Tupla de dos listas (lista de nodos de color 0, lista de nodos de color 1).
        """
        visited[node] = True
        color_0_list = []
        color_1_list = []
        stack = [(node, 0)]  # Start with color 0
        while stack:
            node, color = stack.pop()
            if color == 0:
                color_0_list.append(node)
            else:
                color_1_list.append(node)
            for neighbor in adj[node]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append((neighbor, 1 - color))
        return color_0_list, color_1_list


