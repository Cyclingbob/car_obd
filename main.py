import subprocess
import time
import config as config
import urllib.request
import sys

def is_connected():
    try:
        urllib.request.urlopen(config.online_version, timeout=2)
        return True
    except:
        return False

process = subprocess.Popen(
    ["python", config.program_file],
    stdin=sys.stdin,
    stdout=sys.stdout,
    stderr=sys.stderr,
)

while True:
    return_code = process.poll()

    if return_code is not None:
        process = process = subprocess.Popen(["python", config.program_file])

    time.sleep(2)