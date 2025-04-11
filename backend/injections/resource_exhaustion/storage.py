from subprocess import run
from textwrap import dedent

def storage(storage="1", timeout="10s", public_ip="localhost"):
    playbook = dedent(f'''
        ---
        - name: Stress Load Average on target host(s)
          hosts: all
          become: yes
          tasks:
            - name: Ensure stress-ng is installed
              apt:
                name: stress-ng
                state: present
                update_cache: yes

            - name: Inject load average stress
              command: stress-ng --hdd {storage} --timeout {timeout}
    ''')
    # x storage = x workers * 1GB per worker
    inventory = f'''{public_ip} ansible_user=admin ansible_ssh_private_key_file=~/aws-default.pem'''
    with open("playbook.yml", "w") as f:
        f.write(playbook)
    with open("inventory", "w") as f:
        f.write(inventory)
    run(["ansible-playbook", "-i", "inventory", "playbook.yml"])

storage(storage="10", timeout="10s", public_ip="localhost")