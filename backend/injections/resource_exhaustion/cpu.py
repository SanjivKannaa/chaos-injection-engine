from subprocess import run
from textwrap import dedent

def cpu(cpu_count="1", cpu_load="100", timeout="10s", public_ip="localhost"):
    playbook = dedent(f'''
        ---
        - name: Stress CPU on target host(s)
          hosts: all
          become: yes
          tasks:
            - name: Ensure stress-ng is installed
              apt:
                name: stress-ng
                state: present
                update_cache: yes

            - name: Inject CPU stress
              command: stress-ng --cpu {cpu_count} --cpu-load {cpu_load} --timeout {timeout}
    ''')
    # cpu_count = number of workers = number of cpus
    # cpu load = how much% to load
    # if total number of cores=2, and cpu_count = 4 and cpu_load=50, then both cpu get 2*50=100% load
    inventory = f'''{public_ip} ansible_user=admin ansible_ssh_private_key_file=~/aws-default.pem'''
    with open("playbook.yml", "w") as f:
        f.write(playbook)
    with open("inventory", "w") as f:
        f.write(inventory)
    run(["ansible-playbook", "-i", "inventory", "playbook.yml"])

# cpu(cpu_count="2", cpu_load="50", timeout="10s", public_ip="localhost")