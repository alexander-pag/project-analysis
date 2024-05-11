import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from streamlit_option_menu import option_menu
import json
from Utils import Utils
import copy
import pyautogui as pg
from Graph import Graph
import pandas as pd
from itertools import product
import matplotlib.pyplot as plt
import ast

st.set_page_config(
    page_title="Graph Editor",
    page_icon=":snake:",
    layout="centered",
    initial_sidebar_state="expanded",
)

U = Utils()
G = Graph()

css = U.load_css()
st.markdown(css, unsafe_allow_html=True)

# Verifica si ya existe un estado de sesión, si no, lo crea
default_session_state = {
    "graph": False,
    "nodes": [],
    "copy_nodes": [],
    "edges": [],
    "copy_edges": [],
    "deleted_edges": [],
    "directed": False,
    "weighted": False,
    "conex": False,
    "connected": False,
    "name_graph": "",
    "last_action": "a",
    "window": False,
    "G": G,
}

for key, value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Crear listas de opciones para las barras de navegación
options_file = ["Archivo", "Editar", "Ejecutar", "Herramientas", "Ayuda", "Ventana"]
# Crear las barras de navegación como cajas de selección en la barra lateral
with st.sidebar:
    option = option_menu(
        menu_title="Menú de opciones",
        options=options_file,
        default_index=0,
        icons=["file-earmark", "gear", "play", "tools", "question-circle", "window"],
        orientation="vertical",
        styles={},
    )

