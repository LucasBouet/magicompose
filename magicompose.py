from pathlib import Path

class App:
    def __init__(self):
        self.name = "MagicomPose"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "An application for magical docker compose creation cli-like."
        self.license = "MIT"
        self.file = Path("./docker-compose.yml")
        self.services = []
        self.networks = []

        # Service class for service configuration/export
        class Service:
            def __init__(self, file, name):
                self.file = file
                self.name = name
                self.service_details = {
                    "image": "auto",
                    "ports": [],
                    "volumes": [],
                    "environment": {},  # dict
                    "depends_on": [],
                    "command": "",
                    "networks": [],  # list of network names
                    "restart": "no"
                }

            def configure_interactive(self, available_networks=None):
                available_networks = available_networks or []
                image = input(f"Image for '{self.name}' (default '{self.service_details['image']}'): ").strip()
                if image:
                    self.service_details["image"] = image

                # Ports
                print("Enter port mappings (host:container). Leave blank to finish.")
                while True:
                    p = input("Port mapping: ").strip()
                    if not p:
                        break
                    self.service_details["ports"].append(p)

                # Volumes
                print("Enter volume mappings (host_path:container_path). Leave blank to finish.")
                while True:
                    v = input("Volume mapping: ").strip()
                    if not v:
                        break
                    self.service_details["volumes"].append(v)

                # Environment variables
                print("Enter environment variables as KEY=VALUE. Leave blank to finish.")
                while True:
                    e = input("Env: ").strip()
                    if not e:
                        break
                    if "=" in e:
                        k, v = e.split("=", 1)
                        self.service_details["environment"][k.strip()] = v.strip()
                    else:
                        print("Invalid format. Use KEY=VALUE.")

                # depends_on
                print("Enter dependent service names. Leave blank to finish.")
                while True:
                    d = input("Depends on service: ").strip()
                    if not d:
                        break
                    self.service_details["depends_on"].append(d)

                # Command
                cmd = input("Command to run (leave blank to skip): ").strip()
                if cmd:
                    self.service_details["command"] = cmd

                # Networks selection
                if available_networks:
                    print("Available networks:", ", ".join(available_networks))
                print("Enter network names to attach this service to. Leave blank to finish.")
                while True:
                    n = input("Network: ").strip()
                    if not n:
                        break
                    self.service_details["networks"].append(n)

                # Restart policy
                restart = input("Restart policy (no, always, on-failure, unless-stopped) [no]: ").strip()
                if restart:
                    self.service_details["restart"] = restart

            def print_infos(self):
                lines = [f"Service '{self.name}':"]
                for k, v in self.service_details.items():
                    lines.append(f"  {k}: {v}")
                return "\n".join(lines)

            def export_to_docker_format(self):
                s = f"  {self.name}:\n"
                # image first
                if self.service_details.get("image"):
                    s += f"    image: {self.service_details['image']}\n"
                # ports
                if self.service_details.get("ports"):
                    s += "    ports:\n"
                    for p in self.service_details["ports"]:
                        s += f"      - \"{p}\"\n"
                # volumes
                if self.service_details.get("volumes"):
                    s += "    volumes:\n"
                    for v in self.service_details["volumes"]:
                        s += f"      - \"{v}\"\n"
                # environment
                if self.service_details.get("environment"):
                    s += "    environment:\n"
                    for k, v in self.service_details["environment"].items():
                        s += f"      {k}: \"{v}\"\n"
                # depends_on
                if self.service_details.get("depends_on"):
                    s += "    depends_on:\n"
                    for d in self.service_details["depends_on"]:
                        s += f"      - {d}\n"
                # command
                if self.service_details.get("command"):
                    s += f"    command: \"{self.service_details['command']}\"\n"
                # networks
                if self.service_details.get("networks"):
                    s += "    networks:\n"
                    for n in self.service_details["networks"]:
                        s += f"      - {n}\n"
                # restart
                if self.service_details.get("restart"):
                    s += f"    restart: {self.service_details['restart']}\n"
                return s

        # Network class for network configuration/export
        class Network:
            def __init__(self, name):
                self.name = name
                self.driver = "bridge"
                self.subnet = ""
                self.gateway = ""

            def configure_interactive(self):
                drv = input(f"Driver for network '{self.name}' (default '{self.driver}'): ").strip()
                if drv:
                    self.driver = drv
                sn = input("Subnet (CIDR) (leave blank to skip): ").strip()
                if sn:
                    self.subnet = sn
                gw = input("Gateway (leave blank to skip): ").strip()
                if gw:
                    self.gateway = gw

            def print_infos(self):
                return f"Network '{self.name}': driver={self.driver}, subnet={self.subnet}, gateway={self.gateway}"

            def export_to_docker_format(self):
                s = f"  {self.name}:\n"
                if self.driver:
                    s += f"    driver: {self.driver}\n"
                # Build ipam config only if we have subnet or gateway, to avoid stray newlines/empty keys
                ipam_entries = []
                if self.subnet:
                    ipam_entries.append(f" subnet: {self.subnet}")
                if self.gateway:
                    ipam_entries.append(f"          gateway: {self.gateway}")
                if ipam_entries:
                    s += "    ipam:\n      config:\n        -"
                    for entry in ipam_entries:
                        s += f"{entry}\n"
                return s

        # expose inner classes
        self.Service = Service
        self.Network = Network

    def export_compose(self):
        # Build YAML content
        out = "version: '3.8'\nservices:\n"
        for svc in self.services:
            out += svc.export_to_docker_format()
        if self.networks:
            out += "networks:\n"
            for net in self.networks:
                out += net.export_to_docker_format()
        # Write to file
        try:
            self.file.write_text(out, encoding="utf-8")
            print(f"docker-compose file written to {self.file.resolve()}")
        except Exception as e:
            print("Error writing file:", e)

    def loop(self):
        print(f"Welcome to {self.name} v{self.version}!")
        while True:
            command = input("Enter command (add_service, show_services, add_network, show_networks, export, exit): ").strip()
            if command == "add_service":
                service_name = input("Enter service name: ").strip()
                if not service_name:
                    print("Service name required.")
                    continue
                svc = self.Service(self.file, service_name)
                svc.configure_interactive(available_networks=[n.name for n in self.networks])
                self.services.append(svc)
                print(f"Service '{service_name}' added.")
            elif command == "show_services":
                if not self.services:
                    print("No services defined.")
                for svc in self.services:
                    print(svc.print_infos())
            elif command == "add_network":
                net_name = input("Enter network name: ").strip()
                if not net_name:
                    print("Network name required.")
                    continue
                net = self.Network(net_name)
                net.configure_interactive()
                self.networks.append(net)
                print(f"Network '{net_name}' added.")
            elif command == "show_networks":
                if not self.networks:
                    print("No networks defined.")
                for net in self.networks:
                    print(net.print_infos())
            elif command == "export":
                self.export_compose()
            elif command == "exit":
                print("Exiting MagicomPose.")
                break
            else:
                print("Unknown command. Please try again.")

if __name__ == "__main__":
    app = App()
    app.loop()