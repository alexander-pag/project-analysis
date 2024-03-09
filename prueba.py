import streamlit as st
import networkx as nx
from streamlit_agraph import agraph, Node, Edge, Config
from Utils import Utils

# Se puede modificar los estilos de la pagina desde aquí
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background-color: #FFF6F6;
opacity: 0.8;
background-size: 20px 20px;
}
[data-testid='stHeader']{
display: none !important;
}
[data-testid = 'stAppViewBlockContainer']{
    max-width: 1200px;
}
'canvas' {
    background-color: red;

}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

U = Utils()

# Verifica si ya existe un estado de sesión, si no, lo crea
if "graph" not in st.session_state:
    st.session_state["graph"] = False
if "nodes" not in st.session_state:
    st.session_state["nodes"] = []
if "edges" not in st.session_state:
    st.session_state["edges"] = []
if "directed" not in st.session_state:
    st.session_state["directed"] = False
if "weighted" not in st.session_state:
    st.session_state["weighted"] = False
if "conex" not in st.session_state:
    st.session_state["conex"] = False
if "connected" not in st.session_state:
    st.session_state["connected"] = False
if "name_graph" not in st.session_state:
    st.session_state["name_graph"] = ""

# Crear un expander para el grafo en la barra lateral
with st.sidebar.expander("Grafo"):
    with st.form(key="graph_form"):
        # Checkbox para elegir si el grafo es dirigido
        st.session_state["directed"] = st.checkbox("¿Es dirigido?")

        # Checkbox para elegir si el grafo es ponderado
        weighted = st.checkbox("¿Es ponderado?")

        # Checkbox para elegir si el grafo es completo
        st.session_state["connected"] = st.checkbox("¿Es completo?")

        # Checkbox para elegir si el grafo es conexo
        st.session_state["conex"] = st.checkbox("¿Es conexo?")

        # Campo de texto para introducir la cantidad de nodos
        node_qty = st.text_input("Cantidad de nodos")

        # Botón para generar el grafo
        generate_graph = st.form_submit_button(label="Generar")

        if generate_graph:
            if st.session_state["connected"] and st.session_state["conex"]:
                # Crear un grafo aleatorio conexo y completo
                G = nx.connected_watts_strogatz_graph(
                    int(node_qty), int(node_qty) - 1, 0.5, tries=100
                )
            elif st.session_state["connected"]:
                # Crear un grafo aleatorio completo
                G = nx.complete_graph(int(node_qty))
            elif st.session_state["conex"]:
                # Crear un grafo aleatorio conexo
                G = nx.connected_watts_strogatz_graph(
                    int(node_qty), int(node_qty) // 2, 0.5, tries=100
                )
            else:
                # Crear un grafo aleatorio
                G = nx.gnp_random_graph(
                    int(node_qty), 0.5, directed=st.session_state["directed"]
                )

            # Convertir el grafo de networkx a formato agraph
            nodes = [
                Node(
                    label="Nodo " + str(n),
                    id=n,
                    color=U.generateColor(),
                    shape=U.generateShape(),
                )
                for n in G.nodes()
            ]
            edges = [Edge(str(u), str(v)) for u, v in G.edges()]

            # Guardar los nodos y aristas en el estado de sesión
            st.session_state["nodes"] = nodes
            st.session_state["edges"] = edges

            st.session_state["graph"] = True


# Crea tu configuración
config = Config(
    width="100%",
    height=600,
    directed=st.session_state["directed"],
    physics=False,
    hierarchical=True,
)

# Dibuja tu gráfico
return_value = agraph(
    nodes=st.session_state["nodes"], edges=st.session_state["edges"], config=config
)


"""
elif selectedIE == "Export":
            graph_data = {
                "graph": [
                    {
                        "name": (
                            st.session_state["name_graph"]
                            if st.session_state["name_graph"]
                            else "Grafo"
                        ),
                        "data": [],
                        "generalData1": 100,
                        "generalData2": "Alg",
                        "generalData3": 300,
                    }
                ]
            }

            for node in st.session_state["nodes"]:
                linked_nodes = []
                for edge in st.session_state["edges"]:
                    if edge.source == node.id:
                        linked_nodes.append(
                            {
                                "node_id": edge.to,
                                "weight": int(edge.label) if edge.label else 0,
                            }
                        )
                node_data = {
                    "id": node.id,
                    "label": node.label,
                    "data": {},
                    "type": "",
                    "linkedTo": linked_nodes,
                    "radius": node.size / 50,
                    "coordinates": {"x": 0, "y": 0},
                }
                graph_data["graph"][0]["data"].append(node_data)

            # Convierte el objeto del grafo a una cadena JSON
            json_str = json.dumps(graph_data)

            # Obtener la hora actual
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")

            name = ""
            if st.session_state["name_graph"]:
                name = st.session_state["name_graph"]
            else:
                name = "graph"

            st.download_button(
                label="Descargar JSON",
                data=json_str,
                file_name=(name + current_time + ".json"),
                mime="application/json",
            )




            uploaded_file = st.sidebar.file_uploader(
                "Elige un archivo JSON", type="json"
            )
            if uploaded_file is not None:
                data = json.load(uploaded_file)

                for graph in data["graph"]:
                    for node_data in graph["data"]:
                        node = Node(
                            id=node_data["id"],
                            label=node_data["label"],
                            size=node_data["radius"]
                            * 50,  # Ajusta el tamaño según tus necesidades
                            shape="circularImage",
                            image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png",  # Ajusta la imagen según tus necesidades
                        )
                        st.session_state["nodes"].append(node)

                        for linked_node in node_data["linkedTo"]:
                            edge = Edge(
                                source=node.id,
                                target=linked_node["node_id"],
                                label=str(linked_node["weight"]),
                            )
                            st.session_state["edges"].append(edge)

            # Determinar si el grafo es bipartito o no
            is_bipartite = True
            for edge in st.session_state["edges"]:
                if edge.source == edge.to:
                    is_bipartite = False
                    break

            if is_bipartite:
                st.write("El grafo es bipartito")
"""
