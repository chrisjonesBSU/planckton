import logging
import hoomd.deprecated
import hoomd.md
import hoomd.dump
import hoomd.data
from cme_utils.manip.convert_rigid import init_wrapper
from cme_utils.manip.ff_from_foyer import set_coeffs

file_name_opls = "ptb7_with_ff_opls.hoomdxml"
file_name_gaff = "init.hoomdxml"


class Simulation():
    def __init__(self, input_xml):
        self.input_xml = input_xml
        pass

    def run(self):
        if hoomd.context.exec_conf is None:
            hoomd.context.initialize("--single-mpi --mode=gpu")
        with hoomd.context.SimulationContext():
            system = init_wrapper(self.input_xml)
            nl = hoomd.md.nlist.cell()
            logging.info("Setting coefs")
            hoomd.util.quiet_status()
            system = set_coeffs(self.input_xml, system, nl, e_factor=1.0)
            hoomd.util.unquiet_status()
            integrator_mode = hoomd.md.integrate.mode_standard(dt=0.0001)
            rigid = hoomd.group.rigid_center()
            nonrigid = hoomd.group.nonrigid()
            both_group = hoomd.group.union("both", rigid, nonrigid)
            integrator = hoomd.md.integrate.nvt(group=both_group, tau=0.1, kT=2.0)
            hoomd.dump.gsd(
                filename="out.gsd", period=1e3, group=hoomd.group.all(), overwrite=True
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
                "dihedral_table_energy",
            ]
            hoomd.analyze.log(
                "alkanes.log",
                quantities=log_quantities,
                period=1e5,
                header_prefix="#",
                overwrite=True,
            )
            integrator.randomize_velocities(seed=42)
            hoomd.run(1e6)
            integrator_mode.set_params(dt=0.001)
            hoomd.run(1e6)
            #integrator_mode.set_params(dt=0.0005)
            #hoomd.run(5e6)
            #integrator_mode.set_params(dt=0.005)
            #hoomd.run(1e6)
