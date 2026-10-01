import os

from core.banner import show_banner
from core.ui import pause, success, error, info, warning


REPORT_DIR = "reports"


def ensure_reports():
    os.makedirs(REPORT_DIR, exist_ok=True)


def get_reports():
    ensure_reports()

    return sorted(
        [
            filename
            for filename in os.listdir(REPORT_DIR)
            if os.path.isfile(os.path.join(REPORT_DIR, filename))
        ]
    )


def list_reports():
    show_banner("reports")

    files = get_reports()

    print()
    print("  [ REPORT FILES ]")
    print("  " + "─" * 55)

    if not files:
        warning("No reports found.")
        pause()
        return

    for index, filename in enumerate(files, 1):
        print(f"  [{index:02}] {filename}")

    print()
    pause()


def view_report():
    show_banner("reports")

    files = get_reports()

    if not files:
        warning("No reports available.")
        pause()
        return

    print()
    print("  [ AVAILABLE REPORTS ]")
    print("  " + "─" * 55)

    for index, filename in enumerate(files, 1):
        print(f"  [{index:02}] {filename}")

    print()

    choice = input("  Report number > ").strip()

    try:
        index = int(choice) - 1
        filename = files[index]
    except (ValueError, IndexError):
        error("Invalid report selection.")
        pause()
        return

    path = os.path.join(REPORT_DIR, filename)

    show_banner("reports")

    print(f"  [ REPORT ] {filename}")
    print("  " + "─" * 65)
    print()

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as file:
            content = file.read()

        if content:
            print(content)
        else:
            info("This report is empty.")

    except Exception as exc:
        error(f"Could not read report: {exc}")

    print()
    pause()


def delete_report():
    show_banner("reports")

    files = get_reports()

    if not files:
        warning("No reports available.")
        pause()
        return

    print()
    print("  [ DELETE REPORT ]")
    print("  " + "─" * 55)

    for index, filename in enumerate(files, 1):
        print(f"  [{index:02}] {filename}")

    print()

    choice = input("  Report number > ").strip()

    try:
        index = int(choice) - 1
        filename = files[index]
    except (ValueError, IndexError):
        error("Invalid report selection.")
        pause()
        return

    confirm = input(
        f"\n  Delete '{filename}'? [y/N] > "
    ).strip().lower()

    if confirm != "y":
        info("Delete cancelled.")
        pause()
        return

    try:
        os.remove(os.path.join(REPORT_DIR, filename))
        success(f"Deleted: {filename}")

    except Exception as exc:
        error(f"Delete failed: {exc}")

    pause()


def clear_reports():
    show_banner("reports")

    files = get_reports()

    if not files:
        warning("Report directory is already empty.")
        pause()
        return

    print()
    print("  [ CLEAR REPORT CENTER ]")
    print("  " + "─" * 55)
    print(f"  Reports found: {len(files)}")
    print()

    confirm = input(
        "  Delete ALL reports? [y/N] > "
    ).strip().lower()

    if confirm != "y":
        info("Operation cancelled.")
        pause()
        return

    deleted = 0

    for filename in files:
        try:
            os.remove(os.path.join(REPORT_DIR, filename))
            deleted += 1
        except OSError:
            pass

    success(f"{deleted} report(s) deleted.")
    pause()


def reports_menu():
    while True:

        # كل دخول إلى Reports ينظف الشاشة
        # ويعرض Banner الخاص بـ Reports فقط
        show_banner("reports")

        print()
        print("  [01] ◆ List Reports")
        print("  [02] ◆ View Report")
        print("  [03] ◆ Delete Report")
        print("  [04] ◆ Clear All Reports")
        print()
        print("  [00] ← Back")
        print()

        choice = input("  Reports > ").strip()

        if choice == "01":
            list_reports()

        elif choice == "02":
            view_report()

        elif choice == "03":
            delete_report()

        elif choice == "04":
            clear_reports()

        elif choice == "00":
            return

        else:
            error("Invalid option.")
            pause()
