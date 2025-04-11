from chaoslib.experiment import run_experiment
from chaosaws.ec2.actions import restart_instances

# Define a chaos experiment
experiment = {
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
