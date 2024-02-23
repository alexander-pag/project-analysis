import streamlit as st

# Crear listas de opciones para las barras de navegación
opciones_menu1 = ["Opción 1", "Opción 2", "Opción 3"]
opciones_menu2 = ["Opción A", "Opción B", "Opción C"]

# Crear las barras de navegación como cajas de selección en la barra lateral
opcion_seleccionada_menu1 = st.sidebar.selectbox("Menú 1", opciones_menu1)
opcion_seleccionada_menu2 = st.sidebar.selectbox("Menú 2", opciones_menu2)

# Mostrar información basada en las opciones seleccionadas
st.write(
    f"Has seleccionado {opcion_seleccionada_menu1} del Menú 1 y {opcion_seleccionada_menu2} del Menú 2."
)
