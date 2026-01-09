import matplotlib.pyplot as plt

def read_inst(name):
    """
    Lit une instance PD-TSP au format TSPLIB.

    Retourne :
    - coords   : dict {ville: (x, y)}
    - display  : dict {ville: (x, y)}   # pour affichage
    - capacity : int
    - demand   : dict {ville: demande}
    """

    coords = {}
    display = {}
    demand = {}
    capacity = None

    section = None

    with open(name, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # En-tête
            if line.startswith("CAPACITY"):
                capacity = int(line.split(":")[1])
                continue

            # Sections
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

            # Lecture des sections
            if section == "coords":
                i, x, y = line.split()
                coords[int(i)] = (float(x), float(y))

            elif section == "display":
                i, x, y = line.split()
                display[int(i)] = (float(x), float(y))

            elif section == "demand":
                i, d = line.split()
                demand[int(i)] = int(d)

    return coords, capacity, demand, display

def print_pretty_results(instance, tour, decision):
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
    print("="*50 + "\n")

import math

def get_spaced_display(display_coords, min_dist=100):
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
    display = instance.display
    
    coords = get_spaced_display(display)

    plt.figure(figsize=(10, 8))
    
    # 1. Tracé des trajets (flèches)
    for k in range(len(tour) - 1):
        u, v = tour[k], tour[k+1]
        x1, y1 = coords[u]; x2, y2 = coords[v]
        plt.arrow(x1, y1, x2-x1, y2-y1, head_width=8, head_length=12, 
                  fc='blue', ec='blue', length_includes_head=True, alpha=0.5)

    # 2. Simulation du poids et affichage des points
    temp_weight = instance.w0
    for i, node in enumerate(tour):
        x, y = coords[node]
        
        # Identification du type de ville
        is_delivery = len(instance.villes[node]['deliveries']) > 0
        is_depot = (node == tour[0] or node == tour[-1])
        
        # Style des points
        if is_depot:
            color, marker, size = 'gold', 's', 400
        else:
            color = 'salmon' if is_delivery else 'lightgreen'
            marker, size = 'o', 250

        plt.scatter(x, y, s=size, c=color, edgecolors='black', zorder=5, marker=marker)

        # Calcul du contenu de l'étiquette
        picked_objs = []
        node_decisions = decisions.get(node, [])
        for idx, pris in enumerate(node_decisions):
            if pris == 1:
                obj = instance.villes[node]['pickups'][idx]
                picked_objs.append(f"k{obj['id_k']}")
                temp_weight += obj['poids']
        
        for d in instance.villes[node]['deliveries']:
            temp_weight -= d['poids']

        # --- Logique d'affichage Gauche / Droite ---
        objs_str = f"Objs: {','.join(picked_objs)}" if picked_objs else "Livraison" if is_delivery else "Transit"
        label_node = "DEPOT" if is_depot else f"Ville {node}"
        text_info = f"{label_node}\n{objs_str}\n$W_{{out}}$: {int(temp_weight)}kg"

        # Si livraison -> décalage à gauche (ha = right)
        # Si ramassage -> décalage à droite (ha = left)
        if is_delivery and not is_depot:
            offset_x = -15
            align = 'right'
        else:
            offset_x = 15
            align = 'left'

        plt.text(x + offset_x, y, text_info, fontsize=9, fontweight='bold',
                 ha=align, va='center',
                 bbox=dict(facecolor='white', alpha=0.9, edgecolor=color, boxstyle='round,pad=0.4'),
                 zorder=10)

    plt.title("Tour PD-TSP : Livraisons (Gauche) vs Ramassages (Droite)", fontsize=16)
    plt.grid(True, linestyle=':', alpha=0.4)
    plt.axis("equal")
    plt.tight_layout()
    plt.show()