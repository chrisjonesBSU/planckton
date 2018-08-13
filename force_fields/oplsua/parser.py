from dataclasses import dataclass, InitVar


FOYER_XML = True
PI = 3.141592653589
ff_par = "oplsua.par.edits"
ff_par_HEADER = 2
ff_par_OPLS_TYPE_END = 434

ff_sb = "oplsua.sb.edits"
ff_sb_HEADER = 2
ff_sb_HARMONIC_BOND_END = 178

ff_sb_HARMONIC_ANGLE_START = 179

ff_aa_dihedrial = "../oplsaa/oplsaa.par.edits"
ff_aa_dihedrial_SKIP = 4038

# Taken from https://pubs.acs.org/doi/pdf/10.1021/ja00214a001
UA_MASS = {"C": 12.0107, "O": 15.9994, "N": 14.0067, "H": 1.008, "C2": 14.027,
           "CH": 13.019, "C3": 15.035, "CD": 12.0107, "O2": 15.9994, "N3": 14.0067,
           "H3": 1.008, "OH": 12.0107, "HO": 1.008, "SH": 32.06, "HS": 1.008,
           "S": 32.06, "NA": 14.0067, "NB": 14.0067}

@dataclass(frozen=False)
class OPLSUA_type:
    opls_type: str
    atomic_name: str
    atomic_number: int
    charge: float
    sigma: float
    epsilon: float
    mass_dic: InitVar
    _def = ""
    _desc = ""
    _doi = ""

    def __post_init__(self, mass_dic):
        self.mass = mass_dic[self.atomic_name]


@dataclass(frozen=True)
class HarmonicBond:
    class_1: str
    class_2: str
    k: float
    lenght: float


@dataclass(frozen=True)
class HarmonicAngle:
    class_1: str
    class_2: str
    class_3: str
    k: float
    angle: float


@dataclass(frozen=True)
class RBTorsion:
    class_1: str
    class_2: str
    class_3: str
    class_4: str
    c0: float
    c1: float
    c2: float
    c3: float
    c4: float
    c5: float


def write_xml(xml_data, xml_name):
    with open(xml_name, "w") as f:
        f.write(xml_data)


def opls_dihedral_to_RB_torsion(f1, f2, f3, f4):
    c0 = f2 + 0.5 * (f1 + f3)
    c1 = 0.5 * (-f1 + 3 * f3)
    c2 = -f2 + 4 * f4
    c3 = -2 * f3
    c4 = -4 * f4
    c5 = 0
    return c0, c1, c2, c3, c4, c5


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
    new_opls_type = OPLSUA_type(
        opls_type, atomic_number, atomic_name, charge, sigma, epsilon, mass_dic=UA_MASS
    )
    oplsua_list.append(new_opls_type)

print(f"lines skipped in {ff_par} {problem_lines} \n")

with open(ff_sb, "r") as f:
    ff_sb_lines = f.readlines()


harmonic_bond_types = []
for line in ff_sb_lines[ff_sb_HEADER:ff_sb_HARMONIC_BOND_END]:
    raw_harmonic_bond_type = line.strip(" ").strip().split(" ")
    harmonic_bond_array = list(filter(None, raw_harmonic_bond_type))
    # In some cases, there is a space between two classes, ie C -CA this causes an
    # issue when we split things up, so we check to see if we need to concatenate
    # the first two items in our list
    if "-" not in harmonic_bond_array[0]:
        harmonic_bond_array[:2] = ["".join(harmonic_bond_array[:2])]
    class_1, class_2 = harmonic_bond_array[0].split("-")
    # We need to convert kcal/(Å**2 mol) to kJ/(nm**2 mol)
    k = float(harmonic_bond_array[1]) * (4.184 * 100 * 2)
    # We need to convert Å to nm
    lenght = float(harmonic_bond_array[2]) / 10
    new_harmonic_bond = HarmonicBond(class_1, class_2, k, lenght)
    harmonic_bond_types.append(new_harmonic_bond)

harmonic_angle_types = []
for line in ff_sb_lines[ff_sb_HARMONIC_ANGLE_START:]:
    # ** seems to indicate a comment
    if line.startswith("**"):
        continue
    raw_harmonic_angle_type = line.strip(" ").strip().split(" ")
    harmonic_angle_array = list(filter(None, raw_harmonic_angle_type))
    while len(harmonic_angle_array[0].split("-")) != 3:
        harmonic_angle_array[0] += harmonic_angle_array.pop(1)
    class_1, class_2, class_3 = harmonic_angle_array[0].split("-")
    # We need to convert kcal/(deg**2 mol) to kJ/(rad**2 mol)
    k = float(harmonic_angle_array[1]) * (4.184 * 2)
    # We need to converd deg to rad
    angle = float(harmonic_angle_array[2]) * (PI / 180)
    new_harmonic_angle = HarmonicAngle(class_1, class_2, class_3, k, angle)
    harmonic_angle_types.append(new_harmonic_angle)


