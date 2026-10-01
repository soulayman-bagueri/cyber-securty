from colorama import init, Fore, Style

from core.ui import (
    clear,
    pause,
    success,
    error
)

from core.banner import show_banner
from core.menu import show_menu

from modules.network import network_menu
from modules.scanner import scanner_menu
from modules.recon import recon_menu
from modules.web import web_menu
from modules.system import system_menu
from modules.audit import audit_menu
from modules.reports import reports_menu


init(autoreset=True)


def about():

    clear()

    print(Fore.GREEN + r"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                 ██████╗ ██████╗ ███████╗                    ║
║                ██╔════╝██╔═══██╗██╔════╝                    ║
║                ██║     ██║   ██║█████╗                      ║
║                ██║     ██║   ██║██╔══╝                      ║
║                ╚██████╗╚██████╔╝███████╗                    ║
║                 ╚═════╝ ╚═════╝ ╚══════╝                    ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                  CYBERFORGE INFORMATION                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Version        : 1.0                                       ║
║  Platform       : Kali Linux                                ║
║  Engine         : Python                                    ║
║  Interface      : Terminal                                  ║
║                                                              ║
║  Network visibility                                          ║
║  Local security auditing                                     ║
║  TCP scanning                                                ║
║  DNS reconnaissance                                          ║
║  Web security inspection                                     ║
║  Security reports                                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""" + Style.RESET_ALL)

    pause()


def main():

    while True:

        clear()

        show_banner()
        show_menu()

        choice = input(
            Fore.GREEN +
            "\n┌─[ CyberForge ]\n└──► " +
            Style.RESET_ALL
        ).strip()

        if choice == "01":
            network_menu()

        elif choice == "02":
            scanner_menu()

        elif choice == "03":
            recon_menu()

        elif choice == "04":
            web_menu()

        elif choice == "05":
            system_menu()

        elif choice == "06":
            audit_menu()

        elif choice == "07":
            reports_menu()

        elif choice == "08":
            about()

        elif choice == "00":

            clear()

            print(
                Fore.GREEN +
                "\n[+] CyberForge session terminated.\n" +
                Style.RESET_ALL
            )

            break

        else:

            error("Invalid option.")
            pause()


if __name__ == "__main__":
    main()
