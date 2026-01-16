
def greedy_delivery(instance, linear=True, alpha=0.01, beta=0.01):
    """
    Glouton qui ne prend pas en compte la distance, on livre en priorité les objets lourds, 
    puis on va ramasser les objets les plus rentables.

    critique est une valeur de seuil pour la décision des objets à prendre
    """
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
        best_profit = float('inf')
        best_cand_delivery = None
        best_cand_profit = None
        next_node = None 
        min_max =  float('inf')
        for cand in customers:
            # nombre de livraison restante
            nb_rest_cand = len(customers)

            # Check livraisons
            poids_deliv = sum(d['poids'] for d in instance.villes[cand]['deliveries'])
            if poids_deliv > 0:
                if poids_deliv > best_delivery:
                    best_delivery = poids_deliv
                    best_cand_delivery = cand
            
            # Check objets profitables
            min_max = 0

            if instance.villes[cand]['pickups'] == []:
                best_profit = 0
                best_cand_profit = cand

            for obj in instance.villes[cand]['pickups']:
                ratio =  obj['poids']
                if ratio > min_max:
                    min_max = ratio

            if best_profit != 0 and  min_max < best_profit:
                best_profit = min_max
                best_cand_profit = cand

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

            for idx, obj, ratio in pickups_with_idx:
                if linear:
                    cout = (alpha * obj['poids'])
                else:
                    cout = (obj['poids'] * alpha +  beta *(obj['poids']**2 ))

                if current_load + obj['poids'] <= instance.capacity and obj['profit'] > cout*nb_rest_cand :
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


