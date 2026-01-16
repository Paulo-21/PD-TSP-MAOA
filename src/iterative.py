"""
L'idée est la suivante: on commence avec une solution initiale, généré avec greedy ou nearest
Ensuite on fait des swap de ville si autorisé, et on redécide des objets à prendre ou pas
"""
def repair_decisions(instance, tour, alpha, beta, linear):
    """
    Prend un tour imposé et remplit le camion intelligemment à chaque étape.
    Retourne le dictionnaire 'decision' optimisé pour ce tour.
    """
    current_load = instance.w0
    decisions = {node: [] for node in instance.villes}
    
    # On suit le tour (sauf le dépôt final pour les actions)
    for node in tour[:-1]:
        # On livre d'abord (allège le camion)
        for obj in instance.villes[node]['deliveries']:
            current_load -= obj['poids']
            
        # On choisit quoi ramasser (Sac à dos glouton)
        pickups = instance.villes[node]['pickups']
        node_decisions = [0] * len(pickups)
        
        # Tri par ratio profit/poids
        sorted_pickups = sorted(enumerate(pickups), 
                               key=lambda x: x[1]['profit']/x[1]['poids'], reverse=True)
        
        for idx, obj in sorted_pickups:
            # Optionnel : ajouter ici ton test "obj['profit'] > cout_futur"
            if current_load + obj['poids'] <= instance.capacity:
                node_decisions[idx] = 1
                current_load += obj['poids']
        
        decisions[node] = node_decisions
        
    return decisions

def hill_climbing(instance, tour_initial, alpha=0.01, beta=0.01, linear=True, distance=True):
    cpt = 0
    current_tour = tour_initial
    current_decisions = repair_decisions(instance, current_tour, alpha, beta, linear)
    _, current_score = instance.evaluate_solution(current_tour, current_decisions, alpha, beta, linear, distance=distance)
    
    improved = True
    while improved:
        improved = False
        # On parcourt les voisins (stratégie de Swap)
        for i in range(1, len(current_tour) - 2): # On ne touche pas au dépôt de départ
            for j in range(i + 1, len(current_tour) - 2): # Ni au dépôt de fin
                
                # Générer le voisin (Swap)
                new_tour = current_tour[:]
                new_tour[i], new_tour[j] = new_tour[j], new_tour[i]
                
                # Réparer les objets pour ce nouveau tour
                new_decisions = repair_decisions(instance, new_tour, alpha, beta, linear)
                
                # Évaluer
                success, new_score = instance.evaluate_solution(new_tour, new_decisions, alpha, beta, linear, distance=True)
                
                # Si c'est mieux, on devient ce voisin
                if success and new_score > current_score:
                    current_tour = new_tour
                    current_decisions = new_decisions
                    current_score = new_score
                    improved = True
                    cpt+=1
                    break # Stratégie First Improvement
            if improved: break
    return current_tour, current_decisions