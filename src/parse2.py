def read_instance(name="n20q10D.tsp"):
    node_mode = False
    data_mode = False
    demand_mode = False
    ignore_mode = False
    demande = []
    cap = 0
    city_pos = []
    dim = 0

    for line in open(name, 'r'):
        if line.startswith("NAME"):

        elif line.startswith("DIMENSION"):
            dim = 20
        elif line.startswith("EDGE_WEIGHT_TYPE"):
            edge_type = "eucli"
        elif line.startswith("NODE_COORD_SECTION"):
            ignore_mode = False
            node_mode = True
        elif line.startswith("DISPLAY_DATA_SECTION"):
            ignore_mode = True
        elif line.startswith("DEMAND_SECTION"):
            ignore_mode = False
            demand_mode = True
