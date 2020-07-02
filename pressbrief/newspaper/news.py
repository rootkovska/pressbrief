import html
import time

from pyshorteners import Shortener

from utils.regex_patterns import html_tag_pattern


class News:
    def __init__(self, title: str, summary: str, url: str, published_date: time.struct_time, author: str) -> None:
        self.title = title
        self.summary = self._cleanse(summary)
        self.url = Shortener().tinyurl.short(url)
        self.published_date = time.strftime("%A, %B %e, %H:%M UTC", published_date)
        self.author = author or "N/A"

    def _cleanse(self, text: str) -> str:
        cleansed_text = " ".join(html.unescape(text).split())
        cleansed_text = html_tag_pattern.sub("", cleansed_text)
        cleansed_text = cleansed_text.strip("[]<>")
        cleansed_text = f"{cleansed_text[:1024]} ..." if len(cleansed_text) > 1024 else cleansed_text
        return cleansed_text
