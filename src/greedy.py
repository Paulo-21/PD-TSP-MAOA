def solve_greedy_delivery(instance, linear=True):
    nodes = list(instance.villes.keys())
    start_node = nodes[0] 
    end_node = nodes[-1]  
    
    decision = {i: [] for i in nodes}
    
    customers = [n for n in nodes if n != start_node and n != end_node]
    tour = [start_node]
    current_load = instance.w0

    all_w = [current_load]

    while customers:
        best_delivery = 0
        best_profit = 0
        best_cand_delivery = None
        best_cand_profit = None
        best_obj = None
        next_node = None 

        for cand in customers:
            # Check livraisons
            poids_deliv = sum(d['poids'] for d in instance.villes[cand]['deliveries'])
            if poids_deliv > 0:
                if poids_deliv > best_delivery:
                    best_delivery = poids_deliv
                    best_cand_delivery = cand
            
            # Check objets profitables
            for i, obj in enumerate(instance.villes[cand]['pickups']):
                ratio = obj['profit'] / obj['poids']
                if ratio > best_profit and current_load + obj['poids'] <= instance.capacity:
                    best_profit = ratio
                    best_cand_profit = cand
                    best_obj = i

        # Logique de décision
        if best_cand_delivery is not None:
            next_node = best_cand_delivery
            current_load -= best_delivery

        elif best_cand_profit is not None:
            next_node = best_cand_profit

            # On prépare la liste de décisions (0 par défaut)
            num_pickups = len(instance.villes[next_node]['pickups'])
            decision[next_node] = [0] * num_pickups

            # Stratégie : On trie les objets de CETTE ville par rentabilité
            # On récupère les objets avec leur index d'origine pour mettre à jour 'decision'
            pickups_with_idx = []
            for idx, obj in enumerate(instance.villes[next_node]['pickups']):
                pickups_with_idx.append((idx, obj, obj['profit'] / obj['poids']))
            # Tri par ratio décroissant
            pickups_with_idx.sort(key=lambda x: x[2], reverse=True)

            # On prend tout ce qui rentre dans le camion
            for idx, obj, ratio in pickups_with_idx:
                if current_load + obj['poids'] <= instance.capacity:
                    decision[next_node][idx] = 1
                    current_load += obj['poids']
                    
        else:
            # Si aucune ville n'est "attractive", on prend la première disponible pour ne pas bloquer l'algorithme
            next_node = customers[0]
            # On n'oublie pas d'initialiser les décisions même si on ne prend rien
            decision[next_node] = [0 for _ in range(len(instance.villes[next_node]['pickups']))]

        # Mise à jour
        tour.append(next_node)
        customers.remove(next_node)
        all_w.append(current_load)

    tour.append(end_node)
    return tour, decision, all_w