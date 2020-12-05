import requests
import json
from time import time, sleep
from threading import Semaphore, Thread
from matplotlib import pyplot as plt

SERVER_IP = 'http://localhost:5000/'
WORK      = SERVER_IP + 'work'
REGION    = lambda reg: '{}/{}'.format(WORK, reg)
MACHINE   = lambda reg, machine: "{}/{}".format(REGION(reg), machine)

latency = {'emea': 0, 'asia': 0, 'us': 0}
wait_between_regions = None

def thread_send_request(reg):
    url = REGION(reg)
    
    start_time = time()
    response = requests.get(url)
    end_time = time()

    request_callback(response, end_time - start_time)

def send_request(reg):
    t = Thread(target = thread_send_request, args=(reg,))
    t.daemon = True
    t.start()

def request_callback(response, total_time):
    latency[json.loads(response.text)['region']] += (total_time * 1000)
    wait_between_regions.release()


def compute_latency(num_requests):
    global wait_between_regions

    wait_between_regions = Semaphore(num_requests)

    for region in latency.keys():
        for _ in range(num_requests):
            wait_between_regions.acquire()
            send_request(region)

    for _ in range(num_requests):
        wait_between_regions.acquire()

    for region in latency.keys():
        latency[region] = round(latency[region] / num_requests, 2)

    return latency

def plot(latencies):
    plt.plot([10, 50, 100, 150], 'emea', data=latencies, markersize=12, color='tab:blue', linewidth=2, label='emea')
    plt.plot([10, 50, 100, 150], 'asia', data=latencies, markersize=12, color='tab:orange', linewidth=2, label='asia')
    plt.plot([10, 50, 100, 150], 'us', data=latencies, markersize=12, color='tab:green', linewidth=2, label='us')

    plt.xlabel('Concurrent requests')
    plt.ylabel('Latency (ms)')
    plt.xticks([10, 50, 100, 150])
    plt.yticks(range(0, 7000, 500))

    plt.legend()
    plt.title('Latency of regions')

    plt.savefig('../plots/latency.png')


if __name__ == '__main__':
    latencies = {'emea': [], 'asia': [], 'us': []}

    for r in [10, 50, 100, 150]:
        latency = compute_latency(r)
        
        for k in latency.keys():
            latencies[k].append(latency[k])

        sleep(5)
    
    plot(latencies)
