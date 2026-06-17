#!/usr/bin/env python3
"""
Data models blueprint for Weather and News Dashboard.
Defines core data structures used throughout the application.
"""


class NewsItem:
    """
    Represents a single Hacker News story item.
    """
    def __init__(
        self,
        id: int,
        title: str,
        url: str,
        score: int,
        by: str,
        time: int,  # Unix timestamp in seconds
        desc: str | None = None,
        domain: str | None = None,
    ):
        self.id = id
        self.title = title
        self.url = url
        self.score = score
        self.by = by
        self.time = time
        self.desc = desc
        self.domain = domain

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "score": self.score,
            "by": self.by,
            "time": self.time,
            "desc": self.desc,
            "domain": self.domain,
        }

    def is_active(self) -> bool:
        """Check if story is still active (not removed from HN)."""
        return self.url != "-"

    def to_json(self):
        """Convert to JSON-serializable dict."""
        return self.to_dict()

    def __repr__(self):
        return f"NewsItem(id={self.id}, title='{self.title[:30]}...')"
