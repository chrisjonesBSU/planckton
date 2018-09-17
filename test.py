import parmed as pmd
import mbuild as mb


foyer_kwargs = None#{"assert_angle_params": False,
                #"assert_dihedral_params": False}

gaff = False
opls = True
box_params = {"n_compounds":[100,100], "box":[100,100,100], "fix_orientation":False}

#box_params = {"n_compounds":100, "density":100, "fix_orientation":False}
if gaff:
    itic_mb = mb.load("compounds/itic_typed.mol2")
    itic_pmd = pmd.load_file("compounds/itic_typed.mol2")
    types_needed = set()
    for atom_pmd, atom_mb in zip(itic_pmd, itic_mb):
        atom_mb.name = "_{}".format(atom_pmd.type)
        types_needed.add(atom_pmd.type)
    
    itic_mb.save("temp.hoomdxml", overwrite=True)
    itic_mb = mb.load("temp.hoomdxml")
    
    ptb7_mb = mb.load("compounds/ptb7_typed.mol2")
    ptb7_pmd = pmd.load_file("compounds/ptb7_typed.mol2")
    types_needed = set()
    for atom_pmd, atom_mb in zip(ptb7_pmd, ptb7_mb):
        atom_mb.name = "_{}".format(atom_pmd.type)
        types_needed.add(atom_pmd.type)
    
    ptb7_mb.save("temp.hoomdxml", overwrite=True)
    ptb7_mb = mb.load("temp.hoomdxml")
    
    box = mb.packing.fill_box([itic_mb, ptb7_mb], **box_params)
    box.save("blend_gaff.hoomdxml",
         forcefield_files="force_fields/gaff/opv_gaff.xml",
         overwrite=True,
         ref_distance=3.56359487256,
         ref_mass=32.06,
         ref_energy=1,
         foyer_kwargs=foyer_kwargs)
    print("GAFF DONE")
if opls:
    itic_mb = mb.load("compounds/itic_typed.mol2")

    for atom in itic_mb:
        if atom.name.startswith("H"):
            itic_mb.remove(atom)
    for atom in itic_mb:
        if atom.name.startswith("H"):
            itic_mb.remove(atom)
    for atom in itic_mb:
        if atom.name.startswith("H"):
            itic_mb.remove(atom)
    for atom in itic_mb:
        if atom.name.startswith("H"):
            itic_mb.remove(atom)
    for atom in itic_mb:
        if atom.name.startswith("H"):
            itic_mb.remove(atom)
    itic_mb.save("temp.hoomdxml", overwrite=True)
    itic_mb = mb.load("temp.hoomdxml")

    ptb7_mb = mb.load("compounds/ptb7_typed.mol2")

    for atom in ptb7_mb:
        if atom.name.startswith("H"):
            ptb7_mb.remove(atom)
    for atom in ptb7_mb:
        if atom.name.startswith("H"):
            ptb7_mb.remove(atom)
    for atom in ptb7_mb:
        if atom.name.startswith("H"):
            ptb7_mb.remove(atom)
    for atom in ptb7_mb:
        if atom.name.startswith("H"):
            ptb7_mb.remove(atom)
    for atom in ptb7_mb:
        if atom.name.startswith("H"):
            ptb7_mb.remove(atom)
    ptb7_mb.save("temp.hoomdxml", overwrite=True)
    ptb7_mb = mb.load("temp.hoomdxml")

    box = mb.packing.fill_box([ptb7_mb, itic_mb], **box_params)
    box.save("blend_opls.hoomdxml", 
              overwrite=True,
              forcefield_files="force_fields/oplsua/opls-custom.xml",
              ref_distance=3.9050,
              ref_mass=32.06,
              ref_energy=0.3550,
              foyer_kwargs=foyer_kwargs)
