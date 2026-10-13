import os
import sys
import sqlite3
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'campus_maintenance.db')


def print_table(rows, headers):
    """Print tabular data cleanly in the terminal."""
    if not rows:
        print("  (Table is empty)")
        return

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    divider = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_str = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"

    print(divider)
    print(header_str)
    print(divider)
    for row in rows:
        row_str = "| " + " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row)) + " |"
        print(row_str)
    print(divider)


def show_local_db():
    if not os.path.exists(DB_PATH):
        print(f"[!] Local database file not found at: {DB_PATH}")
        return

    print("================================================================================")
    print(f"SMART CAMPUS MAINTENANCE SYSTEM - SQLITE 3 DATABASE VIEWER")
    print(f"Database File: {DB_PATH}")
    print("================================================================================\n")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall() if t[0] != 'sqlite_sequence']
    print(f"Tables in Database: {', '.join(tables)}\n")

    for table in tables:
        print(f"--- Table: {table} ---")
        cursor.execute(f"PRAGMA table_info({table});")
        headers = [col[1] for col in cursor.fetchall()]

        cursor.execute(f"SELECT * FROM {table};")
        rows = cursor.fetchall()
        print(f"Total Rows: {len(rows)}")
        print_table(rows, headers)
        print()

    conn.close()


def show_docker_db():
    print("================================================================================")
    print(f"DOCKER CONTAINER PERSISTENT DATABASE (campus_maintenance_data)")
    print("================================================================================\n")
    cmd = [
        "docker", "exec", "campus-maintenance-ansible",
        "python", "-c",
        "import sqlite3; conn = sqlite3.connect('data/campus_maintenance.db'); cursor = conn.cursor(); "
        "cursor.execute('PRAGMA table_info(maintenance_requests);'); headers = [c[1] for c in cursor.fetchall()]; "
        "cursor.execute('SELECT * FROM maintenance_requests;'); rows = cursor.fetchall(); "
        "print('HEADERS:' + ','.join(headers)); "
        "for r in rows: print('ROW:' + ' | '.join(str(x) for x in r))"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            lines = res.stdout.strip().splitlines()
            headers = []
            rows = []
            for line in lines:
                if line.startswith("HEADERS:"):
                    headers = line.replace("HEADERS:", "").split(",")
                elif line.startswith("ROW:"):
                    rows.append(line.replace("ROW:", "").split(" | "))
            print(f"Total Rows in Docker Container: {len(rows)}")
            print_table(rows, headers)
        else:
            print("  (Container 'campus-maintenance-ansible' is not currently active)")
    except Exception as e:
        print(f"  (Could not query Docker container: {e})")


def main():
    show_local_db()
    if "--docker" in sys.argv:
        show_docker_db()


if __name__ == '__main__':
    main()
