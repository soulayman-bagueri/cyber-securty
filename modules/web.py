import os
import re
import socket
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests

from core.banner import show_banner
from core.ui import (
    GREEN,
    RED,
    WHITE,
    CYAN,
    YELLOW,
    RESET,
    pause,
)

REPORT_DIR = "reports"

SECURITY_HEADERS = {
    "Content-Security-Policy": "CSP",
    "Strict-Transport-Security": "HSTS",
    "X-Content-Type-Options": "X-Content-Type-Options",
    "X-Frame-Options": "X-Frame-Options",
    "Referrer-Policy": "Referrer-Policy",
    "Permissions-Policy": "Permissions-Policy",
    "Cross-Origin-Opener-Policy": "COOP",
    "Cross-Origin-Resource-Policy": "CORP",
    "Cross-Origin-Embedder-Policy": "COEP",
}

USER_AGENT = (
    "CyberForge-WebSecurity/1.0 "
    "(authorized passive security assessment)"
)


def ensure_reports():
    os.makedirs(REPORT_DIR, exist_ok=True)


def save_report(content, target):
    ensure_reports()

    hostname = urlparse(target).hostname or "target"
    hostname = re.sub(r"[^a-zA-Z0-9._-]", "_", hostname)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"web_{hostname}_{timestamp}.txt"
    path = os.path.join(REPORT_DIR, filename)

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

    return path


def normalize_url(value):
    value = value.strip()

    if not value:
        return None

    if not value.startswith(("http://", "https://")):
        value = "https://" + value

    return value


def print_header(title):
    print()
    print(CYAN + f"── {title} " + "─" * max(1, 52 - len(title)) + RESET)


def check_headers(response, report_lines):
    print_header("SECURITY HEADERS")

    present = 0
    missing = 0

    for header, label in SECURITY_HEADERS.items():
        value = response.headers.get(header)

        if value:
            present += 1

            print(
                GREEN
                + f"[✓] {label}"
                + RESET
                + f" : {value[:140]}"
            )

            report_lines.append(f"[PRESENT] {header}: {value}")
        else:
            missing += 1

            print(
                YELLOW
                + f"[!] {label}"
                + RESET
                + " : missing"
            )

            report_lines.append(f"[MISSING] {header}")

    return present, missing


def check_cookies(response, report_lines):
    print_header("COOKIE SECURITY")

    cookies = response.cookies

    if not cookies:
        print(CYAN + "[i] No cookies detected in response." + RESET)
        report_lines.append("No cookies detected.")
        return

    for cookie in cookies:
        secure = getattr(cookie, "secure", False)

        rest = getattr(cookie, "_rest", {}) or {}

        http_only = any(
            key.lower() == "httponly"
            for key in rest.keys()
        )

        same_site = None

        for key, value in rest.items():
            if key.lower() == "samesite":
                same_site = value

        print()
        print(WHITE + f"Cookie: {cookie.name}" + RESET)

        if secure:
            print(GREEN + "  [✓] Secure" + RESET)
        else:
            print(YELLOW + "  [!] Secure flag not detected" + RESET)

        if http_only:
            print(GREEN + "  [✓] HttpOnly" + RESET)
        else:
            print(YELLOW + "  [!] HttpOnly flag not detected" + RESET)

        if same_site:
            print(GREEN + f"  [✓] SameSite={same_site}" + RESET)
        else:
            print(YELLOW + "  [!] SameSite not detected" + RESET)

        report_lines.append(
            f"Cookie: {cookie.name} | "
            f"Secure={secure} | "
            f"HttpOnly={http_only} | "
            f"SameSite={same_site}"
        )


