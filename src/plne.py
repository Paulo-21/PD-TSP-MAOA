import sys
import gurobipy as gp
from gurobipy import GRB, LinExpr, quicksum
from parse import read_inst
from data import prepare_split_data
from model import PDTSP_Instance
from parse import read_inst ,plot_tour_detailed, print_pretty_results

instance_name = "../instances/TS2004t2/n20mosA.tsp"
instance_name = "../instances/TS2004t2/n60q1000J.tsp"
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
model.addConstrs( (quicksum(xit[i][t] for i in range(nb_ville)) == 1) for t in range(nb_ville))
model.addConstrs( (quicksum(xit[i][t] for t in range(nb_ville)) == 1) for i in range(nb_ville))

#Contrainte pour la capacité du camion plein de beu.
model.addConstr(wi[0] == w0)
for t in range(1,nb_ville):
    model.addConstr(  wi[t] == wi[t-1] - quicksum(ztik[t][i][k] for i in range(nb_ville) for k in range(len(ztik[t][i])))
        + quicksum(ytik[t][i][k] for i in range(nb_ville) for k in range(len(ytik[t][i]))  ))

for i in range(nb_ville):
    for k in range(len(ztik[0][i])):
        model.addConstr(quicksum(ztik[t][i][k] for t in range(nb_ville)) == 1, name="z")

for i in range(nb_ville):
    for k in range(len(ytik[0][i])):
        model.addConstr(quicksum(ytik[t][i][k] for t in range(nb_ville)) == 1, name="z")
model.addConstr(xit[0][0] == 1)
model.addConstr(xit[nb_ville-1][nb_ville-1] == 1)
#model.addConstr(xit[nb_ville][1] == 1)
z = LinExpr()
z += quicksum(ytik[t][i][k] * villes_multi[i]['pickup'][k]['profit'] for k in range(len(ztik[t][i])) for i in range(nb_ville) for t in range(nb_ville))
z -= quicksum( a * wi[t] for t in range(nb_ville))

model.setObjective(z, GRB.MAXIMIZE)

model.optimize()

print('Valeur de la fonction objectif :', model.objVal)
instance = PDTSP_Instance(villes_multi, capacity, w0, demand, display)
tour = []
decision = {i: [] for i in range(nb_ville)}
for t in range(nb_ville):
    for i in range(nb_ville):
        if xit[t][i].X == 1.0:
            tour.append(i+1)
            print(i+1)
            for k, el in enumerate(ztik[t][i]):
                if el == 1.0:
                    decision[i].append( abs(villes_multi[i]['pickup'][k]))
allw = [w for w in wi]

plot_tour_detailed(instance, tour, decision, )
