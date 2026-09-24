from flask import Flask, render_template_string, abort
import sqlite3

app = Flask(__name__)

DB_FILE = "news.db"


HOME_HTML = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Indian Defence News</title>

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

    {% if articles %}

        <div class="articles">

            {% for article in articles %}

                <div class="card">

                    {% if article[2] %}

                        <img
                            class="card-image"
                            src="{{ article[2] }}"
                            alt="{{ article[1] }}"
                        >

                    {% endif %}

                    <div class="card-content">

                        <div class="category">
                            Defence News
                        </div>

                        <h2>
                            {{ article[1] }}
                        </h2>

                        <a
                            class="read-more"
                            href="/article/{{ article[0] }}"
                        >
                            Read Full Article →
                        </a>

                    </div>

                </div>

            {% endfor %}

        </div>

    {% else %}

        <div class="empty">
            No published articles yet.
        </div>

    {% endif %}

</div>


<footer>

    Indian Defence News

</footer>

</body>

</html>
"""


ARTICLE_HTML = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>{{ article[1] }}</title>

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

    <a class="back" href="/">
        ← Back to Latest News
    </a>

    <div class="article-box">

        <div class="category">
            Defence News
        </div>

        <h1>
            {{ article[1] }}
        </h1>

        {% if article[2] %}

            <img
                class="hero-image"
                src="{{ article[2] }}"
                alt="{{ article[1] }}"
            >

        {% endif %}

        <div class="article">

            {% for paragraph in article[3].split('\\n') %}

                {% if paragraph.strip() %}

                    <p>
                        {{ paragraph }}
                    </p>

                {% endif %}

            {% endfor %}

        </div>

        <div class="source">

            Source reference:

            <a
                href="{{ article[4] }}"
                target="_blank"
                rel="noopener noreferrer"
            >
                {{ article[4] }}
            </a>

        </div>

    </div>

</div>

</body>

</html>
"""


def get_articles():

    conn = sqlite3.connect(DB_FILE)

    articles = conn.execute(
        """
        SELECT
            prid,
            ai_title,
            image_url
        FROM articles
        WHERE status = 'AI_REWRITTEN'
        ORDER BY date DESC
        """
    ).fetchall()

    conn.close()

    return articles


def get_article(prid):

    conn = sqlite3.connect(DB_FILE)

    article = conn.execute(
        """
        SELECT
            prid,
            ai_title,
            image_url,
            ai_article,
            source_url
        FROM articles
        WHERE prid = ?
          AND status = 'AI_REWRITTEN'
        """,
        (prid,)
    ).fetchone()

    conn.close()

    return article


@app.route("/")
def home():

    articles = get_articles()

    return render_template_string(
        HOME_HTML,
        articles=articles
    )


@app.route("/article/<prid>")
def article(prid):

    article_data = get_article(prid)

    if not article_data:

        abort(404)

    return render_template_string(
        ARTICLE_HTML,
        article=article_data
    )


if __name__ == "__main__":

    print("=" * 70)
    print("LOCAL DEFENCE NEWS WEBSITE")
    print("=" * 70)
    print()
    print("Homepage:")
    print("http://127.0.0.1:5000")
    print()
    print("Press CTRL+C to stop the server.")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )