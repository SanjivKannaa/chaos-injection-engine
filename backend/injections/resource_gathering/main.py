import json
import subprocess

terraform_dir = "~/chaosbank/deployment/v2 old/"

def get_terraform_state_json() -> dict:
    result = subprocess.run(
        ['terraform', 'show', '-json'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=terraform_dir
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error getting Terraform state: {result.stderr.decode()}")
    return json.loads(result.stdout.decode())

def extract_resources(tf_state: dict):
    resource_list = []

    values = tf_state.get("values", {}).get("root_module", {}).get("resources", [])
    child_modules = tf_state.get("values", {}).get("root_module", {}).get("child_modules", [])

    def extract_from_module(mod):
        for res in mod.get("resources", []):
            resource_type = res.get("type")
            name = res.get("name")
            address = res.get("address")
            values = res.get("values", {})

            resource_info = {
                "type": resource_type,
                "name": name,
                "address": address,
                "values": values
            }

            resource_list.append(resource_info)

    extract_from_module({"resources": values})
    for mod in child_modules:
        extract_from_module(mod)

    return resource_list

def filter_ec2_instances(resources):
    return [r for r in resources if r["type"] == "aws_instance"]

def main():
    tf_state = get_terraform_state_json()
    resources = extract_resources(tf_state)

    ec2_instances = filter_ec2_instances(resources)
    print("Discovered EC2 Instances:\n")

    for ec2 in ec2_instances:
        values = ec2['values']
        tags = values.get("tags", {})
        instance_name = tags.get("Name", "Unnamed")

        print(f"Instance Name   : {instance_name}")
        print(f"Instance ID     : {values.get('id', 'N/A')}")
        print(f"Public IP       : {values.get('public_ip', 'N/A')}")
        print(f"Private IP      : {values.get('private_ip', 'N/A')}")
        print(f"Availability Zone: {values.get('availability_zone', 'N/A')}")
        print(f"Subnet ID       : {values.get('subnet_id', 'N/A')}")
        print(f"AMI ID          : {values.get('ami', 'N/A')}")
        print(f"Instance Type   : {values.get('instance_type', 'N/A')}")
        print(f"Tags            : {json.dumps(tags)}")
        print("-" * 60)

if __name__ == "__main__":
    main()
