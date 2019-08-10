# Expressions:
# Main object: {"LETTERS": [...], "EXP": {...}}
#
# {"AND": [{...}, {...}, ...]}
# {"OR": [{...}, {...}, ...]}
# {"NOT": {...}}
# {"VAL": letter (object) / pure value (bool)}

# ---- CONSTANTS ----
SE_TRUE = {"VAL": True}
SE_FALSE = {"VAL": False}

# ---- BASIC FUNCTIONS ----
def exp_check (exp):
    if exp["EXP"] == SE_TRUE: return True
    elif exp["EXP"] == SE_FALSE: return False
    return None

def letter_update (exp):
    new_letters = []

    def expl (subexp):
        if "VAL" in subexp:
            if not isinstance(subexp["VAL"], bool) and subexp["VAL"] not in new_letters:
                new_letters.append(subexp["VAL"])
        elif "NOT" in subexp:
            expl(subexp["NOT"])
        elif "AND" in subexp:
            for e in subexp["AND"]: expl(e)
        elif "OR" in subexp:
            for e in subexp["OR"]: expl(e)
    
    expl(exp["EXP"])
    return {"LETTERS": new_letters, "EXP": exp["EXP"]}

def letter_create (bexp):
    return exp_simp1(letter_update({"LETTERS": [], "EXP": bexp}))

def exp_replace (exp, letter, val):
    if letter not in exp["LETTERS"]: return exp
    
    def expl (subexp):
        if "VAL" in subexp:
            if subexp["VAL"] == letter:
                return {"VAL": val}
            else: return {"VAL": subexp["VAL"]}
        elif "NOT" in subexp:
            return {"NOT": expl(subexp["NOT"])}
        elif "AND" in subexp:
            return {"AND": [expl(e) for e in subexp["AND"]]}
        elif "OR" in subexp:
            return {"OR": [expl(e) for e in subexp["OR"]]}
    
    new_letters = exp["LETTERS"].copy()
    new_letters.remove(letter)
    return {"LETTERS": new_letters, "EXP": expl(exp["EXP"])}

def exp_replace_multiple (exp, values):
    tmp = exp
    for letter in values:
        tmp = exp_replace(tmp, letter, values[letter])
    return tmp

def exp_simp1 (exp):
    def expl (subexp):
        if "VAL" in subexp:
            return {"VAL": subexp["VAL"]}
        elif "NOT" in subexp:
            a = expl(subexp["NOT"])
            if a == SE_TRUE: return SE_FALSE
            elif a == SE_FALSE: return SE_TRUE
            else: return {"NOT": a}
        elif "AND" in subexp:
            tmp = []
            for e in subexp["AND"]:
                a = expl(e)
                if a == SE_TRUE: continue
                elif a == SE_FALSE: return SE_FALSE
                else: tmp.append(a)
            if len(tmp) == 1: return tmp[0]
            elif len(tmp) == 0: return SE_TRUE
            return {"AND": tmp}
        elif "OR" in subexp:
            tmp = []
            for e in subexp["OR"]:
                a = expl(e)
                if a == SE_TRUE: return SE_TRUE
                elif a == SE_FALSE: continue
                else: tmp.append(a)
            if len(tmp) == 1: return tmp[0]
            elif len(tmp) == 0: return SE_FALSE
            return {"OR": tmp}
    
    return {"LETTERS": exp["LETTERS"].copy(), "EXP": expl(exp["EXP"])}

def exp_replace_simp1 (exp, values):
    return exp_simp1(exp_replace_multiple(exp, values))

def get_value (exp, values):
    return exp_check(exp_replace_simp1(exp, values))

def create_table (exp):
    letters = exp["LETTERS"]
    if len(letters) == 0: return []

    t = [[False], [True]]
    for i in range(1, len(letters)):
        t = [[False] + e for e in t] + [[True] + e for e in t]
    
    q = []
    for e in t:
        b = {letters[i]: e[i] for i in range(len(e))}
        q.append((b, get_value(exp, b)))
    
    return q

# ---- SOLUTIONS FUNCTIONS ----
def is_same_base (s1, s2):
    for e in s1:
        if e in s2 and s1[e] != s2[e]: return False
    return True

def union (s1, s2):
    s = {}
    for e in s1:
        s[e] = s1[e]
    for e in s2:
        s[e] = s2[e]
    return s

def get_simple_solutions (exp, val):
    q = create_table(exp)
    t = []
    for e in q:
        if e[1] == val: t.append(e[0])
    return t

def update_solutions (s, si):
    tmp = []
    if len(s) == 0:
        return si
    for e in s:
        for f in si:
            if is_same_base(f, e):
                tmp.append(union(e, f))
    return tmp

def get_solutions (exps, vals):
    s = get_simple_solutions(exps[0], vals[0])

    for i in range(1, len(vals)):
        tmp1 = get_simple_solutions(exps[i], vals[i])
        s = update_solutions(s, tmp1)
    
    return s

def solutions_always_same (s):
    if len(s) == 0: return {}
    
    t = {}
    for l in s[0]:
        tmp0 = s[0][l]
        tmp1 = True
        for e in s[1:]:
            tmp1 = e[l] == tmp0
            if not tmp1: break
        if tmp1: t[l] = tmp0
    return t

def solutions_remove (s, letters):
    t = []
    for e in s:
        for f in letters:
            e.pop(f)
        if e != {}:
            t.append(e)
    return t