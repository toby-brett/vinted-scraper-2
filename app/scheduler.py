import argparse
import random
import time

import logging

from app import runner
from config import settings
import domain.models as models
from scraper.browser import BrowserSession
import utils.utils as utils

import argparse
import logging
import os
from datetime import datetime


def setup_logging(job_name: str, log_dir: str = "logs") -> None:

    os.makedirs(log_dir, exist_ok=True)

    # Safe filename
    safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in job_name).strip("_")
    ts = datetime.utcnow().strftime("%Y%m%d")
    log_path = os.path.join(log_dir, f"{safe}_{ts}.log")

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Avoid duplicate handlers if main() is called more than once
    root.handlers.clear()

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    # Terminal
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)

    # File
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)

    root.addHandler(sh)
    root.addHandler(fh)

    logging.info(f"Logging to terminal + {log_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--jobs_opc',
        required=True,
        help="Path to json folder"
    )
    args = parser.parse_args()
    jobs = utils.load_jobs(args.jobs)

    while True:
        with BrowserSession() as session:

            runtimes = []
            errors = 0
            for job in jobs:
                rt = models.JobRuntime(
                    job=job,
                    session=session,
                    seen_ids=utils.load_ids(job.id_path),
                    data_storer=job.data_storer
                )
                runtimes.append(rt)

            while True:

                if errors > settings.MAX_ERRORS:
                    raise RuntimeError("Max consecutive errors exceeded")

                for runtime in runtimes:

                    setup_logging(getattr(runtime.job, "name", runtime.job.search))

                    tick_result = runner.tick(runtime)
                    if tick_result is None: # CLOUDFARE BLOCKING
                        logging.fatal("Cloudflare blocked - sleeping for 1 hour and resetting browser")
                        time.sleep(60 * 60)
                        break

                    logging.info(f"[{runtime.job.search}] Ticks completed: {tick_result}")
                    logging.info(f"[{runtime.job.search}] Tick warnings: {tick_result.warnings}")

                    if tick_result.return_status == "error":
                        errors += 1
                        logging.warning(f"[{runtime.job.search}] Error count = {errors}")

                    elif tick_result.return_status == "blocked":
                        logging.info(f"[{runtime.job.search}] Blocked - creating new browser and sleeping 1 hour")
                        time.sleep(settings.BLOCK_COOLDOWN_SECONDS)
                        break

                    else:
                        errors = 0
                        pause = random.randint(settings.RETRY_SLEEP_SECONDS, settings.RETRY_SLEEP_SECONDS * 2)
                        logging.info(f"[{runtime.job.search}] Sleeping {pause}s")
                        time.sleep(pause)
                        logging.info(f"[{runtime.job.search}] Sleeping finished")
                        logging.info("")

if __name__ == "__main__":
    main()