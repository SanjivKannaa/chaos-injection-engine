from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, create_refresh_token
from extensions import db
from models import Resources
from argon2 import PasswordHasher

resource_exhaustion_bp = Blueprint('resource_exhaustion', __name__)
ph = PasswordHasher()

@resource_exhaustion_bp.route('/')
def home():
    return render_template('index.html')

@resource_exhaustion_bp.route('/run-stress', methods=['POST'])
def run_stress():
    data = request.json
    cpu_cores = data.get("cpu")
    memory_load = data.get("ram")
    memory_type = data.get("ram_type") # gb, mb, %
    print({
        "message": "Stress test started! Check your Task Manager.",
        "cpu_cores": cpu_cores,
        "memory_load": memory_load,
        "memory_type": memory_type
    })

    if not cpu_cores or not memory_load:
        return jsonify({"message": "Invalid input"}), 400

    stress_command = f"stress-ng --cpu {cpu_cores} --vm 1 --vm-bytes {memory_load}M --timeout 15s"
    os.system(stress_command)


    return {
        "message": "Stress test started! Check your Task Manager.",
        "cpu_cores": cpu_cores,
        "memory_load": memory_load,
        "memory_type": memory_type
    }
