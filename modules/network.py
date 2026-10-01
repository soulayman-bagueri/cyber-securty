import subprocess
import socket

from core.banner import show_banner
from core.ui import pause, item, error, warning


def run(command, timeout=20):

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return result.stdout.strip()

    except Exception as e:

        return f"ERROR: {e}"


def network_info():

    show_banner("network")

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    NETWORK INFORMATION                     ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    try:

        route = run(["ip", "route"])

        interface_name = "Unknown"
        gateway = "Unknown"

        for line in route.splitlines():

            parts = line.split()

            if line.startswith("default"):

                if "dev" in parts:
                    interface_name = parts[
                        parts.index("dev") + 1
                    ]

                if "via" in parts:
                    gateway = parts[
                        parts.index("via") + 1
                    ]

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.connect(("1.1.1.1", 80))

        local_ip = sock.getsockname()[0]

        sock.close()

        print(f"\nInterface : {interface_name}")
        print(f"Local IP  : {local_ip}")
        print(f"Gateway   : {gateway}")

    except Exception as e:

        error(str(e))

    pause()


def interfaces():

    show_banner("network")

    print(run(["ip", "-br", "addr"]))

    pause()


def routes():

    show_banner("network")

    print(run(["ip", "route"]))

    pause()


def current_wifi():

    show_banner("network")

    result = run([
        "nmcli",
        "-f",
        "IN-USE,SSID,BSSID,CHAN,SIGNAL,SECURITY",
        "device",
        "wifi"
    ])

    print(result)

    pause()


def scan_wifi():

    show_banner("network")

    print(run([
        "nmcli",
        "-f",
        "IN-USE,SSID,BSSID,CHAN,SIGNAL,SECURITY",
        "device",
        "wifi",
        "list"
    ]))

    pause()


def saved():

    show_banner("network")

    print(
        run([
            "nmcli",
            "-f",
            "NAME,TYPE,DEVICE",
            "connection",
            "show"
        ])
    )

    pause()


def devices():

    show_banner("network")

    print(run(["ip", "neigh"]))

    pause()


def dns():

    show_banner("network")

    target = input(
        "\nDomain / Host > "
    ).strip()

    if not target:
        return

    try:

        hostname, aliases, addresses = socket.gethostbyname_ex(
            target
        )

        print(f"\nHostname : {hostname}")

        for address in addresses:
            print(f"Address  : {address}")

    except socket.gaierror:

        error("DNS lookup failed.")

    pause()


def network_menu():

    while True:

        show_banner("network")

        item("01", "Network Information", "◆")
        item("02", "Network Interfaces", "◆")
        item("03", "Routing Table", "◆")
        item("04", "Current Wi-Fi", "📡")
        item("05", "Scan Wi-Fi", "📡")
        item("06", "Saved Network Profiles", "◆")
        item("07", "Discover Local Devices", "◆")
        item("08", "DNS Lookup", "🔎")

        print()
        item("00", "Back to Main Menu", "←")

        choice = input(
            "\nNetwork > "
        ).strip()

        if choice == "01":
            network_info()

        elif choice == "02":
            interfaces()

        elif choice == "03":
            routes()

        elif choice == "04":
            current_wifi()

        elif choice == "05":
            scan_wifi()

        elif choice == "06":
            saved()

        elif choice == "07":
            devices()

        elif choice == "08":
            dns()

        elif choice == "00":
            return

        else:
            error("Invalid option.")
            pause()
