import requests
import json
from time import time
from matplotlib import pyplot as plt

SERVER_IP = 'http://localhost:5000/'
WORK      = SERVER_IP + 'work'
REGION    = lambda reg: '{}/{}'.format(WORK, reg)
MACHINE   = lambda reg, machine: "{}/{}".format(REGION(reg), machine)

work_times = {'emea 0': 0, 'asia 0': 0, 'asia 1': 0, 'us 0': 0, 'us 1': 0}

def compute_work_time():
    global work_times
    machines = [('emea', 0), ('asia', 0), ('asia', 1), ('us', 0), ('us', 1)]

    for region, machine in machines:
        num_requests = 10
        times = []

        for _ in range(num_requests):
            r = requests.get(MACHINE(region, machine))
            times.append(json.loads(r.text)['work_time'])


        avg_work_time = sum(times) / len(times)
        work_times['{} {}'.format(region, machine)] = round(avg_work_time, 2)

    return work_times

def plot(work_times):
    y = work_times.values()
    x = work_times.keys()

    plt.bar(x, y, color=['tab:blue', 'tab:orange', 'tab:orange', 'tab:green', 'tab:green'])

    plt.xlabel('Nodes')
    plt.ylabel('Work time (ms)')
    plt.ylim([10, 21])
    plt.title('Work time for each node')
    plt.savefig('../plots/work_time.png')


if __name__ == '__main__':
    compute_work_time()
    plot(work_times)

