from parse import read_inst ,plot_tour_detailed, print_pretty_results
from model import PDTSP_Instance
from greedy import greedy_delivery
from nearest import nearest_neighbor
from iterative import hill_climbing
from data import prepare_split_data
from plne import solve_pdtsp_gurobi
import random
import matplotlib.pyplot as plt
import sys


ALPHA = 0.01 
BETA = 0.1
LINEAR = True
DISTANCE = True


def greedy():
    # Lecture du fichier
    filename = "instances/TS2004t2/n20mosA.tsp"
    villes_multi, capacity, w0, demand, display= prepare_split_data(filename, nb_decoupes=2)
    
    # Création de l'instance
    instance = PDTSP_Instance(villes_multi, capacity, w0, display)
    print(f"Instance chargée. Nombre de ville: {len(instance.villes)}")
    print(f"Instance chargée. Capacité: {instance.capacity}")

    # Lancement Glouton
    print("Calcul heuristique gloutonne livraison au plus tôt et objet profitable")
    tour, decision, all_w = greedy_delivery(instance,linear=LINEAR, alpha=ALPHA,  beta=BETA)
    
    if tour:
        print_pretty_results(instance, tour, decision, distance=DISTANCE,  alpha=ALPHA,  beta=BETA)
        
        # Visualisation
        try:
            plot_tour_detailed(instance, tour, decision)
        except Exception as e:
            print("Erreur affichage graph:", e)
    else:
        print("Aucune solution trouvée (Blocage capacité).")


def nearest():
    # Lecture du fichier
    filename = "instances/TS2004t2/n20mosA.tsp"
    villes_multi, capacity, w0, demand, display= prepare_split_data(filename, nb_decoupes=2)
    
    # Création de l'instance
    instance = PDTSP_Instance(villes_multi, capacity, w0, display)
    print(f"Instance chargée. Nombre de ville: {len(instance.villes)}")
    print(f"Instance chargée. Capacité: {instance.capacity}")

    # Lancement Glouton
    print("Calcul par Nearset")
    tour, decision, all_w = nearest_neighbor(instance, alpha=ALPHA,  beta=BETA)
    
    if tour:
        print_pretty_results(instance, tour, decision, distance=DISTANCE, alpha=ALPHA,  beta=BETA)
        
        # Visualisation
        try:
            plot_tour_detailed(instance, tour, decision)
        except Exception as e:
            print("Erreur affichage graph:", e)
    else:
        print("Aucune solution trouvée (Blocage capacité).")

def plne():
    # Lecture du fichier
    filename = "instances/TS2004t2/n20mosA.tsp"
    villes_multi, capacity, w0, demand, display= prepare_split_data(filename, nb_decoupes=2)
    
    # Création de l'instance
    instance = PDTSP_Instance(villes_multi, capacity, w0, display)
    print(f"Instance chargée. Nombre de ville: {len(instance.villes)}")
    print(f"Instance chargée. Capacité: {instance.capacity}")

    # Lancement Glouton
    print("Calcul par PLNE")
    tour, decision = solve_pdtsp_gurobi(instance, alpha=ALPHA)
    
    if tour:
        print_pretty_results(instance, tour, decision, distance=DISTANCE, alpha=ALPHA,  beta=BETA)
        
        # Visualisation
        try:
            plot_tour_detailed(instance, tour, decision)
        except Exception as e:
            print("Erreur affichage graph:", e)
    else:
        print("Aucune solution trouvée (Blocage capacité).")

def iterative():
        # Lecture du fichier
    filename = "instances/TS2004t2/n20mosA.tsp"
    villes_multi, capacity, w0, demand, display= prepare_split_data(filename, nb_decoupes=2)
    
    # Création de l'instance
    instance = PDTSP_Instance(villes_multi, capacity, w0, display)
    print(f"Instance chargée. Nombre de ville: {len(instance.villes)}")
    print(f"Instance chargée. Capacité: {instance.capacity}")

    # Lancement Glouton
    print("Calcul par Iterative Méthode")
    tour, decision = hill_climbing(instance, [i+1 for i in range(21)], alpha=ALPHA,  beta=BETA, linear=LINEAR, distance=DISTANCE)
    
    if tour:
        print_pretty_results(instance, tour, decision, distance=DISTANCE, alpha=ALPHA,  beta=BETA)
        
        # Visualisation
        try:
            plot_tour_detailed(instance, tour, decision)
        except Exception as e:
            print("Erreur affichage graph:", e)
    else:
        print("Aucune solution trouvée (Blocage capacité).")



if __name__ == "__main__":
    if len(sys.argv) >= 2:
        mode = sys.argv[1].lower()
        if mode == 'greedy':
                print("Exécution de l'algorithme Greedy...")
                greedy()
                
        elif mode == 'nearest':
                print("Exécution de l'algorithme Nearest Neighbor...")
                nearest()
                
        elif mode == 'plne':
            print("Exécution de l'algorithme PLNE...")
            plne()

        elif mode == 'iterative':
            print("Exécution de l'algorithme Hill Climbing...")
            iterative()
        
        elif mode == 'compare':
            plne()
            greedy()
            nearest()
            iterative()
        
        else:
                print(f"Erreur : Mode '{mode}' inconnu. Utilisez 'greedy' ou 'nearest'.")
    else:
        # Action par défaut si aucun argument n'est fourni
        print("Aucun argument détecté, exécution du mode par défaut (nearest)...")
        nearest()