def check_cors(response, report_lines):
    print_header("CORS")

    value = response.headers.get("Access-Control-Allow-Origin")

    if value:
        print(CYAN + f"[i] Access-Control-Allow-Origin: {value}" + RESET)
        report_lines.append(
            f"Access-Control-Allow-Origin: {value}"
        )

        if value == "*":
            print(
                YELLOW
                + "[!] Wildcard CORS policy detected."
                + RESET
            )
            report_lines.append(
                "[WARNING] Wildcard Access-Control-Allow-Origin detected."
            )
    else:
        print(GREEN + "[✓] No CORS wildcard header detected." + RESET)
        report_lines.append(
            "No Access-Control-Allow-Origin header detected."
        )


def check_robots(session, base_url, report_lines):
    print_header("ROBOTS.TXT")

    url = urljoin(base_url, "/robots.txt")

    try:
        response = session.get(
            url,
            timeout=10,
            allow_redirects=True,
        )

        if response.status_code == 200:
            text = response.text[:5000]

            print(
                GREEN
                + f"[✓] robots.txt found ({len(response.text)} bytes)"
                + RESET
            )

            lines = [
                line.strip()
                for line in text.splitlines()
                if line.strip()
            ]

            for line in lines[:12]:
                print(CYAN + f"  {line}" + RESET)

            if len(lines) > 12:
                print(
                    CYAN
                    + f"  ... {len(lines) - 12} more lines"
                    + RESET
                )

            report_lines.append(
                f"robots.txt: FOUND ({len(response.text)} bytes)"
            )

            for line in lines:
                report_lines.append(f"  {line}")

        else:
            print(
                YELLOW
                + f"[!] robots.txt returned HTTP {response.status_code}"
                + RESET
            )

            report_lines.append(
                f"robots.txt: HTTP {response.status_code}"
            )

    except requests.RequestException as exc:
        print(RED + f"[!] robots.txt error: {exc}" + RESET)
        report_lines.append(f"robots.txt error: {exc}")


def check_security_txt(session, base_url, report_lines):
    print_header("SECURITY.TXT")

    url = urljoin(base_url, "/.well-known/security.txt")

    try:
        response = session.get(
            url,
            timeout=10,
            allow_redirects=True,
        )

        if response.status_code == 200:
            print(
                GREEN
                + "[✓] security.txt found"
                + RESET
            )

            text = response.text[:5000]

            for line in text.splitlines()[:15]:
                if line.strip():
                    print(CYAN + f"  {line}" + RESET)

            report_lines.append(
                "security.txt: FOUND"
            )

            report_lines.extend(
                f"  {line}"
                for line in text.splitlines()
                if line.strip()
            )

        else:
            print(
                YELLOW
                + f"[!] security.txt not found "
                f"(HTTP {response.status_code})"
                + RESET
            )

            report_lines.append(
                f"security.txt: HTTP {response.status_code}"
            )

    except requests.RequestException as exc:
        print(RED + f"[!] security.txt error: {exc}" + RESET)
        report_lines.append(f"security.txt error: {exc}")


def dns_information(hostname, report_lines):
    print_header("DNS INFORMATION")

    try:
        addresses = socket.getaddrinfo(
            hostname,
            None,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM,
        )

        unique = sorted(
            {
                item[4][0]
                for item in addresses
                if item[4]
            }
        )

        if unique:
            for address in unique:
                print(GREEN + f"[+] {address}" + RESET)
                report_lines.append(f"DNS: {address}")
        else:
            print(YELLOW + "[!] No addresses resolved." + RESET)
            report_lines.append("DNS: no addresses resolved.")

    except socket.gaierror as exc:
        print(RED + f"[!] DNS resolution failed: {exc}" + RESET)
        report_lines.append(f"DNS resolution failed: {exc}")


def redirect_information(response, report_lines):
    print_header("REDIRECT CHAIN")

    history = response.history

    if not history:
        print(GREEN + "[✓] No HTTP redirects detected." + RESET)
        report_lines.append("Redirects: none")
        return

    for index, item in enumerate(history, start=1):
        location = item.headers.get("Location", "")

        print(
            CYAN
            + f"[{index}] "
            + RESET
            + f"{item.status_code} "
            + f"{item.url} "
            + "-> "
            + f"{location}"
        )

        report_lines.append(
            f"Redirect {index}: "
            f"{item.status_code} {item.url} -> {location}"
        )

    print(
        GREEN
        + f"[+] Final destination: {response.url}"
        + RESET
    )

    report_lines.append(
        f"Final destination: {response.url}"
    )


