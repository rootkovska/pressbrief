import logging
import time
from itertools import chain, islice
from typing import List

import feedparser

from newspaper.news import News


class Newspaper:
    def __init__(self, name: str, rss_feeds: List[str], limit: int) -> None:
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.rss_feeds = rss_feeds
        self.limit = limit

    def extract_news_list(self) -> List[News]:
        self.logger.info(f"Downloading news for {self.name} ...")

        news_list = chain.from_iterable(
            map(
                lambda rss_feed: [
                    self._extract_news(rss_entry)
                    for rss_entry in islice(self._get_today_rss_entries(rss_feed), 0, self.limit)
                ],
                self.rss_feeds,
            )
        )

        self.logger.info("News downloaded")
        return news_list

    def _get_today_rss_entries(self, rss_feed: str) -> List[feedparser.FeedParserDict]:
        rss_entries = feedparser.parse(rss_feed).entries
        return filter(self._is_today_news, rss_entries)

    def _extract_news(self, rss_entry: feedparser.FeedParserDict) -> News:
        title = rss_entry.title
        summary = rss_entry.summary
        url = rss_entry.link
        published_date = (
            rss_entry.published_parsed if hasattr(rss_entry, "published_parsed") else rss_entry.updated_parsed
        )
        author = rss_entry.author if hasattr(rss_entry, "author") else None

        return News(title, summary, url, published_date, author)

    def _is_today_news(self, rss_entry: feedparser.FeedParserDict) -> bool:
        date = (
            rss_entry.published_parsed if hasattr(rss_entry, "published_parsed") else
            rss_entry.updated_parsed if hasattr(rss_entry, "updated_parsed") else None
        )
        return date is not None and date.tm_mday == time.gmtime().tm_mday
