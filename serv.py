import subprocess

def get_system_services():
    try:
        output = subprocess.check_output(['service', '--status-all'], universal_newlines=True)
        lines = output.split('\n')
        services = []
        for line in lines:
            if line.startswith(' [ + ]') or line.startswith(' [ - ]'):
                service_name = line.split(']')[1].strip()
                services.append(service_name)
        return services
    except subprocess.CalledProcessError:
        return None

services = get_system_services()
if services is not None:
    print("Список системных сервисов Ubuntu:")
    for service in services:
        print(service)
else:
    print("Не удалось получить список системных сервисов.")