def calculate_summary(present, missing, response):
    total = present + missing

    if total:
        percentage = round((present / total) * 100)
    else:
        percentage = 0

    https = response.url.lower().startswith("https://")

    return total, percentage, https


def web_check():
    show_banner("web")

    target = input(
        GREEN
        + "\nWeb Target > "
        + RESET
    ).strip()

    url = normalize_url(target)

    if not url:
        print(RED + "\n[!] Invalid URL." + RESET)
        pause()
        return

    parsed = urlparse(url)

    if not parsed.hostname:
        print(RED + "\n[!] Could not parse hostname." + RESET)
        pause()
        return

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8",
        }
    )

    report_lines = []

    started = datetime.now()

    report_lines.append("CYBERFORGE WEB SECURITY REPORT")
    report_lines.append("=" * 70)
    report_lines.append(f"Target: {url}")
    report_lines.append(f"Hostname: {parsed.hostname}")
    report_lines.append(f"Started: {started.isoformat()}")
    report_lines.append("")

    try:
        response = session.get(
            url,
            timeout=15,
            allow_redirects=True,
        )

    except requests.RequestException as exc:
        print(RED + f"\n[!] Request failed: {exc}" + RESET)
        report_lines.append(f"Request failed: {exc}")

        path = save_report(
            "\n".join(report_lines),
            url,
        )

        print(
            CYAN
            + f"\n[i] Report saved: {path}"
            + RESET
        )

        pause()
        return

    print_header("TARGET INFORMATION")

    print(GREEN + f"[+] Status       : {response.status_code}" + RESET)
    print(GREEN + f"[+] Final URL    : {response.url}" + RESET)
    print(GREEN + f"[+] Server       : {response.headers.get('Server', 'Not disclosed')}" + RESET)
    print(GREEN + f"[+] Content-Type : {response.headers.get('Content-Type', 'Unknown')}" + RESET)
    print(GREEN + f"[+] Content Size : {len(response.content)} bytes" + RESET)
    print(GREEN + f"[+] Encoding     : {response.encoding or 'Unknown'}" + RESET)

    report_lines.extend(
        [
            "TARGET INFORMATION",
            f"HTTP Status: {response.status_code}",
            f"Final URL: {response.url}",
            f"Server: {response.headers.get('Server', 'Not disclosed')}",
            f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}",
            f"Content Size: {len(response.content)} bytes",
            f"Encoding: {response.encoding or 'Unknown'}",
            "",
        ]
    )

    print_header("RESPONSE HEADERS")

    for key, value in response.headers.items():
        print(
            WHITE
            + f"{key}: "
            + RESET
            + value[:180]
        )

        report_lines.append(
            f"{key}: {value}"
        )

    redirect_information(response, report_lines)

    report_lines.append("")
    present, missing = check_headers(
        response,
        report_lines,
    )

    check_cookies(
        response,
        report_lines,
    )

    check_cors(
        response,
        report_lines,
    )

    dns_information(
        parsed.hostname,
        report_lines,
    )

    base_url = f"{parsed.scheme}://{parsed.netloc}"

    check_robots(
        session,
        base_url,
        report_lines,
    )

    check_security_txt(
        session,
        base_url,
        report_lines,
    )

    print_header("HTTPS / TLS")

    if response.url.lower().startswith("https://"):
        print(GREEN + "[✓] HTTPS enabled" + RESET)
        report_lines.append("HTTPS: ENABLED")
    else:
        print(RED + "[!] HTTPS not enabled" + RESET)
        report_lines.append("HTTPS: NOT ENABLED")

    if response.url.lower().startswith("https://"):
        print(
            GREEN
            + "[✓] Final connection uses HTTPS"
            + RESET
        )

    total, percentage, https = calculate_summary(
        present,
        missing,
        response,
    )

    print_header("SECURITY SUMMARY")

    print(
        WHITE
        + f"Security headers present : {present}/{total}"
        + RESET
    )

    print(
        WHITE
        + f"Security headers missing : {missing}/{total}"
        + RESET
    )

    print(
        WHITE
        + f"Header coverage          : {percentage}%"
        + RESET
    )

    print(
        GREEN
        + f"HTTPS                    : {'YES' if https else 'NO'}"
        + RESET
    )

    report_lines.extend(
        [
            "",
            "SECURITY SUMMARY",
            f"Security headers present: {present}/{total}",
            f"Security headers missing: {missing}/{total}",
            f"Header coverage: {percentage}%",
            f"HTTPS: {'YES' if https else 'NO'}",
            "",
            "NOTE:",
            "This report performs passive HTTP/HTTPS checks.",
            "It does not attempt exploitation or intrusive testing.",
        ]
    )

    path = save_report(
        "\n".join(report_lines),
        url,
    )

    print_header("REPORT")

    print(
        GREEN
        + "[✓] Full report saved:"
        + RESET
    )

    print(
        CYAN
        + f"    {path}"
        + RESET
    )

    pause()


