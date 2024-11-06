import csv
import yaml
import argparse

def get_server_type(hostname):
    """Determine server type based on keywords in the hostname."""
    if "web" in hostname.lower():
        return "webservers"
    elif "db" in hostname.lower():
        return "dbservers"
    else:
        return "appservers"

def build_inventory(input_file, output_file, service_name):
    """Build and save an Ansible inventory structure from a CSV file."""
    # Initialize a nested dictionary for the Ansible inventory
    inventory = {
        "all": {
            "vars": {
                "service_name": service_name.upper()  # Add the uppercase service_name variable
            },
            "children": {
                service_name: {  # Use the service name as specified
                    "children": {}
                }
            }
        }
    }

    # Read the CSV file and build the inventory structure
    with open(input_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hostname = row["Name"].lower()
            datacenter = hostname[:3]
            server_type = get_server_type(hostname)
            
            # Create nested structure for datacenter if it doesn't exist
            if datacenter not in inventory["all"]["children"][service_name]["children"]:
                inventory["all"]["children"][service_name]["children"][datacenter] = {"children": {}}
            
            # Create nested structure for server_type group if it doesn't exist
            server_group = f"{datacenter}_{server_type}"
            if server_group not in inventory["all"]["children"][service_name]["children"][datacenter]["children"]:
                inventory["all"]["children"][service_name]["children"][datacenter]["children"][server_group] = {
                    "hosts": {},
                    "vars": {
                        "server_type": server_type  # Add server_type variable
                    }
                }
            
            # Add the host to the appropriate server group
            inventory["all"]["children"][service_name]["children"][datacenter]["children"][server_group]["hosts"][hostname] = ""

    # Custom representer to avoid showing empty strings as null
    class CustomDumper(yaml.SafeDumper):
        def represent_str(self, data):
            if data == "":
                return self.represent_scalar('tag:yaml.org,2002:null', '')
            return self.represent_scalar('tag:yaml.org,2002:str', data)

    yaml.add_representer(str, CustomDumper.represent_str, Dumper=CustomDumper)

    # Write the inventory structure to a YAML file
    with open(output_file, "w") as yamlfile:
        yaml.dump(inventory, yamlfile, Dumper=CustomDumper, default_flow_style=False)

    print(f"Ansible inventory file '{output_file}' created successfully with service name '{service_name}'.")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Generate an Ansible inventory YAML from a CSV file.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input CSV file.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output YAML file.")
    parser.add_argument("-s", "--service", required=True, help="Service name to be used as the parent group.")
    
    args = parser.parse_args()

    # Build inventory using the provided input, output, and service name
    build_inventory(args.input, args.output, args.service)

if __name__ == "__main__":
    main()
