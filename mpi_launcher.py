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
    parser.add_argument('--hostfile', action='store', default="./src/hostFile",
                        help='Override default hostfile')
    parser.add_argument('--wpm', action='store', default="4",
                        help="Workers Per Machine (Default is 4)")
    parser.add_argument('--setup-ssh', action='store_true', help="set up ssh on known lab computers")

    args = parser.parse_args()

    if check_mpi():
        print("exiting.")
        return
    if args.setup_ssh:
        setup_ssh()


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

# Login to all machines possible and setup ssh passwordless
def setup_ssh():
    user = input("What is your ssh username?: ")
    hostname = platform.node()
    print("Hostname found:" + hostname)
    ssh_path = path.expanduser("~/.ssh/")
    if not path.exists(ssh_path + "id_rsa.pub"):
        print("ERROR: public ssh key at" + "does not exist, please generate one")
        print("Run:ssh-keygen")
        exit(1)

    print("Setting up connections with MPAC Lab Nodes")
    alive_nodes = list()
# Get health of MPAC Lab and find all active nodes
    for i in range(1, 37):
        if i < 10:
            cmd = "127x0" + str(i) + ".csc.calpoly.edu"
        else:
            cmd = "127x" + str(i) + ".csc.calpoly.edu"
            val = 0
        try:
            val = subprocess.check_output(['ping', '-c 1', cmd])
        except subprocess.CalledProcessError as e:
            continue
        if val != 0:
            alive_nodes.append(cmd)

# add nodes to known_hosts file
    for node in alive_nodes:
        system("ssh-keygen -R " + node)
        system("ssh-keyscan -H " + node + " >> ~/.ssh/known_hosts")
        system("ssh-keyscan -H " + hostname + " >> ~/.ssh/known_hosts")
        # setup public ssh key login
        system("ssh-copy-id -i ~/.ssh/id_rsa.pub " + user + "@" + node)

    print("Successful setup ssh keys with:")
    for node in alive_nodes: print(node)


    print("Setup Complete")

if __name__ == '__main__':
    main()