if option == "Ayuda":
    st.session_state["window"] = True
    st.write(
        """
        # Ayuda
        - **Archivo**: En esta sección se encuentran las opciones para abrir, guardar y exportar el grafo.
        - **Editar**: En esta sección se encuentran las opciones para agregar, editar y eliminar nodos y aristas.
        - **Ejecutar**: En esta sección se encuentran las opciones para ejecutar algoritmos sobre el grafo.
        - **Herramientas**: En esta sección se encuentran las opciones para realizar operaciones sobre el grafo.
        - **Ayuda**: En esta sección se encuentran las opciones para obtener ayuda.
        - **Ventana**: En esta sección se encuentran las opciones para mostrar la ventana de resultados.
        """
    )

    st.write(
        """
        # Manual de usuario
        - Si deseas obtener más información sobre el uso de la aplicación, puedes descargar el manual de usuario.
        """
    )

    with open("manual.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()

        st.download_button(
            label="Descargar Manual de Usuario",
            data=PDFbyte,
            file_name="manual.pdf",
            mime="application/octet-stream",
        )

if option == "Herramientas":
    st.session_state["window"] = True
    st.write(
        """
        # Herramientas
        - Opción no disponible por el momento.
        """
    )

if option == "Ejecutar":
    st.session_state["window"] = True
    selected = option_menu(
        menu_title=None,
        options=[
            "Analizar Grafo",
            "Estrategia 1",
            "Ejecutar Algoritmo",
            "Ejecutar Algoritmo",
        ],
        default_index=0,
        icons=["envelope-open", "x-square"],
        orientation="horizontal",
        styles={},
    )

    if selected == "Analizar Grafo":
        st.session_state["window"] = False
        is_bipartite, components = U.analyze_graph(
            st.session_state["nodes"], st.session_state["edges"]
        )
        type = "Conexo" if len(components) == 1 else "Disconexo"
        st.write("# Análisis de Grafo Bipartito")
        if is_bipartite and type == "Conexo":
            st.write("El grafo es bipartito y conexo")
        elif is_bipartite and type == "Disconexo":
            st.write("El grafo es bipartito y disconexo")
        elif not is_bipartite and type == "Conexo":
            st.write("El grafo no es bipartito y es conexo")
        else:
            st.write("El grafo no es bipartito y es disconexo")
        st.write("Componentes conectados:")
        for i, component in enumerate(components):
            st.write(f"Componente {i + 1}: {component}")

    elif selected == "Estrategia 1":
        Tres = {
            "A": {
                (0, 0, 0): 1,
                (1, 0, 0): 1,
                (0, 1, 0): 0,
                (1, 1, 0): 0,
                (0, 0, 1): 0,
                (1, 0, 1): 0,
                (0, 1, 1): 0,
                (1, 1, 1): 1,
            },
            "B": {
                (0, 0, 0): 0,
                (1, 0, 0): 1,
                (0, 1, 0): 0,
                (1, 1, 0): 1,
                (0, 0, 1): 0,
                (1, 0, 1): 0,
                (0, 1, 1): 1,
                (1, 1, 1): 0,
            },
            "C": {
                (0, 0, 0): 0,
                (1, 0, 0): 1,
                (0, 1, 0): 0,
                (1, 1, 0): 0,
                (0, 0, 1): 0,
                (1, 0, 1): 1,
                (0, 1, 1): 0,
                (1, 1, 1): 1,
            },
        }

        Cuatro = {
            "A": {
                (0, 0, 0, 0): 0,
                (1, 0, 0, 0): 0,
                (0, 1, 0, 0): 0,
                (1, 1, 0, 0): 0,
                (0, 0, 1, 0): 1,
                (1, 0, 1, 0): 0,
                (0, 1, 1, 0): 0,
                (1, 1, 1, 0): 1,
                (0, 0, 0, 1): 0,
                (1, 0, 0, 1): 0,
                (0, 1, 0, 1): 0,
                (1, 1, 0, 1): 1,
                (0, 0, 1, 1): 0,
                (1, 0, 1, 1): 0,
                (0, 1, 1, 1): 0,
                (1, 1, 1, 1): 0,
            },
            "B": {
                (0, 0, 0, 0): 0,
                (1, 0, 0, 0): 1,
                (0, 1, 0, 0): 0,
                (1, 1, 0, 0): 0,
                (0, 0, 1, 0): 0,
                (1, 0, 1, 0): 0,
                (0, 1, 1, 0): 0,
                (1, 1, 1, 0): 0,
                (0, 0, 0, 1): 0,
                (1, 0, 0, 1): 1,
                (0, 1, 0, 1): 0,
                (1, 1, 0, 1): 0,
                (0, 0, 1, 1): 0,
                (1, 0, 1, 1): 1,
                (0, 1, 1, 1): 0,
                (1, 1, 1, 1): 0,
            },
            "C": {
                (0, 0, 0, 0): 1,
                (1, 0, 0, 0): 1,
                (0, 1, 0, 0): 1,
                (1, 1, 0, 0): 0,
                (0, 0, 1, 0): 0,
                (1, 0, 1, 0): 0,
                (0, 1, 1, 0): 0,
                (1, 1, 1, 0): 0,
                (0, 0, 0, 1): 0,
                (1, 0, 0, 1): 0,
                (0, 1, 0, 1): 0,
                (1, 1, 0, 1): 0,
                (0, 0, 1, 1): 1,
                (1, 0, 1, 1): 0,
                (0, 1, 1, 1): 0,
                (1, 1, 1, 1): 0,
            },
            "D": {
                (0, 0, 0, 0): 0,
                (1, 0, 0, 0): 1,
                (0, 1, 0, 0): 0,
                (1, 1, 0, 0): 0,
                (0, 0, 1, 0): 0,
                (1, 0, 1, 0): 0,
                (0, 1, 1, 0): 0,
                (1, 1, 1, 0): 1,
                (0, 0, 0, 1): 0,
                (1, 0, 0, 1): 0,
                (0, 1, 0, 1): 1,
                (1, 1, 0, 1): 0,
                (0, 0, 1, 1): 1,
                (1, 0, 1, 1): 1,
                (0, 1, 1, 1): 0,
                (1, 1, 1, 1): 0,
            },
        }

        Cinco = {
            "A": {
                (0, 0, 0, 0, 0): 1,
                (1, 0, 0, 0, 0): 0,
                (0, 1, 0, 0, 0): 0,
                (1, 1, 0, 0, 0): 0,
                (0, 0, 1, 0, 0): 0,
                (1, 0, 1, 0, 0): 0,
                (0, 1, 1, 0, 0): 0,
                (1, 1, 1, 0, 0): 0,
                (0, 0, 0, 1, 0): 0,
                (1, 0, 0, 1, 0): 0,
                (0, 1, 0, 1, 0): 0,
                (1, 1, 0, 1, 0): 0,
                (0, 0, 1, 1, 0): 0,
                (1, 0, 1, 1, 0): 0,
                (0, 1, 1, 1, 0): 0,
                (1, 1, 1, 1, 0): 0,
                (0, 0, 0, 0, 1): 0,
                (1, 0, 0, 0, 1): 0,
                (0, 1, 0, 0, 1): 0,
                (1, 1, 0, 0, 1): 0,
                (0, 0, 1, 0, 1): 0,
                (1, 0, 1, 0, 1): 0,
                (0, 1, 1, 0, 1): 0,
                (1, 1, 1, 0, 1): 0,
                (0, 0, 0, 1, 1): 0,
                (1, 0, 0, 1, 1): 0,
                (0, 1, 0, 1, 1): 0,
                (1, 1, 0, 1, 1): 0,
                (0, 0, 1, 1, 1): 0,
                (1, 0, 1, 1, 1): 0,
                (0, 1, 1, 1, 1): 0,
                (1, 1, 1, 1, 1): 0,
            },
            "B": {
                (0, 0, 0, 0, 0): 0,
                (1, 0, 0, 0, 0): 0,
                (0, 1, 0, 0, 0): 0,
                (1, 1, 0, 0, 0): 0,
                (0, 0, 1, 0, 0): 0,
                (1, 0, 1, 0, 0): 0,
                (0, 1, 1, 0, 0): 1,
                (1, 1, 1, 0, 0): 0,
                (0, 0, 0, 1, 0): 0,
                (1, 0, 0, 1, 0): 0,
                (0, 1, 0, 1, 0): 0,
                (1, 1, 0, 1, 0): 0,
                (0, 0, 1, 1, 0): 0,
                (1, 0, 1, 1, 0): 0,
                (0, 1, 1, 1, 0): 0,
                (1, 1, 1, 1, 0): 0,
                (0, 0, 0, 0, 1): 0,
                (1, 0, 0, 0, 1): 0,
                (0, 1, 0, 0, 1): 0,
                (1, 1, 0, 0, 1): 0,
                (0, 0, 1, 0, 1): 0,
                (1, 0, 1, 0, 1): 0,
                (0, 1, 1, 0, 1): 0,
                (1, 1, 1, 0, 1): 0,
                (0, 0, 0, 1, 1): 0,
                (1, 0, 0, 1, 1): 0,
                (0, 1, 0, 1, 1): 0,
                (1, 1, 0, 1, 1): 0,
                (0, 0, 1, 1, 1): 0,
                (1, 0, 1, 1, 1): 0,
                (0, 1, 1, 1, 1): 1,
                (1, 1, 1, 1, 1): 0,
            },
            "C": {
                (0, 0, 0, 0, 0): 0,
                (1, 0, 0, 0, 0): 0,
                (0, 1, 0, 0, 0): 0,
                (1, 1, 0, 0, 0): 0,
                (0, 0, 1, 0, 0): 0,
                (1, 0, 1, 0, 0): 0,
                (0, 1, 1, 0, 0): 0,
                (1, 1, 1, 0, 0): 0,
                (0, 0, 0, 1, 0): 0,
                (1, 0, 0, 1, 0): 0,
                (0, 1, 0, 1, 0): 0,
                (1, 1, 0, 1, 0): 0,
                (0, 0, 1, 1, 0): 0,
                (1, 0, 1, 1, 0): 0,
                (0, 1, 1, 1, 0): 1,
                (1, 1, 1, 1, 0): 0,
                (0, 0, 0, 0, 1): 0,
                (1, 0, 0, 0, 1): 0,
                (0, 1, 0, 0, 1): 0,
                (1, 1, 0, 0, 1): 0,
                (0, 0, 1, 0, 1): 0,
                (1, 0, 1, 0, 1): 0,
                (0, 1, 1, 0, 1): 0,
                (1, 1, 1, 0, 1): 0,
                (0, 0, 0, 1, 1): 0,
                (1, 0, 0, 1, 1): 0,
                (0, 1, 0, 1, 1): 0,
                (1, 1, 0, 1, 1): 0,
                (0, 0, 1, 1, 1): 0,
                (1, 0, 1, 1, 1): 0,
                (0, 1, 1, 1, 1): 0,
                (1, 1, 1, 1, 1): 1,
            },
            "D": {
                (0, 0, 0, 0, 0): 0,
                (1, 0, 0, 0, 0): 0,
                (0, 1, 0, 0, 0): 0,
                (1, 1, 0, 0, 0): 0,
                (0, 0, 1, 0, 0): 0,
                (1, 0, 1, 0, 0): 0,
                (0, 1, 1, 0, 0): 1,
                (1, 1, 1, 0, 0): 0,
                (0, 0, 0, 1, 0): 0,
                (1, 0, 0, 1, 0): 0,
                (0, 1, 0, 1, 0): 0,
                (1, 1, 0, 1, 0): 0,
                (0, 0, 1, 1, 0): 0,
                (1, 0, 1, 1, 0): 0,
                (0, 1, 1, 1, 0): 0,
                (1, 1, 1, 1, 0): 0,
                (0, 0, 0, 0, 1): 0,
                (1, 0, 0, 0, 1): 0,
                (0, 1, 0, 0, 1): 0,
                (1, 1, 0, 0, 1): 0,
                (0, 0, 1, 0, 1): 0,
                (1, 0, 1, 0, 1): 0,
                (0, 1, 1, 0, 1): 0,
                (1, 1, 1, 0, 1): 0,
                (0, 0, 0, 1, 1): 0,
                (1, 0, 0, 1, 1): 0,
                (0, 1, 0, 1, 1): 0,
                (1, 1, 0, 1, 1): 0,
                (0, 0, 1, 1, 1): 0,
                (1, 0, 1, 1, 1): 0,
                (0, 1, 1, 1, 1): 0,
                (1, 1, 1, 1, 1): 0,
            },
            "E": {
                (0, 0, 0, 0, 0): 0,
                (1, 0, 0, 0, 0): 0,
                (0, 1, 0, 0, 0): 0,
                (1, 1, 0, 0, 0): 0,
                (0, 0, 1, 0, 0): 0,
                (1, 0, 1, 0, 0): 0,
                (0, 1, 1, 0, 0): 0,
                (1, 1, 1, 0, 0): 0,
                (0, 0, 0, 1, 0): 0,
                (1, 0, 0, 1, 0): 0,
                (0, 1, 0, 1, 0): 0,
                (1, 1, 0, 1, 0): 0,
                (0, 0, 1, 1, 0): 0,
                (1, 0, 1, 1, 0): 0,
                (0, 1, 1, 1, 0): 0,
                (1, 1, 1, 1, 0): 0,
                (0, 0, 0, 0, 1): 0,
                (1, 0, 0, 0, 1): 0,
                (0, 1, 0, 0, 1): 0,
                (1, 1, 0, 0, 1): 0,
                (0, 0, 1, 0, 1): 1,
                (1, 0, 1, 0, 1): 0,
                (0, 1, 1, 0, 1): 0,
                (1, 1, 1, 0, 1): 0,
                (0, 0, 0, 1, 1): 0,
                (1, 0, 0, 1, 1): 0,
                (0, 1, 0, 1, 1): 0,
                (1, 1, 0, 1, 1): 0,
                (0, 0, 1, 1, 1): 0,
                (1, 0, 1, 1, 1): 0,
                (0, 1, 1, 1, 1): 0,
                (1, 1, 1, 1, 1): 0,
            },
        }

        # Función para obtener el subconjunto seleccionado
        def obtener_subconjunto(selected_subconjunto):
            if selected_subconjunto == "Tres":
                return Tres
            elif selected_subconjunto == "Cuatro":
                return Cuatro
            elif selected_subconjunto == "Cinco":
                return Cinco

        # Interfaz de usuario
        selected_subconjunto = st.radio(
            "Selecciona un subconjunto:", ["Tres", "Cuatro", "Cinco"]
        )  # Agrega más opciones si es necesario

        subconjunto_seleccionado = obtener_subconjunto(selected_subconjunto)

        resultado, listaNodos = U.generate_state_transitions(subconjunto_seleccionado)
        tablacomparativa = U.generarTablaDistribuida(resultado)
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
            boton = st.button("Generar distribución")

        if boton:
            optionep.sort()
            optionef.sort()
            cadena1 = "".join(optionep)
            cadena2 = "".join(optionef)
            st.write(f"## **P({cadena2}$^t$ $^+$ $^1$ | {cadena1}$^t$ = {valorE})**")
            distribucionProbabilidades = U.generarDistribucionProbabilidades(
                subconjunto_seleccionado, optionep, optionef, valorE, listaNodos
            )
            df = pd.DataFrame(
                distribucionProbabilidades[1:], columns=distribucionProbabilidades[0]
            )

            st.dataframe(df)

            st.session_state["window"] = False
            st.session_state["nodes"], st.session_state["edges"] = [], []
            U.generarGrafoTablaDistribucion(
                listaNodos, st.session_state["nodes"], st.session_state["edges"]
            )

            combinaciones_ep = U.generar_combinaciones(optionep, valorE)
            combinaciones_ef = U.generar_combinaciones(optionef)

            res = U.encontrar_distribuciones_combinaciones(
                combinaciones_ep,
                combinaciones_ef,
                distribucionProbabilidades,
                subconjunto_seleccionado,
                listaNodos,
            )

            possible_divisions = U.convertir_probabilidades_tuplas(res)

            # Inicializar el mínimo y la mejor partición
            min_emd = float("inf")
            best_partition = None

            # Encontrar la mejor partición
            best_partition, min_emd = U.encontrar_mejor_particion(
                distribucionProbabilidades[1][1:], possible_divisions
            )

            # Mostrar el resultado
            print("La mejor partición es:", best_partition, "\n")
            print("Con un EMD de:", min_emd, "\n")

            st.write(f"{best_partition}")
            df0 = pd.DataFrame(best_partition[0][1:], columns=best_partition[0][0])
            df1 = pd.DataFrame(best_partition[1][1:], columns=best_partition[1][0])

            col1, col2 = st.columns(2)

            with col1:
                partes = best_partition[1][0][0].split("\\")
                lista1 = ast.literal_eval(partes[0].strip())
                lista2 = ast.literal_eval(partes[1].strip())

                cadena1 = "".join(lista1)
                cadena2 = "".join(lista2)

                st.write(
                    f"## **P({cadena2}$^t$ $^+$ $^1$ | {cadena1}$^t$ = {best_partition[1][1][0]})**"
                )
                st.dataframe(df1)

                # U.marcarAristas(lista1, lista2, optionep, optionef)
            with col2:
                partes = best_partition[0][0][0].split("\\")
                lista1 = ast.literal_eval(partes[0].strip())
                lista2 = ast.literal_eval(partes[1].strip())

                cadena1 = "".join(lista1)
                cadena2 = "".join(lista2)
                st.write(
                    f"## **P({cadena2}$^t$ $^+$ $^1$ | {cadena1}$^t$ = {best_partition[0][1][0]})**"
                )
                st.dataframe(df0)

            U.marcarAristas(lista1, lista2, optionep, optionef)

    elif selected == "Ejecutar Algoritmo":
        st.write("Función no disponible por el momento")

if option == "Archivo":
    st.session_state["window"] = False
    opcionesArchivo = [
        "Nuevo grafo",
        "Open/Close",
        "Guardar Como",
        "Import/Export",
        "Salir",
    ]
    selected = option_menu(
        menu_title=None,
        options=opcionesArchivo,
        default_index=0,
        icons=[
            "plus-circle",
            "envelope-open",
            "save",
            "file-earmark-arrow-up",
            "x-square",
        ],
        orientation="horizontal",
        styles={},
    )

    if selected == "Salir":
        # Cerrar la aplicación con ctrl+w
        pg.hotkey("ctrl", "w")

    elif selected == "Guardar Como" and st.session_state["graph"]:
        json_str = U.generate_graph_json(
            st.session_state["nodes"], st.session_state["edges"]
        )
        U.create_download_button(json_str)

    elif selected == "Open/Close":
        selected1 = option_menu(
            menu_title=None,
            options=["Open", "Close"],
            default_index=0,
            icons=["envelope-open", "x-square"],
            orientation="horizontal",
            styles={},
        )

        if selected1 == "Open" and not st.session_state["graph"]:
            uploaded_file = st.sidebar.file_uploader(
                "Elige un archivo JSON", type="json"
            )
            if uploaded_file is not None:
                data = json.load(uploaded_file)

                U.open_json_file(data)
                U.posicionate()

        elif selected1 == "Close":
            st.session_state["graph"] = False
            st.session_state["nodes"] = []
            st.session_state["edges"] = []

    elif selected == "Import/Export":
        selectedIE = option_menu(
            menu_title=None,
            options=["Import to TXT", "Export to XLSX", "Export to image"],
            default_index=0,
            icons=[
                "file-earmark-arrow-down",
                "file-earmark-arrow-up",
                "file-earmark-image",
            ],
            orientation="horizontal",
            styles={},
        )

        if selectedIE == "Import to TXT" and not st.session_state["graph"]:
            uploaded_file = st.sidebar.file_uploader(
                "Elige un archivo de texto plano", type="txt"
            )
            if uploaded_file is not None:
                # Lee el contenido del archivo y lo convierte a un diccionario de Python
                data = json.load(uploaded_file)
                U.open_json_file(data)

        elif selectedIE == "Export to image" and st.session_state["graph"]:
            U.export_to_image()

        elif selectedIE == "Export to XLSX" and st.session_state["graph"]:
            U.export_to_xlsx(st.session_state["nodes"], st.session_state["edges"])

    if selected == "Nuevo grafo":
        options_graph = ["Select", "Personalizado", "Aleatorio"]
        graph_option = st.sidebar.selectbox("Choose", options_graph)

        if graph_option == "Personalizado":
            states = U.generate_graph_personalized()

            if states:
                st.session_state["graph"] = True
                st.session_state["name_graph"] = states[0]
                st.session_state["directed"] = states[1]
                st.session_state["weighted"] = states[2]

            # Si existe un grafo, mostrar los widgets para el nodo
            if st.session_state["graph"]:
                U.add_node_to_graph("Agregar Nodo")

            if len(st.session_state["nodes"]) > 1:
                U.add_edge_to_graph("Agregar Arista")

        if graph_option == "Aleatorio":
            U.generate_graph_random()


elif option == "Editar":
    st.session_state["window"] = False
    opcionesEditar = [
        "Nodo",
        "Arista",
        "Deshacer",
    ]
    selected = option_menu(
        menu_title=None,
        options=opcionesEditar,
        default_index=0,
        icons=["circle", "arrows", "arrow-counterclockwise"],
        orientation="horizontal",
        styles={},
    )

    if not (st.session_state["graph"]):
        st.sidebar.warning("No se ha creado un grafo para editar.")

    if selected == "Nodo":
        selected = option_menu(
            menu_title=None,
            options=["Agregar Nodo", "Editar Nodo", "Eliminar Nodo"],
            default_index=0,
            icons=["plus-circle", "gear", "trash"],
            orientation="horizontal",
            styles={},
        )
        if selected == "Agregar Nodo":
            U.add_node_to_graph(selected)

        elif selected == "Editar Nodo":
            U.add_node_to_graph(selected)

        elif selected == "Eliminar Nodo":
            U.add_node_to_graph(selected)

    elif selected == "Arista":
        selected = option_menu(
            menu_title=None,
            options=["Agregar Arista", "Editar Arista", "Eliminar Arista"],
            default_index=0,
            icons=["plus-circle", "gear", "trash"],
            orientation="horizontal",
            styles={},
        )
        if selected == "Agregar Arista":
            U.add_edge_to_graph("Agregar Arista")

        elif selected == "Editar Arista":
            U.add_edge_to_graph("Editar Arista")

        elif selected == "Eliminar Arista":
            U.add_edge_to_graph("Eliminar Arista")

    elif selected == "Deshacer":
        # Deshacer el último cambio en los nodos o las aristas
        last_action = st.session_state.get("last_action")
        if last_action:
            if last_action in ["New Node", "Edit Node"]:
                st.session_state["nodes"] = copy.deepcopy(
                    st.session_state["copy_nodes"]
                )
            elif last_action in ["Delete Node"]:
                st.session_state["edges"] = copy.deepcopy(
                    st.session_state["copy_edges"]
                )
                st.session_state["nodes"] = copy.deepcopy(
                    st.session_state["copy_nodes"]
                )
            elif last_action in ["New Edge", "Delete Edge", "Edit Edge"]:
                st.session_state["edges"] = copy.deepcopy(
                    st.session_state["copy_edges"]
                )
        U.posicionate()

elif option == "Ventana":
    st.session_state["window"] = True
    U.generate_table_data()

if not st.session_state["window"]:
    # Crea tu configuración
    config = Config(
        width="100%",
        height=600,
        directed=st.session_state["directed"],
        physics=False,
        hierarchical=False,
    )

    # Dibuja tu gráfico
    return_value = agraph(
        nodes=st.session_state["nodes"], edges=st.session_state["edges"], config=config
    )
