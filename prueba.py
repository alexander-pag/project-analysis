import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

if "nodes" not in st.session_state:
    st.session_state["nodes"] = []

if "edges" not in st.session_state:
    st.session_state["edges"] = []

# Añade un nodo
st.session_state["nodes"].append(
    Node(id="1", label="Node 1", color="red", shape="star")
)

st.session_state["nodes"].append(
    Node(id="2", label="Node 2", color="red", shape="triangle")
)

st.session_state["nodes"].append(
    Node(id="3", label="Node 3", color="red", shape="square")
)

st.session_state["nodes"].append(
    Node(id="4", label="Node 4", color="red", shape="diamond")
)

st.session_state["nodes"].append(Node(id="5", label="Node 5", color="red"))

# Crea tu configuración
config = Config(
    width="100%",
    height=600,
    directed=False,
    physics=False,
    hierarchical=True,
)

# Dibuja tu gráfico
return_value = agraph(
    nodes=st.session_state["nodes"], edges=st.session_state["edges"], config=config
)
