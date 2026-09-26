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


def is_indian_defence(title):
    keywords = [
        # Indian Armed Forces
        "INDIAN NAVY",
        "INDIAN NAVAL",
        "NAVAL",
        "INDIAN ARMY",
        "INDIAN AIR FORCE",
        "IAF",
        "ARMY",
        "AIR FORCE",
        "COAST GUARD",
        "INDIAN COAST GUARD",

        # Defence organisations
        "MINISTRY OF DEFENCE",
        "DEFENCE MINISTRY",
        "DEFENCE RESEARCH",
        "DRDO",
        "DEFENCE RESEARCH AND DEVELOPMENT",
        "DEPARTMENT OF DEFENCE",

        # Ships and naval systems
        "INS ",
        "WARSHIP",
        "WARSHIPS",
        "FRIGATE",
        "DESTROYER",
        "CORVETTE",
        "SUBMARINE",
        "AIRCRAFT CARRIER",
        "MISSILE VESSEL",
        "PATROL VESSEL",
        "LANDING SHIP",
        "NEXT GENERATION MISSILE VESSEL",

        # Aircraft
        "FIGHTER AIRCRAFT",
        "FIGHTER JET",
        "MILITARY AIRCRAFT",
        "COMBAT AIRCRAFT",
        "HELICOPTER",
        "HELICOPTERS",
        "TEJAS",
        "RAFALE",
        "SUKHOI",
        "MIRAGE 2000",
        "MIG-29",
        "C-17",
        "C-130J",
        "APACHE",
        "CHINOOK",

        # Missiles and weapons
        "MISSILE",
        "MISSILES",
        "TORPEDO",
        "ROCKET",
        "ROCKETS",
        "WEAPON",
        "WEAPONS",
        "AMMUNITION",
        "AIR DEFENCE",
        "ANTI-AIRCRAFT",
        "ANTI AIRCRAFT",
        "ANTI-AIRFIELD",
        "BRAHMOS",
        "AKASH",
        "AGNI",
        "PRITHVI",
        "ASTRA",
        "PINAKA",

        # Defence procurement / contracts
        "DEFENCE CONTRACT",
        "DEFENCE CONTRACTS",
        "DEFENCE PROCUREMENT",
        "DEFENCE ACQUISITION",
        "MILITARY PROCUREMENT",
        "DEFENCE DEAL",
        "DEFENCE DEALS",
        "CONTRACT WITH",
        "PROCUREMENT",
        "ACQUISITION",
        "ATMANIRBHAR",
        "AATMANIRBHAR",
        "MAKE IN INDIA",

        # Defence exercises / operations
        "MILITARY EXERCISE",
        "MILITARY EXERCISES",
        "DEFENCE EXERCISE",
        "JOINT EXERCISE",
        "JOINT EXERCISES",
        "BILATERAL EXERCISE",
        "MARITIME EXERCISE",
        "WAR EXERCISE",
        "MALABAR",
        "VARUNA",
        "MILAN",
        "SLINEX",
        "KONKAN",
        "SAMUDRA",
        "ADMM-PLUS",

        # Defence technology
        "DEFENCE TECHNOLOGY",
        "MILITARY TECHNOLOGY",
        "DEFENCE SYSTEM",
        "DEFENCE SYSTEMS",
        "SURVEILLANCE SYSTEM",
        "RADAR",
        "ELECTRONIC WARFARE",
        "UNMANNED",
        "UAV",
        "DRONE",
        "DRONES",
        "COMBAT SYSTEM",

        # General defence terminology
        "DEFENCE",
        "DEFENSE",
        "MILITARY",
        "ARMED FORCES",
        "AEROSPACE",
        "SECURITY FORCES",
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
    print("INDIAN DEFENCE NEWS MONITOR")
    print("=" * 70)
    print()
    print("Searching PIB...")
    print(f"Date range: {start_date} to {today}")
    print()

    results = search_pib(start_date, today)

    print("Total Defence press releases:", len(results))
    print()

    defence_results = [
        item
        for item in results
        if is_indian_defence(item.get("Press_Title", ""))
    ]

    print("Potential Indian Defence releases:", len(defence_results))
    print()

    new_count = 0

    for item in defence_results:
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