import subprocess
import os
import json
from pathlib import Path
from datetime import datetime

REPORT_DIR = Path("reports")


def run_command(command, timeout=15):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }

    except FileNotFoundError:
        return {
            "code": 127,
            "stdout": "",
            "stderr": f"Command not found: {command[0]}"
        }

    except subprocess.TimeoutExpired:
        return {
            "code": 124,
            "stdout": "",
            "stderr": "Command timed out"
        }

    except Exception as e:
        return {
            "code": 1,
            "stdout": "",
            "stderr": str(e)
        }


def save_audit(data):
    REPORT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_file = REPORT_DIR / f"security_audit_{timestamp}.json"
    txt_file = REPORT_DIR / f"security_audit_{timestamp}.txt"

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("CYBERFORGE LOCAL SECURITY AUDIT\n")
        f.write("=" * 70 + "\n\n")

        for key, value in data.items():
            f.write(f"[ {key.upper()} ]\n")
            f.write(str(value))
            f.write("\n\n")

    print("\n[+] Audit reports created:")
    print(f"    {json_file}")
    print(f"    {txt_file}")


def firewall_status():
    print("\n[ FIREWALL STATUS ]")
    print("=" * 70)

    detected = []
    results = {}

    # ---------------------------------------------------------
    # UFW
    # ---------------------------------------------------------

    ufw = run_command(["ufw", "status"])

    if ufw["code"] != 127:

        results["ufw"] = ufw["stdout"] or ufw["stderr"]

        if "Status: active" in ufw["stdout"]:
            detected.append("UFW: ACTIVE")

        elif "Status: inactive" in ufw["stdout"]:
            detected.append("UFW: INSTALLED / INACTIVE")

        else:
            detected.append("UFW: AVAILABLE")

    # ---------------------------------------------------------
    # firewalld
    # ---------------------------------------------------------

    firewall_cmd = run_command(
        ["firewall-cmd", "--state"]
    )

    if firewall_cmd["code"] != 127:

        results["firewalld"] = (
            firewall_cmd["stdout"]
            or firewall_cmd["stderr"]
        )

        if "running" in firewall_cmd["stdout"].lower():
            detected.append("firewalld: ACTIVE")

        else:
            detected.append("firewalld: NOT ACTIVE")

    # ---------------------------------------------------------
    # nftables
    # ---------------------------------------------------------

    nft = run_command(
        ["nft", "list", "ruleset"],
        timeout=15
    )

    if nft["code"] != 127:

        if nft["stdout"]:
            results["nftables"] = nft["stdout"]
            detected.append("nftables: RULESET PRESENT")

        else:
            results["nftables"] = (
                nft["stderr"] or
                "No nftables ruleset returned."
            )

            detected.append("nftables: NO RULESET")

    # ---------------------------------------------------------
    # iptables
    # ---------------------------------------------------------

    iptables = run_command(
        ["iptables", "-S"],
        timeout=15
    )

    if iptables["code"] != 127:

        results["iptables"] = (
            iptables["stdout"]
            or iptables["stderr"]
        )

        if iptables["stdout"]:
            lines = iptables["stdout"].splitlines()

            policy_lines = [
                line for line in lines
                if line.startswith("-P ")
            ]

            if policy_lines:
                detected.append("iptables: AVAILABLE")

                print("\n[IPTABLES POLICIES]")

                for line in policy_lines:
                    print(f"  {line}")

            else:
                detected.append("iptables: AVAILABLE")

    # ---------------------------------------------------------
    # Display
    # ---------------------------------------------------------

    if detected:

        print("\n[+] Firewall technologies detected:\n")

        for item in detected:
            print(f"  • {item}")

    else:

        print("\n[!] No supported firewall manager detected.")

    # ---------------------------------------------------------
    # Details
    # ---------------------------------------------------------

    print("\n" + "-" * 70)
    print("[ DETAILS ]")
    print("-" * 70)

    for name, value in results.items():

        print(f"\n[{name.upper()}]")

        if value:
            print(value[:8000])

        else:
            print("No information available.")

    return {
        "detected": detected,
        "results": results
    }


