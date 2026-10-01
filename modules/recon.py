import socket
import subprocess
import json
from datetime import datetime
from pathlib import Path

from core.ui import (
    banner,
    pause,
    item,
    success,
    info,
    warning,
    error
)


REPORT_DIR = Path("reports")


def run_command(command, timeout=20):

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return result

    except Exception as e:

        class Result:
            returncode = 1
            stdout = ""
            stderr = str(e)

        return Result()


def save_report(name, data):

    REPORT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    path = REPORT_DIR / f"{name}_{timestamp}.json"

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    success(f"Report saved: {path}")


def dns_lookup():

    banner(
        "DNS LOOKUP",
        "DOMAIN RESOLUTION ENGINE",
        "🔎"
    )

    target = input("\nDomain / Host > ").strip()

    if not target:
        return

    try:

        hostname, aliases, addresses = socket.gethostbyname_ex(
            target
        )

        print()
        print(f"  Hostname : {hostname}")

        print("\n  Addresses:")

        for address in addresses:
            print(f"    └─ {address}")

        save_report(
            "dns_lookup",
            {
                "target": target,
                "hostname": hostname,
                "aliases": aliases,
                "addresses": addresses,
                "timestamp": datetime.now().isoformat()
            }
        )

    except socket.gaierror:

        error("DNS lookup failed.")

    pause()


def reverse_dns():

    banner(
        "REVERSE DNS",
        "IP ADDRESS RESOLUTION",
        "🔄"
    )

    target = input("\nIP Address > ").strip()

    if not target:
        return

    try:

        hostname, aliases, addresses = socket.gethostbyaddr(
            target
        )

        print()
        print(f"  Hostname : {hostname}")

        if aliases:
            print("\n  Aliases:")

            for alias in aliases:
                print(f"    └─ {alias}")

        save_report(
            "reverse_dns",
            {
                "target": target,
                "hostname": hostname,
                "aliases": aliases,
                "addresses": addresses,
                "timestamp": datetime.now().isoformat()
            }
        )

    except socket.herror:

        error("Reverse DNS failed.")

    pause()


def domain_records():

    banner(
        "DNS RECORDS",
        "DOMAIN RECORD INSPECTOR",
        "◆"
    )

    domain = input("\nDomain > ").strip()

    if not domain:
        return

    records = {}

    for record_type in [
        "A",
        "AAAA",
        "MX",
        "NS",
        "TXT"
    ]:

        result = run_command(
            [
                "dig",
                "+short",
                record_type,
                domain
            ]
        )

        values = result.stdout.splitlines()

        records[record_type] = values

        print(f"\n[{record_type}]")

        if values:

            for value in values:
                print(f"  └─ {value}")

        else:

            print("  └─ No result")

    save_report(
        "dns_records",
        {
            "domain": domain,
            "records": records,
            "timestamp": datetime.now().isoformat()
        }
    )

    pause()


def whois_lookup():

    banner(
        "WHOIS",
        "DOMAIN REGISTRATION INFORMATION",
        "◆"
    )

    target = input("\nDomain / IP > ").strip()

    if not target:
        return

    result = run_command(
        ["whois", target],
        timeout=25
    )

    if result.returncode != 0 and not result.stdout:

        error(
            "WHOIS failed. Make sure 'whois' is installed."
        )

    else:

        print()
        print(result.stdout[:12000])

        save_report(
            "whois",
            {
                "target": target,
                "result": result.stdout,
                "timestamp": datetime.now().isoformat()
            }
        )

    pause()


def recon_menu():

    while True:

        banner(
            "RECON CENTER",
            "CYBERFORGE INFORMATION ENGINE",
            "🔎"
        )

        item("01", "DNS Lookup", "◆")
        item("02", "Reverse DNS", "◆")
        item("03", "DNS Records", "◆")
        item("04", "WHOIS", "◆")

        print()
        item("00", "Back to Main Menu", "←")

        choice = input(
            "\n┌─[ Recon ]\n└──► "
        ).strip()

        if choice == "01":
            dns_lookup()

        elif choice == "02":
            reverse_dns()

        elif choice == "03":
            domain_records()

        elif choice == "04":
            whois_lookup()

        elif choice == "00":
            return

        else:
            error("Invalid option.")
            pause()
