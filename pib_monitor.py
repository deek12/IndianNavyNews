import requests
import json
import sqlite3
from datetime import datetime, timedelta

API_URL = "https://www.pib.gov.in/AdvanceSearch.aspx/SearchRecord"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
}

MINISTRY_ID = "33"
LANG_ID = "1"
REGION_ID = "3"
MODULE_ID = "6"

DB_FILE = "news.db"


def search_pib(start_date, end_date):
    payload = {
        "moduleid": MODULE_ID,
        "ministryId": MINISTRY_ID,
        "text": "",
        "sday": str(start_date.day),
        "smonth": str(start_date.month),
        "syear": str(start_date.year),
        "eday": str(end_date.day),
        "emonth": str(end_date.month),
        "eyear": str(end_date.year),
        "pageindex": 1,
        "pagesize": 100,
        "langid": LANG_ID,
        "regionid": REGION_ID,
    }

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return json.loads(data["d"])


def is_indian_navy(title):
    keywords = [
        "INDIAN NAVY",
        "INS ",
        "NAVAL",
        "INDIAN NAVAL",
        "NEXT GENERATION MISSILE VESSEL",
        "NGMV",
        "SLINEX",
        "MALABAR",
        "VARUNA",
        "MILAN",
        "KONKAN",
        "SAMUDRA",
    ]

    title_upper = title.upper()

    return any(keyword in title_upper for keyword in keywords)


def save_article(item):
    prid = str(item.get("PRID"))
    title = item.get("Press_Title", "")
    date = item.get("Published_Date", "")
    url = f"https://www.pib.gov.in/PressReleseDetail.aspx?PRID={prid}"

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO articles
        (prid, title, date, url)
        VALUES (?, ?, ?, ?)
        """,
        (prid, title, date, url),
    )

    conn.commit()
    conn.close()

    return cursor.rowcount == 1


def main():
    today = datetime.now().date()
    start_date = today - timedelta(days=7)

    print("=" * 70)
    print("INDIAN NAVY NEWS MONITOR")
    print("=" * 70)
    print()
    print("Searching PIB...")
    print(f"Date range: {start_date} to {today}")
    print()

    results = search_pib(start_date, today)

    print("Total Defence press releases:", len(results))
    print()

    navy_results = [
        item
        for item in results
        if is_indian_navy(item.get("Press_Title", ""))
    ]

    print("Potential Indian Navy releases:", len(navy_results))
    print()

    new_count = 0

    for item in navy_results:
        prid = item.get("PRID")
        title = item.get("Press_Title")
        date = item.get("Published_Date")

        url = f"https://www.pib.gov.in/PressReleseDetail.aspx?PRID={prid}"

        is_new = save_article(item)

        print("-" * 70)

        if is_new:
            print("NEW ARTICLE")
            new_count += 1
        else:
            print("ALREADY SAVED")

        print("TITLE:", title)
        print("DATE :", date)
        print("URL  :", url)

    print()
    print("=" * 70)
    print("NEW ARTICLES SAVED:", new_count)
    print("=" * 70)


if __name__ == "__main__":
    main()
