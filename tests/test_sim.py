from planckton.init import Compound, Pack
from planckton.sim import Simulation

pcbm_file = "compounds/pcbm_typed.mol2"
itic_file = "compounds/itic_typed.mol2"
ff_file = "compounds/gaff_pcbm.4fxml"
pcbm = Compound(pcbm_file)
itic = Compound(itic_file)

packer = Pack([pcbm, itic], ff_file=ff_file, n_compounds=[10,10], density=0.5)
packer.pack()
my_sim = Simulation("init.hoomdxml", kT=3.0, gsd_write=1e2, log_write=1e2, e_factor=0.5, n_steps=1e3)
my_sim._continue()
