from itertools import product


def convertir_a_lista(cadena):
    # Dividir la cadena en componentes separados por saltos de línea y convertir cada uno a entero
    return [int(x) for x in cadena.split() if x.strip()]


def generar_diccionario(cadena, tamaño, letra, num_bits):
    # Convertir la cadena a lista de enteros
    valores = convertir_a_lista(cadena)

    # Verificar que el tamaño sea una potencia de 2
    if tamaño != 2**num_bits:
        raise ValueError("El tamaño debe ser igual a 2^num_bits.")

    # Verificar que el número de valores coincida con el tamaño
    if len(valores) != tamaño:
        raise ValueError(
            "La cantidad de valores no coincide con el tamaño especificado."
        )

    # Generar todas las combinaciones posibles de num_bits
    combinaciones = list(product([0, 1], repeat=num_bits))

    # Crear el diccionario de salida
    resultado = {letra: {}}

    # Asignar los valores proporcionados a las combinaciones
    for i, combinacion in enumerate(combinaciones):
        resultado[letra][combinacion] = valores[i]

    return resultado


def guardar_en_python_file(diccionario, archivo):
    with open(archivo, "w") as file:
        file.write(f"{diccionario}")


# Ejemplo de uso:
cadena = """
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
1
0
"""
tamaño = 256
letra = "H"
num_bits = 8

diccionario = generar_diccionario(cadena, tamaño, letra, num_bits)
# Para no sobreescribir en states.py, se guarda en resultado.py
guardar_en_python_file(diccionario, "resultado.py")

print(f'Diccionario guardado en "resultado.py".')
