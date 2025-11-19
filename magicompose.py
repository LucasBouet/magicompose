import os

class App:
    def __init__(self):
        """Initialize the MagicomPose application with metadata and service management."""
        self.name = "MagicomPose"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "An application for magical docker compose creation cli-like."
        self.license = "MIT"
        self.file = "./docker-compose.yml"

        class Services:
            def __init__(self, file, name):
                self.service = """"""
                self.service_details = {
                    "service": "",
                    "image": "auto",
                    "ports": [],
                    "volumes": [],
                    "environment": {},
                    "depends_on": [],
                    "command": "",
                    "networks": {},
                    "restart": "no"
                }
                self.file = file
                self.name = name

            def add_service(self, service_name):
                """Add a new service to the docker-compose configuration."""
                self.service_details["service"] = service_name

            def print_infos(self):
                """Print the current service details."""
                result = ''
                for key, value in self.service_details.items():
                    result += f"{key}: {value}\n"
                return result

            def set_setting(self, key, value):
                """Set a specific setting for the service."""
                if key in self.service_details:
                    if key == "networks":
                        network, test, ip = value.strip().split(':')
                        self.service_details[key][network] = {
                            "ipv4_address": ip,
                        }
                    else: 
                        if isinstance(self.service_details[key], list):
                            self.service_details[key].append(value)
                        elif isinstance(self.service_details[key], dict):
                            k, v = value.split('=', 1)
                            self.service_details[key][k] = v
                        print(f"Setting {key} updated to {self.service_details[key]}")
                else:
                    print(f"Setting {key} does not exists currently.")

            def export_to_docker_format(self):
                """Export the service details to docker-compose format."""
                self.service += f"  {self.service_details['service']}:\n"
                for key, value in self.service_details.items():
                    if key != "service" and value:
                        if isinstance(value, list):
                            self.service += f"    {key}:\n"
                            for item in value:
                                self.service += f"      - {item}\n"
                        elif isinstance(value, dict):
                            self.service += f"    {key}:\n"
                            for k, v in value.items():
                                self.service += f"      {k}: {v}\n"
                        else:
                            self.service += f"    {key}: {value}\n"
                return self.service

            def help(self, key):
                """Provide help information for a specific setting."""
                help_texts = {
                    "image": "Specifies the Docker image to use for the service. ('$name')",
                    "ports": "Maps ports from the host to the container. ($YourPort:$ContainerPort)",
                    "volumes": "Mounts host paths or named volumes into the container. ($Host_path:$ContainerPath)",
                    "environment": "Sets environment variables for the service. ($KEY=$VALUE)",
                    "depends_on": "Specifies dependencies between services. ($ServiceName)",
                    "command": "Overrides the default command for the container. ($CommandToRun)",
                    "networks": "Configures custom networks for the service. ($NetworkName:setIp:$IP)",
                    "restart": "Defines the restart policy for the service. (no, always, on-failure, unless-stopped)"
                }
                return help_texts.get(key, "No help available for this setting.")
    
            
    
    def loop(self)