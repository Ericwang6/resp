# resp
A Python Wrapper for Mainstream RESP Charges Calculator

### Examples
Now the package only support Gaussian for QM calculation and Multiwfn for charge fitting.
```python
from resp.calculator import RESPCalculator
import numpy as np

# An example for hydrogen
coords = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]])
atom_symbols = ["H", "H"]
eqvcons = [1, 2]  # requires atom 1 and atom 2 have the same charge
chgcons = [1, 2, 0.0] # requires the sum of charges of atom 1 and atom 2 is zero
vsite_coords = [0.0, 0.0, 0.37] # add virtual sites
# dpdispatcher settings
mdata = {
  "qm": {
    "machine": {
        "batch_type": "Slurm",
        "context_type": "LocalContext",
        "local_root" : "",
        "remote_root": "",
    },
    "resources": {
        "number_node": 1,
        "cpu_per_node": 28,
        "gpu_per_node": 0,
        "queue_name": "cpu",
        "group_size": 1,
        "source_list": ["~/env/g16.env"],
        "mem": "20GB"
    }
  },
  "fit": {
    "machine": {
        "batch_type": "shell",
        "context_type": "LocalContext",
        "local_root" : "",
        "remote_root": "",
    },
    "resources": {
        "number_node": 1,
        "cpu_per_node": 28,
        "gpu_per_node": 0,
        "queue_name": "cpu",
        "group_size": 1,
        "source_list": ["~/env/multiwfn.env"]
    }
  }
}

cc = RESPCalculator(coords,
                    atom_symbols,
                    mdata,
                    eqvcons = eqvcons,             # equivalence constraints
                    vsite_coords = vsite_coords,   # virtual sites
                    chgcons = chgcons,             # charge constraints
                    job_name = "job",
                    task_path = "/work/path",
                    qm_engine = "gaussian",
                    qm_level = "HF/3-21G",
                    charge = 0,
                    mult = 1,
                    fit_engine = "Multiwfn")
chg = cc.calculate()
```
