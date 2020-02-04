from os import system, makedirs, chdir, path
import os
import time
import subprocess
import sys
import glob
import argparse
import re
import platform
from yaml import load
from mpi_utils import get_alive_nodes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--commandfile', type=str, required=True, help="File containing commands to be distributed, each on a separate line")
    parser.add_argument('--cfg', type=str, required=True, help="launcher yaml configuration file")
    args = parser.parse_args()
    with open(args.cfg) as f:
        launcher_cfg = load(f)
    launch(args.commandfile, launcher_cfg)


def launch(commandfile, cfg):
    args = [
        cfg['mpiexec-path']
    ]
    for ma in cfg['mpi-args']:
        args.extend(ma.split())

    alive_nodes = get_alive_nodes(cfg['hosts'])
    args.extend([
        '--host',
        ','.join([','.join([n]*cfg['processes-per-node']) for n in alive_nodes])
    ])

    args.extend([
        '-np',
        str(len(cfg['hosts']) * cfg['processes-per-node'])
    ])

    args.extend([
        cfg['python'],
        'command_distributor.py',
        commandfile
    ])
    print(' '.join(args))

    os.execv(cfg['mpiexec-path'], args)


if __name__ == '__main__':
    main()
