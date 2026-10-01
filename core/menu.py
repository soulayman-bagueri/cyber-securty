from core.ui import (
    GREEN,
    CYAN,
    MAGENTA,
    WHITE,
    RESET,
    item
)


def show_menu():

    print(
        f"{GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}"
    )

    print(
        f"{GREEN}║{RESET}"
        f"{WHITE}{'CYBERFORGE CONTROL CENTER'.center(60)}{RESET}"
        f"{GREEN}║{RESET}"
    )

    print(
        f"{GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}"
    )

    item("01", "NETWORK CENTER", "🌐")
    item("02", "TCP PORT SCANNER", "🔌")
    item("03", "RECON CENTER", "🔎")
    item("04", "WEB SECURITY", "🌍")
    item("05", "SYSTEM CENTER", "🖥")
    item("06", "LOCAL SECURITY AUDIT", "🛡")
    item("07", "REPORT CENTER", "📊")
    item("08", "ABOUT CYBERFORGE", "ℹ")

    print(
        f"{GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}"
    )

    item("00", "EXIT", "×")

    print(
        f"{GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}"
    )
