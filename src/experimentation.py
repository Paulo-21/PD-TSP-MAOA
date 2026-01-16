import matplotlib.pyplot as plt
import time
import numpy as np
import os
from model import PDTSP_Instance
from data import prepare_split_data
from iterative import hill_climbing
from plne import solve_pdtsp_gurobi
from greedy import greedy_delivery
from nearest import nearest_neighbor

# --- CONFIGURATION ---
FIGURES_DIR = "figures"
LETTRES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

if not os.path.exists(FIGURES_DIR):
    os.makedirs(FIGURES_DIR)

def get_instance(n, lettre='A'):
    path = "instances/TS2004t2/" if n < 80 else "instances/TS2004t3/"
    filename = f"{path}n{n}mos{lettre}.tsp"
    try:
        v_m, cap, w0, dem, disp = prepare_split_data(filename)
        return PDTSP_Instance(v_m, cap, w0, disp)
    except FileNotFoundError:
        return None

def run_all_algos(instance, a, b, is_linear):
    results = {}
    # Greedy (3 retours)
    t_g, d_g, _ = greedy_delivery(instance, alpha=a, beta=b, linear=is_linear)
    _, s_g = instance.evaluate_solution(t_g, d_g, alpha=a, beta=b, linear=is_linear, distance=True)
    results['Greedy'] = s_g

    # Nearest (3 retours)
    t_n, d_n, _ = nearest_neighbor(instance, alpha=a, beta=b, linear=is_linear)
    _, s_n = instance.evaluate_solution(t_n, d_n, alpha=a, beta=b, linear=is_linear, distance=True)
    results['Nearest'] = s_n

    # Hill Climbing (2 retours)
    t_h, d_h = hill_climbing(instance, None, alpha=a, beta=b, linear=is_linear, distance=True)
    _, s_h = instance.evaluate_solution(t_h, d_h, alpha=a, beta=b, linear=is_linear, distance=True)
    results['Hill Climbing'] = s_h

    # PLNE (Gurobi) - Limité à N=60
    n_villes = len(instance.villes)
    if n_villes <= 60:
        t_p, d_p = solve_pdtsp_gurobi(instance, alpha=a, beta=b, linear=is_linear, distance=True)
        if t_p:
            _, s_p = instance.evaluate_solution(t_p, d_p, alpha=a, beta=b, linear=is_linear, distance=True)
            results['PLNE'] = s_p
        else: results['PLNE'] = None
    else:
        results['PLNE'] = None
    return results

def plot_comparison(n_villes, x_values, param_type='alpha'):
    # On détermine les bornes pour nommer le fichier de façon unique
    v_min, v_max = min(x_values), max(x_values)
    print(f"Analyse {param_type} [range {v_min:.4f}-{v_max:.4f}] - N={n_villes}...")
    
    instance = get_instance(n_villes, 'A')
    if instance is None: return

    algos = ['Greedy', 'Nearest', 'Hill Climbing', 'PLNE']
    final_res = {name: [] for name in algos}
    
    for val in x_values:
        if param_type == 'alpha':
            res = run_all_algos(instance, a=val, b=0.01, is_linear=True)
        else: # beta
            res = run_all_algos(instance, a=0.0002, b=val, is_linear=False)
        for name in algos:
            final_res[name].append(res[name])
            
    plt.figure(figsize=(12, 7))
    for name, scores in final_res.items():
        if any(s is not None for s in scores):
            plt.plot(x_values, scores, label=name, lw=2)
            
    plt.title(f"Sensibilité {param_type} (N={n_villes}) | Range: {v_min:.4f} à {v_max:.4f}")
    plt.xlabel(param_type.capitalize())
    plt.ylabel("Score Global Z")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Nom du fichier unique basé sur N et la plage de valeurs
    filename = f"comp_{param_type}_N{n_villes}_range_{v_min:.4f}_{v_max:.4f}.png"
    plt.savefig(os.path.join(FIGURES_DIR, filename))
    plt.close()

def plot_runtime_comparison(tailles):
    print(f"Benchmark temporel (Moyenne sur {len(LETTRES)} instances)...")
    times = {'Greedy': [], 'Nearest': [], 'Hill Climbing': [], 'PLNE': []}
    
    for n in tailles:
        temp_times = {key: [] for key in times.keys()}
        for lettre in LETTRES:
            instance = get_instance(n, lettre)
            if instance is None: continue
            
            # Greedy
            s = time.time(); greedy_delivery(instance, alpha=0.0002, linear=True); temp_times['Greedy'].append(time.time()-s)
            # Nearest
            s = time.time(); nearest_neighbor(instance, alpha=0.0002, linear=True); temp_times['Nearest'].append(time.time()-s)
            # HC
            s = time.time(); hill_climbing(instance, None, alpha=0.0002, linear=True, distance=True); temp_times['Hill Climbing'].append(time.time()-s)
            # PLNE
            if n <= 60:
                s = time.time(); solve_pdtsp_gurobi(instance, alpha=0.0002, linear=True, distance=True); temp_times['PLNE'].append(time.time()-s)
        
        for key in times.keys():
            if temp_times[key]: times[key].append(np.mean(temp_times[key]))
        print(f" -> N={n} terminé.")

    plt.figure(figsize=(12, 7))
    for name, t_list in times.items():
        if t_list: plt.plot(tailles[:len(t_list)], t_list, label=name, marker='o', lw=2)
    
    plt.yscale('log')
    plt.title("Temps de calcul moyen (Instances A-J)")
    plt.xlabel("N")
    plt.ylabel("Temps (s) - Log Scale")
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.savefig(f"{FIGURES_DIR}/runtime_multi_instances.png")
    plt.close()

if __name__ == "__main__":
    print("Démarrage de l'analyse nocturne multi-échelle...")
    
    # Génération des plages logarithmiques (1.0 -> 0.1, 0.1 -> 0.01, etc.)
    ranges = []
    for i in range(4):
        start = 10**(-i)
        stop = 10**(-i-1)
        ranges.append(np.linspace(start, stop, 100))
    
    for n in [20, 300]:
        for r in ranges:
            plot_comparison(n, r, 'alpha')
        for r in ranges:
            plot_comparison(n, r, 'beta')
    
    plot_runtime_comparison([20, 40, 60, 100, 200, 300, 500])
    print(f"\nTerminé ! Dossier : {os.path.abspath(FIGURES_DIR)}")