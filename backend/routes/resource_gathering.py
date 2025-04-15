from flask import Blueprint, request, jsonify, make_response, render_template
from extensions import db
import os
from models import Resources
import subprocess
import json

terraform_dir = "/v1/"

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

def get_infrastructure_summary():
    tf_state = get_terraform_state_json()
    resources = extract_resources(tf_state)

    summary = {
        "ec2_instances": [],
    }

    # Direct EC2 Instances
    ec2_instances = filter_ec2_instances(resources)

    for ec2 in ec2_instances:
        values = ec2['values']
        tags = values.get("tags", {})
        instance_info = {
            "name": tags.get("Name", "Unnamed"),
            "instance_id": values.get("id", "N/A"),
            "public_ip": values.get("public_ip", "N/A"),
            "private_ip": values.get("private_ip", "N/A"),
            "availability_zone": values.get("availability_zone", "N/A"),
            "subnet_id": values.get("subnet_id", "N/A"),
            "ami_id": values.get("ami", "N/A"),
            "instance_type": values.get("instance_type", "N/A"),
            "tags": tags
        }
        summary["ec2_instances"].append(instance_info)

    # Auto Scaling Groups and their instances
    asg_resources = filter_asg_resources(resources)

    for asg in asg_resources:
        values = asg['values']
        asg_name = values.get('name')
        asg_tags = values.get('tag', [])
        
        asg_name_tag = "Unnamed"
        for tag in asg_tags:
            if tag.get('key') == 'Name':
                asg_name_tag = tag.get('value')
                break

        instance_ids = get_asg_instances(asg_name)
        instances_info = []

        if instance_ids:
            instances = get_ec2_instance_details(instance_ids)

            for instance in instances:
                instance_data = {
                    "name": instance['Tags'].get('Name', 'Unnamed'),
                    "instance_id": instance['InstanceId'],
                    "public_ip": instance.get('PublicIp'),
                    "private_ip": instance.get('PrivateIp'),
                    "availability_zone": instance.get('AvailabilityZone'),
                    "subnet_id": instance.get('SubnetId'),
                    "ami_id": instance.get('ImageId'),
                    "instance_type": instance.get('InstanceType'),
                    "tags": instance['Tags']
                }
                summary["ec2_instances"].append(instance_data)

    return summary


resource_gathering_bp = Blueprint('resource_gathering', __name__)

@resource_gathering_bp.route('/', methods=["POST"])
def gather(version="v1"):
    data = request.json
    global terraform_dir
    terraform_dir = "/" + data.get("version") + "/"
    try:
        return make_response(get_infrastructure_summary()), 200
    except Exception as e:
        return make_response({"error": e}), 500