def web_menu():
    while True:
        show_banner("web")

        print(
            WHITE
            + "01  "
            + CYAN
            + "HTTP/HTTPS SECURITY CHECK"
            + RESET
        )

        print(
            WHITE
            + "02  "
            + CYAN
            + "RESPONSE HEADERS"
            + RESET
        )

        print(
            WHITE
            + "03  "
            + CYAN
            + "DNS INFORMATION"
            + RESET
        )

        print(
            WHITE
            + "04  "
            + CYAN
            + "ROBOTS / SECURITY.TXT"
            + RESET
        )

        print(
            WHITE
            + "00  "
            + RED
            + "BACK"
            + RESET
        )

        choice = input(
            GREEN
            + "\nWeb Security > "
            + RESET
        ).strip()

        if choice == "01":
            web_check()

        elif choice == "02":
            show_banner("web")

            target = input(
                GREEN
                + "\nURL > "
                + RESET
            ).strip()

            url = normalize_url(target)

            if not url:
                print(RED + "\n[!] Invalid URL." + RESET)
                pause()
                continue

            try:
                response = requests.get(
                    url,
                    headers={"User-Agent": USER_AGENT},
                    timeout=15,
                    allow_redirects=True,
                )

                show_banner("web")
                print_header("RESPONSE HEADERS")

                for key, value in response.headers.items():
                    print(
                        CYAN
                        + f"{key}"
                        + RESET
                        + f": {value}"
                    )

            except requests.RequestException as exc:
                print(
                    RED
                    + f"\n[!] Request failed: {exc}"
                    + RESET
                )

            pause()

        elif choice == "03":
            show_banner("web")

            target = input(
                GREEN
                + "\nHostname > "
                + RESET
            ).strip()

            if not target:
                print(RED + "\n[!] Hostname required." + RESET)
                pause()
                continue

            report_lines = []

            dns_information(
                target,
                report_lines,
            )

            pause()

        elif choice == "04":
            show_banner("web")

            target = input(
                GREEN
                + "\nURL > "
                + RESET
            ).strip()

            url = normalize_url(target)

            if not url:
                print(RED + "\n[!] Invalid URL." + RESET)
                pause()
                continue

            session = requests.Session()
            session.headers.update(
                {"User-Agent": USER_AGENT}
            )

            report_lines = []

            check_robots(
                session,
                url,
                report_lines,
            )

            check_security_txt(
                session,
                url,
                report_lines,
            )

            pause()

        elif choice == "00":
            break

        else:
            print(
                RED
                + "\n[!] Invalid option."
                + RESET
            )
            pause()
