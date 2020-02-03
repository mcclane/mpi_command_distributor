from mpi4py import MPI
import numpy as np
import os
from queue import Queue

def main():
    rank = MPI.COMM_WORLD.Get_rank()
    if rank == 0:
        command_queue = Queue()
        for c in ["ls", "lsasdf", "ls"]:
            command_queue.put(c)
        manager(command_queue)
    else:
        worker()

def manager(command_queue):
    status = MPI.Status()
    while not command_queue.empty():
        received = MPI.COMM_WORLD.recv(status=status)
        print("received ", received, "from", status.Get_source())
        if 'return_codes' in received:
            print("Return codes received from", status.Get_source(), received['return_codes'])
        MPI.COMM_WORLD.send({
            'commands': [
                command_queue.get()
             ]}, 
             dest=status.Get_source()
        )
    print("Sending out stop signals")
    for i in range(MPI.COMM_WORLD.Get_size() - 1):
        received = MPI.COMM_WORLD.recv(status=status)
        if 'return_codes' in received:
            print("Return codes received from", status.Get_source(), received['return_codes'])
        MPI.COMM_WORLD.send({
                'stop'
            },
            dest=status.Get_source())
    print("Master done")

            


def worker():
    MPI.COMM_WORLD.send({'ready'}, dest=0)
    while True:
        received = MPI.COMM_WORLD.recv(source=0)
        if 'commands' in received:
            results = []
            for cmd in received['commands']:
                return_code = os.system(cmd)
                results.append([cmd, return_code])
            MPI.COMM_WORLD.send({
                    'return_codes': results
                }, 
                dest=0)
        elif 'stop' in received:
            break



if __name__ == '__main__':
    main()
