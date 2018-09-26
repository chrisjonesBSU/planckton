from dataclasses import dataclass


PI = 3.141592653589


class AmberFFParams:
    types = []
    bonds = []
    angles = []
    dihedrals = []
    impropers = []
    lj = []


def kcal2kJ(val):
    return float(val) * 4.184


def ang2nm(val):
    return float(val)/10


def amber_bond2openmm_bond(val):
    # don't forget the factor of two between functional forms
    # 100 is for 1/ang to 1/nm
    return kcal2kJ(val) * (100 * 2)


def amber_angle2openmm_angle(val):
    # don't forget the factor of two between functional forms
    return kcal2kJ(val) * 2


def deg2rad(val):
    return float(val) * (PI / 180)


def parse_mass(line):
    line = line.strip().split(" ")
    line = list(filter(None, line))
    amber_type, mass, atomic_polarizability = line
    new_type = AmberType(amber_type, mass, atomic_polarizability)
    print(new_type)


def parse_bond(line):
    line = line.strip().split(" ")
    line = list(filter(None, line))
    if "-" not in line[0]:
        line[:2] = ["".join(line[:2])]
    classes = line[0].split("-")
    k, r0 = line[1:3]
    # Unit conversions
    k, r0 = amber_bond2openmm_bond(k), ang2nm(r0)
    new_bond = AmberBond(*classes, k, r0)
    print(new_bond)


def parse_angle(line):
    line = line.strip().split(" ")
    line = list(filter(None, line))
    while len(line[0].split("-")) != 3:
        line[0] += line.pop(1)
    classes = line[0].split("-")
    k, theta0 = line[1:3]
    # Unit conversions
    k, theta0 = amber_angle2openmm_angle(k), deg2rad(theta0)
    new_angle = AmberAngle(*classes, k, theta0)
    print(new_angle)


def parse_dihedral(line):
    line = line.strip().split(" ")
    line = list(filter(None, line))
    while len(line[0].split("-")) != 4:
        line[0] += line.pop(1)
    classes = line[0].split("-")
    devider, barrier, phase, periodicity = map(float, line[1:5])
    # http://ambermd.org/doc12/Amber18.pdf#page=247&zoom=auto,-398,716
    # Section 14.1.6 in amber18 manual
    k_eff = barrier/devider
    # Unit conversions
    k_eff, phase = kcal2kJ(k_eff), deg2rad(phase)
    new_dihedral = AmberDihedral(*classes, k_eff, phase, periodicity)
    print(new_dihedral)


def parse_improper(line):
    line = line.strip().split(" ")
    line = list(filter(None, line))
    while len(line[0].split("-")) != 4:
        line[0] += line.pop(1)
    classes = line[0].split("-")
    barrier, phase, periodicity = map(float, line[1:4])
    k_eff = barrier
    # Unit conversions
    k_eff, phase = kcal2kJ(k_eff), deg2rad(phase)
    new_improper = AmberImproper(*classes, k_eff, phase, periodicity)
    print(new_improper)


def parse_lj(line):
    line = line.strip().split(" ")
    line = list(filter(None, line))
    amber_type, sigma, epsilon = line
    # Unit conversions
    sigma, epsilon = ang2nm(sigma), kcal2kJ(epsilon)
    new_amber_lj = AmberLJ(amber_type, sigma, epsilon)
    print(new_amber_lj)


sections = {
    "mass": {"key": "MASS\n", "parser": parse_mass},
    "bond": {"key": "BOND\n", "parser": parse_bond},
    "angle": {"key": "ANGLE\n", "parser": parse_angle},
    "dihedral": {"key": "DIHE\n", "parser": parse_dihedral},
    "improper": {"key": "IMPROPER\n", "parser": parse_improper},
    "lj": {"key": "NONBON\n", "parser": parse_lj},
}


@dataclass(frozen=False)
class AmberType:
    amber_type: str
    mass: float
    atomic_polarizability: float


@dataclass(frozen=False)
class AmberBond:
    amber_type_1: str
    amber_type_2: str
    k: float
    r0: float


@dataclass(frozen=False)
class AmberAngle:
    amber_type_1: str
    amber_type_2: str
    amber_type_3: str
    k: float
    theta0: float


@dataclass(frozen=False)
class AmberDihedral:
    amber_type_1: str
    amber_type_2: str
    amber_type_3: str
    amber_type_4: str
    k_eff_1: float
    phase_1: float
    periodicty_1: float
    k_eff_2: float = 0
    phase_2: float = 0
    periodicty_2: float = 0
    k_eff_3: float = 0
    phase_3: float = 0
    periodicty_3: float = 0
    k_eff_4: float = 0
    phase_4: float = 0
    periodicty_4: float = 0


@dataclass(frozen=False)
class AmberImproper:
    amber_type_1: str
    amber_type_2: str
    amber_type_3: str
    amber_type_4: str
    k_eff: float
    phase: float
    periodicty: float


@dataclass(frozen=False)
class AmberLJ:
    amber_type_1: str
    sigma: float
    epsilon: float


def get_section(key, line, f):
    if line == key["key"]:
        line = f.readline()  # Skip over header
        while line != "\n":
            parser = key["parser"]
            parser(line)
            line = f.readline()


if __name__ == "__main__":
    #ff_params = "eh-idtbr-frcmod"
    ff_params = "all-frcmod"
    with open(ff_params) as f:
        line = f.readline()
        while line:
            for key, value in sections.items():
                get_section(value, line, f)
            line = f.readline()
