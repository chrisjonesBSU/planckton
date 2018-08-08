from dataclasses import dataclass


# opls.par header
# 0   1  2    3          4        5       6+
# TYP AN AT   CHARGE     SIGMA    EPSILON Misc
# Type Atomic-Number Element Charge(?) Sigma(Å) Epsilon(kcal/mol)

# openMM units -> nm, amu, kJ/mole, proton charge

ff_par = "oplsua.par"
ff_par_HEADER = 2
ff_par_OPLS_TYPE_END = 434

ff_sb = "oplsua.sb"


@dataclass(order=True, frozen=True)
class OPLSUA_type:
    opls_type: str
    atomic_name: str
    atomic_number: int
    charge: float
    sigma: float
    epsilon: float
    mass: float = -1


def write_xml(xml_data, xml_name):
    with open(xml_name, "w") as f:
        f.write(xml_data)


oplsua_list = []
problem_lines = []


with open(ff_par, "r") as f:
    ff_par_lines = f.readlines()

for line in ff_par_lines[ff_par_HEADER:ff_par_OPLS_TYPE_END]:
    raw_opls_type = line.strip(" ").strip().split(" ")
    opls_param_array = list(filter(None, raw_opls_type))
    if opls_param_array[0] == "#":
        continue
    opls_type = f"opls_{int(opls_param_array[0]):03d}"
    try:
        atomic_name = opls_param_array[1]
    except IndexError:
        problem_lines.append(opls_param_array)
        continue

    atomic_number = opls_param_array[2]
    charge = opls_param_array[3]
    # We need to convert Å to nm
    sigma = float(opls_param_array[4]) / 10
    # We need to convert kcal/mol to kJ/mol
    epsilon = float(opls_param_array[5]) * 4.184
    new_opls_type = OPLSUA_type(opls_type, atomic_number, atomic_name, charge, sigma, epsilon)
    oplsua_list.append(new_opls_type)

print(problem_lines)

openMM_xml = "<ForceField>\n"
# Atom Types
openMM_xml += "<AtomTypes>\n"
for opls_type in oplsua_list:
    openMM_xml += f' <Type name="{opls_type.opls_type}" class="{opls_type.atomic_name}" element="{opls_type.atomic_name}" mass="{opls_type.mass}"/>\n'
openMM_xml += "</AtomTypes>\n"
# Harmonic Bond Force
# Harmonic Angle Force
# Periodic Torsion Force (proper & improper)
# Non-bonded Force
openMM_xml += '<NonbondedForce coulomb14scale="0.833333" lj14scale="0.5">\n'
for opls_type in oplsua_list:
    openMM_xml += f' <Atom type="{opls_type.opls_type}" charge="{opls_type.charge}" sigma="{opls_type.sigma}" epsilon="{opls_type.epsilon}"/>\n'
openMM_xml += '</NonbondedForce>\n'

openMM_xml += "</ForceField>\n"
write_xml(openMM_xml, "oplsua.xml")
