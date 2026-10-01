import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.ui import (
    banner,
    section,
    pause,
    item,
    success,
    info,
    warning,
    error
)


COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "TELNET",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NETBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MYSQL",
    3389: "RDP",
    5432: "POSTGRESQL",
    5900: "VNC",
    8080: "HTTP-ALT",
    8443: "HTTPS-ALT"
}


def scan_port(host, port):

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    sock.settimeout(0.6)

    try:

        result = sock.connect_ex((host, port))

        return port if result == 0 else None

    finally:

        sock.close()


def scanner():

    banner(
        "TCP PORT SCANNER",
        "CYBERFORGE NETWORK SCANNING ENGINE",
        "🔌"
    )

    target = input("\nTarget IP / Host > ").strip()

    if not target:
        error("Target cannot be empty.")
        pause()
        return

    print()

    print("  Scan mode:")
    print("  [01] Common ports")
    print("  [02] Full TCP range")
    print("  [03] Custom range")

    mode = input("\n┌─[ Scan Mode ]\n└──► ").strip()

    if mode == "01":

        ports = list(COMMON_PORTS.keys())

    elif mode == "02":

        ports = range(1, 65536)

    elif mode == "03":

        try:

            start = int(input("Start port > "))
            end = int(input("End port   > "))

            if start < 1 or end > 65535 or start > end:
                raise ValueError

            ports = range(start, end + 1)

        except ValueError:

            error("Invalid port range.")
            pause()
            return

    else:

        error("Invalid mode.")
        pause()
        return

    try:

        host_ip = socket.gethostbyname(target)

    except socket.gaierror:

        error("Unable to resolve target.")
        pause()
        return

    print()
    info(f"Target : {target}")
    info(f"IP     : {host_ip}")
    info(f"Ports  : {len(ports)}")

    print()
    print("Scanning...")
    print()

    open_ports = []

    with ThreadPoolExecutor(max_workers=100) as executor:

        futures = {
            executor.submit(
                scan_port,
                host_ip,
                port
            ): port
            for port in ports
        }

        for future in as_completed(futures):

            result = future.result()

            if result:

                open_ports.append(result)

                service = COMMON_PORTS.get(
                    result,
                    "UNKNOWN"
                )

                print(
                    f"  {GREEN if False else ''}"
                    f"[OPEN] {result:<6} {service}"
                )

    open_ports.sort()

    print()

    if open_ports:

        success(
            f"Scan completed — {len(open_ports)} open port(s)."
        )

    else:

        info("No open ports found in selected range.")

    pause()


def scanner_menu():

    while True:

        banner(
            "TCP PORT SCANNER",
            "AUTHORIZED NETWORK TESTING",
            "🔌"
        )

        item("01", "Start TCP Scan", "◆")

        print()
        item("00", "Back to Main Menu", "←")

        choice = input(
            "\n┌─[ Scanner ]\n└──► "
        ).strip()

        if choice == "01":
            scanner()

        elif choice == "00":
            return

        else:
            error("Invalid option.")
            pause()
