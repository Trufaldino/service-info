import subprocess
import json
from flask import Flask, render_template, redirect
from flask_httpauth import HTTPBasicAuth
import sys
import psutil
import re
import datetime


class UbuntuSystemService:
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.auth = HTTPBasicAuth()
        self.users = {
            "admin": "password"  # Придумайте логин пароль для входа
        }

        @self.auth.verify_password
        def verify_password(username, password):
            if username in self.users and password == self.users[username]:
                return username

    def get_service_status(self, service_name):
        try:
            output = subprocess.check_output(['sudo','service', service_name, 'status'], stderr=subprocess.STDOUT, universal_newlines=True)
            lines = output.split('\n')
            status = {}
            logs = subprocess.check_output(['journalctl', '-u', service_name, '--since', self.start_time.strftime('%Y-%m-%d %H:%M:%S')], universal_newlines=True)
            keys = ['Loaded', 'Active', 'Docs', 'Main PID', 'Tasks']
            for line in lines:
                for key in keys:
                    if key in line:
                        key, value = line.split(':', 1)
                        status[key.strip()] = value.strip()
                        break
            status['logs'] = logs.split('\n')

            main_pid = re.search(r'\d+', status.get('Main PID', '')).group() 
            if main_pid:
                try:
                    process = psutil.Process(int(main_pid))
                    child_pids = process.children(recursive=True)
                    total_cpu_percent = process.cpu_percent(interval=1)
                    memory_sz = process.memory_info().rss
                    for child_pid in child_pids:
                        child_process = psutil.Process(int(child_pid.pid))
                        total_cpu_percent += child_process.cpu_percent(interval=1)
                        memory_sz += child_process.memory_info().rss
                    status['Processor usage'] = f"{total_cpu_percent:.2f}%"
                    status['RAM usage'] = f"{memory_sz / 1024 / 1024:.2f} MB"
                except psutil.NoSuchProcess:
                    status['Processor usage'] = 'N/A'
                    status['RAM usage'] = 'N/A'
            else:
                status['Processor usage'] = 'N/A'
                status['RAM usage'] = 'N/A'

            return json.dumps(status)
        except subprocess.CalledProcessError as e:
            if e.returncode == 3:
                return json.dumps({"status": f"The service '{service_name}' is inactive"})
            else:
                return json.dumps({"error": f"Failed to get status for service '{service_name}': {e}"})

    def start_service(self, service_name):
        try:
            subprocess.check_output(['sudo', 'service', service_name, 'start'])
            return True
        except subprocess.CalledProcessError as e:
            return False

    def stop_service(self, service_name):
        try:
            subprocess.check_output(['sudo', 'service', service_name, 'stop'])
            return True
        except subprocess.CalledProcessError as e:
            return False

    def restart_reload_service(self, service_name):
        try:
            subprocess.check_output(['sudo', 'service', service_name, 'restart'])
            subprocess.check_output(['sudo', 'service', service_name, 'reload'])
            return True
        except subprocess.CalledProcessError as e:
            return False


app = Flask(__name__)
ubuntu_service = UbuntuSystemService()

if len(sys.argv) > 1:
    service_name = sys.argv[1]
else:
    raise ValueError('Please enter a service name as a command-line argument. For example: python3 serv.py nginx')


@app.before_request
@ubuntu_service.auth.login_required
def before_request():
    pass


@app.route('/')
def index():
    service_status = ubuntu_service.get_service_status(service_name)
    parsed_status = json.loads(service_status)
    logs = parsed_status.get('logs', [])
    return render_template('index.html', service_status=parsed_status, logs=logs, service_name=service_name)


@app.route('/start', methods=['POST'])
def enable_service():
    if ubuntu_service.start_service(service_name):
        return redirect('/')
    else:
        return "Failed to start the service."


@app.route('/stop', methods=['POST'])
def disable_service():
    if ubuntu_service.stop_service(service_name):
        return redirect('/')
    else:
        return "Failed to disable the service."


@app.route('/restart_reload', methods=['POST'])
def restart_reload_service():
    if ubuntu_service.restart_reload_service(service_name):
        return redirect('/')
    else:
        return "Failed to restart and reload the service."


if __name__ == '__main__':
    app.run()
