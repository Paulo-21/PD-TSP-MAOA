import math

class PDTSP_Instance:
    def __init__(self, villes_multi, capacity, w0, display):
        """
        villes_multi : dictionnaire issu de prepare_split_data
        capacity : Wmax
        w0 : Poids initial au départ du dépôt
        display : coordonnées des villes pour l'affichage
        dist_matrix : Matrice des distances euclidienne entre chaque villes

        """
        self.villes = villes_multi
        self.capacity = capacity
        self.w0 = w0
        self.display = display
        self.dist_matrix = self._compute_distances()

    def _compute_distances(self):
        dist = {}
        for i, data_i in self.villes.items():
            dist[i] = {}
            for j, data_j in self.villes.items():
                c1, c2 = data_i['coords'], data_j['coords']
                d = math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)
                dist[i][j] = int(d + 0.5) # Arrondi TSPLIB standard
        return dist

    def evaluate_solution(self, tour, decisions, alpha=0.01, beta=0.01, linear=True, distance=False):
        """
        tour : [1, 5, 3, ..., 21]
        decisions : dict {id_ville: [1, 0, 1]} indiquant quels objets de 'pickups' sont pris.
        """
        current_weight = self.w0
        total_profit = 0
        total_transport_cost = 0
        
        # Vérification charge initiale
        if current_weight > self.capacity:
            return False, -float('inf'),

        for i in range(len(tour) - 1):
            u = tour[i]
            v = tour[i+1]
            
            # Coût du trajet u -> v (basé sur le poids en quittant u)
            d_uv = 1
            if distance:
                d_uv = self.dist_matrix[u][v]
            if linear:
                cost = d_uv * (alpha * current_weight)
            else:
                cost = d_uv * (alpha * current_weight + beta * (current_weight**2))
            
            total_transport_cost += cost
            
            # Action à la ville v 
            # Livraisons 
            for obj in self.villes[v]['deliveries']:
                current_weight -= obj['poids']
            
            # Ramassages 
            choix_v = decisions.get(v, []) # Liste de 0 et 1
            pickups_dispo = self.villes[v]['pickups']
            
            for idx, pris in enumerate(choix_v):
                if pris == 1 and idx < len(pickups_dispo):
                    obj = pickups_dispo[idx]
                    current_weight += obj['poids']
                    total_profit += obj['profit']
            
            # Vérifications
            if current_weight > self.capacity:
                return False, -float('inf'), 
            if current_weight < 0:
                return False, -float('inf'),

        score_z = total_profit - total_transport_cost
        return True, score_z