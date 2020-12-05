import requests
import json
from time import time
from matplotlib import pyplot as plt

SERVER_IP = 'http://localhost:5000/'
WORK      = SERVER_IP + 'work'
REGION    = lambda reg: '{}/{}'.format(WORK, reg)
MACHINE   = lambda reg, machine: "{}/{}".format(REGION(reg), machine)

response_times = {'emea 0': 0, 'asia 0': 0, 'asia 1': 0, 'us 0': 0, 'us 1': 0}

def compute_response_time():
    global response_times
    machines = [('emea', 0), ('asia', 0), ('asia', 1), ('us', 0), ('us', 1)]

    for region, machine in machines:
        num_requests = 10
        times = []

        for _ in range(num_requests):
            r = requests.get(MACHINE(region, machine))
            times.append(json.loads(r.text)['response_time'])


        avg_response_time = sum(times) / len(times)
        response_times['{} {}'.format(region, machine)] = round(avg_response_time, 2)

    return response_times

def plot(response_times):
    y = response_times.values()
    x = response_times.keys()

    plt.bar(x, y, color=['tab:blue', 'tab:orange', 'tab:orange', 'tab:green', 'tab:green'])

    plt.xlabel('Nodes')
    plt.ylabel('Response time (ms)')
    # plt.ylim([10, 21])
    plt.title('Response for each node')
    plt.savefig('../plots/response_time.png')


if __name__ == '__main__':
    compute_response_time()
    plot(response_times)

