import streamlit as st
from streamlit_agraph import agraph, Config
from streamlit_option_menu import option_menu
import json
from Utils import Utils
import copy
import pyautogui as pg
from Graph import Graph
import pandas as pd
import ast
from Node import MyNode
from File import File
from Edge import MyEdge
import time

st.set_page_config(
    page_title="Graph Editor",
    page_icon=":snake:",
    layout="centered",
    initial_sidebar_state="expanded",
)

U = Utils()
G = Graph()
N = MyNode()
F = File()
E = MyEdge()

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
    "tables": {},
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
            "Estrategia 2",
            "Ejecutar Algoritmo",
        ],
        default_index=0,
        icons=["envelope-open", "play", "play", "play"],
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
        # Mostrar los componentes conectados con nombres de nodos
        for i, component in enumerate(components):
            st.write(f"Componente {i + 1}: {component}")

    elif selected == "Estrategia 1":

        subconjunto_seleccionado = U.select_subconjunto_UI()
        ##st.session_state["window"] = False
        st.session_state["tables"] = U.tablas(subconjunto_seleccionado)

        resultado, listaNodos = U.generate_state_transitions(subconjunto_seleccionado)
        tablacomparativa = U.generarTablaDistribuida(resultado)

        boton, optionep, optionef, valorE = U.strategies(tablacomparativa, listaNodos)

        if boton:
            start_time = time.time()
            distribucionProbabilidades = U.strategies_UI(
                optionep, optionef, valorE, listaNodos, subconjunto_seleccionado, G
            )

            combinaciones_ep = U.generar_combinaciones(optionep, valorE)
            combinaciones_ef = U.generar_combinaciones(optionef)

            best_partition, min_emd = U.encontrar_distribuciones_combinaciones(
                combinaciones_ep,
                combinaciones_ef,
                distribucionProbabilidades,
                subconjunto_seleccionado,
                listaNodos,
            )

            df0 = pd.DataFrame(
                best_partition[0][0][1:], columns=best_partition[0][0][0]
            )
            df1 = pd.DataFrame(
                best_partition[0][1][1:], columns=best_partition[0][1][0]
            )

            col1, col2 = st.columns(2)

            with col1:
                partes = best_partition[0][1][0][0].split("\\")
                lista10 = ast.literal_eval(partes[0].strip())
                lista20 = ast.literal_eval(partes[1].strip())

                cadena10 = "".join(lista10)
                cadena20 = "".join(lista20)

                st.write(
                    f"## **P({cadena20}$^t$ $^+$ $^1$ | {cadena10}$^t$ = {best_partition[0][1][1][0]})**"
                )
                st.dataframe(df1)

            with col2:
                partes = best_partition[0][0][0][0].split("\\")
                lista11 = ast.literal_eval(partes[0].strip())
                lista21 = ast.literal_eval(partes[1].strip())

                cadena11 = "".join(lista11)
                cadena21 = "".join(lista21)
                st.write(
                    f"## **P({cadena21}$^t$ $^+$ $^1$ | {cadena11}$^t$ = {best_partition[0][0][1][0]})**"
                )
                st.dataframe(df0)

            U.marcarAristas(lista11, lista21, lista10, lista20, optionep, optionef)

            end_time = time.time()

            total_time = end_time - start_time

            st.write(f"Tiempo de ejecución: {round(total_time, 4)} segundos")
            st.write("El emd es: ", min_emd)

            # df = pd.DataFrame(
            #     divided_system.reshape(
            #         len(divided_system[0][0][1][1:]),
            #         len(divided_system[0][1][1][1:]),
            #     ),
            #     columns=divided_system[0][1][0][1:],
            #     index=divided_system[0][0][0][1:],
            # )

            # st.write("## **Distribución de probabilidades**")
            # st.dataframe(df)

    elif selected == "Estrategia 2":

        subconjunto_seleccionado = U.select_subconjunto_UI()
        st.session_state["tables"] = U.tablas(subconjunto_seleccionado)
        ##st.session_state["window"] = False

        resultado, listaNodos = U.generate_state_transitions(subconjunto_seleccionado)
        tablacomparativa = U.generarTablaDistribuida(resultado)

        boton, optionep, optionef, valorE = U.strategies(tablacomparativa, listaNodos)

        if boton:
            inicio = time.time()
            distribucionProbabilidades = U.strategies_UI(
                optionep, optionef, valorE, listaNodos, subconjunto_seleccionado, G
            )

            def ordenar_por_destino(aristas):
                aristas.sort(key=lambda arista: arista.to)
                return aristas

            st.session_state["edges"] = ordenar_por_destino(st.session_state["edges"])

            def filtrarArista(ep, ef):
                arista_eliminar = []
                edges = st.session_state["edges"]
                for arista in edges:
                    nombre_origen, nombre_destino = (
                        st.session_state["nodes"][arista.source].label,
                        st.session_state["nodes"][arista.to].label[0],
                    )
                    if nombre_origen not in ep or nombre_destino not in ef:
                        arista_eliminar.append(arista)
                st.session_state["edges"] = [
                    arista for arista in edges if arista not in arista_eliminar
                ]

            filtrarArista(optionep, optionef)
            _, components = U.analyze_graph(
                st.session_state["nodes"], st.session_state["edges"]
            )
            numcomponents = len(components)
            numcomponents = U.estrategia2(
                st.session_state["edges"],
                subconjunto_seleccionado,
                listaNodos,
                distribucionProbabilidades,
                optionep,
                optionef,
                valorE,
                numcomponents,
            )
            
            fin = time.time()
            for i in st.session_state["edges"]:
                i.label = ""
            
            st.write(f"Valor de perdida: {numcomponents}")
            st.write(f"Tiempo de ejecución: {round((fin - inicio), 4)} segundos")
            
            ##U.posicionate()


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
        json_str = G.generate_graph_json(
            st.session_state["nodes"],
            st.session_state["edges"],
            st.session_state["graph"],
            st.session_state["directed"],
            st.session_state["weighted"],
            st.session_state["connected"],
            st.session_state["conex"],
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

                F.open_json_file(
                    data,
                    st.session_state["nodes"],
                    st.session_state["edges"],
                    st.session_state["graph"],
                )
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
                F.open_json_file(data)

        elif selectedIE == "Export to image" and st.session_state["graph"]:
            F.export_to_image()

        elif selectedIE == "Export to XLSX" and st.session_state["graph"]:
            F.export_to_xlsx(
                st.session_state["nodes"],
                st.session_state["edges"],
                st.session_state["weighted"],
            )

    if selected == "Nuevo grafo":
        options_graph = ["Select", "Personalizado", "Aleatorio"]
        graph_option = st.sidebar.selectbox("Choose", options_graph)

        if graph_option == "Personalizado":
            states = G.generate_graph_personalized()

            if states:
                st.session_state["graph"] = True
                st.session_state["name_graph"] = states[0]
                st.session_state["directed"] = states[1]
                st.session_state["weighted"] = states[2]

            # Si existe un grafo, mostrar los widgets para el nodo
            if st.session_state["graph"]:
                nodes, edges, last_action, copy_nodes, copy_edges = N.add_node_to_graph(
                    "Agregar Nodo",
                    st.session_state["graph"],
                    st.session_state["nodes"],
                    st.session_state["edges"],
                    st.session_state["last_action"],
                    st.session_state["copy_nodes"],
                    st.session_state["copy_edges"],
                )

                st.session_state["nodes"] = nodes
                st.session_state["edges"] = edges
                st.session_state["last_action"] = last_action
                st.session_state["copy_nodes"] = copy_nodes
                st.session_state["copy_edges"] = copy_edges

            if len(st.session_state["nodes"]) > 1:
                edges, last_action, copy_edges = E.add_edge_to_graph(
                    "Agregar Arista",
                    st.session_state["graph"],
                    st.session_state["nodes"],
                    st.session_state["edges"],
                    st.session_state["last_action"],
                    st.session_state["copy_edges"],
                    st.session_state["weighted"],
                    st.session_state["directed"],
                )

                st.session_state["edges"] = edges
                st.session_state["last_action"] = last_action
                st.session_state["copy_edges"] = copy_edges
            U.posicionate()

        if graph_option == "Aleatorio":

            nodes, edges, graph, last_action, name = G.generate_graph_random()

            st.session_state["nodes"] = nodes
            st.session_state["edges"] = edges
            st.session_state["graph"] = graph
            st.session_state["last_action"] = last_action
            st.session_state["name_graph"] = name
            U.posicionate()


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
            nodes, edges, last_action, copy_nodes, copy_edges = N.add_node_to_graph(
                selected,
                st.session_state["graph"],
                st.session_state["nodes"],
                st.session_state["edges"],
                st.session_state["last_action"],
                st.session_state["copy_nodes"],
                st.session_state["copy_edges"],
            )

            st.session_state["nodes"] = nodes
            st.session_state["edges"] = edges
            st.session_state["last_action"] = last_action
            st.session_state["copy_nodes"] = copy_nodes
            st.session_state["copy_edges"] = copy_edges

        elif selected == "Editar Nodo":
            nodes, edges, last_action, copy_nodes, copy_edges = N.add_node_to_graph(
                selected,
                st.session_state["graph"],
                st.session_state["nodes"],
                st.session_state["edges"],
                st.session_state["last_action"],
                st.session_state["copy_nodes"],
                st.session_state["copy_edges"],
            )

            st.session_state["nodes"] = nodes
            st.session_state["edges"] = edges
            st.session_state["last_action"] = last_action
            st.session_state["copy_nodes"] = copy_nodes
            st.session_state["copy_edges"] = copy_edges

        elif selected == "Eliminar Nodo":
            nodes, edges, last_action, copy_nodes, copy_edges = N.add_node_to_graph(
                selected,
                st.session_state["graph"],
                st.session_state["nodes"],
                st.session_state["edges"],
                st.session_state["last_action"],
                st.session_state["copy_nodes"],
                st.session_state["copy_edges"],
            )

            st.session_state["nodes"] = nodes
            st.session_state["edges"] = edges
            st.session_state["last_action"] = last_action
            st.session_state["copy_nodes"] = copy_nodes
            st.session_state["copy_edges"] = copy_edges

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
            edges, last_action, copy_edges = E.add_edge_to_graph(
                "Agregar Arista",
                st.session_state["graph"],
                st.session_state["nodes"],
                st.session_state["edges"],
                st.session_state["last_action"],
                st.session_state["copy_edges"],
                st.session_state["weighted"],
                st.session_state["directed"],
            )

            st.session_state["edges"] = edges
            st.session_state["last_action"] = last_action
            st.session_state["copy_edges"] = copy_edges

        elif selected == "Editar Arista":
            edges, last_action, copy_edges = E.add_edge_to_graph(
                "Editar Arista",
                st.session_state["graph"],
                st.session_state["nodes"],
                st.session_state["edges"],
                st.session_state["last_action"],
                st.session_state["copy_edges"],
                st.session_state["weighted"],
                st.session_state["directed"],
            )

            st.session_state["edges"] = edges
            st.session_state["last_action"] = last_action
            st.session_state["copy_edges"] = copy_edges

        elif selected == "Eliminar Arista":
            edges, last_action, copy_edges = E.add_edge_to_graph(
                "Eliminar Arista",
                st.session_state["graph"],
                st.session_state["nodes"],
                st.session_state["edges"],
                st.session_state["last_action"],
                st.session_state["copy_edges"],
                st.session_state["weighted"],
                st.session_state["directed"],
            )

            st.session_state["edges"] = edges
            st.session_state["last_action"] = last_action
            st.session_state["copy_edges"] = copy_edges

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
