import json
import streamlit as st
import numpy as np
import pandas as pd

# Cargar el JSON
with open("data.json", "r") as f:
    data = json.load(f)

# Extraer los nombres de los objetos dentro del JSON
options = [list(obj.keys())[0] for obj in data]

# Crear el select dinámico con los nombres extraídos
selected_option = st.selectbox("Selecciona un nombre:", options)

# Obtener los valores de la opción seleccionada
selected_values = None
for entry in data:
    if selected_option in entry:
        selected_values = entry[selected_option]
        break

# Mostrar el select dinámico
st.write("Has seleccionado:", selected_option)

# crear selects dinámicamente dependiente de la longitud de la opción elegida
letter = selected_option.split(",")

# Calcular la longitud de la lista de opciones
length = len(letter)

# Crear un diccionario para almacenar los valores de cada letra
letter_values = {}
for i, l in enumerate(letter):
    letter_values[l] = [item for item in selected_values]

# Crear un DataFrame a partir del diccionario original
original_df = pd.DataFrame({k: pd.Series(v) for k, v in letter_values.items()})
st.write("Valores originales:")

# Mostrar los valores originales para cada letra por separado
for l in letter:
    st.write(f"Letra {l}:")
    st.write(original_df[l])

# Verificar si ya se ha creado la lista de matrices o si la longitud de letter ha cambiado
if "matrices" not in st.session_state or len(st.session_state.matrices) != length:
    # Crear matrices con las mismas dimensiones para cada select
    st.session_state.matrices = [
        np.random.randint(2, size=(3, 2**length)) for _ in range(length)
    ]


# Crear un diccionario para almacenar los valores seleccionados de cada select
select_values = {}

# Crear select boxes para cada letra en letter
for i, l in enumerate(letter):
    # Crear el select box y almacenar su valor seleccionado en select_values
    select_values[l] = st.selectbox(
        f"Selecciona un valor para {l}",
        options=[tuple(row) for row in st.session_state.matrices[i]],
    )

# Agregar un botón para actualizar los valores
if st.button("Actualizar valores"):
    for i, l in enumerate(letter):
        # Obtener el valor seleccionado para esta letra
        selected_value = select_values[l]

        # Actualizar los valores para esta letra manteniendo las claves intactas
        for j, item in enumerate(letter_values[l]):
            # Conservar la tupla de la clave y actualizar solo el valor
            key = list(item.keys())[0]
            if key == selected_option:
                item[key] = selected_value

# Mostrar los valores actualizados
st.write("Valores actualizados:")

# Iterar sobre las claves de letter_values y mostrar clave-valor para cada letra
for key in letter_values.keys():
    st.write(f"Letra {key}:")
    for item in letter_values[key]:
        st.write(item)
