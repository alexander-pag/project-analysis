from Utils import Utils
import json

U = Utils()


class Graph:
    def __init__(
        self, name="G", directed=False, complete=False, connected=False, weighted=False
    ):
        self.node_dict = {}
        self.num_nodes = 0
        self.name = name
        self.directed = directed
        self.complete = complete
        self.connected = connected
        self.weighted = weighted

    def __iter__(self):
        return iter(self.node_dict.values())

    def add_node(
        self,
        id,
        label,
        coordinates=None,
        radius=None,
        type=None,
        data=None,
    ):
        self.num_nodes += 1
        new_node = Node(id, label)

        if coordinates is not None:
            new_node.coordinates = coordinates
        if radius is not None:
            new_node.radius = radius
        if type is not None:
            new_node.type = type
        if data is not None:
            new_node.data = data

        self.node_dict[id] = new_node
        return new_node

    def get_nodes(self):
        pass

    def add_edge(self, from_node_id, to_node_id, weight=0):
        if from_node_id not in self.node_dict:
            print("Nodo de origen no encontrado.")
            return
        if to_node_id not in self.node_dict:
            print("Nodo de destino no encontrado.")
            return

        self.node_dict[from_node_id].add_neighbour(to_node_id, weight)
        if not self.directed:
            self.node_dict[to_node_id].add_neighbour(from_node_id, weight)

    def set_name(self, name):
        self.name = name

    def imprimir_nodos(self):
        for node_id, node in self.node_dict.items():
            print(node)

    def export_to_json(self, filename):
        graph_data = {
            "graph": [
                {
                    "name": self.name,
                    "data": [],
                    "generalData1": 100,
                    "generalData2": "Alg",
                    "generalData3": 300,
                }
            ]
        }

        for node_id, node in self.node_dict.items():
            node_data = {
                "id": node.id,
                "label": node.label,
                "data": node.data,
                "type": node.type,
                "linkedTo": node.adjacent,  # Asumiendo que 'linked_to' es un atributo de los nodos
                "radius": node.radius,
                "coordinates": node.coordinates,
            }
            graph_data["graph"][0]["data"].append(node_data)

        with open(filename, "w") as file:
            json.dump(graph_data, file, indent=4)

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
        Encuentra los componentes conectados en el grafo.
        Args:
            nodes (list): Lista de nodos.
            edges (list): Lista de aristas.
        Returns:
            list: Lista de componentes conectados (cada componente es una lista de nodos).
        """
        adj = self.create_adjacency_list(nodes, edges)
        visited = {node.id: False for node in nodes}
        components = []
        for node in nodes:
            if not visited[node.id]:
                components.append([])
                self.is_connected(node.id, visited, components[-1], adj)
        return components

    def is_connected(self, node, visited, component, adj):
        """
        Determina si el grafo es conexo utilizando búsqueda en profundidad.
        Args:
            node (int): Nodo actual.
            visited (dict): Diccionario de nodos visitados.
            component (list): Lista de nodos en el componente conectado actual.
            adj (dict): Lista de adyacencia.
        """
        visited[node] = True
        component.append(node)
        for neighbor in adj[node]:
            if not visited[neighbor]:
                self.is_connected(neighbor, visited, component, adj)
