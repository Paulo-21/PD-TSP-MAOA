
import numpy as np

def nearest_neighbor(instance, alpha=1.0, beta=3.0, linear=True):
    """
    On utilise une méthode qui calcule le score pour chaque ville à partir de la ville courante
    ainsi on va dans la ville qui a le meilleur score
    """
    nodes = list(instance.villes.keys())
    start_node = nodes[0]
    end_node = nodes[-1]
    
    decision = {i: [] for i in nodes}
    customers = [n for n in nodes if n != start_node and n != end_node]
    tour = [start_node]
    current_load = instance.w0
    all_w = [current_load]

    current_node = start_node

    while customers:
        best_score = -float('inf')
        best_cand = None
        best_pickups = []
        best_deliv_poids = 0

        for cand in customers:
            dist = instance.dist_matrix[current_node][cand]
            all_dist = []

            # On prend le max des distance moyenne des distances vers les autres et le dépôt
            for cand2 in customers:
                others = [n for n in customers if n != cand2] + [end_node]
                avg_dist_restante = sum(instance.dist_matrix[cand2][o] for o in others) 
                all_dist.append(avg_dist_restante)

            max_dist = np.median(all_dist)

            # (Transport Cost)
            if linear:
                transport_cost = dist * current_load * alpha
            else:
                transport_cost = dist * ( current_load * alpha +  beta *(current_load**2 ) )
   
            # On calcule ce qu'on livre (allègement)
            poids_deliv = sum(d['poids'] for d in instance.villes[cand]['deliveries'])
            if linear:
                gain_allegement = poids_deliv * alpha * max_dist
            else:
                gain_allegement = max_dist * (poids_deliv * alpha +  beta *(poids_deliv**2 ))
           

            # Simulation sac à dos pour les pickups
            temp_load = current_load - poids_deliv
            temp_profit = 0
            temp_pickups = [0] * len(instance.villes[cand]['pickups'])
            
            # Tri par ratio profit/poids
            pickups = sorted(enumerate(instance.villes[cand]['pickups']), 
                            key=lambda x: x[1]['profit']/x[1]['poids'], reverse=True)
            
            for idx, obj in pickups:
                # Coût futur estimé pour cet objet précis
                if linear:
                    cout_futur_objet = obj['poids'] * max_dist * alpha
                else:    
                    cout_futur_objet = max_dist * (obj['poids']*alpha + beta *(obj['poids']**2 ))
                
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

        # Exécution du mouvement
        if best_cand is None: best_cand = customers[0] # Sécurité

        # Calcul du poids final après opérations dans la ville
        poids_ramasse = sum(instance.villes[best_cand]['pickups'][i]['poids'] 
                            for i, v in enumerate(best_pickups) if v == 1)
        
        current_load = current_load - best_deliv_poids + poids_ramasse
        current_node = best_cand
        
        decision[current_node] = best_pickups
        tour.append(current_node)
        customers.remove(current_node)
        all_w.append(current_load)

    # Retour final au dépôt
    tour.append(end_node)
    all_w.append(current_load)
    
    return tour, decision, all_w