def listening_ports():
    print("\n[ LISTENING PORTS ]")
    print("=" * 70)

    result = run_command(
        ["ss", "-lntup"],
        timeout=15
    )

    if result["code"] != 0:
        print("[!] Unable to inspect listening ports.")
        print(result["stderr"])
        return ""

    print(result["stdout"])

    return result["stdout"]


def ssh_configuration():
    print("\n[ SSH CONFIGURATION ]")
    print("=" * 70)

    config = Path("/etc/ssh/sshd_config")

    if not config.exists():
        print("[*] OpenSSH server configuration not found.")
        return ""

    interesting = []

    try:

        with open(
            config,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            for line in f:

                stripped = line.strip()

                if not stripped:
                    continue

                if stripped.startswith("#"):
                    continue

                keywords = [
                    "permitrootlogin",
                    "passwordauthentication",
                    "pubkeyauthentication",
                    "port "
                ]

                if any(
                    keyword in stripped.lower()
                    for keyword in keywords
                ):
                    interesting.append(stripped)

    except PermissionError:
        print("[!] Permission denied.")
        return ""

    if interesting:

        for line in interesting:
            print(f"  {line}")

    else:
        print("[*] No explicit SSH settings found.")

    return "\n".join(interesting)


def home_permissions():
    print("\n[ HOME DIRECTORY PERMISSIONS ]")
    print("=" * 70)

    home = Path.home()

    try:

        stat = home.stat()

        mode = oct(stat.st_mode & 0o777)

        print(f"Home : {home}")
        print(f"Mode : {mode}")

        if mode in ("0o777", "0o775"):
            print(
                "[!] Home directory has relatively broad permissions."
            )

        else:
            print("[+] Home directory permissions inspected.")

        return {
            "path": str(home),
            "mode": mode
        }

    except Exception as e:

        print(f"[!] Permission check failed: {e}")
        return {}


def system_services():
    print("\n[ RUNNING SERVICES ]")
    print("=" * 70)

    result = run_command(
        [
            "systemctl",
            "--type=service",
            "--state=running",
            "--no-pager"
        ],
        timeout=15
    )

    if result["code"] != 0:

        print("[!] Unable to query services.")
        print(result["stderr"])

        return ""

    print(result["stdout"])

    return result["stdout"]


def full_audit():

    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                 CYBERFORGE SECURITY AUDIT                  ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    audit = {
        "timestamp": datetime.now().isoformat(),
        "hostname": os.uname().nodename,
        "user": os.getenv("USER", "unknown")
    }

    print("\n[1/5] Checking listening ports...")
    audit["listening_ports"] = listening_ports()

    print("\n[2/5] Checking firewall...")
    audit["firewall"] = firewall_status()

    print("\n[3/5] Checking SSH...")
    audit["ssh_configuration"] = ssh_configuration()

    print("\n[4/5] Checking home permissions...")
    audit["home_permissions"] = home_permissions()

    print("\n[5/5] Checking running services...")
    audit["running_services"] = system_services()

    save_audit(audit)

    print("\n" + "=" * 70)
    print("[+] FULL SECURITY AUDIT COMPLETE")
    print("=" * 70)


def audit_menu():

    while True:

        print("\n")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                 LOCAL SECURITY AUDIT                       ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║  [01] Listening Ports                                      ║")
        print("║  [02] Firewall Status                                      ║")
        print("║  [03] SSH Configuration                                    ║")
        print("║  [04] Home Permissions                                     ║")
        print("║  [05] Running Services                                     ║")
        print("║  [06] FULL SECURITY AUDIT                                  ║")
        print("║  [00] Back                                                 ║")
        print("╚══════════════════════════════════════════════════════════════╝")

        choice = input("\nCyberForge > ").strip()

        if choice == "01":
            listening_ports()

        elif choice == "02":
            firewall_status()

        elif choice == "03":
            ssh_configuration()

        elif choice == "04":
            home_permissions()

        elif choice == "05":
            system_services()

        elif choice == "06":
            full_audit()

        elif choice == "00":
            break

        else:
            print("[!] Invalid option.")
