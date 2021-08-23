def make_gaussian_input(coord,
                        atom_symbols, 
                        fname=None, 
                        header='#force HF/3-21G nosymm',
                        foot="",
                        title='mol', 
                        charge=0, 
                        mult=1):
    ret = header + "\n\n" + title + "\n\n" + str(charge) + " " + str(mult) + "\n"
    coord = coord.reshape(-1, 3)
    for atype, c in zip(atom_symbols, coord):
        ret += atype + " "
        ret += " ".join([f"{x:.4f}" for x in c])
        ret += "\n"
    if foot:
        ret += "\n" + foot + "\n"
    else:
        ret += "\n"
    if fname:
        with open(fname, "w+") as f:
            f.write(ret)
    return ret
    