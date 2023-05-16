import subprocess
import json

class UbuntuSystemService:
    def get_service_status(self, service_name):
        try:
            output = subprocess.check_output(['service', service_name, 'status'], universal_newlines=True)
            lines = output.split('\n')
            status = {}
            logs = []
            for line in lines:
                if line.startswith('Loaded') or line.startswith('Active') or line.startswith('Docs') or line.startswith('Main PID') or line.startswith('Tasks'):
                    key, value = line.split(':', 1)
                    status[key.strip()] = value.strip()
                elif 'systemd[' in line:
                    logs.append(line.strip())
            status['logs'] = logs
            return json.dumps(status)
        except subprocess.CalledProcessError as e:
            return json.dumps({"error": f"Failed to get status for service '{service_name}': {e}"})

# Пример использования
ubuntu_service = UbuntuSystemService()

service_name = 'nginx'  # Замените на имя сервиса, который вы хотите проверить
service_status = ubuntu_service.get_service_status(service_name)
print(service_status)