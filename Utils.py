import random
import streamlit as st
import pandas as pd
from states import Tres, Cuatro, Cinco, Seis, Ocho
from itertools import product
import datetime


class Utils:
    def generateDate(self):
        return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    def generateColor(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

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
        elif selected_subconjunto == "Seis":
            return Seis
        elif selected_subconjunto == "Ocho":
            return Ocho

    def select_subconjunto_UI(self):
        option = st.radio(
            "Selecciona un subconjunto:", ["Tres", "Cuatro", "Cinco", "Seis", "Ocho"]
        )
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
        self, optionep, optionef, valorE, listaNodos, subconjunto_seleccionado, P
    ):

        optionep.sort()
        optionef.sort()
        cadena1 = "".join(optionep)
        cadena2 = "".join(optionef)
        st.write(f"## **P({cadena2}$^t$ $^+$ $^1$ | {cadena1}$^t$ = {valorE})**")

        distribucionProbabilidades = P.generarDistribucionProbabilidades(
            subconjunto_seleccionado, optionep, optionef, valorE, listaNodos
        )

        df = pd.DataFrame(
            distribucionProbabilidades[1:], columns=distribucionProbabilidades[0]
        )

        st.dataframe(df)

        st.session_state["window"] = False
        st.session_state["nodes"], st.session_state["edges"] = [], []

        P.generarGrafoTablaDistribucion(
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

    def normalizar_lista(self, lista):
        # Convertir todos los elementos a cadenas de texto
        return [[str(element) for element in sublist] for sublist in lista]

    def crear_dataframe(self, r):
        normalizado = self.normalizar_lista(r)
        df = pd.DataFrame(normalizado)
        return df
