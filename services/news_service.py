#!/usr/bin/env python3
"""
News Service - Hacker News API integration.
Fetches top stories with rate limiting, caching, and proper error handling.

Usage:
    service = NewsService()
    news_items = service.fetch_and_get_news(max_items=10)
    service.display_news(news_items)
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Optional, List, Any

import requests
from requests.exceptions import HTTPError, Timeout, RequestException

from .service import BaseService
from data.models import NewsItem
from config import Config


class NewsService(BaseService):
    """
    Service for fetching and displaying Hacker News top stories.
    
    Handles:
    - HTTP requests to Hacker News API
    - Rate limiting (429 responses) with exponential backoff
    - 404 errors (removed stories)
    - File-based caching with configurable duration
    - Retries with configurable attempts and delay
    
    Configuration:
    - retry_attempts: Number of retry attempts (default: 3)
    - retry_delay: Base delay between retries in seconds (default: 5)
    - cache_duration: Cache expiration in seconds (default: 3600, i.e., 1 hour)
    - cache_file: Path to cache file (default: config.DATA_CACHE_FILE)
    - max_count: Maximum number of stories to fetch (default: 5)
    """

    def __init__(self, config=None):
        super().__init__("NewsService", config)
        
        # Helper to handle both Config class (attribute access) and dict (dict access)
        def _get_val(key, default):
            if config is None:
                return default
            if hasattr(config, key):
                v = getattr(config, key)
                return v if v is not None else default
            return self.config.get(key, default) if isinstance(self.config, dict) else default
        
        self._api_url = _get_val("HNEWS_API_URL", "https://hacker-news.firebaseio.com/v0")
        self._top_stories_path = f"{self._api_url}/{_get_val('TOP_STORY_PATH', '/topstories.json')}"
        self._newstory_path = f"{self._api_url}/{_get_val('NEWSTORY_PATH', '/item/')}"
        self._max_count = min(_get_val("MAX_NEWS_COUNT", 10), _get_val("MAX_NEWS_ITEMS", 10))
        self._cache_file = _get_val("DATA_CACHE_FILE", "/Users/amoghb/.openclaw/workspace/news_cache.json")
        self._cache_duration = _get_val("cache_duration", 3600)
        
        # Retry configuration
        self._retry_attempts = _get_val("RETRY_ATTEMPTS", 3)
        self._retry_delay = _get_val("RETRY_DELAY_SECONDS", 5)
        
        # Initialize cache storage
        self._cache: dict[str, Any] = {}

    def fetch_and_get_news(self, max_items: Optional[int] = None) -> List[NewsItem]:
        """
        Fetch top stories from Hacker News, cache results, and display in terminal.
        
        Args:
            max_items: Maximum number of items to return (defaults to self._max_count)
            
        Returns:
            List of NewsItem objects (may contain fewer items if some stories are removed)
            
        Raises:
            Exception: If unable to fetch any stories after all retries
        """
        if max_items is None:
            max_items = self._max_count
        
        self._log("INFO", f"Fetching top {max_items} stories from Hacker News...")
        
        # Try cache first
        cached_data = self._get_cached_stories(max_items)
        if cached_data:
            self._log("INFO", f"Using cached data (age: {self._calc_cache_age()})")
            return [self._rebuild_news_items(cached_data)]
        
        # Fetch story IDs from API
        story_ids = self._fetch_story_ids(max_items)
        if not story_ids:
            raise Exception("Could not fetch story IDs. Check your internet connection.")
        
        # Fetch details for each story
        news_items = self._fetch_story_details(story_ids)
        
        # Cache the results
        self._cache_stories(news_items)
        
        self._log("INFO", f"Successfully fetched {len(news_items)} stories")
        self.display_news(news_items)
        return news_items

    def _fetch_story_ids(self, count: int) -> List[int]:
        """
        Fetch top story IDs from Hacker News API.
        
        Args:
            count: Number of story IDs to fetch
            
        Returns:
            List of story IDs
        """
        url = f"{self._top_stories_path}?limit={count}"
        data = self._fetch_json(url)
        
        if data is None:
            return []
            
        self._log("INFO", f"Fetched {len(data)} story IDs")
        return data

    def _fetch_story_details(self, story_ids: List[int]) -> List[NewsItem]:
        """
        Fetch detailed information for a list of story IDs.
        
        Args:
            story_ids: List of story IDs to fetch
            
        Returns:
            List of NewsItem objects (excludes failed/removed stories)
        """
        news_items: List[NewsItem] = []
        active_count = 0
        failed_count = 0
        
        for story_id in story_ids:
            details = self._fetch_story_id_details(story_id)
            
            if details is None:
                failed_count += 1
                continue
                
            try:
                item = NewsItem(
                    id=story_id,
                    title=details.get("title", "Untitled"),
                    url=details.get("url", ""),
                    score=details.get("score", 0),
                    by=details.get("by", "anonymous"),
                    time=details.get("time", int(time.time())),
                    desc=details.get("desc", ""),
                    domain=details.get("domain", "hacker-news"),
                )
                news_items.append(item)
                active_count += 1
            except Exception as e:
                self._log("ERROR", f"Failed to parse story {story_id}: {str(e)[:50]}")
                failed_count += 1
        
        self._log("INFO", f"Retrieved {active_count} active stories ({failed_count} failed)")
        return news_items

    def _fetch_json(self, url: str, max_retries: int = None) -> Optional[dict]:
        """
        Fetch JSON data from a URL with retry logic and rate limiting handling.
        
        Args:
            url: URL to fetch
            max_retries: Maximum retry attempts (None for infinite with backoff)
            
        Returns:
            Parsed JSON data or None on failure
        """
        if max_retries is None:
            max_retries = self._retry_attempts
        delay = self._retry_delay
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return response.json()
            except HTTPError as e:
                status_code = e.response.status_code
                
                if status_code == 404:
                    # Story removed - return None for this story
                    return None
                    
                elif status_code == 429:
                    # Rate limited - respect Retry-After header
                    retry_after = int(e.response.headers.get("Retry-After", delay))
                    self._log("WARN", f"Rate limited (429). Waiting {retry_after}s before retry {attempt + 1}...")
                    time.sleep(retry_after)
                    continue
                else:
                    # Other HTTP errors - don't retry
                    self._log("ERROR", f"HTTP {status_code}: {e.response.text[:100]}")
                    return None
                    
            except Timeout:
                if attempt < max_retries - 1:
                    self._log("WARN", f"Request timed out on attempt {attempt + 1}. Retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    self._log("ERROR", "Request timeout. Please check your connection.")
                    return None
                    
            except RequestException as e:
                if attempt < max_retries - 1:
                    self._log("WARN", f"Request error on attempt {attempt + 1}: {str(e)[:50]}. Retrying...")
                    time.sleep(delay)
                    continue
                else:
                    self._log("ERROR", f"Failed to fetch after {max_retries} attempts: {str(e)[:50]}")
                    return None
                    
            except Exception as e:
                self._log("ERROR", f"Unexpected error on attempt {attempt + 1}: {str(e)[:50]}")
                return None
                
            # No retry needed, return successful response
            return response.json()
            
        # Exhausted all retries
        self._log("ERROR", f"All {max_retries} retry attempts failed.")
        return None

    def _fetch_story_id_details(self, story_id: int) -> Optional[dict]:
        """
        Fetch details for a single story ID.
        
        Args:
            story_id: The story ID to fetch
            
        Returns:
            Story details dict or None if removed/not found
        """
        url = f"{self._newstory_path}{story_id}.json"
        data = self._fetch_json(url, max_retries=self._retry_attempts)
        
        if data is None:
            return None
            
        self._log("DEBUG", f"Fetched story {story_id}")
        return data

    def _rebuild_news_items(self, cached_data: dict) -> List[NewsItem]:
        """
        Rebuild NewsItem objects from cached data.
        
        Args:
            cached_data: Cached story details
            
        Returns:
            List of NewsItem objects
        """
        items = []
        for i, data in enumerate(cached_data):
            items.append(NewsItem(
                id=data.get("id"),
                title=data.get("title", "Untitled"),
                url=data.get("url", ""),
                score=data.get("score", 0),
                by=data.get("by", "anonymous"),
                time=data.get("time", int(time.time())),
                desc=data.get("desc", ""),
                domain=data.get("domain", "hacker-news"),
            ))
        return items

    def _cache_stories(self, items: List[NewsItem]):
        """
        Save news items to cache file.
        
        Args:
            items: List of NewsItem objects
        """
        # Create parent directory if needed
        cache_dir = os.path.dirname(self._cache_file)
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            
        # Prepare cache data
        cache_data = {
            "items": [item.to_dict() for item in items],
            "count": len(items),
            "timestamp": time.time(),
        }
        
        # Write to file
        with open(self._cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
            
        self._cache["last_fetch"] = {
            "timestamp": time.time(),
            "count": len(items),
        }
        self.last_call = time.time()
        
        self._log("INFO", f"Cached {len(items)} items to {self._cache_file}")

    def _get_cached_stories(self, max_items: int) -> Optional[List[dict]]:
        """
        Retrieve cached news items.
        
        Args:
            max_items: Maximum number of items to return
            
        Returns:
            List of story dicts if cache is valid, None otherwise
        """
        # Check file exists
        if not os.path.exists(self._cache_file):
            return None
            
        # Check if we already have cached data in memory (from previous calls)
        if "last_fetch" in self._cache:
            cache_age = time.time() - self._cache["last_fetch"]["timestamp"]
            if cache_age < self._cache_duration:
                items = self._cache.get("items", [])
                if len(items) >= max_items:
                    return items[:max_items]
                    
        # Read from file
        try:
            with open(self._cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cache_age = time.time() - data.get("timestamp", 0)
                
                if cache_age < self._cache_duration:
                    return data.get("items", [])
        except json.JSONDecodeError:
            self._log("WARN", "Corrupt cache file. Clearing and refetching.")
        except FileNotFoundError:
            pass
            
        return None

    def fetch_top_stories(self, count: Optional[int] = None) -> List[int]:
        """
        Fetch top story IDs from Hacker News API.
        
        Args:
            count: Number of story IDs to fetch (defaults to self._max_count)
            
        Returns:
            List of story IDs
        """
        if count is None:
            count = self._max_count
            
        url = f"{self._top_stories_path}?limit={count}"
        data = self._fetch_json(url)
        
        if data is None:
            return []
            
        self._log("INFO", f"Fetched {len(data)} story IDs")
        return data
    
    def fetch_story_details(self, story_ids: List[int]) -> List[NewsItem]:
        """
        Fetch detailed information for a list of story IDs.
        
        Args:
            story_ids: List of story IDs
            
        Returns:
            List of NewsItem objects
        """
        news_items: List[NewsItem] = []
        active_count = 0
        failed_count = 0
        
        for story_id in story_ids:
            details = self._fetch_story_id_details(story_id)
            
            if details is None:
                failed_count += 1
                continue
                
            try:
                item = NewsItem(
                    id=story_id,
                    title=details.get("title", "Untitled"),
                    url=details.get("url", ""),
                    score=details.get("score", 0),
                    by=details.get("by", "anonymous"),
                    time=details.get("time", int(time.time())),
                    desc=details.get("desc", ""),
                    domain=details.get("domain", "hacker-news"),
                )
                news_items.append(item)
                active_count += 1
            except Exception as e:
                self._log("ERROR", f"Failed to parse story {story_id}: {str(e)[:50]}")
                failed_count += 1
        
        self._log("INFO", f"Retrieved {active_count} active stories ({failed_count} failed)")
        return news_items
    
    def fetch_top_stories(self, count: Optional[int] = None) -> List[int]:
        """
        Fetch top story IDs from Hacker News API.
        
        Args:
            count: Number of story IDs to fetch (defaults to self._max_count)
            
        Returns:
            List of story IDs
        """
        if count is None:
            count = self._max_count
            
        url = f"{self._top_stories_path}?limit={count}"
        data = self._fetch_json(url)
        
        if data is None:
            return []
            
        self._log("INFO", f"Fetched {len(data)} story IDs")
        return data
    
    def display_news(self, items: List[NewsItem]) -> None:
        """
        Display news items in formatted terminal output.
        
        Args:
            items: List of NewsItem objects to display
        """
        if not items:
            print("\n⚠️  No news available. Please check your connection and try again.")
            return
            
        print("\n" + "=" * 60)
        print("  📰 Latest Hacker News Headlines")
        print("=" * 60)
        print(f"Showing {len(items)} items")
        
        for idx, item in enumerate(items, 1):
            print(f"\n{idx}. {item.title}")
            print(f"   📌 [#{item.id}] {item.title[:60]}..." if len(item.title) > 60 else f"   📌 [#{item.id}] {item.title}")
            print(f"   ⭐ Score: {item.score:,}")
            if item.by and item.by != "anonymous":
                print(f"   👤 Author: {item.by}")
            if item.desc and len(item.desc) <= 150:
                print(f"   📝 {item.desc[:150].replace(chr(10), ' ')}")
            print(f"   🔗 {item.domain or 'hacker-news'}")
            print(f"   🕒 {self._format_timestamp(item.time)}")

    def display_news_batch(self, items: List[NewsItem]) -> None:
        """
        Display news in a compact batch format (one per line).
        
        Args:
            items: List of NewsItem objects to display
        """
        if not items:
            print("\n⚠️  No news available.")
            return
            
        print("\n📰 News Batch:")
        print(f"{'ID'.ljust(5)} | {'Score'.ljust(8)} | {'Title (truncated)'}")
        print("-" * 60)
        
        for item in items[:10]:  # Limit to 10 items for compact view
            title_short = item.title[:40] + "..." if len(item.title) > 40 else item.title
            print(f"{str(item.id).ljust(5)} | {str(item.score).ljust(8)} | {title_short}")

    def _format_timestamp(self, timestamp: int) -> str:
        """
        Format a Unix timestamp into a readable string.
        
        Args:
            timestamp: Unix timestamp in seconds
            
        Returns:
            Formatted timestamp string
        """
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%b %d, %Y at %H:%M")

    def _calc_cache_age(self) -> str:
        """Calculate cache age in a human-readable format."""
        if self.last_call is None:
            return "No cached data"
            
        seconds = time.time() - self.last_call
        if seconds < 60:
            return f"{seconds:.0f}s ago"
        elif seconds < 3600:
            return f"{seconds/60:.0f}m ago"
        elif seconds < 86400:
            return f"{seconds/3600:.0f}h ago"
        else:
            return f"{seconds/86400:.0f}d ago"

    def clear_cache(self) -> None:
        """Clear the news cache file and in-memory cache."""
        if os.path.exists(self._cache_file):
            os.remove(self._cache_file)
            self._log("INFO", f"Cleared cache file: {self._cache_file}")
        self._cache.clear()
        self.last_call = None
