import numpy as np

def nearest_neighbor(instance, alpha=1.0, beta=3.0, linear=True):
    nodes = list(instance.villes.keys())
    start_node = nodes[0]
    end_node = nodes[-1]
    
    # Pré-tri des pickups par ratio 
    sorted_pickups_all = {}
    for n in nodes:
        sorted_pickups_all[n] = sorted(enumerate(instance.villes[n]['pickups']), 
                                       key=lambda x: x[1]['profit']/x[1]['poids'], reverse=True)

    decision = {i: [] for i in nodes}
    customers = set(nodes[1:-1]) #Utilisation d'un set
    tour = [start_node]
    current_load = instance.w0
    all_w = [current_load]
    current_node = start_node

    while customers:
        best_score = -float('inf')
        best_cand = None
        best_pickups = []
        best_deliv_poids = 0

        # Estimation simplifiée de la distance restante
        # Au lieu de np.median, on utilise une estimation basée sur le nombre de clients
        n_restant = len(customers)
        # On peut pré-calculer la distance moyenne de la matrice pour gagner du temps
        avg_dist_matrix = np.mean(list(instance.dist_matrix[current_node].values()))

        for cand in customers:
            dist = instance.dist_matrix[current_node][cand]
            
            # (Transport Cost)
            if linear:
                transport_cost = dist * current_load * alpha
            else:
                transport_cost = dist * (current_load * alpha + beta * (current_load**2))

            # Allègement
            poids_deliv = sum(d['poids'] for d in instance.villes[cand]['deliveries'])
            
            # C'est l'estimation de "combien de temps ce poids restera dans le camion"
            dist_estimee_restante = avg_dist_matrix * (n_restant-1)

            if linear:
                gain_allegement = poids_deliv * alpha * dist_estimee_restante
            else:
                gain_allegement = dist_estimee_restante * (poids_deliv * alpha + beta * (poids_deliv**2))

            # Simulation sac à dos
            temp_load = current_load - poids_deliv
            temp_profit = 0
            temp_pickups = [0] * len(instance.villes[cand]['pickups'])
            
            for idx, obj in sorted_pickups_all[cand]:
                if linear:
                    cout_futur_objet = obj['poids'] * dist_estimee_restante * alpha
                else:    
                    cout_futur_objet = dist_estimee_restante * (obj['poids']*alpha + beta *(obj['poids']**2 ))
                
                if temp_load + obj['poids'] <= instance.capacity:
                    if obj['profit'] > cout_futur_objet:
                        temp_profit += obj['profit']
                        temp_load += obj['poids']
                        temp_pickups[idx] = 1

            score = temp_profit - transport_cost + gain_allegement

            if score > best_score:
                best_score = score
                best_cand = cand
                best_pickups = temp_pickups
                best_deliv_poids = poids_deliv

        # Exécution
        if best_cand is None: best_cand = list(customers)[0]

        poids_ramasse = sum(instance.villes[best_cand]['pickups'][i]['poids'] 
                            for i, v in enumerate(best_pickups) if v == 1)
        
        current_load = current_load - best_deliv_poids + poids_ramasse
        current_node = best_cand
        decision[current_node] = best_pickups
        tour.append(current_node)
        customers.remove(current_node)
        all_w.append(current_load)

    tour.append(end_node)
    all_w.append(current_load)
    return tour, decision, all_w