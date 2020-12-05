from time import time, sleep
from matplotlib import pyplot as plt
from controller import mainf

algorithms = [
    'round-robin',
    'machine-weighted-round-robin',
    'region-weighted-round-robin',
    'least-response-time',
    'least-connections',
]

def plot_total_times():
    request_count = [250, 500, 750, 1000, 1250]

    total_times = {k: [] for k in algorithms}

    for alg in algorithms:
        for r in request_count:
            total_times[alg].append(mainf(r, alg)[2])
            sleep(5)

    plt.plot(request_count, 'round-robin', data=total_times, markersize=12, color='tab:blue', linewidth=3, label='Round Robin')
    plt.plot(request_count, 'machine-weighted-round-robin', data=total_times, markersize=12, color='tab:green', linewidth=3, label='Machine Weighted Round Robin')
    plt.plot(request_count, 'region-weighted-round-robin', data=total_times, markersize=12, color='tab:orange', linewidth=3, label='Region Weighted Round Robin')
    plt.plot(request_count, 'least-response-time', data=total_times, markersize=12, color='tab:red', linewidth=3, label='Least response time')
    plt.plot(request_count, 'least-connections', data=total_times, markersize=12, color='tab:cyan', linewidth=3, label='Least connections')

    plt.xlabel('Requests')
    plt.ylabel('Total time (s)')
    plt.xticks(request_count)
    plt.yticks(range(0, 90, 10))

    plt.legend()
    plt.title('Load balancing algorithms total times')

    plt.text(650, 1, "Lower is better")

    plt.savefig('plots/total_times.png')


def plot_time_per_request():
    req_count = 500
    total_times = {k: None for k in algorithms}

    for alg in algorithms:
        times, _, _ = mainf(500, alg)

        for i in range(len(times)):
            times[i] *= 1000

        total_times[alg] = times
        sleep(5)

    plt.plot(range(req_count), 'round-robin', data=total_times, markersize=12, color='tab:blue', linewidth=1, label='Round Robin')
    plt.plot(range(req_count), 'machine-weighted-round-robin', data=total_times, markersize=12, color='tab:green', linewidth=1, label='Machine Weighted Round Robin')
    plt.plot(range(req_count), 'region-weighted-round-robin', data=total_times, markersize=12, color='tab:orange', linewidth=1, label='Region Weighted Round Robin')
    plt.plot(range(req_count), 'least-response-time', data=total_times, markersize=12, color='tab:red', linewidth=1, label='Least response time')
    plt.plot(range(req_count), 'least-connections', data=total_times, markersize=12, color='tab:cyan', linewidth=1, label='Least connections')

    plt.xlabel('Requests')
    plt.ylabel('Total time per request (ms)')
    plt.xticks(range(0, req_count + 1, 50))
    plt.ylim([0, 21000])

    plt.legend()
    plt.title('Load balancing algorithms requests\' response times')

    plt.text(650, 1, "Lower is better")

    plt.savefig('plots/total_req_times.png')


def plot_time_to_send():
    req_count = 500
    total_times = {k: None for k in algorithms}

    for alg in algorithms:
        _, times, _ = mainf(500, alg)

        for i in range(len(times)):
            times[i] *= 1000

        total_times[alg] = times
        sleep(5)


    plt.plot(range(req_count), 'round-robin', data=total_times, markersize=12, color='tab:blue', linewidth=2, label='Round Robin')
    plt.plot(range(req_count), 'machine-weighted-round-robin', data=total_times, markersize=12, color='tab:green', linewidth=2, label='Machine Weighted Round Robin')
    plt.plot(range(req_count), 'region-weighted-round-robin', data=total_times, markersize=12, color='tab:orange', linewidth=2, label='Region Weighted Round Robin')
    plt.plot(range(req_count), 'least-response-time', data=total_times, markersize=12, color='tab:red', linewidth=2, label='Least response time')
    plt.plot(range(req_count), 'least-connections', data=total_times, markersize=12, color='tab:cyan', linewidth=2, label='Least connections')

    plt.xlabel('Requests')
    plt.ylabel('Total until request was sent (ms)')
    plt.xticks(range(0, req_count + 1, 50))
    plt.ylim([0, 21000])

    plt.legend()
    plt.title('Load balancing algorithms requests\' time to send')

    plt.savefig('plots/total_send_times.png')
    

if __name__ == '__main__':
    plot_total_times()
    plot_time_per_request()
    plot_time_to_send()