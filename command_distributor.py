from mpi4py import MPI
import numpy as np
import os
import sys
from socket import gethostname
import time

COMMAND_CHUNK_SIZE = 5

def main():
    rank = MPI.COMM_WORLD.Get_rank()
    if len(sys.argv) < 2:
            print("usage: mpiexec ... python3.4 <file with list of commands>")
            return
    if rank == 0:
        m = Manager({
            'command_file': sys.argv[1]
        })
        m.manage()
    else:
        worker()


class Manager:
    def __init__(self, args):
        self.args = args

    def process_return_codes(self, received):
        print("Return codes received from", received['hostname'], received['return_codes'])
        
    def stop_workers(self):
        status = MPI.Status()
        print("Sending out stop signals")
        for i in range(MPI.COMM_WORLD.Get_size() - 1):
            received = MPI.COMM_WORLD.recv(status=status)
            if 'return_codes' in received:
                self.process_return_codes(received)
            MPI.COMM_WORLD.send({
                    'stop'
                },
                dest=status.Get_source())
        print("Master done")

    def manage(self):
        MPI.COMM_WORLD.Barrier()
        status = MPI.Status()
        with open(self.args['command_file']) as command_file:
            nextline = command_file.readline()
            while nextline:
                received = MPI.COMM_WORLD.recv(status=status)
                if 'ready' in received:
                    print("Worker ready:", status.Get_source())
                if 'return_codes' in received:
                    self.process_return_codes(received)

                commands_to_send = []
                i = 0
                while i < COMMAND_CHUNK_SIZE and nextline:
                    commands_to_send.append(nextline.strip())
                    nextline = command_file.readline()
                    i += 1

                MPI.COMM_WORLD.send({
                        'commands': commands_to_send
                    }, 
                    dest=status.Get_source()
                )
        self.stop_workers()
        MPI.COMM_WORLD.Barrier()

        
def worker():
    hostname = gethostname()
    MPI.COMM_WORLD.Barrier()
    MPI.COMM_WORLD.send({'ready'}, dest=0)
    while True:
        received = MPI.COMM_WORLD.recv(source=0)
        if 'commands' in received:
            results = []
            for cmd in received['commands']:
                return_code = os.system(cmd)
                results.append([cmd, return_code])
            MPI.COMM_WORLD.send({
                    'return_codes': results,
                    'hostname': hostname
                }, 
                dest=0)
        elif 'stop' in received:
            break
        time.sleep(1)
    MPI.COMM_WORLD.Barrier()


if __name__ == '__main__':
    main()
