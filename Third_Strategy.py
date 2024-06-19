import random
from Probabilities import Probabilities
import numpy as np
from scipy.stats import wasserstein_distance

P = Probabilities()


class ThirdStrategy:
    def __init__(self):
        self.loss_cache = {}

    def calcular_costo(self, particion, subconjunto, original, listaNodos):
        partition_key = tuple(map(tuple, particion))
        if partition_key in self.loss_cache:
            return self.loss_cache[partition_key]

        ep1, ef1, vp1, ep2, ef2, vp2 = particion

        if ep1:
            ep1, vp1 = zip(*sorted(zip(ep1, vp1)))
        if ep2:
            ep2, vp2 = zip(*sorted(zip(ep2, vp2)))

        ef1.sort()
        ef2.sort()

        r1 = P.generarDistribucionProbabilidades(subconjunto, ep1, ef1, vp1, listaNodos)
        r2 = P.generarDistribucionProbabilidades(subconjunto, ep2, ef2, vp2, listaNodos)

        # print("Particion: ", particion, "R1: ", r1, "R2: ", r2)

        tensor1 = np.tensordot(r2[1][1:], r1[1][1:], axes=0).flatten()
        tensor2 = np.tensordot(r1[1][1:], r2[1][1:], axes=0).flatten()

        emd1 = wasserstein_distance(original[1][1:], tensor1)
        emd2 = wasserstein_distance(original[1][1:], tensor2)

        min_emd = min(emd1, emd2)

        self.loss_cache[partition_key] = (min_emd, r1, r2)
        return min_emd, r1, r2

    def generate_random_partition(
        self, estados_presentes, estados_futuros, valores_estados_presentes
    ):
        n_ep = len(estados_presentes)
        n_ef = len(estados_futuros)
        partition_type = np.random.choice(["empty_ef", "empty_ep", "full"])

        estados_presentes = np.array(estados_presentes)
        estados_futuros = np.array(estados_futuros)
        valores_estados_presentes = np.array(valores_estados_presentes)

        if partition_type == "empty_ef" and n_ef > 0:
            i = np.random.randint(n_ef)
            ef1 = [estados_futuros[i]]
            ef2 = np.delete(estados_futuros, i).tolist()
            partition = (
                [],
                ef1,
                [],
                estados_presentes.tolist(),
                ef2,
                valores_estados_presentes.tolist(),
            )
        elif partition_type == "empty_ep" and n_ep > 0:
            i = np.random.randint(n_ep)
            ep1 = [estados_presentes[i]]
            vp1 = [valores_estados_presentes[i]]
            ep2 = np.delete(estados_presentes, i).tolist()
            vp2 = np.delete(valores_estados_presentes, i).tolist()
            partition = (ep1, [], vp1, ep2, estados_futuros.tolist(), vp2)
        else:
            percentage = np.random.uniform(0.1, 0.2)
            num_ep1 = max(1, int(n_ep * percentage))
            num_ef1 = max(1, int(n_ef * percentage))

            ep_indices = np.random.choice(n_ep, num_ep1, replace=False)
            ef_indices = np.random.choice(n_ef, num_ef1, replace=False)

            ep1 = estados_presentes[ep_indices].tolist()
            ef1 = estados_futuros[ef_indices].tolist()
            vp1 = valores_estados_presentes[ep_indices].tolist()
            ep2 = np.delete(estados_presentes, ep_indices).tolist()
            ef2 = np.delete(estados_futuros, ef_indices).tolist()
            vp2 = np.delete(valores_estados_presentes, ep_indices).tolist()

            partition = (ep1, ef1, vp1, ep2, ef2, vp2)

        return partition

    def metropolis_update(
        self,
        replica,
        estados_presentes,
        estados_futuros,
        valores_estados_presentes,
        subconjunto,
        original_system,
        listaNodos,
    ):
        current_partition = replica["partition"]
        current_loss = replica["loss"]
        new_partition = self.generate_random_partition(
            estados_presentes, estados_futuros, valores_estados_presentes
        )
        new_loss, r1, r2 = self.calcular_costo(
            new_partition, subconjunto, original_system, listaNodos
        )
        delta_loss = new_loss - current_loss

        if delta_loss < 0 or random.uniform(0, 1) < np.exp(
            -replica["beta"] * delta_loss
        ):
            replica["partition"] = new_partition
            replica["loss"] = new_loss
            replica["r1"] = r1
            replica["r2"] = r2

    def replica_exchange(self, replicas):
        for i in range(len(replicas) - 1):
            replica1, replica2 = replicas[i], replicas[i + 1]
            delta = (replica2["beta"] - replica1["beta"]) * (
                replica1["loss"] - replica2["loss"]
            )
            if delta < 0 or random.uniform(0, 1) < np.exp(-delta):
                replica1["partition"], replica2["partition"] = (
                    replica2["partition"],
                    replica1["partition"],
                )
                replica1["loss"], replica2["loss"] = replica2["loss"], replica1["loss"]
                replica1["r1"], replica2["r1"] = replica2["r1"], replica1["r1"]
                replica1["r2"], replica2["r2"] = replica2["r2"], replica1["r2"]
