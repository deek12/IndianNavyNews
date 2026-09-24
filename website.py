import sqlite3
import os
import html


DB_FILE = "news.db"
SITE_DIR = "docs"


def esc(text):
    return html.escape(text or "")


def get_articles():
    conn = sqlite3.connect(DB_FILE)

    rows = conn.execute(
        """
        SELECT
            prid,
            ai_title,
            image_url,
            ai_article,
            source_url,
            date
        FROM articles
        WHERE status = 'AI_REWRITTEN'
        ORDER BY date DESC
        """
    ).fetchall()

    conn.close()

    return rows


def make_paragraphs(text):

    paragraphs = []

    for paragraph in (text or "").splitlines():

        paragraph = paragraph.strip()

        if paragraph:
            paragraphs.append(
                "<p>" + esc(paragraph) + "</p>"
            )

    return "\n".join(paragraphs)


def create_homepage(articles):

    cards = []

    for article in articles:

        prid = article[0]
        title = article[1] or "Indian Defence News"
        image_url = article[2] or ""

        image_html = ""

        if image_url:

            image_html = """
<img
    class="card-image"
    src="IMAGE_URL"
    alt="ARTICLE_TITLE">
""".replace(
                "IMAGE_URL",
                esc(image_url)
            ).replace(
                "ARTICLE_TITLE",
                esc(title)
            )

        card = """
<div class="card">

    IMAGE

    <div class="card-content">

        <div class="category">
            Defence News
        </div>

        <h2>
            TITLE
        </h2>

        <a
            class="read-more"
            href="article/PRID/">

            Read Full Article →

        </a>

    </div>

</div>
""".replace(
            "IMAGE",
            image_html
        ).replace(
            "TITLE",
            esc(title)
        ).replace(
            "PRID",
            esc(str(prid))
        )

        cards.append(card)

    if cards:

        articles_html = """
<div class="articles">

CARDS

</div>
""".replace(
            "CARDS",
            "\n".join(cards)
        )

    else:

        articles_html = """
<div class="empty">
    No published articles yet.
</div>
"""

    page = """
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0">

<title>
Indian Defence News
</title>

<meta
    name="description"
    content="Latest Indian defence, military and strategic affairs news.">

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f4f4;
    color: #222;
}

header {
    background: #111827;
    color: white;
    padding: 22px 20px;
}

.header-inner {
    max-width: 1100px;
    margin: auto;
}

.site-title {
    margin: 0;
    font-size: 28px;
}

.site-description {
    margin-top: 6px;
    color: #cbd5e1;
    font-size: 14px;
}

.container {
    max-width: 1100px;
    margin: 35px auto;
    padding: 0 20px;
}

.section-title {
    font-size: 26px;
    margin-bottom: 25px;
}

.articles {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(300px, 1fr));
    gap: 25px;
}

.card {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow:
        0 2px 10px rgba(0,0,0,0.08);
}

.card-image {
    width: 100%;
    height: 210px;
    object-fit: cover;
}

.card-content {
    padding: 20px;
}

.category {
    color: #64748b;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}

.card h2 {
    font-size: 21px;
    line-height: 1.35;
    margin: 0 0 15px 0;
}

.read-more {
    display: inline-block;
    color: #2563eb;
    text-decoration: none;
    font-weight: bold;
}

.read-more:hover {
    text-decoration: underline;
}

.empty {
    background: white;
    padding: 30px;
    border-radius: 8px;
}

footer {
    margin-top: 50px;
    padding: 25px;
    background: #111827;
    color: #cbd5e1;
    text-align: center;
    font-size: 13px;
}

</style>

</head>

<body>

<header>

<div class="header-inner">

<h1 class="site-title">
Indian Defence News
</h1>

<div class="site-description">
Defence, military and strategic affairs
</div>

</div>

</header>

<div class="container">

<h2 class="section-title">
Latest News
</h2>

ARTICLES

</div>

<footer>
Indian Defence News
</footer>

</body>

</html>
""".replace(
        "ARTICLES",
        articles_html
    )

    os.makedirs(
        SITE_DIR,
        exist_ok=True
    )

    output_file = os.path.join(
        SITE_DIR,
        "index.html"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(page)

    print(
        "CREATED:",
        output_file
    )


def create_article_page(article):

    prid = article[0]
    title = article[1] or "Indian Defence News"
    image_url = article[2] or ""
    article_text = article[3] or ""
    source_url = article[4] or ""

    article_directory = os.path.join(
        SITE_DIR,
        "article",
        str(prid)
    )

    os.makedirs(
        article_directory,
        exist_ok=True
    )

    image_html = ""

    if image_url:

        image_html = """
<img
    class="hero-image"
    src="IMAGE_URL"
    alt="ARTICLE_TITLE">
""".replace(
            "IMAGE_URL",
            esc(image_url)
        ).replace(
            "ARTICLE_TITLE",
            esc(title)
        )

    article_html = make_paragraphs(
        article_text
    )

    description = article_text[:155]

    page = """
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0">

<title>
ARTICLE_TITLE
</title>

<meta
    name="description"
    content="ARTICLE_DESCRIPTION">

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f4f4;
    color: #222;
}

header {
    background: #111827;
    color: white;
    padding: 22px 20px;
}

.header-inner {
    max-width: 900px;
    margin: auto;
}

.site-title {
    margin: 0;
    font-size: 25px;
}

.container {
    max-width: 900px;
    margin: 40px auto;
    padding: 0 20px;
}

.article-box {
    background: white;
    padding: 30px;
    box-shadow:
        0 2px 10px rgba(0,0,0,0.08);
}

.category {
    color: #64748b;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
}

h1 {
    font-size: 40px;
    line-height: 1.2;
    margin: 0 0 25px 0;
}

.hero-image {
    width: 100%;
    max-height: 550px;
    object-fit: cover;
    margin-bottom: 30px;
}

.article {
    font-size: 19px;
    line-height: 1.8;
}

.article p {
    margin-bottom: 22px;
}

.source {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
    font-size: 13px;
    color: #666;
}

.source a {
    color: #555;
    word-break: break-all;
}

.back {
    display: inline-block;
    margin-bottom: 20px;
    color: #2563eb;
    text-decoration: none;
    font-weight: bold;
}

.back:hover {
    text-decoration: underline;
}

@media (max-width: 600px) {

    h1 {
        font-size: 30px;
    }

    .article-box {
        padding: 20px;
    }

    .article {
        font-size: 17px;
    }

}

</style>

</head>

<body>

<header>

<div class="header-inner">

<h1 class="site-title">
Indian Defence News
</h1>

</div>

</header>

<div class="container">

<a
    class="back"
    href="../../index.html">

    ← Back to Latest News

</a>

<div class="article-box">

<div class="category">
Defence News
</div>

<h1>
ARTICLE_TITLE
</h1>

IMAGE

<div class="article">

ARTICLE_TEXT

</div>

<div class="source">

Source reference:

<a
    href="SOURCE_URL"
    target="_blank"
    rel="noopener noreferrer">

SOURCE_URL

</a>

</div>

</div>

</div>

</body>

</html>
"""

    page = page.replace(
        "ARTICLE_TITLE",
        esc(title)
    )

    page = page.replace(
        "ARTICLE_DESCRIPTION",
        esc(description)
    )

    page = page.replace(
        "IMAGE",
        image_html
    )

    page = page.replace(
        "ARTICLE_TEXT",
        article_html
    )

    page = page.replace(
        "SOURCE_URL",
        esc(source_url)
    )

    output_file = os.path.join(
        article_directory,
        "index.html"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(page)

    print(
        "CREATED:",
        output_file
    )


def main():

    print("=" * 70)
    print("STATIC DEFENCE NEWS WEBSITE GENERATOR")
    print("=" * 70)
    print()

    articles = get_articles()

    print(
        "AI_REWRITTEN ARTICLES:",
        len(articles)
    )

    print()

    if not articles:

        print(
            "No AI_REWRITTEN articles found."
        )

        return

    os.makedirs(
        SITE_DIR,
        exist_ok=True
    )

    for article in articles:

        create_article_page(
            article
        )

    create_homepage(
        articles
    )

    print()
    print("=" * 70)
    print("STATIC WEBSITE GENERATION COMPLETE")
    print("=" * 70)
    print()

    print(
        "Website folder:",
        os.path.abspath(SITE_DIR)
    )

    print()

    print(
        "GitHub Pages URL:"
    )

    print(
        "https://deek12.github.io/IndianNavyNews/"
    )


if __name__ == "__main__":

    main()