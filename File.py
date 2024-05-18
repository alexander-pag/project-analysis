from streamlit_agraph import Edge, Node
import streamlit as st
import pandas as pd
import pyautogui as pg
import io
from Utils import Utils

U = Utils()


class File:
    def open_json_file(self, data, nodes, edges):
        for graph in data["graph"]:
            for node_data in graph["data"]:
                node = Node(
                    id=node_data["id"],
                    label=node_data["label"],
                    color=node_data["color"],
                    shape=node_data["shape"],
                    font={"color": "#FFFFFF"},
                    size=15,
                )
                nodes.append(node)

                for linked_node in node_data["linkedTo"]:
                    edge = Edge(
                        source=node.id,
                        target=linked_node["node_id"],
                        color=linked_node["color"],
                        width=linked_node["width"],
                        dashes=linked_node["dashes"],
                        label=(
                            str(linked_node["weight"]) if linked_node["weight"] else ""
                        ),
                    )
                    edges.append(edge)

                    graph = True

    def export_to_image(self):
        # Definir las coordenadas del área de la captura de pantalla
        x, y, width, height = 580, 320, 1150, 720

        # Tomar la captura de pantalla
        screenshot = pg.screenshot(region=(x, y, width, height))

        # Crear un objeto BytesIO para guardar la imagen
        buf = io.BytesIO()

        # Guardar la captura de pantalla en el objeto BytesIO
        screenshot.save(buf, format="png")

        date = U.generateDate()

        # Crear un botón de descarga para la imagen
        st.download_button(
            label="Descargar imagen",
            data=buf.getvalue(),
            file_name="graph-" + date + ".png",
            mime="image/png",
        )

    def export_to_xlsx(self, nodes, edges, weighted):
        # Crea una lista para almacenar los datos de los nodos
        nodes_data = []

        # Recorre cada nodo y arista en el estado de la sesión
        for node in nodes:
            linked_nodes = [
                {
                    "node_id": edge.to,
                    "weight": edge.label if weighted else 0,
                    "color": edge.color,
                }
                for edge in edges
                if edge.source == node.id
            ]
            # Agrega los datos del nodo a la lista
            nodes_data.append(
                {
                    "id": node.id,
                    "label": node.label,
                    "color": node.color,
                    "shape": node.shape,
                    "size": node.size,
                    "data": {},
                    "type": "",
                    "linkedTo": ", ".join(
                        [
                            f"(node_id: {ln['node_id']}) (weight: {ln['weight']}) (color: {ln['color']})"
                            for ln in linked_nodes
                        ]
                    ),
                    "radius": node.size / 2,
                    "coordinates": {"x": 0, "y": 0},
                }
            )

        # Crea un DataFrame para los nodos
        nodes_df = pd.DataFrame(nodes_data)

        # Crea un objeto BytesIO para guardar el archivo XLSX
        buf = io.BytesIO()

        # Guarda los datos de los nodos en un archivo XLSX
        nodes_df.to_excel(buf, index=False)

        date = U.generateDate()

        # Crea un botón de descarga para el archivo XLSX
        st.download_button(
            label="Descargar XLSX",
            data=buf.getvalue(),
            file_name="graph-" + date + ".xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
