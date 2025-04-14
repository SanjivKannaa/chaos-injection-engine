import json
import subprocess

terraform_dir = "/home/jsk/chaosbank/deployment/v2/"

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
    return [r for r in resources if r["type"] in ["aws_instance"]]

def filter_asg_resources(resources):
    return [r for r in resources if r["type"] in ["aws_autoscaling_group"]]

def get_asg_instances(asg_name):
    """Get instances in an Auto Scaling Group using AWS CLI"""
    cmd = [
        'aws', 'autoscaling', 'describe-auto-scaling-groups',
        '--auto-scaling-group-names', asg_name
    ]
    
    result = subprocess.run(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    if result.returncode != 0:
        print(f"Error getting ASG instances: {result.stderr.decode()}")
        return []
    
    asg_data = json.loads(result.stdout.decode())
    instances = []
    
    for asg in asg_data.get('AutoScalingGroups', []):
        for instance in asg.get('Instances', []):
            instances.append(instance.get('InstanceId'))
    
    return instances

def get_ec2_instance_details(instance_ids):
    """Get detailed information about EC2 instances"""
    if not instance_ids:
        return []
    
    instance_ids_str = ' '.join(instance_ids)
    cmd = [
        'aws', 'ec2', 'describe-instances',
        '--instance-ids'
    ] + instance_ids
    
    result = subprocess.run(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    if result.returncode != 0:
        print(f"Error getting EC2 details: {result.stderr.decode()}")
        return []
    
    ec2_data = json.loads(result.stdout.decode())
    instances = []
    
    for reservation in ec2_data.get('Reservations', []):
        for instance in reservation.get('Instances', []):
            # Convert tags list to dictionary
            tags = {}
            for tag in instance.get('Tags', []):
                tags[tag.get('Key')] = tag.get('Value')
            
            instance_info = {
                'InstanceId': instance.get('InstanceId'),
                'PublicIp': instance.get('PublicIpAddress', 'N/A'),
                'PrivateIp': instance.get('PrivateIpAddress', 'N/A'),
                'AvailabilityZone': instance.get('Placement', {}).get('AvailabilityZone', 'N/A'),
                'SubnetId': instance.get('SubnetId', 'N/A'),
                'ImageId': instance.get('ImageId', 'N/A'),
                'InstanceType': instance.get('InstanceType', 'N/A'),
                'Tags': tags
            }
            instances.append(instance_info)
    
    return instances

def main():
    tf_state = get_terraform_state_json()
    resources = extract_resources(tf_state)

    # Print direct EC2 instances
    ec2_instances = filter_ec2_instances(resources)
    print("Discovered Direct EC2 Instances:\n")

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
    
    # Get ASG info and instances
    asg_resources = filter_asg_resources(resources)
    print("\nDiscovered Auto Scaling Groups and their Instances:\n")
    
    for asg in asg_resources:
        values = asg['values']
        asg_name = values.get('name')
        asg_tags = values.get('tag', [])
        
        # Get the Name tag value if present
        asg_name_tag = "Unnamed"
        for tag in asg_tags:
            if tag.get('key') == 'Name':
                asg_name_tag = tag.get('value')
                break
        
        print(f"ASG Name: {asg_name} ({asg_name_tag})")
        print(f"Desired Capacity: {values.get('desired_capacity')}")
        print(f"Min/Max Size: {values.get('min_size')}/{values.get('max_size')}")
        
        # Get instances in this ASG
        instance_ids = get_asg_instances(asg_name)
        
        if not instance_ids:
            print("No instances found in this ASG")
            print("-" * 60)
            continue
        
        print(f"Found {len(instance_ids)} instances in ASG: {', '.join(instance_ids)}")
        print("\nInstance Details:")
        
        instances = get_ec2_instance_details(instance_ids)
        
        for idx, instance in enumerate(instances, 1):
            print(f"\n  Instance #{idx}:")
            print(f"  Instance Name   : {instance['Tags'].get('Name', 'Unnamed')}")
            print(f"  Instance ID     : {instance['InstanceId']}")
            print(f"  Public IP       : {instance['PublicIp']}")
            print(f"  Private IP      : {instance['PrivateIp']}")
            print(f"  Availability Zone: {instance['AvailabilityZone']}")
            print(f"  Subnet ID       : {instance['SubnetId']}")
            print(f"  AMI ID          : {instance['ImageId']}")
            print(f"  Instance Type   : {instance['InstanceType']}")
            print(f"  Tags            : {json.dumps(instance['Tags'])}")
        
        print("-" * 60)

if __name__ == "__main__":
    main()