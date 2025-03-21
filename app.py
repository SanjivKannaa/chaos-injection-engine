from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__, template_folder="stressng-frontend")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-stress', methods=['POST'])
def run_stress():
    data = request.json
    cpu_cores = data.get("cpu")
    memory_load = data.get("ram")

    if not cpu_cores or not memory_load:
        return jsonify({"message": "Invalid input"}), 400

    stress_command = f"wsl stress-ng --cpu {cpu_cores} --vm 1 --vm-bytes {memory_load}M --timeout 15s"
    os.system(stress_command)


    return jsonify({"message": "Stress test started! Check your Task Manager."})

if __name__ == '__main__':
    app.run(debug=True)
