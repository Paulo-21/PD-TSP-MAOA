# PD-TSP : Pickup and Delivery Traveling Salesman Problem

Ce projet implémente et compare différentes approches de résolution pour le problème du voyageur de commerce avec collectes et livraisons (PD-TSP). L'objectif est de maximiser le profit des ramassages tout en minimisant les coûts de transport liés au poids (linéaire et quadratique).

##  Fonctionnalités

Le projet propose quatre méthodes de résolution :
- **Greedy (Glouton)** : Une approche rapide basée sur le profit immédiat.
- **Nearest Neighbor** : Une variante du plus proche voisin pondérée par le profit et le coût de transport.
- **Hill Climbing (Iterative)** : Une recherche locale utilisant l'algorithme **2-opt** pour optimiser la tournée.
- **PLNE (Gurobi)** : Une formulation mathématique exacte (Programme Linéaire en Nombres Entiers).

##  Structure du projet

- `model.py` : Définition de la classe `PDTSP_Instance` et de la fonction d'évaluation du score $Z$.
- `plne.py` : Modèle d'optimisation mathématique utilisant la bibliothèque Gurobi.
- `iterative.py` : Implémentation de la recherche locale 2-opt.
- `greedy.py` & `nearest.py` : Algorithmes constructifs.
- `experimentation.py` : Script principal pour l'analyse et la génération des graphiques de sensibilité.
- `data.py` : Préparation  des données des instances.
- `parse.py`  Parsing et Visualisation des données des instances.
- `main.py` Test des fonctionnalité, prend en argument "compare" pour comparer les différentes instance, sinon le nom de la méthode voulu "plne", "iterative", "greedy" et "nearest"
