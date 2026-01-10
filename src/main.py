from parse import read_inst ,plot_tour_detailed, print_pretty_results
from model import PDTSP_Instance
from greedy import solve_greedy_delivery
from data import prepare_split_data
import random
import matplotlib.pyplot as plt


def main():
    # Lecture du fichier
    filename = "../instances/TS2004t2/n20mosA.tsp"
    #filename = "../instances/TS2004t2/n60q1000J.tsp"
    villes_multi, capacity, w0, demand, display= prepare_split_data(filename, nb_decoupes=2)

    # Création de l'instance
    instance = PDTSP_Instance(villes_multi, capacity, w0, demand, display)
    print(f"Instance chargée. Nombre de ville: {len(instance.villes)}")
    print(f"Instance chargée. Capacité: {instance.capacity}")

    # Lancement Glouton
    print("Calcul heuristique gloutonne livraison au plus tôt et objet profitable")
    tour, decision, all_w = solve_greedy_delivery(instance)
    print(tour)
    if tour:
        print_pretty_results(instance, tour, decision)
        valid, score = instance.evaluate_solution(tour, decision)
        print(f"Résultat -> Valide: {valid}, Score: {score:.2f}")

        # Visualisation
        try:
            plot_tour_detailed(instance, tour, decision)
        except Exception as e:
            print("Erreur affichage graph:", e)
    else:
        print("Aucune solution trouvée (Blocage capacité).")

if __name__ == "__main__":
    main()
