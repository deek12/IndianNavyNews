import subprocess
import sys
import sqlite3
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr


DB_FILE = "news.db"
LOG_FILE = "automation.log"


def log(message=""):
    print(message)


def run_script(script_name):

    log()
    log("=" * 70)
    log(f"RUNNING: {script_name}")
    log("=" * 70)
    log()

    result = subprocess.run(
        [sys.executable, script_name],
        capture_output=True,
        text=True
    )

    if result.stdout:
        log(result.stdout)

    if result.stderr:
        log("ERROR OUTPUT:")
        log(result.stderr)

    if result.returncode != 0:

        log(
            f"{script_name} FAILED "
            f"with exit code {result.returncode}"
        )

        return False

    log(
        f"{script_name} completed successfully."
    )

    return True


def database_status():

    conn = sqlite3.connect(DB_FILE)

    rows = conn.execute(
        """
        SELECT status, COUNT(*)
        FROM articles
        GROUP BY status
        ORDER BY status
        """
    ).fetchall()

    conn.close()

    log()
    log("=" * 70)
    log("DATABASE STATUS")
    log("=" * 70)

    for status, count in rows:
        log(f"{status}: {count}")


def main():

    start_time = datetime.now()

    log("=" * 70)
    log("INDIAN DEFENCE NEWS AUTOMATION")
    log("=" * 70)
    log()

    log(
        "START TIME:",
    )
    log(
        start_time.strftime("%Y-%m-%d %H:%M:%S")
    )

    log()

    # Step 1:
    # Discover new PIB articles.
    if not run_script("pib_monitor.py"):

        log()
        log("Automation stopped during PIB discovery.")
        return

    # Step 2:
    # Find public web sources and extract content.
    while True:

        conn = sqlite3.connect(DB_FILE)

        article = conn.execute(
            """
            SELECT prid
            FROM articles
            WHERE status = 'DISCOVERED'
            ORDER BY date DESC
            LIMIT 1
            """
        ).fetchone()

        conn.close()

        if not article:
            break

        if not run_script("source_finder.py"):

            log()
            log("Source finder failed.")
            break

    # Step 3:
    # Rewrite all available source articles with local AI.
    if not run_script("ai_rewriter.py"):

        log()
        log("AI rewriting stage failed.")

    database_status()

    end_time = datetime.now()

    log()
    log("=" * 70)
    log("AUTOMATION COMPLETE")
    log("=" * 70)

    log(
        "END TIME:",
    )
    log(
        end_time.strftime("%Y-%m-%d %H:%M:%S")
    )

    log(
        "DURATION:",
    )
    log(
        str(end_time - start_time)
    )


if __name__ == "__main__":

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as log_file:

        with redirect_stdout(log_file), redirect_stderr(log_file):

            main()