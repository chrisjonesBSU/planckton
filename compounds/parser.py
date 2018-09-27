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
    return float(val) / 10


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
    new_type = AtomType(amber_type, mass, atomic_polarizability)
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
    new_bond = HarmonicBondForce(*classes, k, r0)
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
    new_angle = HarmonicAngleForce(*classes, k, theta0)
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
    k_eff = barrier / devider
    # Unit conversions
    k_eff, phase = kcal2kJ(k_eff), deg2rad(phase)
    new_dihedral = PeriodicTorsionForce(*classes, k_eff, phase, periodicity)
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
    new_improper = PeriodicTorsionForceImproper(*classes, k_eff, phase, periodicity)
    print(new_improper)


def parse_lj(line):
    line = line.strip().split(" ")
    line = list(filter(None, line))
    amber_type, r_min, epsilon = line
    # Unit conversions
    sigma, epsilon = ang2nm(r_min), kcal2kJ(epsilon)
    sigma = sigma * 2 ** (-1 / 6) * 2
    new_amber_lj = NonbondedForce(amber_type, sigma, epsilon)
    print(new_amber_lj)
    new_amber_lj.__test__()


sections = {
    "mass": {"key": "MASS\n", "parser": parse_mass},
    "bond": {"key": "BOND\n", "parser": parse_bond},
    "angle": {"key": "ANGLE\n", "parser": parse_angle},
    "dihedral": {"key": "DIHE\n", "parser": parse_dihedral},
    "improper": {"key": "IMPROPER\n", "parser": parse_improper},
    "lj": {"key": "NONBON\n", "parser": parse_lj},
}


class OpenMMXMLField:
    # AtomTypes name, class, element, mass
    # HarmonicBondForce types, k, r0
    # HarmonicAngleForce types, k, theta
    # PeriodicTorsionForce types, periodicity, phase, k
    # NonbondedForce type, sigma, epsilon
    def __repr__(self):
        attrs = ", ".join("%s = %r" % (k, v) for k, v in self.__dict__.items())
        return "%s(%s)" % (self.__class__.__name__, attrs)

    def __test__(self):
        print(tuple([*self.__dict__.values()] + [self.__class__.__name__]))


class AtomType(OpenMMXMLField):
    def __init__(self, name, mass, atomic_polarizability):
        self.name = name
        self.mass = mass
        self._class = name
        self.element = name[0].upper()
        self.atomic_polarizability = atomic_polarizability


class HarmonicBondForce(OpenMMXMLField):
    def __init__(self, class_1, class_2, k, r0):
        self.class_1 = class_1
        self.class_2 = class_2
        self.k = k
        self.r0 = r0


class HarmonicAngleForce(OpenMMXMLField):
    def __init__(self, class_1, class_2, class_3, k, theta0):
        self.class_1 = class_1
        self.class_2 = class_2
        self.class_3 = class_3
        self.k = k
        self.theta0 = theta0


class PeriodicTorsionForceImproper(OpenMMXMLField):
    def __init__(self, class_1, class_2, class_3, class_4, k, phase, periodicity):
        self.class_1 = class_1
        self.class_2 = class_2
        self.class_3 = class_3
        self.class_4 = class_4
        self.k = k
        self.phase = phase
        self.periodicity = periodicity


class PeriodicTorsionForce(PeriodicTorsionForceImproper):
    # some logic for classes to merge into one for negitive perodicity
    pass


class NonbondedForce(OpenMMXMLField):
    def __init__(self, class_1, sigma, epsilon):
        self.class_1 = class_1
        self.sigma = sigma
        self.epsilon = epsilon


def get_section(key, line, f):
    if line == key["key"]:
        line = f.readline()  # Skip over header
        while line != "\n":
            parser = key["parser"]
            parser(line)
            line = f.readline()


if __name__ == "__main__":
    # ff_params = "eh-idtbr-frcmod"
    ff_params = "all-frcmod"
    with open(ff_params) as f:
        line = f.readline()
        while line:
            for key, value in sections.items():
                get_section(value, line, f)
            line = f.readline()
