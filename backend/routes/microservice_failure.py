from flask import Blueprint, request, jsonify, make_response, render_template
from extensions import db
import os
from models import Resources
from chaoslib.experiment import run_experiment
import subprocess

microservice_failure_bp = Blueprint('microservice_failure', __name__)

@microservice_failure_bp.route('/start', methods=['POST'])
def start():
    data = request.json
    start_experiment = {
        "version": "1.0.0",
        "title": "EC2 outage",
        "description": "Killing an EC2 instance",
        "configuration": {
            "aws_region": "ap-south-1"
        },
        "force": "True",
        "method": [
            {
                "type": "action",
                "name": "stop-instance",
                "provider": {
                    "type": "python",
                    "module": "chaosaws.ec2.actions",
                    "func": "stop_instances",
                    "arguments": {
                        "instance_ids": [data.get("instance_ids")]
                        # "az": "ap-south-1a"
                    }
                },
                "pauses": {
                    "after": 10
                }
            }
        ]
    }
    with open("start_ec2.py", "w") as f:
        f.writelines("\nfrom chaoslib.experiment import run_experiment")
        f.writelines("\nstart_experiment="+str(start_experiment))
        f.writelines("\nrun_experiment(start_experiment)")
    # return ["aws ec2 start-instances --instance-ids ", data.get("instance_ids")]
    subprocess.run(["aws ec2 start-instances --instance-ids " + data.get("instance_ids")], shell=True)
    return make_response({"message": "done"}), 200

@microservice_failure_bp.route('/stop', methods=['POST'])
def stop():
    data = request.json
    stop_experiment = {
        "version": "1.0.0",
        "title": "EC2 outage",
        "description": "Killing an EC2 instance",
        "configuration": {
            "aws_region": "ap-south-1"
        },
        "force": "True",
        "method": [
            {
                "type": "action",
                "name": "stop-instance",
                "provider": {
                    "type": "python",
                    "module": "chaosaws.ec2.actions",
                    "func": "stop_instances",
                    "arguments": {
                        "instance_ids": [data.get("instance_ids")]
                        # "az": "ap-south-1a"
                    }
                },
                "pauses": {
                    "after": 10
                }
            }
        ]
    }
    with open("stop_ec2.py", "w") as f:
        f.writelines("\nfrom chaoslib.experiment import run_experiment")
        f.writelines("\nstop_experiment="+str(stop_experiment))
        f.writelines("\nrun_experiment(stop_experiment)")
    subprocess.run(["aws ec2 stop-instances --instance-ids ", data.get("instance_ids")], shell=True)
    return make_response({"message": "done"}), 200

@microservice_failure_bp.route('/restart', methods=['POST'])
def restart():
    data = request.json
    restart_experiment = {
        "version": "1.0.0",
        "title": "restart EC2 instance",
        "description": "restart EC2 instance",
        "configuration": {
            "aws_region": "ap-south-1"
        },
        "force": "True",
        "method": [
            {
                "type": "action",
                "name": "restart-instance",
                "provider": {
                    "type": "python",
                    "module": "chaosaws.ec2.actions",
                    "func": "restart_instances",
                    "arguments": {
                        "instance_ids": [data.get("instance_ids")]
                        # "az": "ap-south-1a"
                    }
                },
                "pauses": {
                    "after": 10
                }
            }
        ]
    }
    with open("restart_ec2.py", "w") as f:
        f.writelines("\nfrom chaoslib.experiment import run_experiment")
        f.writelines("\nrestart_experiment="+str(restart_experiment))
        f.writelines("\nrun_experiment(restart_experiment)")
    subprocess.run(["aws ec2 stop-instances --instance-ids ", data.get("instance_ids")], shell=True)
    subprocess.run(["aws ec2 start-instances --instance-ids ", data.get("instance_ids")], shell=True)
    return make_response({"message": "done"}), 200