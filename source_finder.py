import sqlite3
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from urllib.parse import urljoin

DB_FILE = "news.db"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/153.0.0.0 Safari/537.36"
    )
}


def search_sources(title):
    try:
        return list(
            DDGS().text(
                title,
                max_results=8
            )
        )
    except Exception as e:
        print("SEARCH ERROR:", e)
        return []


def image_score(img, page_url):
    src = img.get("src") or img.get("data-src") or ""
    alt = img.get("alt") or ""

    if not src:
        return -100

    full_url = urljoin(page_url, src)

    text = (full_url + " " + alt).lower()

    score = 0

    bad_words = [
        "logo",
        "facebook",
        "twitter",
        "instagram",
        "youtube",
        "whatsapp",
        "telegram",
        "linkedin",
        "icon",
        "avatar",
        "author",
        "play-store",
        "playstore",
        "likeus",
        "share",
        "mail",
        "menu",
        "search",
        "banner",
        "advertisement",
        "ad-",
    ]

    for word in bad_words:
        if word in text:
            score -= 50

    good_words = [
        "navy",
        "india",
        "sri-lanka",
        "slinex",
        "ship",
        "exercise",
        "defence",
        "defense",
        "military",
        "warship",
        "ins-",
    ]

    for word in good_words:
        if word in text:
            score += 15

    width = img.get("width")
    height = img.get("height")

    try:
        if width:
            width = int(str(width).replace("px", ""))

            if width >= 500:
                score += 20
            elif width < 200:
                score -= 30

    except:
        pass

    try:
        if height:
            height = int(str(height).replace("px", ""))

            if height >= 300:
                score += 20
            elif height < 100:
                score -= 30

    except:
        pass

    if any(
        extension in full_url.lower()
        for extension in [".jpg", ".jpeg", ".png", ".webp"]
    ):
        score += 5

    return score


def find_best_image(soup, page_url):
    candidates = []

    for img in soup.find_all("img"):

        score = image_score(
            img,
            page_url
        )

        if score <= 0:
            continue

        src = img.get("src") or img.get("data-src") or ""

        full_url = urljoin(
            page_url,
            src
        )

        alt = img.get("alt") or ""

        candidates.append({
            "score": score,
            "url": full_url,
            "alt": alt
        })

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    if not candidates:
        return "", ""

    return (
        candidates[0]["url"],
        candidates[0]["alt"]
    )


def clean_article_text(text):
    unwanted_phrases = [
        "-- Advertisement --",
        "- Advertisement -",
        "Previous article",
        "Next article",
        "More articles",
        "Latest article",
        "Related articles",
        "Related Posts",
        "Related posts",
        "Team BharatShakti",
    ]

    for phrase in unwanted_phrases:
        text = text.replace(
            phrase,
            " "
        )

    text = " ".join(
        text.split()
    )

    return text


def extract_article(url):
    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        page_title = ""

        if soup.title:
            page_title = soup.title.get_text(
                " ",
                strip=True
            )

        # Remove elements that are normally
        # not part of the article.
        for tag in soup([
            "script",
            "style",
            "noscript",
            "nav",
            "footer",
            "header",
            "aside",
            "form",
            "iframe"
        ]):
            tag.decompose()

        # First try the standard article element.
        article = soup.find("article")

        # Then try main content.
        if not article:
            article = soup.find("main")

        # Then try common article-content classes.
        if not article:

            article = soup.find(
                class_=lambda x:
                x and any(
                    word in str(x).lower()
                    for word in [
                        "article-content",
                        "article-body",
                        "entry-content",
                        "post-content",
                        "story-content",
                        "content-area"
                    ]
                )
            )

        if article:

            text = article.get_text(
                " ",
                strip=True
            )

        else:

            text = soup.get_text(
                " ",
                strip=True
            )

        text = clean_article_text(
            text
        )

        if len(text) < 1000:
            return None

        image_url, image_alt = find_best_image(
            soup,
            url
        )

        return {
            "title": page_title,
            "text": text,
            "image_url": image_url,
            "image_alt": image_alt
        }

    except Exception as e:

        print(
            "EXTRACTION ERROR:",
            e
        )

        return None


def save_source(prid, source_url, data):

    conn = sqlite3.connect(
        DB_FILE
    )

    conn.execute(
        """
        UPDATE articles
        SET source_url = ?,
            source_title = ?,
            source_text = ?,
            image_url = ?,
            image_alt = ?,
            status = 'CONTENT_FOUND'
        WHERE prid = ?
        """,
        (
            source_url,
            data["title"],
            data["text"],
            data["image_url"],
            data["image_alt"],
            prid
        )
    )

    conn.commit()
    conn.close()


def main():

    print("=" * 70)
    print("AUTOMATIC WEB SOURCE FINDER")
    print("=" * 70)
    print()

    conn = sqlite3.connect(
        DB_FILE
    )

    article = conn.execute(
        """
        SELECT prid, title, url
        FROM articles
        WHERE status = 'DISCOVERED'
        ORDER BY date DESC
        LIMIT 1
        """
    ).fetchone()

    conn.close()

    if not article:

        print(
            "No DISCOVERED articles found."
        )

        return

    prid, title, pib_url = article

    print("PIB TITLE:")
    print(title)
    print()

    print("Searching web...")

    results = search_sources(
        title
    )

    print(
        "SEARCH RESULTS:",
        len(results)
    )

    print()

    for number, result in enumerate(
        results,
        1
    ):

        source_title = result.get(
            "title",
            ""
        )

        source_url = result.get(
            "href",
            ""
        )

        if not source_url:
            continue

        print("-" * 70)

        print(
            "SOURCE:",
            number
        )

        print(
            "TITLE:",
            source_title
        )

        print(
            "URL:",
            source_url
        )

        print(
            "Extracting..."
        )

        data = extract_article(
            source_url
        )

        if not data:

            print(
                "FAILED: No usable article text"
            )

            continue

        print(
            "TEXT LENGTH:",
            len(data["text"])
        )

        print(
            "IMAGE URL:",
            data["image_url"]
        )

        print(
            "IMAGE ALT:",
            data["image_alt"]
        )

        if not data["image_url"]:

            print(
                "No suitable image. "
                "Trying next source..."
            )

            continue

        save_source(
            prid,
            source_url,
            data
        )

        print()
        print("=" * 70)
        print("SUCCESS")
        print("=" * 70)

        print(
            "STATUS: CONTENT_FOUND"
        )

        print(
            "SOURCE:",
            source_url
        )

        print(
            "IMAGE:",
            data["image_url"]
        )

        return

    print()
    print("=" * 70)
    print("NO USABLE SOURCE FOUND")
    print("=" * 70)


if __name__ == "__main__":
    main()