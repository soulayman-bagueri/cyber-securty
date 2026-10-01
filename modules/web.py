import requests
from urllib.parse import urlparse
from colorama import Fore, Style


SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Permissions-Policy"
]


def web_check():

    target = input(
        Fore.YELLOW +
        "\nURL > " +
        Style.RESET_ALL
    ).strip()

    if not target:
        return

    if not target.startswith(("http://", "https://")):
        target = "https://" + target

    try:

        response = requests.get(
            target,
            timeout=10,
            allow_redirects=True,
            headers={
                "User-Agent":
                "CyberForge-Security-Audit/1.0"
            }
        )

        print(
            Fore.GREEN +
            f"\n[+] Status       : {response.status_code}"
        )

        print(
            Fore.GREEN +
            f"[+] Final URL    : {response.url}"
        )

        print(
            Fore.GREEN +
            f"[+] Server       : "
            f"{response.headers.get('Server', 'Not disclosed')}"
        )

        print(
            Fore.GREEN +
            f"[+] Content-Type : "
            f"{response.headers.get('Content-Type', 'Unknown')}"
        )

        print(Fore.CYAN + "\n[+] SECURITY HEADERS\n")

        for header in SECURITY_HEADERS:

            if header in response.headers:

                print(
                    Fore.GREEN +
                    f"[✓] {header}"
                )

            else:

                print(
                    Fore.YELLOW +
                    f"[!] {header} missing"
                )

        parsed = urlparse(response.url)

        print(Fore.CYAN + "\n[+] TLS / HTTPS")

        if parsed.scheme == "https":

            print(
                Fore.GREEN +
                "[✓] HTTPS enabled"
            )

        else:

            print(
                Fore.YELLOW +
                "[!] Connection is HTTP"
            )

    except requests.RequestException as e:

        print(
            Fore.RED +
            f"[!] Request failed: {e}"
        )


def web_menu():

    while True:

        print("\033c", end="")

        print(Fore.GREEN + """
╔══════════════════════════════════════════════════════════════╗
║                    WEB SECURITY                            ║
╠══════════════════════════════════════════════════════════════╣
║ [1] HTTP/HTTPS Security Check                              ║
║ [0] Back                                                   ║
╚══════════════════════════════════════════════════════════════╝
""" + Style.RESET_ALL)

        c = input(
            Fore.YELLOW +
            "Web > " +
            Style.RESET_ALL
        )

        if c == "1":
            web_check()
            input("\nPress ENTER to continue...")

        elif c == "0":
            return

        else:
            print(Fore.RED + "[!] Invalid option.")
