import random
from parse import read_inst

def prepare_split_data(filename, nb_decoupes=2):
    """
    Transforme les données TSP en données multi-objets.
    nb_decoupes : nombre d'objets maximum par ville.
    """
    coords, capacity, demand, display = read_inst(filename)
    
    # On identifie les dépôts
    if demand[1] >= 0: 
        depot_start = 1
        depot_end = len(coords)
    else:
        depot_start = len(coords)
        depot_end = 1
    
    villes_multi = {}

    for i in coords:
        d = demand.get(i, 0)
        villes_multi[i] = {
            'coords': coords[i],
            'pickups': [],
            'deliveries': [],
            'is_depot': (i == depot_start or i == depot_end)
        }

        if i == depot_start or i == depot_end:
            continue

        if d > 0:
            # RAMASSAGE  : On découpe en plusieurs objets 
            # On divise le poids total d par nb_decoupes
            poids_restant = d
            for k in range(nb_decoupes):
                if poids_restant <= 0: break
                
                # Le dernier objet prend tout le reste, sinon on prend une part
                if k == nb_decoupes - 1:
                    w_k = poids_restant
                else:
                    w_k = random.randint(1, max(1, poids_restant // 2))
                
                # Profit : poids * facteur (entre 1.5 et 3.0 pour rendre le choix attractif)
                profit_k = int(w_k * random.uniform(1.5, 3.0))
                
                villes_multi[i]['pickups'].append({
                    'id_k': k + 1,
                    'poids': w_k,
                    'profit': profit_k
                })
                poids_restant -= w_k

        elif d < 0:
            # LIVRAISON  Généralement un seul bloc obligatoire 
            # Mais on le met en liste pour garder la structure k=1
            villes_multi[i]['deliveries'].append({
                'id_k': 1,
                'poids': abs(d),
                'profit': 0 # Livraison ne rapporte pas de profit direct
            })

    # Poids initial W0 : somme des livraisons
    w0 = demand.get(depot_start, 0)
    
    return villes_multi, capacity, w0, demand, display

# --- Exemple d'utilisation ---
if __name__ == "__main__":
    villes, cap, w0, start, end = prepare_split_data("instances/TS2004t2/n20mosA.tsp", nb_decoupes=3)
    print(f"Camion part avec W0 = {w0} / Wmax = {cap}")
    print(f"Ville 5 (Pickup) : {len(villes[5]['pickups'])} objets générés.")
    for obj in villes[5]['pickups']:
        print(f"  - Objet k={obj['id_k']}: Poids={obj['poids']}, Profit={obj['profit']}")