from netmiko import ConnectHandler
import re
import csv

device = {
    "device_type": "cisco_ios",
    "ip": "192.168.1.10",
    "username": "netadmin",
    "password": "your_password",
}

def get_cdp_neighbors(device):
    connection = ConnectHandler(**device)
    output = connection.send_command("show cdp neighbors detail")
    connection.disconnect()
    return output

def parse_cdp_detail(output):
    devices = []
    blocks = output.split("-----")
    for block in blocks:
        local_int = re.search(r"Interface: (\S+),", block)
        remote_host = re.search(r"Device ID: (\S+)", block)
        remote_ip = re.search(r"IP address: (\S+)", block)
        remote_port = re.search(r"Port ID \(outgoing port\): (\S+)", block)
        platform = re.search(r"Platform: (.+?),", block)

        if all([local_int, remote_host, remote_ip, remote_port, platform]):
            devices.append({
                "Local Interface": local_int.group(1),
                "Remote Device": remote_host.group(1),
                "Remote IP": remote_ip.group(1),
                "Remote Interface": remote_port.group(1),
                "Platform": platform.group(1),
            })
    return devices

def write_to_csv(devices, filename="cdp_inventory.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=devices[0].keys())
        writer.writeheader()
        for device in devices:
            writer.writerow(device)

if __name__ == "__main__":
    print("Connecting to device...")
    raw_output = get_cdp_neighbors(device)
    cdp_entries = parse_cdp_detail(raw_output)
    write_to_csv(cdp_entries)
    print("CDP data written to cdp_inventory.csv")
