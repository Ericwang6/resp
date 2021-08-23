from dpdispatcher import Machine, Resources, Task, Submission
import numpy as np
import json
import os
import warnings
from gaussian import make_gaussian_input
from multiwfn import gen_eqvcons, gen_fitcen, gen_chgcons, make_multiwfn_input, parse_chg


supported_qm_engine = ["gaussian"]
supported_fit_engine = ["Multiwfn"]
pwd = os.getcwd()

class RESPCalculator(object):
    def __init__(self,
                 coord, 
                 atom_symbols,
                 mdata,
                 job_name = "job",
                 vsite_coords = None,
                 eqvcons = None,
                 chgcons = None,
                 task_path = "",
                 qm_engine = "gaussian",
                 qm_level = "HF/3-21G",
                 charge = 0,
                 mult = 1,
                 fit_engine = "Multiwfn"):
        self.coord = coord
        self.atom_symbols = atom_symbols
        self.job_name = job_name
        
        # qm
        assert qm_engine in supported_qm_engine
        self.qm_engine = qm_engine
        self.qm_level = qm_level
        self.charge = 0
        self.mult = 1

        # work path init
        if not task_path:
            task_path = os.path.join(os.path.abspath(os.getcwd()), ".cache")
            warnings.warn(f"Task path is setting to : {task_path}")
        self.task_path     = task_path
        self.qm_task_path  = os.path.join(self.task_path, "qm")
        self.fit_task_path = os.path.join(self.task_path, "fit")
        for path in [self.task_path, self.qm_task_path, self.fit_task_path]:
            if not os.path.exists(path): os.mkdir(path)
        
        # dpdispatcher
        self.mdata = mdata
        self.qm_machine = Machine.load_from_dict(self.mdata['qm']["machine"])
        self.qm_resources = Resources.load_from_dict(self.mdata['qm']["resources"])
        self.fit_machine = Machine.load_from_dict(self.mdata['fit']["machine"])
        self.fit_resources = Resources.load_from_dict(self.mdata['fit']["resources"])
        self.nproc = mdata['qm']["resources"]["cpu_per_node"]
        self.mem = mdata['qm']["resources"].get("mem", "2GB")

        # fit
        assert fit_engine in supported_fit_engine
        self.fit_engine = fit_engine
        self.vsite_coords = vsite_coords
        self.eqvcons = eqvcons
        self.chgcons = chgcons

        # results
        self.chg = None
    
    def add_vsite_coords(self, vsite_coords):
        self.vsite_coords = vsite_coords
    
    def add_eqvcons(self, eqvcons):
        self.eqvcons = eqvcons
    
    def add_chgcons(self, chgcons):
        self.chgcons = chgcons
    
    def change_qm_engine(self, engine):
        assert engine in supported_qm_engine
        self.qm_engine = engine
    
    def change_fit_engine(self, engine):
        assert engine in supported_fit_engine
        self.fit_engine = engine
    
    def run_qm(self):
        if self.qm_engine == "gaussian":
            gjf = os.path.join(self.qm_task_path, f"{self.job_name}.gjf")
            chk = os.path.join(self.qm_task_path, f"{self.job_name}.chk")
            header = f"%nproc={self.nproc}\n%mem={self.mem}\n%chk={chk}\n#force {self.qm_level} nosymm"
            make_gaussian_input(self.coord,
                                self.atom_symbols,
                                header = header,
                                title = self.job_name,
                                charge = self.charge,
                                mult = self.mult,
                                fname = gjf)
            task = Task(
                command = f"g16 {gjf} && formchk {chk}",
                task_work_path = "qm/",
                forward_files = [],
                backward_files = []
            )
            submission = Submission(
                work_base = self.task_path,
                machine = self.qm_machine,
                resources = self.qm_resources,
                task_list = [task]
            )
            submission.run_submission()
            self.multiwfn_infile = chk.replace(".chk", ".fchk")
    
    def run_fit(self):
        if self.fit_engine == "Multiwfn":
            if self.eqvcons is not None:
                eqvcons_input = os.path.join(self.fit_task_path, "eqvcons.txt")
                gen_eqvcons(self.eqvcons, eqvcons_input)
            else:
                eqvcons_input = None

            if self.chgcons is not None:
                chgcons_input = os.path.join(self.fit_task_path, "chgcons.txt") 
                gen_chgcons(self.chgcons, chgcons_input)
            else:
                chgcons_input = None
            
            if self.vsite_coords is not None:
                fitcen_input = os.path.join(self.fit_task_path, "fitcen.txt")
                gen_fitcen(self.vsite_coords, fitcen_input)
            else:
                fitcen_input = None
            
            multiwfn_input = os.path.join(self.fit_task_path, "input")
            make_multiwfn_input(fitcen_input, eqvcons_input, chgcons_input, multiwfn_input)
            task = Task(
                command = f"Multiwfn {self.multiwfn_infile} < {multiwfn_input}",
                task_work_path = "fit/",
                forward_files = [],
                backward_files = [f"{self.job_name}.chg"]
            )
            submission = Submission(
                work_base = self.task_path,
                machine = self.fit_machine,
                resources = self.fit_resources,
                task_list = [task]
            )
            submission.run_submission()
            chg_file = os.path.join(self.fit_task_path, f"{self.job_name}.chg")
            self.chg = parse_chg(chg_file)
        
    def calculate(self):
        self.run_qm()
        self.run_fit()
        return self.chg