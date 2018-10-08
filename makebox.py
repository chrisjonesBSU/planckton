import mbuild as mb
import parmed as pmd


def test_typing(compound_file, ff_file):
    compound_mb = mb.load(compound_file)
    compound_pmd = pmd.load_file(compound_file)
    types_needed = set()
    for atom_pmd, atom_mb in zip(compound_pmd, compound_mb):
        atom_mb.name = "_{}".format(atom_pmd.type)
        types_needed.add(atom_pmd.type)
    box = mb.packing.fill_box(compound_mb,
                              n_compounds=50,
                              box=[6.53, 6.53, 6.53],
                              overlap=0.2,
                              fix_orientation=False)
    box.save("test_typing.hoomdxml",
             overwrite=True,
             forcefield_files="compounds/gaff.4fxml",
             ref_mass=32.06,
             ref_energy=1.046,
             ref_distance=0.35635948725613575)


compound_file = "compounds/itic_typed.mol2"
ff_file = "compounds/gaff.4fxml"
test_typing(compound_file, ff_file)
