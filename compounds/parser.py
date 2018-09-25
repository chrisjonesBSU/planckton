from dataclasses import dataclass

ff_params = "ptb7-frcmod"
# ff_params = "all-frcmod"


class AmberFFParams:
    types = []
    bonds = []
    angles = []
    dihedrals = []
    impropers = []
    lj = []


def parse_mass(line):
    line = line.strip().split(" ")
    line = list(filter(None, line))
    amber_type, mass, atomic_polarizability = line
    new_type = Amber_type(amber_type, mass, atomic_polarizability)
    print(new_type)


def parse_bond(line):
    line = line.strip().split(" ")
    line = list(filter(None, line))
    if "-" not in line[0]:
        line[:2] = ["".join(line[:2])]
    class_1, class_2 = line[0].split("-")
    k, r0 = line[1:]
    new_bond = Amber_bond(class_1, class_2, k, r0)
    print(new_bond)

    pass


def parse_angle():
    pass


def parse_dihedral():
    pass


def parse_improper():
    pass


def parse_lj():
    pass


sections = {
    "mass": {"key": "MASS\n", "parser": parse_mass},
    "bond": {"key": "BOND\n", "parser": parse_bond},
    "angle": {"key": "ANGLE\n", "parser": parse_angle},
    "dihedral": {"key": "DIHE\n", "parser": parse_dihedral},
    "improper": {"key": "IMPROPER\n", "parser": parse_improper},
    "lj": {"key": "NONBON\n", "parser": parse_lj},
}


@dataclass(frozen=False)
class Amber_type:
    amber_type: str
    mass: float
    atomic_polarizability: float


@dataclass(frozen=False)
class Amber_bond:
    amber_type_1: str
    amber_type_2: str
    k: float
    r0: float


def get_section(key, line, f):
    if line == key["key"]:
        line = f.readline()  # Skip over header
        while line != "\n":
            parser = key["parser"]
            parser(line)
            line = f.readline()


if __name__ == "__main__":
    with open(ff_params) as f:
        line = f.readline()
        while line:
            for key, value in sections.items():
                get_section(value, line, f)
            line = f.readline()
