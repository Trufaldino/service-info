import subprocess
import json
from flask import Flask, render_template, redirect


class UbuntuSystemService:
    def get_service_status(self, service_name):
        try:
            output = subprocess.check_output(['service', service_name, 'status'], universal_newlines=True)
            lines = output.split('\n')
            status = {}
            logs = []
            keys = ['Loaded', 'Active', 'Docs', 'Main PID', 'Tasks']
            for line in lines:
                for key in keys:
                    if key in line:
                        key, value = line.split(':', 1)
                        status[key.strip()] = value.strip()
                        break
                else:
                    if 'systemd[' in line:
                        logs.append(line.strip())
            status['logs'] = logs
            return json.dumps(status)
        except subprocess.CalledProcessError as e:
            return json.dumps({"error": f"Failed to get status for service '{service_name}': {e}"})

    def enable_service(self, service_name):
        try:
            subprocess.check_output(['sudo', 'service', service_name, 'start'])
            return True
        except subprocess.CalledProcessError as e:
            return False

    def disable_service(self, service_name):
        try:
            subprocess.check_output(['sudo', 'service', service_name, 'stop'])
            return True
        except subprocess.CalledProcessError as e:
            return False


app = Flask(__name__)
ubuntu_service = UbuntuSystemService()
service_name = 'nginx'  # Замените на имя сервиса, который вы хотите проверить


@app.route('/')
def index():
    service_status = ubuntu_service.get_service_status(service_name)
    parsed_status = json.loads(service_status)
    logs = parsed_status.get('logs', [])
    return render_template('index.html', service_status=parsed_status, logs=logs)


@app.route('/enable', methods=['POST'])
def enable_service():
    if ubuntu_service.enable_service(service_name):
        return redirect('/')
    else:
        return "Failed to enable the service."


@app.route('/disable', methods=['POST'])
def disable_service():
    if ubuntu_service.disable_service(service_name):
        return redirect('/')
    else:
        return "Failed to disable the service."


if __name__ == '__main__':
    app.run()
