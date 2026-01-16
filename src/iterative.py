import numpy as np
from numba import njit
from random import shuffle

# LE MOTEUR NUMBA 
@njit
def _numba_engine(tour, dist_matrix, neighbors):
    n = len(tour)
    current_tour = tour.copy()
    
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 2):
            v_i = current_tour[i]
            # On ne teste que les voisins proches (ID - 1 car les index commencent à 0)
            for v_j in neighbors[v_i - 1]:
                # Trouver l'index de v_j dans le tour
                j = -1
                for idx in range(i + 1, n - 1):
                    if current_tour[idx] == v_j:
                        j = idx
                        break
                if j == -1: continue

                # Delta-Evaluation de la distance (2-Opt)
                # On compare (i-1, i) + (j, j+1) vs (i-1, j) + (i, j+1)
                d_old = dist_matrix[current_tour[i-1]-1, current_tour[i]-1] + \
                        dist_matrix[current_tour[j]-1, current_tour[j+1]-1]
                d_new = dist_matrix[current_tour[i-1]-1, current_tour[j]-1] + \
                        dist_matrix[current_tour[i]-1, current_tour[j+1]-1]
                
                if d_new < d_old - 1e-6: # Petit epsilon pour la précision numérique
                    current_tour[i:j+1] = current_tour[i:j+1][::-1]
                    improved = True
                    break
                    
            if improved: break
    return current_tour

def hill_climbing(instance, tour_initial, alpha=0.01, beta=0.01, linear=True, distance=True):

    n_villes = len(instance.villes)
    
    villes_internes = list(range(2, n_villes + 1))
    shuffle(villes_internes)
    tour_initial = [1] + villes_internes + [n_villes]

    # Remplissage robuste de la matrice NumPy
    dist_matrix = np.zeros((n_villes, n_villes), dtype=np.float64)
    # Format dictionnaire de dictionnaires : {u: {v: dist}}
    for u, destinations in instance.dist_matrix.items():
        for v, d in destinations.items():
            dist_matrix[u-1][v-1] = d

    # Pré-calcul des voisins proches (Top 20)
    # On s'assure que K ne dépasse pas le nombre de villes disponibles
    K = min(20, n_villes - 1)
    neighbors_mat = np.zeros((n_villes, K), dtype=np.int32)
    for i in range(n_villes):
        sorted_indices = np.argsort(dist_matrix[i])
        count = 0
        for idx in sorted_indices:
            if idx != i and count < K:
                neighbors_mat[i][count] = idx + 1 # On stocke l'ID (index+1)
                count += 1

    # EXECUTION DU MOTEUR NUMBA
    tour_arr = np.array(tour_initial, dtype=np.int32)
    final_tour_arr = _numba_engine(tour_arr, dist_matrix, neighbors_mat)
    final_tour = list(final_tour_arr)

    # RÉPARATION DES DÉCISIONS 
    current_load = instance.w0
    final_decisions = {}
    
    n_total = len(final_tour)
    dist_restante_reelle = [0.0] * n_total
    
    # On part de la fin et on remonte pour cumuler les distances à parcourir pour chaque noeud
    for i in range(n_total - 2, -1, -1):
        u = final_tour[i]
        v = final_tour[i+1]
        dist_segment = dist_matrix[u-1][v-1]
        dist_restante_reelle[i] = dist_restante_reelle[i+1] + dist_segment


    # Utilise l'ordre du tour optimisé par Numba
    for i, node in enumerate(final_tour):
        n_total -= 1
        if node not in instance.villes: continue
        
        # Distance exacte qu'il reste à parcourir à partir de ce noeud
        d_future = dist_restante_reelle[i]

        # Livraisons
        for delivery in instance.villes[node]['deliveries']:
            current_load -= delivery['poids']
            
        # Pickups
        pickups = instance.villes[node]['pickups']
        # On trie par rentabilité (Profit / Poids)
        sorted_indices = sorted(range(len(pickups)), 
                                key=lambda k: pickups[k]['profit']/pickups[k]['poids'] if pickups[k]['poids'] > 0 else 0, 
                                reverse=True)
        
        node_decisions = [0] * len(pickups)
        
        for idx in sorted_indices:
            p_obj = pickups[idx]['poids']
            
            # Coût de transport réel pour cet objet jusqu'au dépôt final
            if linear:
                cout_futur_objet = p_obj* d_future * alpha 
            else:    
                cout_futur_objet = d_future * (p_obj*alpha + beta *(p_obj**2 )) 
            
            if current_load + p_obj <= instance.capacity:
                if pickups[idx]['profit'] > cout_futur_objet:
                    node_decisions[idx] = 1
                    current_load += p_obj
        
        final_decisions[node] = node_decisions
        
    return final_tour, final_decisions