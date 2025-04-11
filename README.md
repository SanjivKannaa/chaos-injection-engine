# Chaos Injection Engine

## Contributors

1. Sanjiv Kannaa J (106121116)
2. Sri Vignesh (106121130)
3. M Bhoopesh (106121074)

## File Structure

```
|- backend/
|        |- main.py
|        |- models.py
|        |- extensions.py
|        |- config.py
|        |- routes/
|        |       |- resource_exhaustion.py
|        |       |- microservice_failure.py
|        |       |- network_failure.py
|        |
|        |- injections/
|        |           |- resource_gathering/
|        |           |                   |- main.py
|        |           |
|        |           |- resource_exhaustion/
|        |           |                    |- cpu.py
|        |           |                    |- mem.py
|        |           |                    |- storage.py
|        |           |
|        |           |- microservice_failure/
|        |           |                    |- stop_instance.py
|        |           |                    |- restart_instance.py
|        |           |                    |- az_outage.py
|        |           |
|        |           |- network_failure/
|        |           |                |- ;).py
```

## Schema

```
RESOURCES
resourceId
awsId
publicIP
privateIP
awsName
az
sshKey

```
