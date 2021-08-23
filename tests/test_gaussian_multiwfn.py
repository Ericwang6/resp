import unittest
import os
import sys
import shutil
from context import RESPCalculator
import numpy as np

class TestGaussianMultiwfn(unittest.TestCase):
    def setUp(self):
        self.coords = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]])
        self.atom_symbols = ["H", "H"]
        self.task_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "H2")
        self.eqvcons = [[1, 2]]
        self.chgcons = [[1, 2, 0.0]]
        self.vsite_coords = [[0.0, 0.0, 0.37]]
        self.mdata = {
            "qm": {
                "machine": {
                    "batch_type": "Slurm",
                    "context_type": "LocalContext",
                    "local_root" : self.task_path,
                    "remote_root": self.task_path,
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
                    "local_root" : self.task_path,
                    "remote_root": self.task_path,
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
    
    def test_gaussian_multiwfn(self):
        cc = RESPCalculator(self.coords,
                            self.atom_symbols,
                            self.mdata,
                            eqvcons = self.eqvcons,
                            vsite_coords = self.vsite_coords,
                            chgcons = self.chgcons,
                            job_name = "H2",
                            task_path = self.task_path,
                            qm_engine = "gaussian",
                            qm_level = "HF/3-21G",
                            charge = 0,
                            mult = 1,
                            fit_engine = "Multiwfn")
        chg = cc.calculate()
        self.assertEqual(chg[0], 0.0)
        self.assertEqual(chg[1], 0.0)
    
    def tearDown(self):
        shutil.rmtree(self.task_path)
        os.remove(os.path.join(os.getcwd(), "dpdispatcher.log"))
        pass
        