import argparse
import requests
import json

def get_credentials(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        endpoint = lines[0].strip()
        username = lines[1].strip()
        password = lines[2].strip()
    return endpoint, username, password

def get_mac_addresses(file_path):
    with open(file_path, 'r') as file:
        mac_addresses = [line.strip() for line in file.readlines()]
    return mac_addresses

def fetch_asset_info(endpoint, username, password, mac_address):
    url = f"{endpoint}/api/now/table/cmdb_ci?sysparm_query=mac_address={mac_address}"
    response = requests.get(url, auth=(username, password), headers={"Accept": "application/json"})
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def main():
    parser = argparse.ArgumentParser(description='Fetch asset information from ServiceNow based on MAC addresses.')
    parser.add_argument('mac_file', help='File containing MAC addresses separated by carriage returns.')
    parser.add_argument('credentials_file', help='File containing ServiceNow endpoint, username, and password.')
    args = parser.parse_args()

    endpoint, username, password = get_credentials(args.credentials_file)
    mac_addresses = get_mac_addresses(args.mac_file)

    for mac in mac_addresses:
        try:
            asset_info = fetch_asset_info(endpoint, username, password, mac)
            print(json.dumps(asset_info, indent=4))
        except Exception as e:
            print(f"Failed to fetch information for MAC address {mac}: {e}")

if __name__ == "__main__":
    main()
