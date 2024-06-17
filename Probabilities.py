import streamlit as st
from streamlit_agraph import Node, Edge
from Utils import Utils
from Graph import Graph

U = Utils()
G = Graph()


class Probabilities:
    ## TALLER 3
    def generarDistribucionProbabilidades(
        self, tabla, ep, ef, num, estados, tablasCreadas={}
    ):
        ep_index = [estados.index(i) for i in ep]
        probabilidadesDistribuidas = []

        for i in ef:
            if i in tablasCreadas:
                nueva_tabla = tablasCreadas[i]
            else:
                nueva_tabla = st.session_state["tables"][i]
            filtro2 = self.porcentajeDistribuido(nueva_tabla, ep_index, num)

            probabilidadesDistribuidas.append(filtro2)

        tabla = self.generarTabla(probabilidadesDistribuidas, num)
        tabla[0] = [f"{ep} \ {ef}"] + tabla[0]
        tabla[1] = [num] + tabla[1]

        return tabla

    def generarTabla(
        self, distribucionProbabilidades, num, i=0, binario="", nuevo_valor=1
    ):
        if i == len(distribucionProbabilidades):
            binario = "0" * (len(distribucionProbabilidades) - len(binario)) + binario
            nueva_tupla = tuple(int(bit) for bit in binario)
            return [[nueva_tupla], [nuevo_valor]]
        else:
            tabla1 = self.generarTabla(
                distribucionProbabilidades,
                num,
                i + 1,
                binario + "0",
                nuevo_valor * distribucionProbabilidades[i][1][2],
            )
            tabla2 = self.generarTabla(
                distribucionProbabilidades,
                num,
                i + 1,
                binario + "1",
                nuevo_valor * distribucionProbabilidades[i][1][1],
            )
            return [tabla1[0] + tabla2[0], tabla1[1] + tabla2[1]]

    def porcentajeDistribuido(self, tabla, posiciones, num):
        nueva_tabla = [tabla[0]]
        tabla_filtrada = [
            fila
            for fila in tabla[1:]
            if all(fila[0][pos] == num[i] for i, pos in enumerate(posiciones))
        ]

        valores = [0, 0]
        for fila in tabla_filtrada:
            valor1 = fila[1]
            valor2 = fila[2]
            valores[0] += valor1
            valores[1] += valor2

        valores = [valor / len(tabla_filtrada) for valor in valores]

        nueva_fila = [num, *valores]
        nueva_tabla.append(nueva_fila)

        return nueva_tabla

    def generarTablaComparativa(self, diccionario):
        lista = [["Llave", (1,), (0,)]]
        for key, value in diccionario.items():
            lista.append([key, value, 1 - value])

        return lista

    def generarTablaDistribuida(self, diccionario):
        # Obtener todas las llaves únicas
        llaves_unicas = sorted(list(set(diccionario.keys())))

        # Crear la matriz inicializando con ceros
        matriz = [["Llave"] + llaves_unicas]
        for llave in llaves_unicas:
            fila = [llave]
            for otra_llave in llaves_unicas:
                fila.append(1 if diccionario.get(llave) == otra_llave else 0)
            matriz.append(fila)

        return matriz

    def generate_state_transitions(self, subconjuntos):
        estados = list(subconjuntos.keys())
        transiciones = {}
        estado_actual = [0] * len(estados)

        def helper(i):
            if i == len(estados):
                estado_actual_tuple = tuple(estado_actual)
                estado_futuro = tuple(
                    subconjuntos[estado][estado_actual_tuple] for estado in estados
                )
                transiciones[estado_actual_tuple] = estado_futuro
            else:
                estado_actual[i] = 0
                helper(i + 1)
                estado_actual[i] = 1
                helper(i + 1)

        helper(0)
        return transiciones, estados

    def generarGrafoTablaDistribucion(self, listaNodos, nodes, edges):
        # nodes, edges = [], []
        # print(nodes)
        num = 0
        ultimosNodos1, ultimosNodos2 = [], []
        for i in listaNodos:
            new_node = Node(
                id=num,
                label=i,
                size=15,
                color=U.generateColor(),
                font={"color": "#FFFFFF"},
            )
            new_node2 = Node(
                id=num + 1,
                label=i + "'",
                size=15,
                color=U.generateColor(),
                font={"color": "#FFFFFF"},
            )

            nodes.append(new_node)
            nodes.append(new_node2)
            
            new_edge1 = Edge(
                    source=new_node.id,
                    target=new_node2.id,
                    dashes=False,
                    directed=True,
                )
            edges.append(new_edge1)

            for last_node1 in ultimosNodos1:
                new_edge1 = Edge(
                    source=last_node1.id,
                    target=new_node2.id,
                    dashes=False,
                    directed=True,
                )
                edges.append(new_edge1)

            for last_node2 in ultimosNodos2:
                new_edge2 = Edge(
                    target=last_node2.id,
                    source=new_node.id,
                    dashes=False,
                    directed=True,
                )
                edges.append(new_edge2)

            ultimosNodos1.append(new_node)
            ultimosNodos2.append(new_node2)  # Actualizar el último new_node2
            num = num + 2

        G.posicionate()

    def tablas(self, subconjuntos):
        tabla = {}
        for key, value in subconjuntos.items():
            tabla[key] = self.generarTablaComparativa(value)

        return tabla
