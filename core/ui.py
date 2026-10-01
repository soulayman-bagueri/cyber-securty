import os
import shutil
from colorama import Fore, Style


RESET = Style.RESET_ALL

GREEN = Fore.GREEN
CYAN = Fore.CYAN
MAGENTA = Fore.MAGENTA
BLUE = Fore.BLUE
YELLOW = Fore.YELLOW
RED = Fore.RED
WHITE = Fore.WHITE


def clear():
    os.system("clear")


def width():
    return min(shutil.get_terminal_size().columns, 76)


def line(char="═"):
    print(char * width())


def pause():
    input(
        f"\n{YELLOW}└─[ Press ENTER to continue ]{RESET}"
    )


def banner(title, subtitle, icon="◆"):

    clear()

    w = width()

    print()

    print(
        f"{GREEN}╔{'═' * (w - 2)}╗{RESET}"
    )

    print(
        f"{GREEN}║{RESET}"
        f"{CYAN}{title.center(w - 2)}{RESET}"
        f"{GREEN}║{RESET}"
    )

    print(
        f"{GREEN}║{RESET}"
        f"{MAGENTA}{subtitle.center(w - 2)}{RESET}"
        f"{GREEN}║{RESET}"
    )

    print(
        f"{GREEN}╚{'═' * (w - 2)}╝{RESET}"
    )

    print()


def section(title):

    print()
    print(
        f"{CYAN}┌───[ {WHITE}{title}{CYAN} ]"
        f"{'─' * max(1, width() - len(title) - 11)}┐{RESET}"
    )


def footer():

    print()
    line("─")
    print(
        f"{MAGENTA}  CyberForge{RESET}"
        f"{WHITE} // Kali Linux Security Toolkit{RESET}"
    )
    print()


def success(text):
    print(f"{GREEN}[+] {text}{RESET}")


def info(text):
    print(f"{CYAN}[*] {text}{RESET}")


def warning(text):
    print(f"{YELLOW}[!] {text}{RESET}")


def error(text):
    print(f"{RED}[-] {text}{RESET}")


def item(number, text, icon="◆"):

    print(
        f"  {GREEN}[{number}]{RESET} "
        f"{MAGENTA}{icon}{RESET} "
        f"{WHITE}{text}{RESET}"
    )


def status(label, value):

    print(
        f"  {CYAN}{label:<18}{RESET}"
        f"{WHITE}: {value}{RESET}"
    )
