import requests

from threading import Thread, Barrier, Lock

SERVER_IP = 'http://localhost:5000/'
WORK      = SERVER_IP + 'work'
REGION    = lambda reg: '{}/{}'.format(WORK, reg)
MACHINE   = lambda reg, machine: "{}/{}".format(REGION(reg), machine)

reqs_lock = Lock()
barrier = None
reqs = 0
stop_sending = 0

def stress_thread(reg, machine):
    global reqs_lock, reqs, stop_sending

    num_requests = 1000
    barrier.wait()

    for _ in range(num_requests):
        if not stop_sending:
            try:
                requests.get(MACHINE(reg, machine))
                reqs_lock.acquire()
                reqs += 1
                reqs_lock.release()
            except:
                stop_sending = 1
            

def stress_machine(reg, machine):
    global reqs, stop_sending, barrier

    reqs = 0
    stop_sending = 0
    num_threads = 1000
    barrier = Barrier(num_threads)
    th = []

    for _ in range(num_threads):
        t = Thread(target=stress_thread, args=(reg, machine))
        th.append(t)
        t.start()
    
    for t in th:
        t.join()

    print("Machine {}-{} could handle maximum {} requests".format(reg, machine, reqs))


def stress_all():
    machines = [('emea', 0), ('asia', 0), ('asia', 1), ('us', 0), ('us', 1)]

    for region, machine in machines:
        stress_machine(region, machine)

if __name__ == '__main__':
    stress_all()

