import copy
from scipy.stats import wasserstein_distance
import streamlit as st
from Probabilities import Probabilities
from Graph import Graph

P = Probabilities()
G = Graph()


class SecondStrategy:
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

    def estrategia2(
        self,
        edges,
        subconjuntos,
        estados,
        distribucionOriginal,
        ep,
        ef,
        num,
        numcomponentes,
    ):
        sol = 0
        tablas = {}
        tablas_distribuidas_cache = {}

        # Generar tablas comparativas iniciales
        for key, value in subconjuntos.items():
            tablas[key] = P.generarTablaComparativa(value)

        copiaEdges = edges.copy()
        particion = False

        for arista in edges:
            nombre_origen = st.session_state["nodes"][arista.source].label
            nombre_destino = st.session_state["nodes"][arista.to].label[0]

            # Evitar copiar todas las tablas en cada iteración
            if nombre_destino not in tablas_distribuidas_cache:
                indice = estados.index(nombre_origen)
                tablas_distribuidas_cache[nombre_destino] = tablas[nombre_destino]

            tablas_distribuidas = {
                nombre_destino: tablas_distribuidas_cache[nombre_destino]
            }
            nueva_distribucion = P.generarDistribucionProbabilidades(
                subconjuntos, ep, ef, num, estados, tablas_distribuidas
            )

            if distribucionOriginal[1][1:] == nueva_distribucion[1][1:]:
                tablas[nombre_destino] = tablas_distribuidas[nombre_destino]
                arista.dashes, arista.color = True, "#FFFFFF"
                arista.label = str(0)
                copiaEdges.remove(arista)
                componentes = G.find_connected_components(
                    st.session_state["nodes"], copiaEdges
                )
                if len(componentes) > numcomponentes:
                    particion = True
                    break
            else:
                emd = wasserstein_distance(
                    distribucionOriginal[1][1:], nueva_distribucion[1][1:]
                )
                arista.label = str(emd)

        if not particion:
            st.session_state["edges"] = self.quicksort(st.session_state["edges"])
            lista, sol = self.menoresAristas(
                st.session_state["nodes"], st.session_state["edges"], numcomponentes
            )
            for edge in st.session_state["edges"]:
                if edge in lista:
                    edge.dashes = True
                    if edge.label != "0":
                        edge.color = "#FF0000"

        return sol

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
            0, nodes, edges, 0, [], -1, [], {}, numComponentes, {}
        )
        ##self.posicionate()
        return list, sol
