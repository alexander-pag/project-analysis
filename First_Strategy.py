import numpy as np
from scipy.spatial.distance import hamming
from scipy.stats import wasserstein_distance
from Probabilities import Probabilities

P = Probabilities()


class FirstStrategy:
    # Función para generar una partición inicial aleatoria
    def generar_particion_aleatoria(
        self, estados_presentes, estados_futuros, valores_estados_presentes
    ):
        ep1 = list([])
        ef1 = list(estados_futuros[0])
        vp1 = list([])
        ep2 = list(estados_presentes)
        ef2 = list(estados_futuros[1:])
        vp2 = list(valores_estados_presentes)

        return (ep1, ef1, vp1, ep2, ef2, vp2)

    # Función para calcular el costo de una partición
    def calcular_costo(self, particion, subconjunto, original, listaNodos):
        ep1, ef1, vp1, ep2, ef2, vp2 = particion

        if len(ep1) > 0:
            ep1, vp1 = zip(*sorted(zip(ep1, vp1)))

        ef1 = sorted(ef1)
        ep2, vp2 = zip(*sorted(zip(ep2, vp2)))
        ef2 = sorted(ef2)

        r1 = P.generarDistribucionProbabilidades(subconjunto, ep1, ef1, vp1, listaNodos)
        r2 = P.generarDistribucionProbabilidades(subconjunto, ep2, ef2, vp2, listaNodos)

        # print("Particion: ", particion, "R1: ", r1, "R2: ", r2)

        tensor1 = np.tensordot(r2[1][1:], r1[1][1:], axes=0).flatten()
        tensor2 = np.tensordot(r1[1][1:], r2[1][1:], axes=0).flatten()

        emd1 = hamming(original[1][1:], tensor1)
        emd2 = hamming(original[1][1:], tensor2)
        print("Particion: ", particion, "EMD: ", min(emd1, emd2))
        return min(emd1, emd2), r1, r2

    # Función para generar una nueva partición a partir de una partición dada
    def generar_vecino(self, particion, fase):
        ep1, ef1, vp1, ep2, ef2, vp2 = particion

        nuevo_vecino = False

        while not nuevo_vecino:
            if fase < len(ef2):  # Fase 1: intercambiar elemento entre ef1 y ef2
                ef1.append(ef2.pop(0))
                ef2.append(ef1.pop(0))
            elif fase < len(ef2) + len(
                ep2
            ):  # Fase 2: intercambiar elementos entre ep1 y ep2
                if len(ep1) == 0:
                    ef2.append(ef1.pop(0))
                    ep1.append(ep2.pop(0))
                    vp1.append(vp2.pop(0))
                else:
                    ep1.append(ep2.pop(0))
                    ep2.append(ep1.pop(0))
                    vp1.append(vp2.pop(0))
                    vp2.append(vp1.pop(0))
            else:  # Fase 3: ep1 intercambia elemento con ep2 mientras ef1 permanece igual
                fase_3_index = fase - len(ef2) - len(ep2)
                if fase_3_index < len(ep2):  # intercambiar ep1 y ep2
                    if len(ep1) == 0:
                        ep1.append(ep2.pop(0))
                        vp1.append(vp2.pop(0))
                    else:
                        ep1.append(ep2.pop(0))
                        ep2.append(ep1.pop(0))
                        vp1.append(vp2.pop(0))
                        vp2.append(vp1.pop(0))
                else:  # después de intercambiar ep1 y ep2, cambiar ef1 y ef2
                    ef1.append(ef2.pop(0))
                    ef2.append(ef1.pop(0))

            # Verificar la condición de evitar ep1 y ef1 conteniendo el mismo elemento
            if not (ep1 and ef1 and ep1[0] == ef1[0]):
                nuevo_vecino = True

        return (ep1, ef1, vp1, ep2, ef2, vp2)

    # Algoritmo de Búsqueda Local con EMD y Programación Dinámica
    def busqueda_local_emd(
        self,
        estados_presentes,
        estados_futuros,
        valores_estados_presentes,
        subconjunto,
        listaNodos,
        original_system,
    ):
        mejor_particion = self.generar_particion_aleatoria(
            estados_presentes, estados_futuros, valores_estados_presentes
        )
        mejor_costo, r1, r2 = self.calcular_costo(
            mejor_particion, subconjunto, original_system, listaNodos
        )
        max_iteraciones = (len(estados_presentes) * len(estados_futuros)) + (
            len(estados_presentes) + len(estados_futuros)
        )

        print(max(len(estados_futuros), len(estados_presentes)), max_iteraciones)

        iteraciones_sin_mejora = 0
        particiones_visitadas = set()
        particiones_visitadas.add(tuple(map(tuple, mejor_particion)))

        # ya que puede ser que la primera particion de 0, entonces se termina
        if mejor_costo == 0.0:
            return mejor_particion, mejor_costo, r1, r2

        while iteraciones_sin_mejora < max_iteraciones:
            vecino = self.generar_vecino(mejor_particion, iteraciones_sin_mejora)
            vecino_tuple = tuple(map(tuple, vecino))

            if vecino_tuple in particiones_visitadas:
                iteraciones_sin_mejora += 1
                continue

            particiones_visitadas.add(vecino_tuple)
            costo_vecino, r1, r2 = self.calcular_costo(
                vecino, subconjunto, original_system, listaNodos
            )

            # Terminar si se encuentra un costo EMD de 0
            if costo_vecino == 0.0:
                return vecino, costo_vecino, r1, r2

            if costo_vecino < mejor_costo:
                mejor_particion = vecino
                mejor_costo = costo_vecino
                iteraciones_sin_mejora = 0
            else:
                iteraciones_sin_mejora += 1

        return mejor_particion, mejor_costo, r1, r2
