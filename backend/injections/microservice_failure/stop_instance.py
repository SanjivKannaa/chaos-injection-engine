from chaoslib.experiment import run_experiment
from chaosaws.ec2.actions import stop_instance

# Define a chaos experiment
experiment = {
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
                    "instance_ids": [""]
                    # "az": "ap-south-1a"
                }
            },
            "pauses": {
                "after": 10
            }
        }
    ]
}

# Run the experiment
run_experiment(experiment)
