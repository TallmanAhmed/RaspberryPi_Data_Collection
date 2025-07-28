import os
import time
from hashlib import md5
from pathlib import Path
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
 
 
laptop_ip = ""
ping_count = 5
delay_seconds = 5
remote_path = "/home/ahmed/source"
local_path = Path("/home/raspberrypi/destination")
server = laptop_ip
port = 22
username = "ahmed"
password = ""
 
 
reachable = False
for i in range(ping_count):
    print(f"Pinging {laptop_ip}... (Attempt {i + 1})")
    response = os.system(f"ping -c 1 {laptop_ip} > /dev/null 2>&1")
    if response == 0:
        print("Laptop is reachable")
        reachable = True
        break
    else:
        print("Laptop is not reachable")
        if i < ping_count - 1:
            time.sleep(delay_seconds)
 
if not reachable:
    print("Laptop not reachable after multiple attempts. Exiting.")
    exit(1)
 
 
if not local_path.exists():
    raise Exception("Local path doesn't exist or was deleted.")
local_path.mkdir(parents=True, exist_ok=True)
 
 
def file_md5(fname):
    h = md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(16384), b''):
            h.update(chunk)
    return h.hexdigest()
 
def create_ssh_client(server, port, user, password):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server, port, user, password)
    return client
 
 
ssh = create_ssh_client(server, port, username, password)
 
stdin, stdout, stderr = ssh.exec_command(
    f"cd {remote_path} && for f in *; do [ -f \"$f\" ] && md5sum \"$f\"; done"
)
 
remote_hashes = dict(
    line.strip().split(maxsplit=1)[::-1] for line in stdout if line.strip()
)
 
with SCPClient(ssh.get_transport()) as scp:
    for filename, hash2 in remote_hashes.items():
        local_file = local_path / filename
        remote_file = f"{remote_path}/{filename}"
 
        scp.get(remote_file, str(local_file))
        hash1 = file_md5(local_file)
 
        if hash1 == hash2:
            ssh.exec_command(f"rm '{remote_file}'")
            print(f"Copied and deleted '{filename}' (hash match).")
        else:
            print(f"Hash mismatch on '{filename}'. Not deleted.")
