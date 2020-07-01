import logging
import time
from base64 import b64encode
from typing import List

from yattag import Doc

from exporter.styles import html_style
from newspaper.news import News
from newspaper.newspaper import Newspaper
from qr.qrcoder import QRCoder


class HTMLExporter:
    def __init__(self, url2qrcode: bool) -> None:
        self.logger = logging.getLogger(__name__)
        self.doc = Doc()
        self.url2qrcode = url2qrcode
        self.qrcoder = QRCoder(box_size=5, border=0)

    def as_string(self, newspapers: List[Newspaper], title: str, subtitle: str) -> str:
        self.logger.info("Generating HTML ...")

        tag = self.doc.tag
        text = self.doc.text

        with tag("html"):
            with tag("head"):
                self.doc.asis(html_style)
            with tag("body"):
                with tag("div", klass="title"):
                    text(title)
                with tag("div", klass="subtitle"):
                    text(subtitle)
                for newspaper in newspapers:
                    self._newspaper2html(newspaper)

        html = self.doc.getvalue()

        self.logger.info("HTML generated")
        return html

    def _newspaper2html(self, newspaper: Newspaper) -> None:
        tag = self.doc.tag
        text = self.doc.text

        with tag("div", klass="newspaper"):
            with tag("div", klass="newspaper-name"):
                text(newspaper.name)
            with tag("div", klass="newspaper-info"):
                text(f"{len(newspaper.rss_feeds)} RSS feeds included")
            with tag("div", klass="news-list"):
                for news in newspaper.extract_news_list():
                    self._news2html(news)

    def _news2html(self, news: News) -> None:
        tag = self.doc.tag
        stag = self.doc.stag
        text = self.doc.text

        with tag("div", klass="news-box"):
            with tag("div", klass="news-content"):
                with tag("div", klass="news-text"):
                    with tag("div", klass="news-title"):
                        text(news.title)
                    text(news.summary)
                    if not self.url2qrcode:
                        text(f" ⟶ {news.url}")
                if self.url2qrcode:
                    with tag("div", klass="news-qrcode"):
                        inline_svg = self.qrcoder.generate_inline_svg(news.url)
                        self._inline_svg2data_uri(inline_svg)
            with tag("div", klass="news-info"):
                with tag("div", klass="news-author"):
                    text(news.author)
                with tag("div", klass="news-date"):
                    text(news.published_date)

    def _inline_svg2data_uri(self, inline_svg: str) -> None:
        self.doc.stag("img", src=f"data:image/svg+xml;charset=utf-8;base64,{b64encode(inline_svg).decode()}")
