from flask import Blueprint, request, jsonify, make_response, render_template
from extensions import db
import os
from models import Resources

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

resource_exhaustion_bp = Blueprint('resource_exhaustion', __name__)

@resource_exhaustion_bp.route('/cpu', methods=['POST'])
def cpu_ep():
    data = request.json
    cpu_load = data.get("cpu_load")
    timeout = data.get("timeout")
    public_ip = data.get("public_ip")
    try:
        cpu(cpu_load, timeout, public_ip)
        return make_response({
            "message": "done"
        }), 200
    except Exception as e:
        return make_response({
            "error": e
        }), 500

@resource_exhaustion_bp.route('/mem', methods=['POST'])
def mem_ep():
    data = request.json
    cpu_load = data.get("cpu_load")
    timeout = data.get("timeout")
    public_ip = data.get("public_ip")
    try:
        cpu(cpu_load, timeout, public_ip)
        return make_response({
            "message": "done"
        }), 200
    except Exception as e:
        return make_response({
            "error": e
        }), 500

@resource_exhaustion_bp.route('/storage', methods=['POST'])
def storage_ep():
    data = request.json
    storage = data.get("storage")
    timeout = data.get("timeout")
    public_ip = data.get("public_ip")
    try:
        cpu(storage, timeout, public_ip)
        return make_response({
            "message": "done"
        }), 200
    except Exception as e:
        return make_response({
            "error": e
        }), 500
