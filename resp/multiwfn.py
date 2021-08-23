import numpy as np

def gen_eqvcons(eqvcons, fname=None):
    """
        Generate input file to add equivalence constraints in fitting RESP

        Parameters
        ----------

        eqvcons : list
            1-d or 2-d list, each row containing atom indices on which equiv constraints are added (staring from 1)
        fname : str or None
            Path to write the generated input string
    """
    if isinstance(eqvcons[0], int):
        ret = ",".join([str(x) for x in eqvcons])
    else:
        ret = ""
        for con in eqvcons:
            ret += ",".join([str(x) for x in con]) + "\n"
    if fname is not None:
        with open(fname, 'w') as f:
            f.write(ret)
    return ret

def gen_chgcons(chgcons, fname=None):
    """
        Generate input file to add charge constraints in fitting RESP
        
        Parameters
        ----------

        chgcons : list
            2d-list, with format like [[atom_idx, atom_idx, chg], [atom_idx, ..., atom_idx, chg]]
        fname : str or None
            Path to write the generated input string
    """
    ret = ""
    for con in chgcons:
        ret += ",".join([str(int(x)) for x in con[:-1]])
        ret += f" {con[-1]:.3f}\n"
    if fname is not None:
        with open(fname, 'w') as f:
            f.write(ret)
    return ret 

def gen_fitcen(vsite_coords, fname=None):
    """
        Generate input file to add additional sites (virtual sites) in fitting RESP

        Parameters
        ----------

        vsite_coords : np.ndarray or list
            Coordinates of virtual sites
        fname : str or None
            Path to write the generated input string
    """
    coord = np.array(vsite_coords).reshape(-1, 3)
    ret = str(coord.shape[0]) + "\n"
    for c in coord:
        ret += " ".join([f"{x:.6f}" for x in c]) + "\n"
    if fname is not None:
        with open(fname, 'w') as f:
            f.write(ret)
    return ret    

def make_multiwfn_input(fitcen=None, eqvcons=None, chgcons=None, fname=None):
    """
        Generate input file for Multiwfn-RESP module

        Parameters
        ----------

        fitcen : str or None
            Input file containing addtional fitting center (virtual sites) coordinates
        eqvcons : str or None
            Input file of equivalence constraints
        chgcons : str or None
            Input file of charge constraints
        fname : str or None:
            Path to write the generated input string

    """
    ret = "7\n18\n"
    if eqvcons:
        ret += f"5\n1\n{eqvcons}\n"
    if chgcons:
        ret += f"6\n1\n{chgcons}\n"
    if fitcen:
        ret += f"9\n{fitcen}\n"
    ret += "1\ny\n0\n0\nq"
    if fname is not None:
        with open(fname, 'w') as f:
            f.write(ret)
    return ret

def parse_chg(fname):
    data = np.loadtxt(fname, dtype=str)
    chg = np.array([float(x) for x in data[:, -1]])
    return chg

