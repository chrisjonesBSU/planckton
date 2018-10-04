import hoomd.deprecated
import hoomd.md
import hoomd.dump
import hoomd.data
from cme_utils.manip.convert_rigid import init_wrapper
from cme_utils.manip.ff_from_foyer import set_coeffs

file_name_opls = "ptb7_with_ff_opls.hoomdxml"
file_name_gaff = "test_typing.hoomdxml"

for file_name in [file_name_opls, file_name_gaff]:
    if hoomd.context.exec_conf is None:
        hoomd.context.initialize("--single-mpi")
    with hoomd.context.SimulationContext():
        system = init_wrapper(file_name)
        nl = hoomd.md.nlist.cell()
        system = set_coeffs(file_name, system, nl)
        integrator_mode = hoomd.md.integrate.mode_standard(dt=0.00001)
        rigid = hoomd.group.rigid_center()
        nonrigid = hoomd.group.nonrigid()
        both_group = hoomd.group.union("both", rigid, nonrigid)
        integrator = hoomd.md.integrate.nvt(group=both_group, tau=0.1, kT=2.0)
        hoomd.dump.gsd(
            filename="alkanes.gsd", period=1e5, group=hoomd.group.all(), overwrite=True
        )
        log_quantities = [
            "temperature",
            "pressure",
            "volume",
            "potential_energy",
            "kinetic_energy",
            "pair_lj_energy",
            "bond_harmonic_energy",
            "angle_harmonic_energy",
            "dihedral_opls_energy",
        ]
        hoomd.analyze.log(
            "alkanes.log",
            quantities=log_quantities,
            period=1e5,
            header_prefix="#",
            overwrite=True,
        )
        hoomd.run(1e1)
