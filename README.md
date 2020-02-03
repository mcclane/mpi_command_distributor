# Message Passing Interface (MPI) command distributor
Distributes commands in chunks to be run on an MPI implementing cluster and retrieves the return codes of the commands. This is intended to be simple and generic.

## Why?
This is being developed to screen about 7 million potential malaria drugs on Cal Poly
s MPAC and DIRAC clusters.

## Requirements
- A cluster with an MPI implementation installed. This is currently being developed on the MPAC cluster with OpenMPI installed.
- python3
    + mpi4py

## Running a local example

`mpiexec -n 4 python3.4 test.py`
