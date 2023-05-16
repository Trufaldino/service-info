import subprocess

class UbuntuSystemService:
    def __init__(self):
        self.services = self._get_system_services()

    def _get_system_services(self):
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
            return []

    def get_all_services(self):
        return self.services

    def get_service_status(self, service_name):
        try:
            output = subprocess.check_output(['service', service_name, 'status'], universal_newlines=True)
            return output
        except subprocess.CalledProcessError as e:
            return f"Не удалось получить статус для сервиса '{service_name}': {e}"

# Пример использования
ubuntu_service = UbuntuSystemService()
# all_services = ubuntu_service.get_all_services()

# if all_services:
#     print("Список системных сервисов Ubuntu:")
#     for service in all_services:
#         print(service)
# else:
#     print("Не удалось получить список системных сервисов.")

# Получение статусной информации о сервисе
service_name = 'nginx'  # Замените на имя сервиса, который вы хотите проверить
service_status = ubuntu_service.get_service_status(service_name)
print(f"\nСтатус сервиса '{service_name}':")
print(service_status)