from subprocess import run
from textwrap import dedent

def mem(worker_count="1", memory="500000", timeout="10s", public_ip="localhost"):
    playbook = dedent(f'''
        ---
        - name: Stress Memory on target host(s)
          hosts: all
          become: yes
          tasks:
            - name: Ensure stress-ng is installed
              apt:
                name: stress-ng
                state: present
                update_cache: yes

            - name: Inject memory stress
              command: stress-ng --vm {worker_count} --vm-bytes {memory} --timeout {timeout}
    ''')
    # memory needs to be an integer (bytes)
    inventory = f'''{public_ip} ansible_user=admin ansible_ssh_private_key_file=~/aws-default.pem'''
    with open("playbook.yml", "w") as f:
        f.write(playbook)
    with open("inventory", "w") as f:
        f.write(inventory)
    run(["ansible-playbook", "-i", "inventory", "playbook.yml"])

# mem(worker_count="2", memory="500000", timeout="10s", public_ip="localhost")