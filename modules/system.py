import os
import platform
import socket
import subprocess
from colorama import Fore, Style


def run(cmd):
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        return r.stdout.strip()
    except Exception:
        return ""


def system_info():

    print(Fore.CYAN + "\n╔══ SYSTEM INFORMATION ══╗\n")

    print(Fore.GREEN + f"Hostname : {socket.gethostname()}")
    print(Fore.GREEN + f"OS       : {platform.system()}")
    print(Fore.GREEN + f"Release  : {platform.release()}")
    print(Fore.GREEN + f"Machine  : {platform.machine()}")
    print(Fore.GREEN + f"Python   : {platform.python_version()}")

    print(
        Fore.GREEN +
        f"CPU      : {os.cpu_count()} logical CPUs"
    )

    memory = run([
        "bash",
        "-c",
        "free -h | awk '/Mem:/ {print $3 \" / \" $2}'"
    ])

    print(Fore.GREEN + f"Memory   : {memory or 'unknown'}")

    uptime = run([
        "uptime",
        "-p"
    ])

    print(Fore.GREEN + f"Uptime   : {uptime or 'unknown'}")

    print(Fore.CYAN + "\n╚════════════════════════╝")


def processes():

    print(Fore.CYAN + "\n[+] TOP PROCESSES\n")

    output = run([
        "bash",
        "-c",
        "ps aux --sort=-%cpu | head -n 12"
    ])

    print(output)


def connections():

    print(Fore.CYAN + "\n[+] NETWORK CONNECTIONS\n")

    output = run([
        "ss",
        "-tunap"
    ])

    print(output or "[!] No connection data.")


def system_menu():

    while True:

        print("\033c", end="")

        print(Fore.GREEN + """
╔══════════════════════════════════════════════════════════════╗
║                    SYSTEM CENTER                           ║
╠══════════════════════════════════════════════════════════════╣
║ [1] System information                                     ║
║ [2] Running processes                                      ║
║ [3] Network connections                                    ║
║ [0] Back                                                   ║
╚══════════════════════════════════════════════════════════════╝
""" + Style.RESET_ALL)

        c = input(
            Fore.YELLOW +
            "System > " +
            Style.RESET_ALL
        )

        if c == "1":
            system_info()
        elif c == "2":
            processes()
        elif c == "3":
            connections()
        elif c == "0":
            return
        else:
            print(Fore.RED + "[!] Invalid option.")

        input("\nPress ENTER to continue...")
