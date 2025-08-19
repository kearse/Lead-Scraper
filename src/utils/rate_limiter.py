"""Rate limiting utilities for API calls and web scraping."""

import asyncio
import time
from typing import Dict, Optional
from collections import defaultdict
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.constants import RATE_LIMITS

class TokenBucket:
    """Simple token bucket implementation for rate limiting."""
    
    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens from bucket.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens were acquired, False otherwise
        """
        now = time.time()
        elapsed = now - self.last_refill
        
        # Refill tokens based on elapsed time
        self.tokens = min(
            self.capacity,
            self.tokens + (elapsed * self.refill_rate)
        )
        self.last_refill = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    async def wait_for_tokens(self, tokens: int = 1) -> None:
        """Wait until tokens are available.
        
        Args:
            tokens: Number of tokens needed
        """
        while not await self.acquire(tokens):
            # Calculate wait time for next token
            wait_time = tokens / self.refill_rate
            await asyncio.sleep(min(wait_time, 1.0))

class RateLimiter:
    """Rate limiter for different API sources."""
    
    def __init__(self):
        self._buckets: Dict[str, TokenBucket] = {}
        self._init_buckets()
    
    def _init_buckets(self) -> None:
        """Initialize token buckets for different sources."""
        for source, limit_per_minute in RATE_LIMITS.items():
            # Convert per-minute limit to per-second refill rate
            refill_rate = limit_per_minute / 60.0
            self._buckets[source] = TokenBucket(
                capacity=limit_per_minute, 
                refill_rate=refill_rate
            )
    
    async def acquire(self, source: str, tokens: int = 1) -> bool:
        """Acquire tokens for a specific source.
        
        Args:
            source: API source name
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens were acquired
        """
        if source not in self._buckets:
            # Default rate limit for unknown sources
            refill_rate = 60 / 60.0  # 60 per minute
            self._buckets[source] = TokenBucket(capacity=60, refill_rate=refill_rate)
        
        return await self._buckets[source].acquire(tokens)
    
    async def wait_for_tokens(self, source: str, tokens: int = 1) -> None:
        """Wait for tokens to be available for a source.
        
        Args:
            source: API source name
            tokens: Number of tokens needed
        """
        if source not in self._buckets:
            # Default rate limit for unknown sources
            refill_rate = 60 / 60.0
            self._buckets[source] = TokenBucket(capacity=60, refill_rate=refill_rate)
        
        await self._buckets[source].wait_for_tokens(tokens)

# Global rate limiter instance
rate_limiter = RateLimiter()

# TODO: Future enhancements for rate limiting:
# - Persistent rate limit state (Redis/file-based)
# - Per-IP rate limiting for distributed scraping
# - Dynamic rate limit adjustment based on response headers
# - Exponential backoff on rate limit violations
# - Rate limit bypass detection and handling