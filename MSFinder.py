# Cell values
# {"VAL": (x, y)}

from Exp import *
from sys import argv

# ---- GRID DEF ----
WIDTH = int(argv[1])
HEIGHT = int(argv[2])

GRIDEXP = [[None for j in range(HEIGHT)] for i in range(WIDTH)]
GRIDBOMB = [[None for j in range(HEIGHT)] for i in range(WIDTH)]
GRIDNUMBERS = [[None for j in range(HEIGHT)] for i in range(WIDTH)]
SOLUTIONS = []
ADDED = {}

# ---- MISC FUNCTIONS ---- 
def expression_sum (cases, total_val, tmp = None):
    if total_val < 0 or len(cases) < total_val:
        exit("ERROR!!!! on " + str(tmp))
    if total_val == 0:
        return {"AND": [{"NOT": {"VAL": e}} for e in cases]}
    elif len(cases) == 1:
        if total_val == 1:
            return {"VAL": cases[0]}
        else:
            return {"NOT": {"VAL": cases[0]}}
    elif len(cases) == total_val:
        return {"AND": [{"VAL": e} for e in cases]}
    
    e0 = expression_sum(cases[1:], total_val, tmp)
    e1 = expression_sum(cases[1:], total_val - 1, tmp)

    return {"OR": [{"AND": [{"NOT": {"VAL": cases[0]}}, e0]}, {"AND": [{"VAL": cases[0]}, e1]}]}

def get_near (cell):
    x = cell[0]
    y = cell[1]
    vois = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if x + i >= 0 and x + i < WIDTH and y + j >= 0 and y + j < HEIGHT and (i != 0 or j != 0):
                vois.append((x + i, y + j))
    return vois

def set_cell_type (cell, ctype):
    if ctype == None: return
    x = cell[0]
    y = cell[1]
    if isinstance(ctype, bool):
        GRIDBOMB[x][y] = ctype
    else:
        GRIDNUMBERS[x][y] = ctype
        GRIDBOMB[x][y] = False

def create_cell_exp (cell):
    x = cell[0]
    y = cell[1]
    if GRIDBOMB[x][y] == True or GRIDNUMBERS[x][y] == None: return False
    
    vois = get_near(cell)
    k = GRIDNUMBERS[x][y]

    rem = []

    for e in vois:
        _x = e[0]
        _y = e[1]
        if GRIDBOMB[_x][_y] == True:
            rem.append(e)
            k = k - 1
        elif GRIDBOMB[_x][_y] == False:
            rem.append(e)
    for e in rem: vois.remove(e)
    
    GRIDEXP[x][y] = letter_create(expression_sum(vois, k, cell))

def update_exp_cell (cell_exp, cell_fn):
    x0 = cell_exp[0]
    y0 = cell_exp[1]
    x1 = cell_fn[0]
    y1 = cell_fn[1]

    if GRIDBOMB[x1][y1] == None or GRIDEXP[x0][y0] == None: return
    
    GRIDEXP[x0][y0] = exp_replace_simp1(GRIDEXP[x0][y0], {cell_fn: GRIDBOMB[x1][y1]})

def update_from_cell (cell_fn):
    vois = get_near(cell_fn)
    for e in vois:
        update_exp_cell(e, cell_fn)

def add_solutions_from_cell (cell):
    global SOLUTIONS
    x = cell[0]
    y = cell[1]
    
    if GRIDEXP[x][y] == None: return
    
    tmp_sol = get_simple_solutions(GRIDEXP[x][y], True)
    SOLUTIONS = update_solutions(SOLUTIONS, tmp_sol)

def update_with_single_solution ():
    global SOLUTIONS
    q = solutions_always_same(SOLUTIONS)

    for e in q:
        ADDED[e] = q[e]
        set_cell_type(e, q[e])
        update_from_cell(e)
    
    SOLUTIONS = solutions_remove(SOLUTIONS, q.keys())

def execute_turn ():
    q = {}

    global ADDED
    for i in range(WIDTH):
        for j in range(HEIGHT):
            cell = (i, j)
            create_cell_exp(cell)
            add_solutions_from_cell(cell)
            update_with_single_solution()
    
    while ADDED != {}:
        for e in ADDED:
            q[e] = ADDED[e]
        ADDED = {}
        for i in range(WIDTH):
            for j in range(HEIGHT):
                cell = (i, j)
                create_cell_exp(cell)
                add_solutions_from_cell(cell)
                update_with_single_solution()

    return q

def is_finished ():
    return True not in [None in column for column in GRIDBOMB]

def read_file ():
    f = open("GRID.txt", "r")
    tmp0 = f.readlines()
    f.close()
    tmp1 = []
    for e in tmp0:
        if e == "\n": continue
        p = ""
        if e.endswith(",\n"): p = e[:-2]
        else: p = e[:-1]
        
        a = None
        q = None
        if p.endswith(" :"):
            a = None
            s = p[:-2].split(",")
            q = (int(s[0][1:]), int(s[1][:-1]))
        elif p.endswith(" : True"):
            a = True
            s = p[:-7].split(",")
            q = (int(s[0][1:]), int(s[1][:-1]))
        else:
            a = int(p[-1])
            s = p[:-4].split(",")
            q = (int(s[0][1:]), int(s[1][:-1]))
        tmp1.append((q, a))
    
    return tmp1

def write_file ():
    gen_str = ""
    for i in range(WIDTH):
        for j in range(HEIGHT):
            gen_str += "(" + str(i) + "," + str(j) + ") :"
            if GRIDBOMB[i][j] == True:
                gen_str += " True"
            elif GRIDBOMB[i][j] == False and GRIDNUMBERS[i][j] != None:
                gen_str += " " + str( GRIDNUMBERS[i][j])
            gen_str += ",\n"
        gen_str += "\n"
    
    f = open("GRID.txt", "w")
    f.write(gen_str[:-2])
    f.close()

def reset ():
    global GRIDEXP
    global GRIDBOMB
    global GRIDNUMBERS
    global SOLUTIONS
    global ADDED
    GRIDEXP = [[None for j in range(HEIGHT)] for i in range(WIDTH)]
    GRIDBOMB = [[None for j in range(HEIGHT)] for i in range(WIDTH)]
    GRIDNUMBERS = [[None for j in range(HEIGHT)] for i in range(WIDTH)]
    SOLUTIONS = []
    ADDED = {}