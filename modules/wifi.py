import subprocess
import shutil
from colorama import Fore, Style


def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            return None

        return result.stdout.strip()

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def check_nmcli():
    if not shutil.which("nmcli"):
        print(Fore.RED + "[!] nmcli is not installed.")
        return False

    return True


def current_connection():
    print(Fore.CYAN + "\n[+] Current Wi-Fi connection\n")

    output = run_command([
        "nmcli",
        "-t",
        "-f",
        "ACTIVE,SSID,SIGNAL,SECURITY",
        "device",
        "wifi"
    ])

    if not output:
        print(Fore.RED + "[!] Unable to read Wi-Fi information.")
        return

    found = False

    for line in output.splitlines():
        parts = line.split(":")

        if len(parts) >= 4 and parts[0] == "yes":
            ssid = parts[1] or "<Hidden>"
            signal = parts[2] or "?"
            security = parts[3] or "OPEN"

            print(Fore.GREEN + f"SSID     : {ssid}")
            print(Fore.GREEN + f"Signal   : {signal}%")
            print(Fore.GREEN + f"Security : {security}")

            found = True
            break

    if not found:
        print(Fore.YELLOW + "[!] No active Wi-Fi connection.")


def scan_networks():
    print(Fore.CYAN + "\n[+] Scanning nearby Wi-Fi networks...\n")

    output = run_command([
        "nmcli",
        "-t",
        "-f",
        "SSID,SIGNAL,SECURITY",
        "device",
        "wifi",
        "list",
        "--rescan",
        "yes"
    ])

    if not output:
        print(Fore.RED + "[!] Wi-Fi scan failed.")
        return

    print(Fore.WHITE + "SSID                          SIGNAL     SECURITY")
    print("------------------------------------------------------------")

    seen = set()

    for line in output.splitlines():
        parts = line.split(":")

        if len(parts) < 3:
            continue

        ssid = parts[0].strip()
        signal = parts[1].strip()
        security = ":".join(parts[2:]).strip()

        if not ssid:
            ssid = "<Hidden>"

        if not security:
            security = "OPEN"

        key = (ssid, signal, security)

        if key in seen:
            continue

        seen.add(key)

        print(
            f"{ssid[:28]:28}  "
            f"{signal:>3}%       "
            f"{security}"
        )


def saved_profiles():
    print(Fore.CYAN + "\n[+] Saved NetworkManager profiles\n")

    output = run_command([
        "nmcli",
        "-t",
        "-f",
        "NAME,TYPE",
        "connection",
        "show"
    ])

    if not output:
        print(Fore.RED + "[!] Unable to read saved profiles.")
        return

    for line in output.splitlines():
        parts = line.split(":", 1)

        if len(parts) == 2:
            name, connection_type = parts

            if connection_type == "802-11-wireless":
                print(Fore.GREEN + f"[Wi-Fi] {name}")


def connect_open_network():
    print(Fore.CYAN + "\n[+] Connect to an OPEN Wi-Fi network\n")

    ssid = input(Fore.YELLOW + "SSID > " + Style.RESET_ALL).strip()

    if not ssid:
        print(Fore.RED + "[!] SSID cannot be empty.")
        return

    print(Fore.CYAN + f"\n[+] Connecting to: {ssid}")

    result = subprocess.run(
        ["nmcli", "device", "wifi", "connect", ssid],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode == 0:
        print(Fore.GREEN + "[✓] Connected successfully.")
    else:
        print(Fore.RED + "[!] Connection failed.")
        if result.stderr:
            print(Fore.YELLOW + result.stderr.strip())


def connect_saved_network():
    print(Fore.CYAN + "\n[+] Connect to a saved Wi-Fi profile\n")

    profile = input(
        Fore.YELLOW + "Profile name > " + Style.RESET_ALL
    ).strip()

    if not profile:
        print(Fore.RED + "[!] Profile name cannot be empty.")
        return

    result = subprocess.run(
        ["nmcli", "connection", "up", "id", profile],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode == 0:
        print(Fore.GREEN + "[✓] Connected successfully.")
    else:
        print(Fore.RED + "[!] Connection failed.")
        if result.stderr:
            print(Fore.YELLOW + result.stderr.strip())


def wifi_menu():
    if not check_nmcli():
        input("\nPress ENTER to continue...")
        return

    while True:
        print("\033c", end="")

        print(Fore.GREEN + r"""
╔══════════════════════════════════════════════╗
║              CYBERFORGE WIFI                ║
╠══════════════════════════════════════════════╣
║  [1] Current connection                     ║
║  [2] Scan nearby networks                   ║
║  [3] Saved Wi-Fi profiles                   ║
║  [4] Connect to OPEN network                ║
║  [5] Connect to saved profile               ║
║  [0] Back                                   ║
╚══════════════════════════════════════════════╝
""" + Style.RESET_ALL)

        choice = input(
            Fore.YELLOW + "WiFi > " + Style.RESET_ALL
        ).strip()

        if choice == "1":
            current_connection()
            input("\nPress ENTER to continue...")

        elif choice == "2":
            scan_networks()
            input("\nPress ENTER to continue...")

        elif choice == "3":
            saved_profiles()
            input("\nPress ENTER to continue...")

        elif choice == "4":
            connect_open_network()
            input("\nPress ENTER to continue...")

        elif choice == "5":
            connect_saved_network()
            input("\nPress ENTER to continue...")

        elif choice == "0":
            break

        else:
            print(Fore.RED + "\n[!] Invalid option.")
            input("\nPress ENTER to continue...")
