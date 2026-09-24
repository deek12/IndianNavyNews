import sqlite3
import requests
import time

DB_FILE = "news.db"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen2.5:3b"


def get_articles():

    conn = sqlite3.connect(DB_FILE)

    articles = conn.execute(
        """
        SELECT prid, title, source_text
        FROM articles
        WHERE status = 'CONTENT_FOUND'
          AND source_text IS NOT NULL
          AND length(source_text) > 500
        ORDER BY date DESC
        """
    ).fetchall()

    conn.close()

    return articles


def rewrite_article(source_text):

    prompt = f"""
You are a professional defence-news editor.

Create a completely original news article from the source material below.

STRICT RULES:

- Do not copy sentences word-for-word.
- Do not invent facts.
- Do not invent people, dates, locations, ships, weapons, numbers or quotations.
- Keep all factual information accurate.
- Use clear professional English.
- Write for a general audience interested in defence and military affairs.
- Create an interesting but factual headline.
- Do not mention the source.
- Do not mention that the article was rewritten.
- Do not use markdown.
- Do not add unsupported conclusions.

Return EXACTLY this format:

HEADLINE:
Your headline here

ARTICLE:
Your complete original article here

SOURCE MATERIAL:
{source_text}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=600
    )

    response.raise_for_status()

    return response.json()["response"]


def parse_result(result):

    headline = ""
    article = ""

    if "HEADLINE:" in result:

        after_headline = result.split(
            "HEADLINE:",
            1
        )[1]

        if "ARTICLE:" in after_headline:

            headline = after_headline.split(
                "ARTICLE:",
                1
            )[0].strip()

            article = after_headline.split(
                "ARTICLE:",
                1
            )[1].strip()

    if not article and "ARTICLE:" in result:

        article = result.split(
            "ARTICLE:",
            1
        )[1].strip()

    if "SOURCE MATERIAL:" in article:

        article = article.split(
            "SOURCE MATERIAL:",
            1
        )[0].strip()

    return headline, article


def save_result(prid, headline, article):

    conn = sqlite3.connect(DB_FILE)

    conn.execute(
        """
        UPDATE articles
        SET ai_title = ?,
            ai_article = ?,
            status = 'AI_REWRITTEN'
        WHERE prid = ?
        """,
        (
            headline,
            article,
            prid
        )
    )

    conn.commit()
    conn.close()


def main():

    print("=" * 70)
    print("LOCAL AI ARTICLE REWRITER")
    print("=" * 70)
    print()

    articles = get_articles()

    if not articles:

        print("No CONTENT_FOUND articles available.")

        return

    print(
        "ARTICLES TO PROCESS:",
        len(articles)
    )

    print()

    successful = 0
    failed = 0

    for number, article in enumerate(
        articles,
        1
    ):

        prid, title, source_text = article

        print("=" * 70)
        print(
            f"ARTICLE {number} OF {len(articles)}"
        )
        print("=" * 70)

        print("PRID:", prid)
        print("SOURCE TITLE:", title)
        print(
            "SOURCE TEXT LENGTH:",
            len(source_text)
        )

        print()
        print("Sending article to Qwen 2.5 3B...")
        print("Please wait...")
        print()

        try:

            result = rewrite_article(
                source_text
            )

            headline, rewritten_article = parse_result(
                result
            )

            if not rewritten_article:

                print(
                    "ERROR: AI returned no usable article."
                )

                failed += 1

                continue

            save_result(
                prid,
                headline,
                rewritten_article
            )

            successful += 1

            print(
                "HEADLINE:",
                headline
            )

            print(
                "ARTICLE LENGTH:",
                len(rewritten_article)
            )

            print(
                "STATUS: AI_REWRITTEN"
            )

        except Exception as e:

            failed += 1

            print(
                "ERROR:",
                e
            )

        print()

        # Small pause between local AI jobs.
        if number < len(articles):

            print(
                "Moving to next article..."
            )

            time.sleep(2)

    print("=" * 70)
    print("AI REWRITING COMPLETE")
    print("=" * 70)

    print(
        "SUCCESSFUL:",
        successful
    )

    print(
        "FAILED:",
        failed
    )


if __name__ == "__main__":
    main()