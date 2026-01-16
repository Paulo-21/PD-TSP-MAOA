import sys
import gurobipy as gp
from gurobipy import GRB, LinExpr, quicksum
from parse import read_inst
from data import prepare_split_data
from model import PDTSP_Instance
from parse import read_inst ,plot_tour_detailed, print_pretty_results

instance_name = "../instances/TS2004t2/n20mosA.tsp"
#instance_name = "../instances/TS2004t2/n60q1000J.tsp"
DEBUG = False
a = 1
if len(sys.argv) >= 2:
    DEBUG = True
villes_multi, capacity, w0, demand, display= prepare_split_data(instance_name, nb_decoupes=2)
"""
print(villes_multi)
print(capacity)
print(w0)
print(demand)
print(display)
"""

model = gp.Model("DP-TSP")
#model.setParam('OutputFlag', 0)
nb_ville = len(villes_multi)
xit = [model.addVars(nb_ville, vtype=GRB.BINARY) for _ in range(nb_ville)]
wi  =  model.addVars(nb_ville, vtype=GRB.CONTINUOUS, ub=capacity, lb=0, name="capacity")
ztik = []
ytik = []
print(villes_multi.keys())
for p in range(nb_ville):
    zik = []
    yik = []
    for dep in villes_multi.values():

        zk = model.addVars(len(dep['deliveries']), vtype=GRB.BINARY)
        yk = model.addVars(len(dep['pickups']), vtype=GRB.BINARY)
        zik.append(zk)
        yik.append(yk)
    ztik.append(zik)
    ytik.append(yik)
#Contrainte du TSP
model.addConstrs((quicksum(xit[t][i] for i in range(nb_ville)) == 1) for t in range(nb_ville))
model.addConstrs((quicksum(xit[t][i] for t in range(nb_ville)) == 1) for i in range(nb_ville))

#Contrainte pour la capacité du camion plein de beu.
model.addConstr(wi[0] == w0)
for t in range(1,nb_ville):
    model.addConstr(  wi[t] == wi[t-1] - quicksum(ztik[t][i][k] for i in range(nb_ville) for k in range(len(ztik[t][i])))
        + quicksum(ytik[t][i][k] for i in range(nb_ville) for k in range(len(ytik[t][i]))  ))

for i in range(nb_ville):
    for k in range(len(ztik[0][i])):
        model.addConstr(quicksum(ztik[t][i][k] for t in range(nb_ville)) == 1, name="a")


for t in range(nb_ville):
    for i in range(nb_ville):
        model.addConstr( quicksum(ztik[t][i][k] for k in range(len(ztik[t][i])) ) == len(ztik[t][i])*xit[t][i])

for t in range(nb_ville):
    for i in range(nb_ville):
        model.addConstr( quicksum(ytik[t][i][k] for k in range(len(ytik[t][i]))) <= len(ytik[t][i])*xit[t][i])

model.addConstr(xit[0][0] == 1)
model.addConstr(xit[nb_ville-1][nb_ville-1] <= 1)

z = LinExpr()
z += quicksum(ytik[t][i][k] * villes_multi[i+1]['pickups'][k]['profit'] for t in range(nb_ville) for i in range(nb_ville) for k in range(len(ytik[t][i])) )
z -= quicksum( a * wi[t] for t in range(nb_ville))

model.setObjective(z, GRB.MAXIMIZE)

model.optimize()

if model.Status == GRB.OPTIMAL:
    print('Valeur de la fonction objectif :', model.objVal)
    print("Modèle faisable, solution optimale trouvée.")
if model.Status == GRB.INFEASIBLE:
    print("Modèle infeasible.")
    searching = False
    exit(1)
elif model.Status == GRB.INF_OR_UNBD:
    print("Infeasible ou non borné (Gurobi n’a pas pu décider).")
    searching = False
    exit(1)
elif model.Status == GRB.UNBOUNDED:
    print("Modèle non borné.")
    searching = False
instance = PDTSP_Instance(villes_multi, capacity, w0, demand, display)
tour = []
nodes = list(instance.villes.keys())
decision = {i: [0] * len(instance.villes[i]['pickups']) for i in nodes}

for t in range(nb_ville):
    for idx in nodes:
        i = int(idx)-1
        if xit[t][i].X == 1.0:
            tour.append(i+1)
            print("VILLE : ", i+1)
            for k, el in enumerate(ytik[t][i]):
                if el == 1.0:
                    decision[idx][k] = 1
                    print("liv ", k)
for kk in range(nb_ville):
    print(wi[kk].X)

print_pretty_results(instance, tour, decision)
valid, score = instance.evaluate_solution(tour, decision)
print(f"Résultat -> Valide: {valid}, Score: {score:.2f}")
plot_tour_detailed(instance, tour, decision, )
