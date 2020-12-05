# Load Balancing Evaluation

## Overview
A series of load balancing policies have been implemented and benchmarked against a system consisting of three regions with a total of five nodes, each simulating a different latency and work time.

<img src="https://i.imgur.com/K6332kP.png" alt="Your image title" width="350"/>

---

## Installation

The system works by pushing docker images to the Heroku service, thus an account must be [created](https://signup.heroku.com/login) beforehand. 

After registering, logging in is required
```bash
heroku login
heroku container:login
docker login
```

A script for deploying the docker images to the heroku was created in the `scripts/` directory
```bash
scripts/deploy_dockers.sh <Heroku username>
```

To start the router locally, run
```bash
scripts/run.sh <Heroku username>
```

The Flask server should start on the port 5000.

---
## Usage

Five load balancing policies have been implemented in the `controller.py` file.
To simulate a policy for a number of requests run
```bash
python3 controller.py <requests count> <policy>

# Available policies are 
#       round-robin,
#       machine-weighted-round-robin,
#       region-weighted-round-robin,
#       least-connections,
#       least-respone-time
```

To generate plots for the performance of the algorithms
```bash
python3 controller_times.py
```