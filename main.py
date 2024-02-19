from Graph import Graph
from Utils import Utils

# Creando grafo
G = Graph(weighted=True)
U = Utils()

# Generates the documentation


# Creando nodo
def creteNode():
    id = int(U.createRandomId())
    label = input("Dale un nombre a tu nodo: ")
    G.add_node(id, label)


# Creando grafo aleatorio
def createGraphRandom():
    if G.num_nodes > 0:
        G.node_dict = {}
        G.num_nodes = 0
        return

    size = input("Cuantos nodos quieres crear: ")
    ("Quieres personalizar tu grafo: ")
    answer = input("Si/No: ")
    if answer.lower() == "si":
        name = input("Dale un nombre al grafo: ")
        G.set_name(name)
        for i in range(int(size)):
            id = int(input("Dale un id: "))
            if id in G.node_dict:
                id = i + 1
            label = input("Dale un nombre: ")
            radius = input("Dale un radio: ")
            radius = float(radius) if radius != "" else None
            type = input("Dale un tipo: ")
            x = input("Coordenadas en el eje X: ")
            y = input("Coordenadas en el eje Y: ")
            coordinates = None
            if x and y:
                coordinates = {"x": x, "y": y}

            G.add_node(
                id, label=label, radius=radius, type=type, coordinates=coordinates
            )
        return
    for i in range(int(size)):
        id = U.createRandomId()
        G.add_node(id, U.createRandomString())


def add_edge():
    from_node_id = int(input("Dame el id del nodo de origen: "))
    if from_node_id not in G.node_dict:
        G.add_node(from_node_id, input("Dale un nombre a tu nodo: "))
        return
    to_node_id = int(input("Dame el id del nodo de destino: "))
    if to_node_id not in G.node_dict:
        G.add_node(to_node_id, input("Dale un nombre a tu nodo: "))
        return
    weight = int(input("Dame el peso de la arista: "))
    G.add_edge(from_node_id, to_node_id, weight)


def viewNodes():
    G.imprimir_nodos()


def importFromJson():
    filename = input("Ingresa el nombre del archivo JSON: ")
    G.load_from_json(filename + ".json")


def exportToJson():
    filename = input("Dame el nombre del archivo: ")
    G.export_to_json(filename + ".json")


def mostrar_menu():
    print("1. Crear nuevo nodo")
    print("2. Crear nuevo nodo aleatorio")
    print("3. Ver nodos")
    print("4. Exportar a JSON")
    print("5. Crear arista")
    print("6. Importar de JSON")
    print("0. Salir")


opciones = {
    "1": creteNode,
    "2": createGraphRandom,
    "3": viewNodes,
    "4": exportToJson,
    "5": add_edge,
    "6": importFromJson,
}

mostrar_menu()

while True:
    seleccion = input("Selecciona una opción: ")

    if seleccion == "0":
        print("Saliendo...")
        break

    if seleccion in opciones:
        opciones[seleccion]()
    else:
        print("Opción inválida. Por favor, selecciona una opción válida.")
