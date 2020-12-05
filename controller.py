import requests
import json
import sys
from time import time

from threading import Thread, Barrier, Lock, RLock, Semaphore

SERVER_IP = 'http://localhost:5000/'
WORK      = SERVER_IP + 'work'
REGION    = lambda reg: '{}/{}'.format(WORK, reg)
MACHINE   = lambda reg, machine: "{}/{}".format(REGION(reg), machine)

def thread_send_request(policy, reg, mach):
    if reg is not None and mach is not None:
        policy.max_requests_per_machine[(reg, mach)].acquire()
    policy.max_requests_total.acquire()

    if reg is None and mach is None:
        url = WORK
    elif mach is None:
        url = REGION(reg)
    else:
        url = MACHINE(reg, mach)
    
    policy.time_to_send.append(time() - policy.start_time)

    response = None
    start_time = time()
    try:
        response = requests.get(url)
    except:
        print(reg, mach)
    end_time = time()

    policy.max_requests_total.release()
    if reg is not None and mach is not None:
        policy.max_requests_per_machine[(reg, mach)].release()

    policy.request_callback(response, end_time - start_time)


class Policy():
    machines = [('emea', 0), ('asia', 0), ('asia', 1), ('us', 0), ('us', 1)]
    regions  = ['emea', 'asia', 'us']

    def __init__(self, req_count):
        self._req_count = req_count
        self._total_time = []
        self.time_to_send = []
        self._req_sent = 0
        self._req_lock = Lock()
        self._finished_lock = RLock()
        self._finished_lock.acquire()
        self.max_requests_per_machine = {mach: Semaphore(50) for mach in Policy.machines}
        self.max_requests_total = Semaphore(100)
        self.start_time = None

    def send_request(self, reg=None, mach=None):
        t = Thread(target = thread_send_request, args=(self, reg, mach))
        t.daemon = True
        t.start()

    def request_callback(self, response, time_total):
        self._total_time.append(time_total)

        self._req_lock.acquire()
        self._req_sent += 1

        if self._req_sent >= self._req_count:
            try:
                self._finished_cv.release()
            except:
                pass

        self._req_lock.release()


    def loop(self):
        self.start_time = time()


class RoundRobinPolicy(Policy):
    def __init__(self, req_count):
        Policy.__init__(self, req_count)
        self.max_requests_total = Semaphore(50)
        
    def loop(self):
        super().loop()
        machine_idx = 0

        for i in range(self._req_count):
            self.send_request(*Policy.machines[machine_idx])
            machine_idx = (machine_idx + 1) % len(Policy.machines)

        while self._req_count > self._req_sent:
            self._finished_lock.acquire()

        return (self._total_time, sorted(self.time_to_send))

class MachineWeightedRoundRobinPolicy(Policy):
    def __init__(self, req_count):
        Policy.__init__(self, req_count)
        self._weights = [80, 120, 120, 90, 90]
        self._sent_requests = [0 for _ in Policy.machines]
        
        
    def loop(self):
        super().loop()
        sent = 0
        
        while sent < self._req_count: 
            if self._sent_requests == self._weights:
                self._sent_requests = [0 for _ in Policy.machines]

            for idx, mach in enumerate(Policy.machines):
                if self._sent_requests[idx] < self._weights[idx]:
                    self.max_requests_total.acquire()
                    self.send_request(*Policy.machines[idx])
                    self.max_requests_total.release()
                    self._sent_requests[idx] += 1
                    sent += 1

                    if sent >= self._req_count:
                            break
        
        while self._req_count > self._req_sent:
            self._finished_lock.acquire()

        return (self._total_time, sorted(self.time_to_send))


class RegionWeightedRoundRobinPolicy(Policy):
    def __init__(self, req_count):
        Policy.__init__(self, req_count)
        self._weights = [100, 250, 150]
        self._sent_requests = [0 for _ in Policy.regions]
        self.max_requests_total = Semaphore(200)
        
    def loop(self):
        super().loop()
        sent = 0

        while sent < self._req_count: 
            if self._sent_requests == self._weights:
                self._sent_requests = [0 for _ in Policy.regions]

            for idx, mach in enumerate(Policy.regions):
                if self._sent_requests[idx] < self._weights[idx]:
                    self.max_requests_total.acquire()
                    self.send_request(reg=Policy.regions[idx])
                    self.max_requests_total.release()
                    self._sent_requests[idx] += 1
                    sent += 1

                    if sent >= self._req_count:
                            break

        while self._req_count > self._req_sent:
            self._finished_lock.acquire()

        return (self._total_time, sorted(self.time_to_send))

class LeastResponseTimePolicy(Policy):
    def __init__(self, req_count):
        Policy.__init__(self, req_count)
        self._last_response_time = {mach: 0 for mach in Policy.machines}
        
    def loop(self):
        super().loop()

        for i in range(self._req_count):
            self.max_requests_total.acquire()
            lrm = min(tuple(self._last_response_time.items()), key=lambda x: x[1])[0]
            self.max_requests_total.release()

            self.send_request(*lrm)

        while self._req_count > self._req_sent:
            self._finished_lock.acquire()

        return (self._total_time, sorted(self.time_to_send))

    def request_callback(self, response, time_total):
        super().request_callback(response, time_total)

        try:
            response = json.loads(response.text)
            self._last_response_time[
                (response['region'], int(response['machine'].replace('Machine ', '')))
            ] = response['response_time']
        except:
            pass
       

class LeastConnectionsPolicy(Policy):
    def __init__(self, req_count):
        Policy.__init__(self, req_count)
        self._active_requests = {mach: 0 for mach in Policy.machines}
        self.max_requests_total = Semaphore(150)
        
    def loop(self):
        super().loop()

        for i in range(self._req_count):
            self.max_requests_total.acquire()
            lrm = min(tuple(self._active_requests.items()), key=lambda x: x[1])[0]
            self._active_requests[lrm] += 1
            self.max_requests_total.release()

            self.send_request(*lrm)

        while self._req_count > self._req_sent:
            self._finished_lock.acquire()

        return (self._total_time, sorted(self.time_to_send))

    def request_callback(self, response, time_total):
        super().request_callback(response, time_total)

        try:
            response = json.loads(response.text)
            self._active_requests[
                (response['region'], int(response['machine'].replace('Machine ', '')))
            ] -= 1
        except:
            pass
       

def mainf(reqcount, policy_name):

    if policy_name == 'round-robin':
        policy = RoundRobinPolicy(reqcount)
    elif policy_name == 'machine-weighted-round-robin':
        policy = MachineWeightedRoundRobinPolicy(reqcount)
    elif policy_name == 'region-weighted-round-robin':
        policy = RegionWeightedRoundRobinPolicy(reqcount)
    elif policy_name == 'least-response-time':
        policy = LeastResponseTimePolicy(reqcount)
    elif policy_name == 'least-connections':
        policy = LeastConnectionsPolicy(reqcount)

    total_start_time = time()
    times = policy.loop()
    total_end_time = time()

    return (*times, (total_end_time - total_start_time))

if __name__ == '__main__':
    try:
        reqcount = int(sys.argv[1])
        policy_name = sys.argv[2]
    except:
        print("Usage:\n     python3 controller.py REQUESTS_COUNT POLICY")
        sys.exit(1)


    mainf(reqcount, policy_name)
    
    
