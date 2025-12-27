import os
import subprocess
import sys
import time
from typing import List

BLOCKED_EXIT_CODE = 67
USERS = ['opc', 'scraper_ip2']
STATE_FILE = '/tmp/vinted-active-user.txt'

def get_active_user() -> str:
    try:
        with open(STATE_FILE, "r") as f:
            u = f.read().strip()
            if u in USERS:
                return u
    except FileNotFoundError:
        pass
    return USERS[0]

def set_active_user(u: str) -> None:
     with open(STATE_FILE, "w") as f:
        f.write(u)

def other_user(u: str) -> str:
    return USERS[1] if u == USERS[0] else USERS[0]

def run_as(user: str, argv: List[str]) -> int:
    # requires sudoers NOPASSWD for this command
    cmd = ["sudo", "-n", "-u", user, sys.executable] + argv
    p = subprocess.run(cmd)
    return p.returncode

def main():
    worker_argv = sys.argv[1:]
    if not worker_argv:
        print("Usage: supervisor.py -m app.runner --jobs_opc ...", file=sys.stderr)
        sys.exit(2)

    while True:
        u = get_active_user()
        print(f"User: {u}")
        rc = run_as(u, worker_argv)

        if rc == BLOCKED_EXIT_CODE:
            print(f"Blocked: Changing user")
            nu = other_user(u)
            set_active_user(nu)
            time.sleep(2)
            continue

        time.sleep(2)

if __name__ == "__main__":
    main()
