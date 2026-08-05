import html
import os

import feedparser
import requests
from bs4 import BeautifulSoup


BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


RSS_SOURCES = {
    "🇦🇿 Azərbaycan xəbərləri": [
        "https://azertag.az/rss-all",
        "https://news.google.com/rss/search?q=Azərbaycan+when:1d&hl=az&gl=AZ&ceid=AZ:az",
    ],
    "🌍 Dünya xəbərləri": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://news.google.com/rss/search?q=world+news+when:1d&hl=en-US&gl=US&ceid=US:en",
    ],
}


def clean_text(text):
    soup = BeautifulSoup(text or "", "html.parser")
    return " ".join(soup.get_text(" ").split())


def collect_news(feed_urls, limit=5):
    articles = []
    seen_titles = set()

    for feed_url in feed_urls:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:15]:
            title = clean_text(entry.get("title", ""))
            link = entry.get("link", "")

            if not title or not link:
                continue

            normalized_title = title.lower()

            if normalized_title in seen_titles:
                continue

            seen_titles.add(normalized_title)

            articles.append({
                "title": title,
                "link": link,
            })

    return articles[:limit]


def build_message():
    lines = [
        "<b>📰 Gündəlik səhər xəbər icmalı</b>",
        "",
    ]

    for section_name, feed_urls in RSS_SOURCES.items():
        lines.append(f"<b>{section_name}</b>")

        articles = collect_news(feed_urls)

        if not articles:
            lines.append("Xəbər tapılmadı.")
        else:
            for index, article in enumerate(articles, start=1):
                title = html.escape(article["title"])
                link = html.escape(article["link"], quote=True)

                lines.append(
                    f'{index}. <a href="{link}">{title}</a>'
                )

        lines.append("")

    lines.append(
        "<i>Xəbərlər avtomatik seçilib. Məlumatı əsas mənbədən yoxlamaq tövsiyə olunur.</i>"
    )

    return "\n".join(lines)


def send_message():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": build_message(),
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=30,
    )

    response.raise_for_status()


if __name__ == "__main__":
    send_message()
    print("Xəbərlər Telegram-a göndərildi.")