with open(ff_aa_dihedrial, "r") as f:
    ff_aa_dihedrial_lines = f.readlines()
rb_torsion_list = []
problem_lines = []

for line in ff_aa_dihedrial_lines[ff_aa_dihedrial_SKIP:]:
    raw_opls_dihedrial_type = line.strip(" ").strip().split(" ")
    dihedrial_array = list(filter(None, raw_opls_dihedrial_type))
    # Check to see if line is a dummy line or leave blank
    if any(_ in dihedrial_array for _ in ("Dummy", "UNASSIGNED")):
        problem_lines.append(dihedrial_array)
        continue
    # Like with the angles and bonds, we need to deal with spaces
    # But with dihedrials, the index is different
    # We also need to catch bad lines
    try:
        while len(dihedrial_array[5].split("-")) != 4:
            dihedrial_array[5] += dihedrial_array.pop(6)
        # We need to remove the double bond notation "="
        class_1, class_2, class_3, class_4 = (
            dihedrial_array[5].replace("=", "").split("-")
        )
    except IndexError:
        problem_lines.append(dihedrial_array)
        continue
    f1, f2, f3, f4 = map(float, dihedrial_array[1:5])
    # Convert to RB style torsions
    c_coefs = opls_dihedral_to_RB_torsion(f1, f2, f3, f4)
    new_rb_torsion = RBTorsion(class_1, class_2, class_3, class_4, *c_coefs)
    rb_torsion_list.append(new_rb_torsion)

print(f"lines skipped in {ff_aa_dihedrial} {problem_lines} \n")



openMM_xml = "<ForceField>\n"

# Atom Types
openMM_xml += "<AtomTypes>\n"
for opls_type in oplsua_list:
    if FOYER_XML:
        openMM_xml += f' <Type name="{opls_type.opls_type}" class="{opls_type.atomic_name}" element="{opls_type.atomic_name}" mass="{opls_type.mass}" def="{opls_type._def}" desc="{opls_type._desc}" doi="{opls_type._doi}"/>\n'
    else:
        openMM_xml += f' <Type name="{opls_type.opls_type}" class="{opls_type.atomic_name}" element="{opls_type.atomic_name}" mass="{opls_type.mass}"/>\n'
openMM_xml += "</AtomTypes>\n"

# Harmonic Bond Force
openMM_xml += "<HarmonicBondForce>\n"
for harmonic_bond in harmonic_bond_types:
    openMM_xml += f' <Bond class1="{harmonic_bond.class_1}" class2="{harmonic_bond.class_2}" length="{harmonic_bond.lenght}" k="{harmonic_bond.k}"/>\n'
openMM_xml += "</HarmonicBondForce>\n"

# Harmonic Angle Force
openMM_xml += "<HarmonicAngleForce>\n"
for harmonic_angle in harmonic_angle_types:
    openMM_xml += f' <Angle class1="{harmonic_angle.class_1}" class2="{harmonic_angle.class_2}" class3="{harmonic_angle.class_3}" angle="{harmonic_angle.angle}" k="{harmonic_angle.k}"/>\n'
openMM_xml += "</HarmonicAngleForce>\n"

# RB Torsionorsion Force
openMM_xml += "<RBTorsionForce>\n"
for rb_torsion in rb_torsion_list:
    openMM_xml += f' <Proper class1="{rb_torsion.class_1}" class2="{rb_torsion.class_2}" class3="{rb_torsion.class_3}" class4="{rb_torsion.class_4}" c0="{rb_torsion.c0}" c1="{rb_torsion.c1}" c2="{rb_torsion.c2}" c3="{rb_torsion.c3}" c4="{rb_torsion.c4}" c5="{rb_torsion.c5}"/>\n'
openMM_xml += "</RBTorsionForce>\n"
# Non-bonded Force
openMM_xml += '<NonbondedForce coulomb14scale="0.833333" lj14scale="0.5">\n'
for opls_type in oplsua_list:
    openMM_xml += f' <Atom type="{opls_type.opls_type}" charge="{opls_type.charge}" sigma="{opls_type.sigma}" epsilon="{opls_type.epsilon}"/>\n'
openMM_xml += "</NonbondedForce>\n"

openMM_xml += "</ForceField>\n"
write_xml(openMM_xml, "oplsua.xml")
