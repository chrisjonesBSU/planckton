# PlanckTon

## Things to add

* Make the jobs easier to restart
** run up to
** don't re-init
** https://hoomd-blue.readthedocs.io/en/stable/restartable-jobs.html#temperature-ramp

## Debug notes 

`singularity exec --nv --bind $(pwd):/run/user/ planckton-test.simg python planckton/init.py`

`singularity exec --nv --bind $(pwd):/run/user/ planckton-test.simg python planckton/sim.py`
