from functools import wraps
from flask import request, jsonify
import time
from collections import defaultdict, deque

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
    
    def is_allowed(self, key: str, limit: str) -> bool:
        """Check if request is allowed based on rate limit"""
        try:
            # Parse limit (e.g., "10/minute", "100/hour")
            count, period = limit.split('/')
            count = int(count)
            
            if period == 'minute':
                window = 60
            elif period == 'hour':
                window = 3600
            else:
                window = 60  # Default to minute
            
            now = time.time()
            requests = self.requests[key]
            
            # Remove old requests outside the window
            while requests and requests[0] <= now - window:
                requests.popleft()
            
            # Check if under limit
            if len(requests) < count:
                requests.append(now)
                return True
            
            return False
            
        except Exception:
            # If rate limiting fails, allow the request
            return True

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(limit: str):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP address as key
            key = request.remote_addr or 'unknown'
            
            if not rate_limiter.is_allowed(key, limit):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'limit': limit
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
