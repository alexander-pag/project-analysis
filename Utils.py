import random
import datetime
import json
import streamlit as st
from streamlit_agraph import agraph, Node, Edge
import copy
import pyautogui as pg
import io
from datetime import datetime
import pandas as pd
import networkx as nx
from itertools import combinations
import itertools
import numpy as np
from scipy.stats import wasserstein_distance
from tabulate import tabulate
from states import Tres, Cuatro, Cinco
from itertools import product


class Utils:
    def createRandomString(self):
        characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        return "".join(random.choice(characters) for i in range(8))

    def createRandomId(self):
        characters = "1234567890"
        return "".join(random.choice(characters) for i in range(4))

    def getDateTime(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generateColor(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def generateDate(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generateShape(self):
        shapes = [
            "dot",
            "star",
            "triangle",
            "triangleDown",
            "hexagon",
            "square",
        ]
        return random.choice(shapes)

    def generateWeight(self):
        return round(random.random(), 4)

    def load_css(self):
        with open("styles.css") as f:
            css = f"<style>{f.read()}</style>"
        return css

    def create_download_button(self, json_str):
        name = st.sidebar.text_input("Nombre del archivo")
        st.sidebar.download_button(
            label="Descargar JSON",
            data=json_str,
            file_name=name + ".json",
            mime="application/json",
        )

    def obtener_subconjunto(self, selected_subconjunto):
        if selected_subconjunto == "Tres":
            return Tres
        elif selected_subconjunto == "Cuatro":
            return Cuatro
        elif selected_subconjunto == "Cinco":
            return Cinco

    def select_subconjunto_UI(self):
        option = st.radio("Selecciona un subconjunto:", ["Tres", "Cuatro", "Cinco"])
        return self.obtener_subconjunto(option)

    def strategies(self, tablacomparativa, listaNodos):
        df = pd.DataFrame(tablacomparativa[1:], columns=tablacomparativa[0])

        cadena = "".join(listaNodos)
        st.write(f"## **P({cadena}$^t$ $^+$ $^1$ | {cadena}$^t$)**")
        st.dataframe(df)

        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        with col1:
            optionep = st.multiselect("Estados presentes:", listaNodos)
        with col2:
            optionef = st.multiselect("Estados futuros:", listaNodos)
        with col3:
            combinaciones = list(product([0, 1], repeat=len(optionep)))
            valorE = st.selectbox("Selecciona el valor presente: ", combinaciones)
        with col4:
            return st.button("Generar distribución"), optionep, optionef, valorE

    def strategies_UI(
        self, optionep, optionef, valorE, listaNodos, subconjunto_seleccionado, G
    ):

        optionep.sort()
        optionef.sort()
        cadena1 = "".join(optionep)
        cadena2 = "".join(optionef)
        st.write(f"## **P({cadena2}$^t$ $^+$ $^1$ | {cadena1}$^t$ = {valorE})**")

        distribucionProbabilidades = self.generarDistribucionProbabilidades(
            subconjunto_seleccionado, optionep, optionef, valorE, listaNodos
        )

        df = pd.DataFrame(
            distribucionProbabilidades[1:], columns=distribucionProbabilidades[0]
        )

        st.dataframe(df)

        st.session_state["window"] = False
        st.session_state["nodes"], st.session_state["edges"] = [], []

        G.generarGrafoTablaDistribucion(
            listaNodos, st.session_state["nodes"], st.session_state["edges"]
        )

        return distribucionProbabilidades

    def generate_table_data(self):
        # Crear un DataFrame con los datos de los nodos
        nodes_df = pd.DataFrame(
            [
                {
                    "ID": node.id,
                    "Nombre": node.label,
                    "Color": node.color,
                    "Forma": node.shape,
                }
                for node in st.session_state["nodes"]
            ]
        )

        # Crear un DataFrame con los datos de las aristas
        edges_df = pd.DataFrame(
            [
                {
                    "Nodo de inicio": edge.source,
                    "Nodo final": edge.to,
                    "Peso": int(edge.label) if st.session_state["weighted"] else 0,
                    "Color": edge.color,
                }
                for edge in list(
                    filter(lambda e: e.dashes == False, st.session_state["edges"])
                )
            ]
        )
        col1, col2 = st.columns(2)
        col1.markdown("<span id='dataframes'>Nodos</span>", unsafe_allow_html=True)
        col1.dataframe(nodes_df, 600, 500)
        col2.markdown("<span id='dataframes'>Aristas</span>", unsafe_allow_html=True)
        col2.dataframe(edges_df, 600, 500)

    def analyze_graph(self, nodes, edges):
        # Filtro las aristas por la propiedad dashes para saber cuales no han sido eliminadas
        # dashes == False => arista sin eliminar
        # dashes == True => arista eliminada
        edges = list(filter(lambda e: e.dashes == False, edges))
        is_bipartite = st.session_state["G"].check_bipartite(nodes, edges)
        components = st.session_state["G"].find_connected_components(nodes, edges)

        return is_bipartite, components

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
        tabla1 = [
            fila
            for fila in tabla
            if all(fila[0][pos] == num[i] for i, pos in enumerate(posiciones))
        ]

        valores = [0, 0]
        for fila in tabla1:
            valor1 = (
                fila[1] if isinstance(fila[1], float) else fila[1][0]
            )  # Asegurar que sea un número
            valor2 = (
                fila[2] if isinstance(fila[2], float) else fila[2][0]
            )  # Asegurar que sea un número
            valores[0] += valor1
            valores[1] += valor2

        valores = [valor / len(tabla1) for valor in valores]

        nueva_fila = [num, *valores]
        nueva_tabla.append(nueva_fila)

        return nueva_tabla

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

    def generarTablaComparativa(self, diccionario):
        lista = [["Llave", (1,), (0,)]]
        for key, value in diccionario.items():
            lista.append([key, float(value), float(1 - value)])

        return lista

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

    # def generar_combinaciones(self, elementos, valores=None, memo=None):
    #     if memo is None:
    #         memo = {}

    #     elementos.sort()  # Ordenar los elementos para garantizar el mismo orden en cada llamada

    #     key = tuple(elementos)
    #     if key in memo:
    #         return memo[key]

    #     combinaciones = []
    #     if valores is None:
    #         valores = [None] * len(elementos)

    #     # Agregar la combinación adicional
    #     combinacion_vacia = [[], elementos, (), tuple(valores)]
    #     combinaciones.append(combinacion_vacia)

    #     for i in range(1, len(elementos)):
    #         for subconjunto in combinations(elementos, i):
    #             complemento = tuple(x for x in elementos if x not in subconjunto)
    #             tupla_subconjunto = tuple(
    #                 valores[elementos.index(elem)] if valores else None
    #                 for elem in subconjunto
    #             )
    #             tupla_complemento = tuple(
    #                 valores[elementos.index(elem)] if valores else None
    #                 for elem in complemento
    #             )
    #             nueva_combinacion = [
    #                 sorted(list(subconjunto)),  # Ordenar los elementos del subconjunto
    #                 sorted(list(complemento)),  # Ordenar los elementos del complemento
    #                 tupla_subconjunto,
    #                 tupla_complemento,
    #             ]
    #             combinacion_invertida = [
    #                 sorted(list(complemento)),  # Ordenar los elementos del complemento
    #                 sorted(list(subconjunto)),  # Ordenar los elementos del subconjunto
    #                 tupla_complemento,
    #                 tupla_subconjunto,
    #             ]
    #             if (
    #                 nueva_combinacion not in combinaciones
    #                 and combinacion_invertida not in combinaciones
    #             ):
    #                 combinaciones.append(nueva_combinacion)

    #     memo[key] = combinaciones
    #     return combinaciones

    def generar_combinaciones(self, elementos, valores=None, memo=None):
        if memo is None:
            memo = {}

        elementos.sort()  # Ordenar los elementos para garantizar el mismo orden en cada llamada

        key = tuple(elementos)
        if key in memo:
            return memo[key]

        combinaciones = []
        if valores is None:
            valores = [None] * len(elementos)

        # Agregar la combinación adicional
        combinacion_vacia = [[], elementos, (), tuple(valores)]
        combinaciones.append(combinacion_vacia)

        n = len(elementos)
        for i in range(1, n):
            for subconjunto in combinations(elementos, i):
                complemento = tuple(x for x in elementos if x not in subconjunto)
                tupla_subconjunto = tuple(
                    valores[elementos.index(elem)] for elem in subconjunto
                )
                tupla_complemento = tuple(
                    valores[elementos.index(elem)] for elem in complemento
                )

                nueva_combinacion = [
                    list(subconjunto),  # Lista de subconjunto
                    list(complemento),  # Lista de complemento
                    tupla_subconjunto,
                    tupla_complemento,
                ]

                # Para evitar agregar combinaciones duplicadas, ordenamos los elementos
                if nueva_combinacion not in combinaciones:
                    combinaciones.append(nueva_combinacion)

        memo[key] = combinaciones
        return combinaciones

    def encontrar_mejor_particion(self, original_system, possible_divisions):
        min_emd = float("inf")
        best_partition = None

        ##st.write(f"{possible_divisions}")
        for partition in possible_divisions:
            current_emd = self.calculate_emd(np.array(original_system), partition)

            if current_emd == 0.0:
                return partition, current_emd

            if current_emd < min_emd:
                min_emd = current_emd
                best_partition = partition

        return best_partition, min_emd

    def encontrar_distribuciones_combinaciones(
        self, combinaciones_ep, combinaciones_ef, original_system, subconjuntos, estados
    ):
        min_emd = float("inf")
        best_partition = None

        for combinacion_ep in combinaciones_ep:
            for combinacion_ef in combinaciones_ef:
                distribuciones = []

                # Verificar si hay elementos en común
                if set(combinacion_ep[0]) & set(combinacion_ef[0]) or set(
                    combinacion_ep[1]
                ) & set(combinacion_ef[1]):
                    continue

                # Verificar si alguna de las combinaciones es vacía
                if (len(combinacion_ep[0]) == 0 and len(combinacion_ef[0]) == 0) or (
                    len(combinacion_ep[1]) == 0 and len(combinacion_ef[1]) == 0
                ):
                    continue

                # Generar las distribuciones de probabilidades
                distribuciones.append(
                    self.generarDistribucionProbabilidades(
                        subconjuntos,
                        combinacion_ep[0],
                        combinacion_ef[0],
                        combinacion_ep[2],
                        estados,
                    )
                )

                distribuciones.append(
                    self.generarDistribucionProbabilidades(
                        subconjuntos,
                        combinacion_ep[1],
                        combinacion_ef[1],
                        combinacion_ep[3],
                        estados,
                    )
                )

                possible_divisions = self.convertir_probabilidades_tuplas(
                    distribuciones
                )

                emd = self.calculate_emd(original_system[1][1:], possible_divisions)

                if emd == 0.0:
                    return possible_divisions, emd

                if emd < min_emd:
                    min_emd = emd
                    best_partition = possible_divisions

                # Verificar si hay elementos en común (en el orden invertido)
                if set(combinacion_ep[0]) & set(combinacion_ef[1]) or set(
                    combinacion_ep[1]
                ) & set(combinacion_ef[0]):
                    continue

                # Verificar si alguna de las combinaciones es vacía (en el orden invertido)
                if (len(combinacion_ep[0]) == 0 and len(combinacion_ef[1]) == 0) or (
                    len(combinacion_ep[1]) == 0 and len(combinacion_ef[0]) == 0
                ):
                    continue

                # Generar las distribuciones de probabilidades (en el orden invertido)
                distribuciones.append(
                    self.generarDistribucionProbabilidades(
                        subconjuntos,
                        combinacion_ep[0],
                        combinacion_ef[1],
                        combinacion_ep[2],
                        estados,
                    )
                )

                distribuciones.append(
                    self.generarDistribucionProbabilidades(
                        subconjuntos,
                        combinacion_ep[1],
                        combinacion_ef[0],
                        combinacion_ep[3],
                        estados,
                    )
                )

                possible_divisions = self.convertir_probabilidades_tuplas(
                    distribuciones
                )

                emd = self.calculate_emd(original_system[1][1:], possible_divisions)

                if emd == 0.0:
                    return possible_divisions, emd

                if emd < min_emd:
                    min_emd = emd
                    best_partition = possible_divisions

        return best_partition, min_emd

    def calculate_emd(self, original_system, system_partition):
        ##st.write(system_partition)
        divided_system = np.tensordot(
            system_partition[0][0][1][1:], system_partition[0][1][1][1:], axes=0
        ).flatten()
        emd = wasserstein_distance(original_system, divided_system)
        print(f"EMD: {emd}")
        return emd

    def convertir_probabilidades_tuplas(self, datos):
        possible_divisions = []
        for i, table in enumerate(datos):

            print(f"\nTabla {i + 1}:")
            df = pd.DataFrame(table[1:], columns=table[0])
            print("\n", tabulate(df.values, headers=df.columns, tablefmt="grid"))

            possible_divisions.append(table)

        possible_divisions = [
            (possible_divisions[i], possible_divisions[i + 1])
            for i in range(0, len(possible_divisions), 2)
        ]
        return possible_divisions

    def marcarAristas(self, lista1, lista2, lista11, lista22, optionep, optionef):
        # Añadir ' a lista2
        lista2 = [i + "'" for i in lista2]

        edges_to_remove = []
        for edge in st.session_state["edges"]:
            source_node = st.session_state["nodes"][edge.source]
            to_node = st.session_state["nodes"][edge.to]

            source_node_color = (
                "#00FFFF"
                if source_node.label in lista1
                else "#FF0000" if source_node.label in lista11 else "#FFFFFF"
            )
            to_node_color = (
                "#00FFFF"
                if to_node.label in lista2
                else "#FF0000" if to_node.label[0] in lista22 else "#FFFFFF"
            )

            source_node.color = source_node_color
            to_node.color = to_node_color

            edge_color = (
                "#00FFFF"
                if (source_node.label in lista1 and to_node.label[0] not in lista22)
                else (
                    "#FFFFFF"
                    if (source_node.label in lista1 and to_node.label[0] in lista22)
                    or (source_node.label in lista11 and to_node.label in lista2)
                    else "#FF0000"
                )
            )
            edge.color = edge_color
            edge.dashes = edge_color == "#FFFFFF"

            if source_node.label not in optionep or to_node.label[0] not in optionef:
                edges_to_remove.append(edge)

        st.session_state["edges"] = [
            edge for edge in st.session_state["edges"] if edge not in edges_to_remove
        ]

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

                colorconjunto1 = self.generateColor()
                colorconjunto2 = self.generateColor()

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

    def expandirTabla(self, tabla, posicion):
        nueva_tabla = [tabla[0]]  # Mantener la primera fila de la tabla original
        indicesVisitados = {}

        for fila in tabla[1:]:
            nuevo_indice = fila[0][:posicion] + fila[0][posicion + 1 :]

            if nuevo_indice not in indicesVisitados:
                nueva_tabla.append(fila)
                indicesVisitados[nuevo_indice] = len(nueva_tabla) - 1
            else:
                index = indicesVisitados[nuevo_indice]
                nueva_tabla[index][1] = (nueva_tabla[index][1] + fila[1]) / 2
                nueva_tabla[index][2] = (nueva_tabla[index][2] + fila[2]) / 2

                nueva_tabla.append(
                    [fila[0], nueva_tabla[index][1], nueva_tabla[index][2]]
                )

        return nueva_tabla
    
    def estrategia2(self, edges, subconjuntos, estados, distribucionOriginal, ep, ef, num, numcomponentes):
        tablas = st.session_state["tables"]
        particion, copiaEdges = False, edges.copy()
        for arista in edges:
            nombre_origen = st.session_state["nodes"][arista.source].label
            nombre_destino = st.session_state["nodes"][arista.to].label[0]

            indice = estados.index(nombre_origen)
            tablas_distribuidas = {nombre_destino: self.expandirTabla(tablas[nombre_destino], indice)}

            nueva_distribucion = self.generarDistribucionProbabilidades(subconjuntos, ep, ef, num, estados, tablas_distribuidas)

            if distribucionOriginal[1][1:] == nueva_distribucion[1][1:]:
                tablas[nombre_destino] = tablas_distribuidas[nombre_destino]
                arista.dashes, arista.color = True, "#00FF00"
                arista.label = str(0)
                copiaEdges.remove(arista)
                _, componentes = self.analyze_graph(st.session_state["nodes"], copiaEdges)
                if len(componentes) > numcomponentes:
                    particion = True
                    break
            else:
                emd = wasserstein_distance(distribucionOriginal[1][1:], nueva_distribucion[1][1:])
                arista.label = str(emd)
        if not particion:
            st.session_state["edges"] = self.quicksort(st.session_state["edges"])
            lista = self.menoresAristas(st.session_state["nodes"], st.session_state["edges"], numcomponentes)
            for edge in st.session_state["edges"]:
                if edge in lista:
                    edge.dashes = True
                    edge.color = "#00FF00"
                

    def quicksort(self, edges):
        if len(edges) <= 1:
            return edges
        else:
            pivot = edges[0]
            less_than_pivot = [
                x for x in edges[1:] if float(x.label) <= float(pivot.label)
            ]
            greater_than_pivot = [
                x for x in edges[1:] if float(x.label) > float(pivot.label)
            ]
            return (
                self.quicksort(less_than_pivot)
                + [pivot]
                + self.quicksort(greater_than_pivot)
            )

    def menoresAristas(self, nodes, edges, numComponentes):
        list, sol = st.session_state["G"].generarSubGrafoMinimo(
            0, nodes, edges, 0, [], -1, [], {}, numComponentes
        )
        ##self.posicionate()
        return list
    
    def tablas(self, subconjuntos):
        tabla = {}
        for key, value in subconjuntos.items():
            tabla[key] = self.generarTablaComparativa(value)
        
        return tabla
            
        
