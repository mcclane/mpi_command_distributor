import os
import time
import subprocess
import sys
import glob
import argparse
import pathlib
from yaml import load
from .mpi_utils import get_reachable_nodes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--commandfile', type=str, required=True, help="File containing commands to be distributed, each on a separate line")
    parser.add_argument('--cfg', type=str, required=True, help="launcher yaml configuration file")
    args = parser.parse_args()
    with open(args.cfg) as f:
        launcher_cfg = load(f)
    launch(args.commandfile, launcher_cfg)


def launch(commandfile, cfg):
    """
        launches the command distributor to distribute and run the commands in the commandfile

        Arguments:
        commandfile: filename with commands to run
        cfg: a dictionary containing desired configuration
            Required keys in cfg:
                'hosts': a list of hostnames to run the commands on, ex: ['127x15.csc.calpoly.edu', 
                                                                          '127x15.csc.calpoly.edu']
                'processes-per-node': The number of processes to launch on each specified host
                'python': the python executable to use, ex: 'python3.4'
                'mpiexec-path': the path to the mpiexec executable, ex: '/usr/lib64/openmpi/bin/mpiexec' 
                'mpi-args': a list of arguments you want for the MPI run command
    """
    args = [
        cfg['mpiexec-path']
    ]
    for ma in cfg['mpi-args']:
        args.extend(ma.split())

    alive_nodes = get_reachable_nodes(cfg['hosts'])
    args.extend([
        '--host',
        ','.join([','.join([n]*cfg['processes-per-node']) for n in alive_nodes])
    ])

    args.extend([
        '-np',
        str(len(alive_nodes) * cfg['processes-per-node'])
    ])

    my_path = pathlib.Path(__file__).parent.absolute()
    args.extend([
        cfg['python'],
        str(my_path / 'command_distributor.py'),
        commandfile
    ])
    print(' '.join(args))

    return subprocess.call(args)


if __name__ == '__main__':
    main()
