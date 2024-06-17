import streamlit as st
from streamlit_agraph import agraph, Config
from streamlit_option_menu import option_menu
import json
from Utils import Utils
import copy
import pyautogui as pg
from Graph import Graph
import ast
from Node import MyNode
from File import File
from Edge import MyEdge
from First_Strategy import FirstStrategy
from Second_Strategy import SecondStrategy
from Third_Strategy import ThirdStrategy
from Brute_Force import BruteForce
from Probabilities import Probabilities
import time
import numpy as np

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
E1 = FirstStrategy()
E2 = SecondStrategy()
E3 = ThirdStrategy()
BF = BruteForce()
P = Probabilities()

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
options_file = ["Archivo", "Editar", "Ejecutar", "Ayuda", "Ventana"]
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
        - **Ayuda**: En esta sección se encuentran las opciones para obtener ayuda.
        - **Ventana**: En esta sección se encuentran las opciones para mostrar la ventana de resultados.
        """
    )

    st.write(
        """
        # Manual de usuario, técnico y documentación
        - Si deseas obtener más información sobre el uso de la aplicación, puedes descargar el manual de usuario, manual técnico o la documentación.
        """
    )

    with open("manual_usuario.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()

        st.download_button(
            label="Descargar Manual de Usuario",
            data=PDFbyte,
            file_name="manual_usuario.pdf",
            mime="application/octet-stream",
        )
    with open("manual_tecnico.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()

        st.download_button(
            label="Descargar Manual Técnico",
            data=PDFbyte,
            file_name="manual_tecnico.pdf",
            mime="application/octet-stream",
        )
    with open("documentacion.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()

        st.download_button(
            label="Descargar Documentación",
            data=PDFbyte,
            file_name="documentacion.pdf",
            mime="application/octet-stream",
        )

if option == "Ejecutar":

    st.session_state["window"] = True
    selected = option_menu(
        menu_title=None,
        options=[
            "Analizar Grafo",
            "Estrategia 1",
            "Estrategia 2",
            "Estrategia 3",
            "Fuerza Bruta",
        ],
        default_index=0,
        icons=["envelope-open", "play", "play", "play"],
        orientation="horizontal",
        styles={},
    )

    if selected == "Analizar Grafo":
        st.session_state["window"] = False
        is_bipartite, components = G.analyze_graph(
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
        st.session_state["tables"] = P.tablas(subconjunto_seleccionado)

        resultado, listaNodos = P.generate_state_transitions(subconjunto_seleccionado)
        tablacomparativa = P.generarTablaDistribuida(resultado)

        boton, optionep, optionef, valorE = U.strategies(tablacomparativa, listaNodos)

        if boton:
            start_time = time.time()
            distribucionProbabilidades = U.strategies_UI(
                optionep, optionef, valorE, listaNodos, subconjunto_seleccionado, P
            )

            # st.write(distribucionProbabilidades[1][1:])

            print(distribucionProbabilidades[1][1:])

            # Función principal
            mejor_particion, mejor_costo, r1, r2 = E1.busqueda_local_emd(
                optionep,
                optionef,
                valorE,
                subconjunto_seleccionado,
                listaNodos,
                distribucionProbabilidades,
            )
            print("Mejor partición encontrada:")
            print(mejor_particion)
            print(f"Mejor costo (EMD): {mejor_costo}")

            print("////////////////////////////////////////")
            print(r1)
            print(r2)

            # Convertir r1 y r2 a DataFrame
            df_r1 = U.crear_dataframe(r1)
            df_r2 = U.crear_dataframe(r2)

            col1, col2 = st.columns(2)

            with col1:
                partes = r1[0][0].split("\\")
                lista10 = ast.literal_eval(partes[0].strip())
                lista20 = ast.literal_eval(partes[1].strip())

                cadena10 = "".join(lista10)
                cadena20 = "".join(lista20)

                st.write(
                    f"## **P({cadena20}$^t$ $^+$ $^1$ | {cadena10}$^t$ = {r1[1][0]})**"
                )
                st.dataframe(df_r1)

            with col2:
                partes = r2[0][0].split("\\")
                lista11 = ast.literal_eval(partes[0].strip())
                lista21 = ast.literal_eval(partes[1].strip())

                cadena11 = "".join(lista11)
                cadena21 = "".join(lista21)
                st.write(
                    f"## **P({cadena21}$^t$ $^+$ $^1$ | {cadena11}$^t$ = {r2[1][0]})**"
                )
                st.dataframe(df_r2)

            E.marcarAristas(lista11, lista21, lista10, lista20, optionep, optionef)

            end_time = time.time()

            total_time = end_time - start_time

            st.write(f"Tiempo de ejecución: {round(total_time, 4)} segundos")
            st.write("El emd es: ", mejor_costo)

    elif selected == "Estrategia 2":

        subconjunto_seleccionado = U.select_subconjunto_UI()
        st.session_state["tables"] = P.tablas(subconjunto_seleccionado)
        ##st.session_state["window"] = False

        resultado, listaNodos = P.generate_state_transitions(subconjunto_seleccionado)
        tablacomparativa = P.generarTablaDistribuida(resultado)

        # print("#############", listaNodos)

        boton, optionep, optionef, valorE = U.strategies(tablacomparativa, listaNodos)

        if boton:
            inicio = time.time()

            distribucionProbabilidades = U.strategies_UI(
                optionep, optionef, valorE, listaNodos, subconjunto_seleccionado, P
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
            _, components = G.analyze_graph(
                st.session_state["nodes"], st.session_state["edges"]
            )
            numcomponents = len(components)
            numcomponents = E2.estrategia2(
                st.session_state["edges"],
                subconjunto_seleccionado,
                listaNodos,
                distribucionProbabilidades,
                optionep,
                optionef,
                valorE,
                numcomponents,
            )
            ##U.posicionate()

            fin = time.time()
            for i in st.session_state["edges"]:
                i.label = ""

            st.write(f"Valor de perdida: {numcomponents}")
            st.write(f"Tiempo de ejecución: {round((fin - inicio), 4)} segundos")

    elif selected == "Estrategia 3":

        subconjunto_seleccionado = U.select_subconjunto_UI()
        st.session_state["tables"] = P.tablas(subconjunto_seleccionado)
        ##st.session_state["window"] = False

        resultado, listaNodos = P.generate_state_transitions(subconjunto_seleccionado)
        tablacomparativa = P.generarTablaDistribuida(resultado)

        boton, optionep, optionef, valorE = U.strategies(tablacomparativa, listaNodos)

        # Ejemplo de uso
        if boton:
            start_time = time.time()

            # Generar la distribución de probabilidades
            distribucionProbabilidades = U.strategies_UI(
                optionep, optionef, valorE, listaNodos, subconjunto_seleccionado, P
            )

            # Parameters for REMCMC
            num_replicas = 4
            beta_values = np.linspace(0.1, 1.0, num_replicas)
            num_iterations = (len(optionep) + len(optionef)) * 10
            swap_interval = 10
            r1 = []
            r2 = []
            max_no_improvement_iterations = 50  # Número de iteraciones sin mejora antes de detenerse
            no_improvement_counter = 0

            # Initialize replicas
            replicas = [
                {
                    "partition": E3.generate_random_partition(
                        optionep, optionef, valorE
                    ),
                    "beta": beta,
                }
                for beta in beta_values
            ]

            # Evaluate initial states
            for replica in replicas:
                replica["loss"], r1, r2 = E3.calcular_costo(
                    replica["partition"],
                    subconjunto_seleccionado,
                    distribucionProbabilidades,
                    listaNodos,
                )
                replica["r1"] = r1
                replica["r2"] = r2

            # Initialize best result
            best_replica = min(replicas, key=lambda x: x["loss"])
            global_best_partition = best_replica["partition"]
            global_best_loss = best_replica["loss"]
            global_best_r1 = best_replica["r1"]
            global_best_r2 = best_replica["r2"]

            # Run REMCMC with simulated annealing
            for iteration in range(num_iterations):
                improvement = False
                for replica in replicas:
                    E3.metropolis_update(
                        replica,
                        optionep,
                        optionef,
                        valorE,
                        subconjunto_seleccionado,
                        distribucionProbabilidades,
                        listaNodos,
                    )
                    # Update global best result
                    if replica["loss"] < global_best_loss:
                        global_best_partition = replica["partition"]
                        global_best_loss = replica["loss"]
                        global_best_r1 = replica["r1"]
                        global_best_r2 = replica["r2"]
                        improvement = True
                        no_improvement_counter = 0

                    # Check if global best loss is 0 and break if true
                    if global_best_loss == 0:
                        break
                # Break the outer loop if global_best_loss is 0
                if global_best_loss == 0:
                    break
                if not improvement:
                    no_improvement_counter += 1
                if no_improvement_counter >= max_no_improvement_iterations:
                    print("Terminado debido a demasiadas iteraciones sin mejora.")
                    break
                if iteration % swap_interval == 0:
                    E3.replica_exchange(replicas)

            # Output results
            print("Best Partition:", global_best_partition)
            print("Loss:", global_best_loss)
            print("Best r1:", global_best_r1)
            print("Best r2:", global_best_r2)

            # Convert r1 and r2 to DataFrame
            df_r1 = U.crear_dataframe(global_best_r1)
            df_r2 = U.crear_dataframe(global_best_r2)

            col1, col2 = st.columns(2)

            with col1:
                partes = global_best_r1[0][0].split("\\")
                lista10 = ast.literal_eval(partes[0].strip())
                lista20 = ast.literal_eval(partes[1].strip())

                cadena10 = "".join(lista10)
                cadena20 = "".join(lista20)

                st.write(
                    f"## **P({cadena20}$^t$ $^+$ $^1$ | {cadena10}$^t$ = {global_best_r1[1][0]})**"
                )
                st.dataframe(df_r1)

            with col2:
                partes = global_best_r2[0][0].split("\\")
                lista11 = ast.literal_eval(partes[0].strip())
                lista21 = ast.literal_eval(partes[1].strip())

                cadena11 = "".join(lista11)
                cadena21 = "".join(lista21)
                st.write(
                    f"## **P({cadena21}$^t$ $^+$ $^1$ | {cadena11}$^t$ = {global_best_r2[1][0]})**"
                )
                st.dataframe(df_r2)

            E.marcarAristas(lista11, lista21, lista10, lista20, optionep, optionef)

            end_time = time.time()

            total_time = end_time - start_time

            st.write(f"Tiempo de ejecución: {round(total_time, 4)} segundos")
            st.write("El emd es: ", global_best_loss)

    elif selected == "Fuerza Bruta":

        subconjunto_seleccionado = U.select_subconjunto_UI()
        ##st.session_state["window"] = False
        st.session_state["tables"] = P.tablas(subconjunto_seleccionado)

        resultado, listaNodos = P.generate_state_transitions(subconjunto_seleccionado)
        tablacomparativa = P.generarTablaDistribuida(resultado)

        boton, optionep, optionef, valorE = U.strategies(tablacomparativa, listaNodos)

        if boton:
            start_time = time.time()
            distribucionProbabilidades = U.strategies_UI(
                optionep, optionef, valorE, listaNodos, subconjunto_seleccionado, P
            )

            # st.write(distribucionProbabilidades[1][1:])

            print(distribucionProbabilidades[1][1:])

            # Función principal
            mejor_particion, mejor_costo, r1, r2 = BF.fuerza_bruta(
                optionep,
                optionef,
                valorE,
                subconjunto_seleccionado,
                listaNodos,
                distribucionProbabilidades,
            )

            print("Mejor partición encontrada:")
            print(mejor_particion)
            print(f"Mejor costo (EMD): {mejor_costo}")

            print("////////////////////////////////////////")
            print(r1)
            print(r2)

            # Convertir r1 y r2 a DataFrame
            df_r1 = U.crear_dataframe(r1)
            df_r2 = U.crear_dataframe(r2)

            col1, col2 = st.columns(2)

            with col1:
                partes = r1[0][0].split("\\")
                lista10 = ast.literal_eval(partes[0].strip())
                lista20 = ast.literal_eval(partes[1].strip())

                cadena10 = "".join(lista10)
                cadena20 = "".join(lista20)

                st.write(
                    f"## **P({cadena20}$^t$ $^+$ $^1$ | {cadena10}$^t$ = {r1[1][0]})**"
                )
                st.dataframe(df_r1)

            with col2:
                partes = r2[0][0].split("\\")
                lista11 = ast.literal_eval(partes[0].strip())
                lista21 = ast.literal_eval(partes[1].strip())

                cadena11 = "".join(lista11)
                cadena21 = "".join(lista21)
                st.write(
                    f"## **P({cadena21}$^t$ $^+$ $^1$ | {cadena11}$^t$ = {r2[1][0]})**"
                )
                st.dataframe(df_r2)

            E.marcarAristas(lista11, lista21, lista10, lista20, optionep, optionef)

            end_time = time.time()

            total_time = end_time - start_time

            st.write(f"Tiempo de ejecución: {round(total_time, 4)} segundos")
            st.write("El emd es: ", mejor_costo)


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
                G.posicionate()

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
            G.posicionate()

        if graph_option == "Aleatorio":

            nodes, edges, graph, last_action, name = G.generate_graph_random()

            st.session_state["nodes"] = nodes
            st.session_state["edges"] = edges
            st.session_state["graph"] = graph
            st.session_state["last_action"] = last_action
            st.session_state["name_graph"] = name
            G.posicionate()


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
            if st.session_state["graph"]:
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
            if st.session_state["graph"]:
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
            if st.session_state["graph"]:
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
        G.posicionate()

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
