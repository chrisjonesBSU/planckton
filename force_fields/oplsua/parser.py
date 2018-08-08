from dataclasses import dataclass

ff_par = "oplsua.par"
ff_sb = "oplsua.sb"

# opls.par header
# 0   1  2    3          4        5       6+
# TYP AN AT   CHARGE     SIGMA    EPSILON Misc
# Type Atomic-Number Element Charge(?) Sigma(Å) Epsilon(kcal/mol)

# openMM units -> nm, amu, kJ/mole, proton charge


@dataclass(order=True)
class OPLSUA_type:
    opls_type: str
    atomic_number: int
    charge: float
    sigma: float
    epsilon: float
    mass: float = -1


oplsua_list = []

with open(ff_par, "r") as f:
    ff_par_lines = f.readlines()

for line in ff_par_lines[2:15]:
    raw_opls_type = line.strip(" ").strip().split(" ")
    opls_param_array = list(filter(None, raw_opls_type))
    opls_type = f"opls_{int(opls_param_array[0]):03d}"
    atomic_number = opls_param_array[2]
    charge = opls_param_array[3]
    # We need to convert Å to nm
    sigma = float(opls_param_array[4])/10
    # We need to convert kcal/mol to kJ/mol
    epsilon = float(opls_param_array[5]) * 4.184
    new_opls_type = OPLSUA_type(opls_type, atomic_number, charge, sigma, epsilon)
    print(new_opls_type)
