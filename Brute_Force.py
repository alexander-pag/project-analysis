import numpy as np
from scipy.spatial.distance import hamming
from Probabilities import Probabilities
from itertools import combinations, chain


P = Probabilities()


class BruteForce:

    def calcular_costo(self, particion, subconjunto, original, listaNodos):
        ep1, ef1, vp1, ep2, ef2, vp2 = particion
        r1 = P.generarDistribucionProbabilidades(subconjunto, ep1, ef1, vp1, listaNodos)
        r2 = P.generarDistribucionProbabilidades(subconjunto, ep2, ef2, vp2, listaNodos)
        tensor = np.tensordot(r1[1][1:], r2[1][1:], axes=0).flatten()
        emd = hamming(original[1][1:], tensor)
        return emd, r1, r2

    # Fuerza bruta para comparar eficiencias
    def fuerza_bruta(
        self,
        estados_presentes,
        estados_futuros,
        valores_estados_presentes,
        subconjunto,
        listaNodos,
        original_system,
    ):

        best_cost = float("inf")
        best_partition = None
        best_r1 = None
        best_r2 = None

        # Generar todas las combinaciones posibles de particiones
        for ep1_indices in chain.from_iterable(
            combinations(range(len(estados_presentes)), r)
            for r in range(len(estados_presentes) + 1)
        ):
            for ef1_indices in chain.from_iterable(
                combinations(range(len(estados_futuros)), r)
                for r in range(len(estados_futuros) + 1)
            ):
                ep1 = [estados_presentes[i] for i in ep1_indices]
                ef1 = [estados_futuros[i] for i in ef1_indices]
                vp1 = [valores_estados_presentes[i] for i in ep1_indices]
                ep2 = [
                    estados_presentes[i]
                    for i in range(len(estados_presentes))
                    if i not in ep1_indices
                ]
                ef2 = [
                    estados_futuros[i]
                    for i in range(len(estados_futuros))
                    if i not in ef1_indices
                ]
                vp2 = [
                    valores_estados_presentes[i]
                    for i in range(len(valores_estados_presentes))
                    if i not in ep1_indices
                ]

                if not ep1 and not ef1:
                    continue
                if not ep2 and not ef2:
                    continue

                particion = (ep1, ef1, vp1, ep2, ef2, vp2)
                costo, r1, r2 = self.calcular_costo(
                    particion, subconjunto, original_system, listaNodos
                )

                if costo < best_cost:
                    best_cost = costo
                    best_partition = particion
                    best_r1 = r1
                    best_r2 = r2

        return best_partition, best_cost, best_r1, best_r2
