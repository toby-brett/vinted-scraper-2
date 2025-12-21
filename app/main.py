import subprocess
import json

from utils.utils import *

with open('jobs.json', 'rb') as f:
    jobs = json.load(f)

for job in jobs:

    log_file = 'logs/' + get_file_starter(job['brand'], job['item']) + '.log'
    job_str = json.dumps(job)
    subprocess.run("nohup python3 -m app.scrape_runner --job '{}' > {} 2>&1 &".format(job_str, log_file), shell=True)

    logging.info(f"app/main.py: Job {job} started")