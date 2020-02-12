# Message Passing Interface (MPI) command distributor

Distributes commands in chunks to be run on an MPI implementing cluster and retrieves the return codes of the commands. This is intended to be simple and generic.


## Why?

Not really sure, but it will probably become useful at some point.

## Requirements

- A cluster with an MPI implementation installed. This is currently being developed on the MPAC cluster with OpenMPI installed.
- python3
    + mpi4py
    + pyYAML


## Running with the launcher

`python3.4 mpi_launcher.py --cfg launcher_cfg.yaml --commandfile commands.txt`

`launcher_cfg.yaml` file contains information about the hosts, mpi installation, mpi arguments, desired processes per node, etc.

`commands.txt` contains each command to be distributed and executed on a separate line.


## Running directly with mpiexec

`mpiexec -n 4 python3.4 command_distributor.py`

`mpiexec --mca btl_tcp_if_include ens6f0 --prefix /usr/lib64/openmpi --hostfile <hostfile> python3.4 command_distributor.py commands.txt`
