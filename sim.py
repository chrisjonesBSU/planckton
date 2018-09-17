import hoomd.deprecated
import hoomd.md
import hoomd.dump
import hoomd.data
import os
import json
import numpy as np
import scipy.spatial
from collections import Counter
import xml.etree.cElementTree as ET
from cme_utils.manip.convert_rigid import init_wrapper

def set_coeffs(file_name, system):
    '''
    Read in the molecular dynamics coefficients exported by Foyer
    '''
    coeffs_dict = get_coeffs(file_name)
    ljnl = hoomd.md.nlist.cell()
    lj = hoomd.md.pair.lj(r_cut=2.5, nlist=ljnl)
    lj.set_params(mode="xplor")

    coeffs_dict['pair_coeffs'] += [[_, 0.0, 0.0] for _ in system.particles.types if _.startswith("_R")]

    for type1 in coeffs_dict['pair_coeffs']:
        for type2 in coeffs_dict['pair_coeffs']:
            lj.pair_coeff.set(type1[0], type2[0],
                              epsilon=np.sqrt(type1[1] * type2[1]) * 0.4,
                              sigma=(type1[2] + type2[2]) / 2)

    if len(coeffs_dict['bond_coeffs']) != 0:
        harmonic_bond = hoomd.md.bond.harmonic()
        for bond in coeffs_dict['bond_coeffs']:
            harmonic_bond.bond_coeff.set(bond[0], k=bond[1], r0=bond[2])

    if len(coeffs_dict['angle_coeffs']) != 0:
        harmonic_angle = hoomd.md.angle.harmonic()
        for angle in coeffs_dict['angle_coeffs']:
            harmonic_angle.angle_coeff.set(angle[0], k=angle[1], t0=angle[2])

    if len(coeffs_dict['dihedral_coeffs']) != 0:
        harmonic_dihedral = hoomd.md.dihedral.opls()
        for dihedral in coeffs_dict['dihedral_coeffs']:
            harmonic_dihedral.dihedral_coeff.set(dihedral[0], k1=dihedral[1],
                                                 k2=dihedral[2],
                                                 k3=dihedral[3],
                                                 k4=dihedral[4])

    for atomID, atom in enumerate(system.particles):
        if not str(atom.type).startswith("_R"):
            atom.mass = coeffs_dict['mass'][str(atom.type)]

    # TODO: Support for charges
    #pppmnl = hoomd.md.nlist.cell()
    #pppm = hoomd.md.charge.pppm(group=hoomd.group.charged(), nlist = pppmnl)
    #pppm.set_params(Nx=64,Ny=64,Nz=64,order=6,rcut=2.70)

    return system

def get_coeffs(file_name):
    coeff_dictionary = {'pair_coeffs': [], 'bond_coeffs': [],
                        'angle_coeffs': [], 'dihedral_coeffs': []}
    with open(file_name, 'r') as xml_file:
        xml_data = ET.parse(xml_file)
    root = xml_data.getroot()
    for config in root:
        for child in config:
            # First get the masses which are different
            if child.tag == 'mass':
                #coeff_dictionary['mass'] = [float(mass) for mass in
                #                            child.text.split('\n') if
                #                            len(mass) > 0]
                masses = [float(_) for _ in
                                            child.text.split('\n') if
                                            len(_) > 0]
            # Now the other coefficients
            if child.tag == 'type':
                #coeff_dictionary['mass'] = [str(atom_type) for atom_type in
                #                            child.text.split('\n') if
                #                            len(atom_type) > 0]
                types = [str(_) for _ in
                                            child.text.split('\n') if
                                            len(_) > 0]
            elif child.tag in coeff_dictionary.keys():
                if child.text is None:
                    continue
                for line in child.text.split('\n'):
                    if len(line) == 0:
                        continue
                    coeff = line.split()
                    coeff_dictionary[child.tag].append(
                        [coeff[0]] + list(map(float, coeff[1:])))
                # coeff_dictionary[child.tag] = child.text.split('\n')
    all_mass_type_pairs = [[pair[0], pair[1]]
            for pair in zip(types, masses)]
    coeff_dictionary['mass'] = {unique[0]:unique[1]
            for unique in set(tuple(unique)
                for unique in all_mass_type_pairs)}
    return coeff_dictionary

hoomd.context.initialize("--single-mpi")
file_name = "blend_opls.hoomdxml"
system = init_wrapper(file_name)
system = set_coeffs(file_name, system)
integrator_mode = hoomd.md.integrate.mode_standard(dt=0.00001);
rigid = hoomd.group.rigid_center()
nonrigid = hoomd.group.nonrigid()
both_group = hoomd.group.union("both", rigid, nonrigid)
integrator = hoomd.md.integrate.nvt(group=both_group, tau=0.1, kT=2.0)
hoomd.dump.gsd(filename="alkanes.gsd", period=1e5, group=hoomd.group.all(), overwrite=True)
log_quantities = ['temperature', 'pressure', 'volume',
                        'potential_energy', 'kinetic_energy',
                        'pair_lj_energy', 'bond_harmonic_energy',
                        'angle_harmonic_energy', 'dihedral_opls_energy']
hoomd.analyze.log("alkanes.log", quantities=log_quantities,
                        period=1e5,
                        header_prefix='#', overwrite=True)
hoomd.run(5e5)
integrator_mode.set_params(dt=0.0001)
hoomd.run(6e5)
integrator_mode.set_params(dt=0.0005)
hoomd.run(6e5)
integrator_mode.set_params(dt=0.001)
hoomd.run_upto(5e6)
