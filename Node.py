class Node:
    def __init__(
        self,
        id,
        label,
        radius=0.4,
        coordinates={"x": 2, "y": 3},
        type="",
        data={},
        linked_to=[],
    ):
        self.id = id
        self.label = label
        self.data = data
        self.type = type
        self.linkedTo = linked_to
        self.radius = radius
        self.coordinates = coordinates
        self.adjacent = []
        self.visited = False
        self.distance = 0
        self.previous = None

    def add_neighbour(self, neighbour, weight=0):
        self.adjacent.append({"node_id": neighbour, "weight": weight})

    def add_linked_to(self, linkedTo):
        self.adjacent.append(linkedTo)

    def get_connections(self):
        return self.adjacent.keys()

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_weight(self, neighbour):
        return self.adjacent[neighbour]

    def set_distance(self, distance):
        self.distance = distance

    def get_distance(self):
        return self.distance

    def set_previous(self, previous):
        self.previous = previous

    def set_visited(self):
        self.visited = True

    def __str__(self):
        type_str = self.type if self.type is not "" else "not type specified"
        return "Node: id: {id} - label: {label} - radius: {radius} - coordinates: {coordinates} - type: {type}".format(
            id=self.id,
            label=self.label,
            radius=self.radius,
            coordinates=self.coordinates,
            type=type_str,
        )
