#!/usr/bin/env python3
"""
Base service class for the Weather and News Dashboard.
Provides common functionality for all services.
"""


class BaseService:
    """
    Abstract base class for dashboard services.
    Provides common methods for logging, error handling, and caching.
    """

    def __init__(self, name: str, config=None):
        """Initialize the service with its name and optional config."""
        self.name = name
        self.config = config or {}
        self.last_call = None
        self._cache = {}
        # Handle Config class or dict - Config uses attribute access, dict uses .get()
        self._cache_duration = 3600  # default
        if config is not None:
            if hasattr(config, "MAX_CACHE_AGE_SECONDS"):
                self._cache_duration = config.MAX_CACHE_AGE_SECONDS

    def should_refresh(self, now=None) -> bool:
        """Check if cached data should be refreshed based on cache duration."""
        if now is None:
            now = __import__("time").time()
        if self.last_call is None:
            return True
        elapsed = now - self.last_call
        return elapsed > self._cache_duration

    def get_cache_key(self, params: dict):
        """Generate a cache key from parameters (override in subclasses)."""
        return f"{self.name}:{str(sorted(params.items()))}"

    def _log(self, level: str, message: str):
        """Log a message at the specified level."""
        print(f"[{self.name.upper()}] {level}: {message}")

    def log(self, level: str = "INFO", message: str = None):
        """Log a message at the specified level."""
        self._log(level, message or "")

    def cache(self, data: dict):
        """Cache data for later reuse."""
        from datetime import datetime
        key = data.get("_cache_key", f"{self.name}:{datetime.now().isoformat()}")
        self._cache[key] = {"data": data, "timestamp": datetime.now().timestamp()}

    def get_cached(self, key: str) -> dict | None:
        """Retrieve cached data if it exists and hasn't expired."""
        cached = self._cache.get(key)
        if cached:
            age = __import__("time").time() - cached["timestamp"]
            if age < self._cache_duration:
                return cached["data"]
            else:
                self._cache.pop(key, None)
        return None

    def clear_cache(self, key: str = None):
        """Clear cache for a specific key or all cached data."""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()

    def _handle_http_error(self, e: Exception, url: str = "Unknown"):
        """Handle HTTP errors with retry logic."""
        # Handle Config class or dict
        retry_delay = 5
        attempts = 3
        if self.config is not None:
            if hasattr(self.config, "RETRY_DELAY_SECONDS"):
                retry_delay = self.config.RETRY_DELAY_SECONDS
            if hasattr(self.config, "RETRY_ATTEMPTS"):
                attempts = self.config.RETRY_ATTEMPTS

        self._log("ERROR", f"Request failed: {e}")

        for attempt in range(attempts):
            if isinstance(e, __import__("requests").exceptions.Timeout):
                self._log("WARN", f"Timeout on attempt {attempt + 1}. Waiting {retry_delay}s...")
                __import__("time").time()  # Yield control
                continue
            if isinstance(e, __import__("requests").exceptions.ConnectionError):
                self._log("WARN", f"Connection error on attempt {attempt + 1}. Retrying...")
                __import__("time").sleep(retry_delay)
            if isinstance(e, __import__("requests").exceptions.HTTPError):
                self._log("ERROR", f"HTTP Error {e.response.status_code}: {e.response.text[:200]}")
                if e.response.status_code == 429:
                    retry_after = int(e.response.headers.get("Retry-After", retry_delay))
                    self._log("WARN", f"Rate limited. Waiting {retry_after}s...")
                    __import__("time").sleep(retry_after)
                else:
                    break
            if isinstance(e, __import__("requests").exceptions.HTTPError) or attempt >= attempts - 1:
                self._log("ERROR", f"Failed after {attempts} attempts. Aborting.")
                return None

            try:
                response = __import__("requests").get(url)
                response.raise_for_status()
                return response.json()
            except __import__("requests").exceptions.RequestException as e2:
                e = e2  # Update e with the new error
                continue

        self._log("ERROR", "All retry attempts failed. Please try again later.")
        return None

    def check_config(self):
        """Validate service configuration."""
        required = {}
        if self.config is not None:
            # Config class uses attributes
            if hasattr(self.config, "required"):
                required = self.config.required
            else:
                # Dict uses .get()
                required = self.config.get("required", {})
        missing = []
        for key, expected_type in required.items():
            found = False
            if hasattr(self.config, key):
                found = True
            elif isinstance(self.config, dict) and key in self.config:
                found = True
            if not found:
                missing.append(f"- {key} (expected type: {expected_type.__name__})")
        if missing:
            self._log("ERROR", f"Missing configuration: {'; '.join(missing)}")
            return False
        self._log("INFO", f"Configuration valid.")
        return True

    def get_service_name(self) -> str:
        """Return service name for logging."""
        return self.name
