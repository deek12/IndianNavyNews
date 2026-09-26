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


def generate_website():

    log()
    log("=" * 70)
    log("GENERATING STATIC WEBSITE")
    log("=" * 70)
    log()

    result = subprocess.run(
        [sys.executable, "website.py"],
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
            "website.py FAILED "
            f"with exit code {result.returncode}"
        )

        return False

    log("website.py completed successfully.")

    return True


def publish_to_github():

    log()
    log("=" * 70)
    log("PUBLISHING WEBSITE TO GITHUB")
    log("=" * 70)
    log()

    # Stage only the public website and generator.
    # news.db remains local because it is in .gitignore.
    add_result = subprocess.run(
        [
            "git",
            "add",
            "docs",
            "website.py"
        ],
        capture_output=True,
        text=True
    )

    if add_result.stdout:
        log(add_result.stdout)

    if add_result.stderr:
        log("GIT ADD OUTPUT:")
        log(add_result.stderr)

    if add_result.returncode != 0:

        log(
            "git add FAILED "
            f"with exit code {add_result.returncode}"
        )

        return False

    # Check whether there is actually anything new to commit.
    diff_result = subprocess.run(
        [
            "git",
            "diff",
            "--cached",
            "--quiet"
        ],
        capture_output=True,
        text=True
    )

    if diff_result.returncode == 0:

        log("No website changes detected.")
        log("Nothing to commit or push.")

        return True

    if diff_result.returncode != 1:

        log(
            "Unable to check staged Git changes."
        )

        return False

    commit_result = subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "Automatically publish latest defence news"
        ],
        capture_output=True,
        text=True
    )

    if commit_result.stdout:
        log(commit_result.stdout)

    if commit_result.stderr:
        log("GIT COMMIT OUTPUT:")
        log(commit_result.stderr)

    if commit_result.returncode != 0:

        log(
            "git commit FAILED "
            f"with exit code {commit_result.returncode}"
        )

        return False

    push_result = subprocess.run(
        [
            "git",
            "push"
        ],
        capture_output=True,
        text=True
    )

    if push_result.stdout:
        log(push_result.stdout)

    if push_result.stderr:
        log("GIT PUSH OUTPUT:")
        log(push_result.stderr)

    if push_result.returncode != 0:

        log(
            "git push FAILED "
            f"with exit code {push_result.returncode}"
        )

        return False

    log()
    log("WEBSITE SUCCESSFULLY PUBLISHED TO GITHUB.")
    log()

    return True


def main():

    start_time = datetime.now()

    log("=" * 70)
    log("INDIAN DEFENCE NEWS AUTOMATION")
    log("=" * 70)
    log()

    log("START TIME:")
    log(
        start_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    log()

    # ------------------------------------------------------------
    # STEP 1: Discover new PIB articles
    # ------------------------------------------------------------

    if not run_script("pib_monitor.py"):

        log()
        log(
            "Automation stopped during PIB discovery."
        )

        return

    # ------------------------------------------------------------
    # STEP 2: Find public sources and extract content
    # ------------------------------------------------------------

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
            log(
                "Source finder failed."
            )

            break

    # ------------------------------------------------------------
    # STEP 3: Rewrite articles with local Qwen AI
    # ------------------------------------------------------------

    if not run_script("ai_rewriter.py"):

        log()
        log(
            "AI rewriting stage failed."
        )

    # ------------------------------------------------------------
    # STEP 4: Generate static website
    # ------------------------------------------------------------

    if not generate_website():

        log()
        log(
            "Website generation failed."
        )

        database_status()

        return

    # ------------------------------------------------------------
    # STEP 5: Publish website to GitHub Pages
    # ------------------------------------------------------------

    if not publish_to_github():

        log()
        log(
            "GitHub publishing failed."
        )

        database_status()

        return

    # ------------------------------------------------------------
    # STEP 6: Show database status
    # ------------------------------------------------------------

    database_status()

    end_time = datetime.now()

    log()
    log("=" * 70)
    log("AUTOMATION COMPLETE")
    log("=" * 70)

    log("END TIME:")

    log(
        end_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    log("DURATION:")

    log(
        str(
            end_time - start_time
        )
    )

    log()
    log(
        "LIVE WEBSITE:"
    )

    log(
        "https://deek12.github.io/IndianNavyNews/"
    )


if __name__ == "__main__":

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as log_file:

        with redirect_stdout(
            log_file
        ), redirect_stderr(
            log_file
        ):

            main()