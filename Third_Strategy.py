import random
from Probabilities import Probabilities
import numpy as np
from scipy.spatial.distance import hamming

P = Probabilities()


class ThirdStrategy:
    # Función para calcular el costo de una partición
    def calcular_costo(self, particion, subconjunto, original, listaNodos):
        ep1, ef1, vp1, ep2, ef2, vp2 = particion

        if len(ep1) > 0:
            ep1, vp1 = zip(*sorted(zip(ep1, vp1)))
        if len(ep2) > 0:
            ep2, vp2 = zip(*sorted(zip(ep2, vp2)))

        ef1 = sorted(ef1)
        ef2 = sorted(ef2)

        r1 = P.generarDistribucionProbabilidades(subconjunto, ep1, ef1, vp1, listaNodos)
        r2 = P.generarDistribucionProbabilidades(subconjunto, ep2, ef2, vp2, listaNodos)

        tensor1 = np.tensordot(r2[1][1:], r1[1][1:], axes=0).flatten()
        tensor2 = np.tensordot(r1[1][1:], r2[1][1:], axes=0).flatten()

        emd1 = hamming(original[1][1:], tensor1)
        emd2 = hamming(original[1][1:], tensor2)
        print("Particion: ", particion, "EMD: ", min(emd1, emd2))
        return min(emd1, emd2), r1, r2

    def generate_random_partition(
        self, estados_presentes, estados_futuros, valores_estados_presentes
    ):
        n_ep = len(estados_presentes)
        n_ef = len(estados_futuros)
        partition_type = random.choice(["empty_ef", "empty_ep", "full"])

        if partition_type == "empty_ef" and n_ef > 0:
            i = random.randint(0, n_ef - 1)
            partition = (
                [],
                [estados_futuros[i]],
                [],
                estados_presentes,
                [ef for ef in estados_futuros if ef != estados_futuros[i]],
                valores_estados_presentes,
            )
        elif partition_type == "empty_ep" and n_ep > 0:
            i = random.randint(0, n_ep - 1)
            partition = (
                [estados_presentes[i]],
                [],
                [valores_estados_presentes[i]],
                [ep for ep in estados_presentes if ep != estados_presentes[i]],
                estados_futuros,
                [valores_estados_presentes[j] for j in range(n_ep) if j != i],
            )
        else:
            percentage = random.uniform(0.1, 0.4)
            num_ep1 = max(1, int(n_ep * percentage))
            num_ef1 = max(1, int(n_ef * percentage))

            ep_indices = random.sample(range(n_ep), num_ep1)
            ef_indices = random.sample(range(n_ef), num_ef1)

            ep1 = [estados_presentes[i] for i in ep_indices]
            ef1 = [estados_futuros[i] for i in ef_indices]

            vp1 = [valores_estados_presentes[i] for i in ep_indices]
            ep2 = [estados_presentes[i] for i in range(n_ep) if i not in ep_indices]
            ef2 = [estados_futuros[i] for i in range(n_ef) if i not in ef_indices]
            vp2 = [
                valores_estados_presentes[i] for i in range(n_ep) if i not in ep_indices
            ]

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
                (
                    replica1["partition"],
                    replica2["partition"],
                ) = (
                    replica2["partition"],
                    replica1["partition"],
                )
                (
                    replica1["loss"],
                    replica2["loss"],
                ) = (
                    replica2["loss"],
                    replica1["loss"],
                )
                (
                    replica1["r1"],
                    replica2["r1"],
                ) = (
                    replica2["r1"],
                    replica1["r1"],
                )
                (
                    replica1["r2"],
                    replica2["r2"],
                ) = (
                    replica2["r2"],
                    replica1["r2"],
                )
