import streamlit
from streamlit_agraph import agraph, Node, Edge, Config

nodes = []
edges = []
nodes.append(
    Node(
        id="Spiderman",
        size=50,
        svg="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png",
    )
)
nodes.append(
    Node(
        id="Captain_Marvel",
        size=50,
        svg="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_captainmarvel.png",
    )
)
edges.append(Edge(source="Captain_Marvel", target="Spiderman", type="CURVE_SMOOTH"))

config = Config(
    width=500,
    height=500,
    nodeHighlightBehavior=True,
    highlightColor="#F7A7A6",  # or "blue"
    directed=False,
    collapsible=True,
    physics=False,
    # coming soon (set for all): node_size=1000, node_color="blue"
)

return_value = agraph(nodes=nodes, edges=edges, config=config)
