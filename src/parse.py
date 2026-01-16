import matplotlib.pyplot as plt
import math


import os

def read_inst(name):
    coords = {}
    display = {}
    demand = {}
    capacity = None
    section = None

    # On récupère le nom du fichier sans le chemin pour le test
    filename = os.path.basename(name)

    with open(name, "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue

            if line.startswith("CAPACITY"):
                capacity = int(line.split(":")[1])
                continue

            if line == "NODE_COORD_SECTION":
                section = "coords"
                continue
            elif line.startswith("DISPLAY_DATA_SECTION"):
                section = "display"
                continue
            elif line == "DEMAND_SECTION":
                section = "demand"
                continue
            elif line == "EOF":
                break

            parts = line.split()
            if section == "coords":
                coords[int(parts[0])] = (float(parts[1]), float(parts[2]))
            elif section == "display":
                display[int(parts[0])] = (float(parts[1]), float(parts[2]))
            elif section == "demand":
                demand[int(parts[0])] = int(parts[1])

    #  LOGIQUE DE SÉLECTION 

    # Si le fichier contient "mos", c'est une instance de Class 1 (Mosheiov)
    # Le dépôt est déjà dupliqué et les demandes sont prêtes.
    if "mos" in filename.lower():
        print(f"Mode Class 1 détecté ({filename}) : Lecture standard.")
        # On ne touche à rien, on retourne les données telles quelles
        return coords, capacity, demand, display

    # Sinon  on applique une transformation
    else:
        print(f"Mode Class 2 détecté ({filename}) : Adaptation du dépôt.")
        
        # Somme des livraisons (poids négatifs hors dépôt)
        total_livraisons = sum(abs(d) for i, d in demand.items() if i != 1 and d < 0)
        
        # Le dépôt de départ (1) fournit tout
        demand[1] = total_livraisons
        
        #  On double le dépôt à la fin
        depot_fin_id = max(coords.keys()) + 1
        coords[depot_fin_id] = coords[1]
        display[depot_fin_id] = display[1]
        
        # Le dépôt de fin récupère tous les ramassages (poids positifs)
        total_ramassages = sum(d for i, d in demand.items() if i != depot_fin_id and d > 0)
        demand[depot_fin_id] = -total_ramassages

        return coords, capacity, demand, display

def print_pretty_results(instance, tour, decision, distance=False, alpha=0.01,  beta=0.01, linear=True):
    print("\n" + "="*50)
    print(f"{'ÉTAPE':<6} | {'VILLE':<6} | {'ACTION':<20} | {'POIDS SORTANT'}")
    print("-" * 50)
    
    curr_w = instance.w0
    for i, node in enumerate(tour):
        actions = []
        # Livraisons
        for d in instance.villes[node]['deliveries']:
            curr_w -= d['poids']
            actions.append(f"Livré {int(d['poids'])}kg")
        
        # Ramassages
        node_decisions = decision.get(node, [])
        for idx, pris in enumerate(node_decisions):
            if pris == 1:
                obj = instance.villes[node]['pickups'][idx]
                curr_w += obj['poids']
                actions.append(f"Pris k{obj['id_k']} ({int(obj['poids'])}kg)")
        
        action_str = ", ".join(actions) if actions else "Aucune"
        step_str = "DÉPART" if i == 0 else "FIN" if i == len(tour)-1 else f"#{i}"
        
        print(f"{step_str:<6} | {node:<6} | {action_str:<20} | {int(curr_w)}kg")
    
    valid, score = instance.evaluate_solution(tour, decision, distance=distance, alpha=alpha,  beta=beta, linear=linear)

    print(f"Résultat -> Valide: {valid}, Score: {score:.2f}")
        
    print("="*50 + "\n")


def get_spaced_display(display_coords, min_dist=300):
    """
    Ecarte les points qui sont trop proches les uns des autres.
    min_dist: distance minimale souhaitée entre deux points.
    """
    # Copie des coordonnées pour ne pas modifier l'original
    new_coords = {n: [c[0], c[1]] for n, c in display_coords.items()}
    nodes = list(new_coords.keys())
    
    # On fait 5 passes pour stabiliser l'écartement (principe de relaxation)
    for _ in range(5):
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n1, n2 = nodes[i], nodes[j]
                x1, y1 = new_coords[n1]
                x2, y2 = new_coords[n2]
                
                dx = x2 - x1
                dy = y2 - y1
                d = math.sqrt(dx**2 + dy**2)
                
                if d < min_dist and d > 0:
                    # Force de répulsion
                    overlap = min_dist - d
                    # On déplace chaque point de la moitié de l'overlap dans des directions opposées
                    move_x = (dx / d) * (overlap / 2)
                    move_y = (dy / d) * (overlap / 2)
                    
                    new_coords[n1][0] -= move_x
                    new_coords[n1][1] -= move_y
                    new_coords[n2][0] += move_x
                    new_coords[n2][1] += move_y
                elif d == 0:
                    # Cas rare où les points sont superposés
                    new_coords[n2][0] += min_dist

    return {n: tuple(c) for n, c in new_coords.items()}


def plot_tour_detailed(instance, tour, decisions):
    # Gestion des coordonnées et mise à l'échelle
    raw_coords = instance.display
    # On écarte les points pour que les boîtes aient de la place
    coords = get_spaced_display(raw_coords, min_dist=400)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    depot_id = tour[0] # L'ID unique du dépôt (ex: 1 ou 0)
    
    #  Simulation des poids pour calculer l'évolution au fil du tour
    temp_weight = instance.w0
    weights_after_node = {} # Poids au moment où l'on quitte l'étape i
    
    for i, node in enumerate(tour):
        # On applique les livraisons/ramassages de l'étape actuelle
        node_decisions = decisions.get(node, [])
        for idx, pris in enumerate(node_decisions):
            if pris == 1:
                temp_weight += instance.villes[node]['pickups'][idx]['poids']
        for d in instance.villes[node]['deliveries']:
            temp_weight -= d['poids']
        
        weights_after_node[i] = temp_weight

    weight_final = temp_weight # Poids après être revenu au dépôt

    # Tracé des flèches
    # On boucle sur tout le tour. La dernière itération pointera vers tour[0]
    for k in range(len(tour) - 1):
        if k == len(tour) - 2:
            u, v = tour[k], tour[0]
        else:
            u, v = tour[k], tour[k+1]
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        
        dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        # s_val : Ajustement de la distance d'arrêt de la flèche
        s_val = min(35, dist * 0.5) 

        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", 
                                    lw=3, 
                                    color='royalblue',
                                    shrinkA=s_val, 
                                    shrinkB=s_val, 
                                    mutation_scale=25), 
                    zorder=1)

    # Tracé des boîtes (On ne dessine chaque ville qu'une fois)
    drawn_nodes = set()
    for i, node in enumerate(tour):
        if node in drawn_nodes: continue
        drawn_nodes.add(node)
        
        x, y = coords[node]
        
        if node == depot_id:
            # Texte spécifique pour le Dépôt Unique
            txt = f"DÉPÔT\nInitial: {int(instance.w0)}kg\nFinal: {int(weight_final)}kg"
            color = 'gold'
        else:
            # Texte pour les villes clientes
            is_delivery = len(instance.villes[node]['deliveries']) > 0
            picked = [f"k{instance.villes[node]['pickups'][idx]['id_k']}" 
                      for idx, p in enumerate(decisions.get(node, [])) if p == 1]
            objs = f"Items: {','.join(picked)}" if picked else ("LIVRAISON" if is_delivery else "TRANSIT")
            
            # On affiche le poids tel qu'il est en quittant cette ville la première fois
            w_out = weights_after_node[i]
            txt = f"VILLE {node}\n{objs}\n$W_{{out}}$: {int(w_out)}kg"
            color = 'salmon' if is_delivery else 'lightgreen'

        ax.text(x, y, txt, fontsize=9, fontweight='bold',
                ha='center', va='center',
                bbox=dict(facecolor='white', alpha=1, edgecolor=color, 
                          boxstyle='round,pad=0.8', lw=2.5),
                zorder=5)

    # Réglages des axes pour éviter le carré blanc
    all_x = [c[0] for c in coords.values()]
    all_y = [c[1] for c in coords.values()]
    margin = 100
    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
    ax.set_aspect('equal')
    
    plt.axis('off')
    plt.title(f"Visualisation PD-TSP - Instance {instance.name if hasattr(instance, 'name') else ''}", fontsize=14)
    plt.tight_layout()
    plt.show()