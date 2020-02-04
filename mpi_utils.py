from os import system, makedirs, chdir, path
import os
import time
import subprocess
import sys
import glob
import argparse
import re
import platform

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hostfile', action='store', default="hostfile",
                        help='Override default hostfile')
    parser.add_argument('--setup-ssh', action='store_true', help="set up ssh on known lab computers")
    args = parser.parse_args()

    if check_mpi():
        print("exiting.")
        return
    if args.setup_ssh:
        possible_nodes = []
        with open(args.hostfile) as f:
            for line in f:
                line = line.strip()
                if line and line[0] != '#':
                    possible_nodes.append(line.split()[0])
        alive_nodes = get_alive_nodes(possible_nodes)
        setup_ssh(alive_nodes)


def get_alive_nodes(possible_nodes):
    print("Checking possible nodes:", possible_nodes)        
        
    alive_nodes = list()
    for node in possible_nodes:
        cmd = ['ping', '-c 1', node]
        val = 0
        try:
            val = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            continue
        if val:
            alive_nodes.append(node)

    return alive_nodes


def setup_ssh(alive_nodes):
    user = input("What is your ssh username?: ")
    hostname = platform.node()
    print("Hostname found:" + hostname)
    ssh_path = path.expanduser("~/.ssh/")
    if not path.exists(ssh_path + "id_rsa.pub"):
        print("ERROR: public ssh key at" + "does not exist, please generate one")
        print("Run:ssh-keygen")
        exit(1)
    
    for node in alive_nodes:
        system("ssh-keygen -R " + node)
        system("ssh-keyscan -H " + node + " >> ~/.ssh/known_hosts")
        system("ssh-keyscan -H " + hostname + " >> ~/.ssh/known_hosts")
        system("ssh-copy-id -i ~/.ssh/id_rsa.pub " + user + "@" + node)

    print("Successful setup ssh keys with:")
    for node in alive_nodes: print(node)

    print("SSH setup Complete")


# checks for the existence of the mpiexec and the correct version
# in order to verify that mpi exists on the main node
def check_mpi():
    FNULL = open(os.devnull, 'w')
    result = ""
    try:
        result = subprocess.check_output(["mpiexec", "--version"], stderr=FNULL)
    except OSError as e:
        print("ERROR: Failed to find MPI in PATH, please add to .bashrc:")
        print("\tLD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64/openmpi/lib")
        print("\tPATH=$PATH:/usr/lib64/openmpi/bin")
        print("\texport LD_LIBRARY_PATH")
        print("\texport PATH")
        return 1
    result = result.decode()
    result = result.split('\n')[0]
    result = result.split(' ')[2]
    major_ver = result.split('.')[0]
    minor_ver = result.split('.')[1]
    if major_ver is not '1':
        print('WARNING: Incorrect version of MPI identified')
        print('Version 1.10 is supported, identified version ' + result)
        return 1
    return 0

if __name__ == '__main__':
    main()

