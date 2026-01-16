import numpy as np
from parse import read_inst ,plot_tour_detailed, print_pretty_results
from model import PDTSP_Instance
from greedy import greedy_delivery
from nearest import nearest_neighbor
from iterative import hill_climbing
from data import prepare_split_data
from plne import solve_pdtsp_gurobi
import matplotlib.pyplot as plt
import sys

BETA = 0.002
LINEAR = True
DISTANCE = True
TAILLE = 20

def compare_alpha_scores(scale, taille, lettre):
    if taille <= 80:
        filename = "instances/TS2004t2/n"+str(taille)+"mos"+lettre+".tsp"
    else:
        filename = "instances/TS2004t3/n"+str(taille)+"mos"+lettre+".tsp"

    villes_multi, capacity, w0, demand, display = prepare_split_data(filename, nb_decoupes=2)
    instance = PDTSP_Instance(villes_multi, capacity, w0, display)

    # On définit les valeurs de alpha : petit pas au début, puis plus large
    # 0.01 à 0.04 puis 0.1 à 2.0
    alphas = [i*scale*5 for i in range(1, 21)]
    
    results = {
        'Greedy': [],
        'Nearest': [],
        'PLNE': [],
        'Hill Climbing': []
    }

    print(f"Lancement de la comparaison sur {len(alphas)} valeurs de alpha...")

    for a in alphas:
        print(f"Test pour alpha = {a:.2f}")
        
        # 1. Greedy
        t_g, d_g, _ = greedy_delivery(instance, linear=LINEAR, alpha=a, beta=BETA)
        _, score_g = instance.evaluate_solution(t_g, d_g, alpha=a, beta=BETA, linear=LINEAR, distance=DISTANCE)
        results['Greedy'].append(score_g)

        # 2. Nearest
        t_n, d_n, _ = nearest_neighbor(instance, alpha=a, beta=BETA)
        _, score_n = instance.evaluate_solution(t_n, d_n, alpha=a, beta=BETA, linear=LINEAR, distance=DISTANCE)
        results['Nearest'].append(score_n)

        # 3. PLNE (Attention : peut être lent selon l'instance)
        try:
            t_p, d_p = solve_pdtsp_gurobi(instance, alpha=a, beta=BETA, linear=LINEAR, distance=DISTANCE)
            _, score_p= instance.evaluate_solution(t_p, d_p, alpha=a, beta=BETA, linear=LINEAR, distance=DISTANCE)
            results['PLNE'].append(score_p)
        except:
            results['PLNE'].append(None)

        # 4. Hill Climbing (basé sur le tour initial de Nearest pour gagner du temps)
        t_i, d_i = hill_climbing(instance, [i+1 for i in range(21)], alpha=a, beta=BETA, linear=LINEAR, distance=DISTANCE)
        _, score_i = instance.evaluate_solution(t_i, d_i, alpha=a, beta=BETA, linear=LINEAR, distance=DISTANCE)
        results['Hill Climbing'].append(score_i)

    # --- Création du graphique combiné ---
    plt.figure(figsize=(10, 7))
    
    markers = {'Greedy': 's', 'Nearest': '^', 'PLNE': 'D', 'Hill Climbing': 'o'}
    colors = {'Greedy': 'blue', 'Nearest': 'green', 'PLNE': 'red', 'Hill Climbing': 'purple'}

    for algo in results:
        # On filtre les éventuels None pour que le tracé soit continu
        valid_a = [a for a, r in zip(alphas, results[algo]) if r is not None]
        valid_r = [r for r in results[algo] if r is not None]
        
        plt.plot(valid_a, valid_r, label=algo, marker=markers[algo], 
                 color=colors[algo], linestyle='-', linewidth=2)

    plt.title(f"Comparaison des Algorithmes (Distance={DISTANCE})", fontsize=14)
    plt.xlabel(r"Coefficient $\alpha$ (coût transport/distance)", fontsize=12)
    plt.ylabel("Score Global $Z$", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)

    # Sauvegarde
    filename = f"figures/comparaison_globale_dist_{DISTANCE}{scale}.png"
    plt.savefig(filename, dpi=300)
    print(f"Graphique combiné sauvegardé : {filename}")

compare_alpha_scores(0.01, TAILLE, 'A')
compare_alpha_scores(0.001, TAILLE, 'A')
compare_alpha_scores(0.0001, TAILLE, 'A')
compare_alpha_scores(0.00001,TAILLE, 'A')
