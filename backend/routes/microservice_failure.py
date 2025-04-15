from flask import Blueprint, request, jsonify, make_response, render_template
from extensions import db
import os
from models import Resources
from chaoslib.experiment import run_experiment
from chaosaws.ec2.actions import restart_instances

microservice_failure_bp = Blueprint('microservice_failure', __name__)

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
                        "instance_ids": data.get("instance_ids")
                        # "az": "ap-south-1a"
                    }
                },
                "pauses": {
                    "after": 10
                }
            }
        ]
    }
    # return stop_experiment
    try:
        run_experiment(stop_experiment)
        return make_response({"message": "done"}), 200
    except Exception as e:
        return make_response({"error": e}), 500

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
                        "instance_ids": data.get("instance_ids")
                        # "az": "ap-south-1a"
                    }
                },
                "pauses": {
                    "after": 10
                }
            }
        ]
    }
    try:
        run_experiment(restart_experiment)
        return make_response({"message": "done"}), 200
    except Exception as e:
        return make_response({"error": e}), 500

