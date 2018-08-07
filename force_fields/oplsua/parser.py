
ff_par = "oplsua.par"
ff_sb = "oplsua.sb"

with open(ff_par, 'r') as f:
    ff_par_lines = f.readlines()

for line in ff_par_lines[2:10]:
    print(line.strip(" ").split(" "))
