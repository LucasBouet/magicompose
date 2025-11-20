from pathlib import Path
from colorama import init as colorama_init, Fore, Style

# initialize colorama (autoreset to avoid manual resets)
colorama_init(autoreset=True)

class App:
    def __init__(self, path=None):
        self.name = "MagicomPose"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "An application for magical docker compose creation cli-like."
        self.license = "MIT"
        self.file = Path(path)
        self.services = []
        self.networks = []

        # small helpers for colored output / prompts
        def _color(text, color):
            return f"{color}{text}{Style.RESET_ALL}"

        self._color = _color
        self.prompt_color = Fore.CYAN
        self.info_color = Fore.GREEN
        self.warn_color = Fore.YELLOW
        self.err_color = Fore.RED
        self.accent_color = Fore.MAGENTA

        def p_input(prompt_text):
            return input(self._color(prompt_text, self.prompt_color))

        def p_info(text):
            print(self._color(text, self.info_color))

        def p_warn(text):
            print(self._color(text, self.warn_color))

        def p_err(text):
            print(self._color(text, self.err_color))

        def p_accent(text):
            print(self._color(text, self.accent_color))

        self.p_input = p_input
        self.p_info = p_info
        self.p_warn = p_warn
        self.p_err = p_err
        self.p_accent = p_accent

        # Service class for service configuration/export
        class Service:
            def __init__(self, file, name):
                self.file = file
                self.name = name
                self.service_details = {
                    "image": "auto",
                    "container_name": "",   # new: allow explicit container_name
                    "ports": [],
                    "expose": [],           # new: container-only exposed ports
                    "volumes": [],
                    "environment": {},  # dict
                    "depends_on": [],
                    "command": "",
                    "networks": {},  # dict: network_name -> ipv4_address (empty string if none)
                    "restart": "no"
                }
                # app reference will be injected by App when created (svc.app = self_app)
                self.app = None

            def configure_interactive(self, available_networks=None):
                available_networks = available_networks or []
                app = self.app  # local shortcut; required for colored I/O

                image = app.p_input(f"Image for '{self.name}' (default '{self.service_details['image']}'): ").strip()
                if image:
                    self.service_details["image"] = image

                # new: custom container name
                cname = app.p_input("Container name (leave blank to skip): ").strip()
                if cname:
                    self.service_details["container_name"] = cname

                # If image appears to be MySQL, offer quick MySQL env setup
                if "mysql" in self.service_details["image"].lower():
                    app.p_accent("Detected MySQL image. Optionally set MySQL environment variables (leave blank to skip each).")
                    mysql_defaults = {
                        "MYSQL_ROOT_PASSWORD": "rootpassword",
                        "MYSQL_DATABASE": "demo",
                        "MYSQL_USER": "user",
                        "MYSQL_PASSWORD": "password"
                    }
                    for k, suggested in mysql_defaults.items():
                        v = app.p_input(f"{k} (suggested '{suggested}'): ").strip()
                        if v:
                            self.service_details["environment"][k] = v

                # Ports
                app.p_info("Enter port mappings (host:container). Leave blank to finish.")
                while True:
                    p = app.p_input("Port mapping: ").strip()
                    if not p:
                        break
                    self.service_details["ports"].append(p)

                # Expose (container-only ports)
                app.p_info("Enter exposed ports (container-only, e.g. 8080). Leave blank to finish.")
                while True:
                    ex = app.p_input("Expose port: ").strip()
                    if not ex:
                        break
                    self.service_details["expose"].append(ex)

                # Volumes
                app.p_info("Add volumes. Choose type 'bind' for host bind (HOST_PATH -> CONTAINER_PATH) or 'named' for named volume (VOLUME_NAME -> CONTAINER_PATH). Leave type blank to finish.")
                while True:
                    vol_type = app.p_input("Volume type (bind/named, leave blank to finish): ").strip().lower()
                    if not vol_type:
                        break
                    if vol_type not in ("bind", "named"):
                        app.p_warn("Invalid type. Use 'bind' or 'named'.")
                        continue
                    src = app.p_input("Host path (for bind) or volume name (for named): ").strip()
                    if not src:
                        app.p_warn("Source/name required. Skipping this entry.")
                        continue
                    tgt = app.p_input("Container path (e.g. /data): ").strip()
                    if not tgt:
                        app.p_warn("Container path required. Skipping this entry.")
                        continue
                    # store structured volume info
                    self.service_details["volumes"].append({
                        "type": vol_type,
                        "source": src,
                        "target": tgt
                    })

                # Environment variables
                app.p_info("Enter environment variables as KEY=VALUE. Leave blank to finish.")
                while True:
                    e = app.p_input("Env: ").strip()
                    if not e:
                        break
                    if "=" in e:
                        k, v = e.split("=", 1)
                        self.service_details["environment"][k.strip()] = v.strip()
                    else:
                        app.p_warn("Invalid format. Use KEY=VALUE.")

                # depends_on
                app.p_info("Enter dependent service names. Leave blank to finish.")
                while True:
                    d = app.p_input("Depends on service: ").strip()
                    if not d:
                        break
                    self.service_details["depends_on"].append(d)

                # Command
                cmd = app.p_input("Command to run (leave blank to skip): ").strip()
                if cmd:
                    self.service_details["command"] = cmd

                # Networks selection (supports name or name=ipv4_address)
                if available_networks:
                    app.p_accent("Available networks: " + ", ".join(available_networks))
                app.p_info("Enter network names to attach this service to. You can specify an IP with 'name=ipv4_address'. Leave blank to finish.")
                while True:
                    n = app.p_input("Network (or name=ip): ").strip()
                    if not n:
                        break
                    if "=" in n:
                        name, ip = n.split("=", 1)
                        name = name.strip()
                        ip = ip.strip()
                        if name:
                            self.service_details["networks"][name] = ip
                    else:
                        self.service_details["networks"][n] = ""

                # Restart policy
                restart = app.p_input("Restart policy (no, always, on-failure, unless-stopped) [no]: ").strip()
                if restart:
                    self.service_details["restart"] = restart

            def print_infos(self):
                lines = [f"Service '{self.name}':"]
                for k, v in self.service_details.items():
                    if k == "networks":
                        if not v:
                            lines.append(f"  networks: []")
                        else:
                            lines.append("  networks:")
                            for name, ip in v.items():
                                if ip:
                                    lines.append(f"    {name}: ipv4_address={ip}")
                                else:
                                    lines.append(f"    {name}")
                    elif k == "volumes":
                        if not v:
                            lines.append("  volumes: []")
                        else:
                            lines.append("  volumes:")
                            for vol in v:
                                if isinstance(vol, dict):
                                    lines.append(f"    - type={vol.get('type')} source={vol.get('source')} target={vol.get('target')}")
                                else:
                                    # fallback for legacy string entries
                                    lines.append(f"    - {vol}")
                    else:
                        lines.append(f"  {k}: {v}")
                return "\n".join(lines)

            def export_to_docker_format(self):
                s = f"  {self.name}:\n"
                # container_name if provided
                if self.service_details.get("container_name"):
                    s += f"    container_name: {self.service_details['container_name']}\n"
                # image first
                if self.service_details.get("image"):
                    s += f"    image: {self.service_details['image']}\n"
                # ports
                if self.service_details.get("ports"):
                    s += "    ports:\n"
                    for p in self.service_details["ports"]:
                        s += f"      - \"{p}\"\n"
                # expose
                if self.service_details.get("expose"):
                    s += "    expose:\n"
                    for ex in self.service_details["expose"]:
                        s += f"      - \"{ex}\"\n"
                # volumes (service-level)
                if self.service_details.get("volumes"):
                    s += "    volumes:\n"
                    for vol in self.service_details["volumes"]:
                        # support structured dicts and legacy string entries
                        if isinstance(vol, dict):
                            src = vol.get("source")
                            tgt = vol.get("target")
                            # long syntax could be used for bind, but keep short syntax for readability
                            s += f"      - \"{src}:{tgt}\"\n"
                        else:
                            s += f"      - \"{vol}\"\n"
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
                # networks: support list or mapping with ipv4_address
                nets = self.service_details.get("networks", {})
                if nets:
                    # if any network has an IP, export as mapping; otherwise export as list
                    if any(ip for ip in nets.values()):
                        s += "    networks:\n"
                        for name, ip in nets.items():
                            if ip:
                                s += f"      {name}:\n"
                                s += f"        ipv4_address: \"{ip}\"\n"
                            else:
                                # empty mapping for networks without specified IP
                                s += f"      {name}: {{}}\n"
                    else:
                        s += "    networks:\n"
                        for name in nets.keys():
                            s += f"      - {name}\n"
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
                self.app = None  # will be injected

            def configure_interactive(self):
                app = self.app
                drv = app.p_input(f"Driver for network '{self.name}' (default '{self.driver}'): ").strip()
                if drv:
                    self.driver = drv
                sn = app.p_input("Subnet (CIDR) (leave blank to skip): ").strip()
                if sn:
                    self.subnet = sn
                gw = app.p_input("Gateway (leave blank to skip): ").strip()
                if gw:
                    self.gateway = gw

            def print_infos(self):
                return f"Network '{self.name}': driver={self.driver}, subnet={self.subnet}, gateway={self.gateway}"

            def export_to_docker_format(self):
                s = f"  {self.name}:\n"
                if self.driver:
                    s += f"    driver: {self.driver}\n"
                # Build ipam config only if we have subnet or gateway
                if self.subnet or self.gateway:
                    s += "    ipam:\n"
                    s += "      config:\n"
                    s += "        -\n"
                    if self.subnet:
                        s += f"          subnet: {self.subnet}\n"
                    if self.gateway:
                        s += f"          gateway: {self.gateway}\n"
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
        # collect named volumes from services and add top-level volumes section
        named_volumes = set()
        for svc in self.services:
            for vol in svc.service_details.get("volumes", []):
                if isinstance(vol, dict) and vol.get("type") == "named":
                    named_volumes.add(vol.get("source"))
        if named_volumes:
            out += "volumes:\n"
            for name in sorted(named_volumes):
                out += f"  {name}:\n"
        # Write to file
        try:
            self.file.write_text(out, encoding="utf-8")
            self.p_info(f"docker-compose file written to {self.file.resolve()}")
        except Exception as e:
            self.p_err(f"Error writing file: {e}")

    def loop(self):
        self.p_accent(f"Welcome to {self.name} v{self.version}!")
        while True:
            command = self.p_input("Enter command (add_service, show_services, add_network, show_networks, export, exit): ").strip()
            if command == "add_service":
                service_name = self.p_input("Enter service name: ").strip()
                if not service_name:
                    self.p_warn("Service name required.")
                    continue
                svc = self.Service(self.file, service_name)
                # inject app reference so Service can use colored I/O
                svc.app = self
                svc.configure_interactive(available_networks=[n.name for n in self.networks])
                self.services.append(svc)
                self.p_info(f"Service '{service_name}' added.")
            elif command == "show_services":
                if not self.services:
                    self.p_warn("No services defined.")
                for svc in self.services:
                    print(self._color(svc.print_infos(), Fore.WHITE))
            elif command == "add_network":
                net_name = self.p_input("Enter network name: ").strip()
                if not net_name:
                    self.p_warn("Network name required.")
                    continue
                net = self.Network(net_name)
                net.app = self
                net.configure_interactive()
                self.networks.append(net)
                self.p_info(f"Network '{net_name}' added.")
            elif command == "show_networks":
                if not self.networks:
                    self.p_warn("No networks defined.")
                for net in self.networks:
                    print(self._color(net.print_infos(), Fore.WHITE))
            elif command == "export":
                self.export_compose()
            elif command == "exit":
                self.p_info("Exiting MagicomPose.")
                break
            else:
                self.p_warn("Unknown command. Please try again.")

if __name__ == "__main__":
    current_path = str(Path.cwd()) + "/docker-compose.yml"
    app = App(path=current_path)
    app.loop()