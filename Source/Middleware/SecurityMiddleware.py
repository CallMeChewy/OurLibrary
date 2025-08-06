# File: SecurityMiddleware.py
# Path: /home/herb/Desktop/AndyLibrary/Source/Middleware/SecurityMiddleware.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-28
# Last Modified: 2025-07-28 06:45AM

"""
Security Middleware for AndyLibrary with 2025 standards
Implements comprehensive security headers, CSRF protection, rate limiting
"""

import time
import json
import logging
import secrets
from typing import Dict, Set, Optional
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware implementing 2025 best practices
    """
    
    def __init__(self, app: ASGIApp, config: Dict = None):
        super().__init__(app)
        self.Logger = logging.getLogger(__name__)
        
        # Security configuration
        self.Config = config or {}
        self.Environment = self.Config.get("environment", "development")
        
        # Rate limiting storage (use Redis in production)
        self.RateLimitStore = defaultdict(list)
        self.CSRFTokens = {}
        
        # Security settings
        self.SecurityHeaders = self._GetSecurityHeaders()
        self.RateLimits = self._GetRateLimits()
        
        # Blocked IPs and suspicious patterns
        self.BlockedIPs: Set[str] = set()
        self.SuspiciousPatterns = [
            'admin', 'wp-admin', 'phpmyadmin', 'sql', 'inject', 
            'script', 'eval', 'exec', '<script', 'javascript:'
        ]
        
        self.Logger.info("🛡️ Security Middleware initialized with 2025 standards")
    
    def _GetSecurityHeaders(self) -> Dict[str, str]:
        """Get security headers based on environment"""
        base_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()"
        }
        
        if self.Environment == "production":
            base_headers.update({
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
                "Content-Security-Policy": (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' https://accounts.google.com; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data: https:; "
                    "connect-src 'self' https://accounts.google.com https://oauth2.googleapis.com; "
                    "frame-ancestors 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self'"
                )
            })
        else:
            # Development CSP (more permissive)
            base_headers["Content-Security-Policy"] = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "connect-src 'self' https://accounts.google.com https://oauth2.googleapis.com"
            )
        
        return base_headers
    
    def _GetRateLimits(self) -> Dict[str, Dict]:
        """Get rate limiting configuration"""
        return {
            "oauth": {"requests": 10, "window": 60},  # 10 OAuth attempts per minute
            "auth": {"requests": 20, "window": 60},   # 20 auth attempts per minute
            "api": {"requests": 100, "window": 60},   # 100 API calls per minute
            "global": {"requests": 1000, "window": 60}  # 1000 total requests per minute
        }
    
    async def dispatch(self, request: Request, call_next):
        """Main security middleware processing"""
        start_time = time.time()
        
        try:
            # Security checks
            security_result = await self._PerformSecurityChecks(request)
            if security_result:
                return security_result
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            self._AddSecurityHeaders(response)
            
            # Log request
            self._LogRequest(request, response, time.time() - start_time)
            
            return response
            
        except Exception as e:
            self.Logger.error(f"Security middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Security processing failed"}
            )
    
    async def _PerformSecurityChecks(self, request: Request) -> Optional[Response]:
        """Perform comprehensive security checks"""
        client_ip = self._GetClientIP(request)
        
        # 1. Blocked IP check
        if client_ip in self.BlockedIPs:
            self.Logger.warning(f"🚫 Blocked IP attempted access: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={"error": "Access denied"}
            )
        
        # 2. Rate limiting
        rate_limit_response = self._CheckRateLimit(request, client_ip)
        if rate_limit_response:
            return rate_limit_response
        
        # 3. Malicious pattern detection
        if self._DetectMaliciousPatterns(request):
            self.Logger.warning(f"🚨 Malicious pattern detected from {client_ip}: {request.url}")
            self._AddSuspiciousIP(client_ip)
            return JSONResponse(
                status_code=400,
                content={"error": "Bad request"}
            )
        
        # 4. OAuth-specific security
        if request.url.path.startswith("/api/auth/oauth"):
            oauth_check = self._CheckOAuthSecurity(request)
            if oauth_check:
                return oauth_check
        
        return None
    
    def _GetClientIP(self, request: Request) -> str:
        """Get client IP with proxy header support"""
        # Check for forwarded headers (common in production)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _CheckRateLimit(self, request: Request, client_ip: str) -> Optional[Response]:
        """Check rate limiting for various endpoints"""
        now = datetime.utcnow()
        path = request.url.path
        
        # Determine rate limit category
        if "/oauth" in path:
            limit_type = "oauth"
        elif "/auth" in path:
            limit_type = "auth"
        elif "/api" in path:
            limit_type = "api"
        else:
            limit_type = "global"
        
        limit_config = self.RateLimits[limit_type]
        key = f"{client_ip}:{limit_type}"
        
        # Clean old entries
        self.RateLimitStore[key] = [
            timestamp for timestamp in self.RateLimitStore[key]
            if now - timestamp < timedelta(seconds=limit_config["window"])
        ]
        
        # Check limit
        if len(self.RateLimitStore[key]) >= limit_config["requests"]:
            self.Logger.warning(f"⚡ Rate limit exceeded for {client_ip} on {limit_type}")
            
            # Progressive penalties
            if len(self.RateLimitStore[key]) > limit_config["requests"] * 2:
                self._AddSuspiciousIP(client_ip)
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": limit_config["window"]
                },
                headers={"Retry-After": str(limit_config["window"])}
            )
        
        # Record request
        self.RateLimitStore[key].append(now)
        return None
    
    def _DetectMaliciousPatterns(self, request: Request) -> bool:
        """Detect malicious patterns in request"""
        # Check URL path
        path_lower = request.url.path.lower()
        query_lower = str(request.url.query).lower() if request.url.query else ""
        
        for pattern in self.SuspiciousPatterns:
            if pattern in path_lower or pattern in query_lower:
                return True
        
        # Check User-Agent for bot patterns
        user_agent = request.headers.get("user-agent", "").lower()
        bot_patterns = ['bot', 'crawler', 'spider', 'scraper', 'scan']
        
        # Allow legitimate bots but log them
        if any(pattern in user_agent for pattern in bot_patterns):
            if not any(legit in user_agent for legit in ['googlebot', 'bingbot', 'facebookexternalhit']):
                self.Logger.info(f"🤖 Suspicious bot detected: {user_agent}")
                return True
        
        return False
    
    def _CheckOAuthSecurity(self, request: Request) -> Optional[Response]:
        """OAuth-specific security checks"""
        # CSRF protection for OAuth callbacks
        if "callback" in request.url.path:
            # Validate state parameter exists
            state = request.query_params.get("state")
            if not state:
                self.Logger.warning("🚨 OAuth callback without state parameter")
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid OAuth request"}
                )
            
            # Check for replay attacks
            if self._IsReplayAttack(state):
                self.Logger.warning("🚨 Potential OAuth replay attack detected")
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid OAuth state"}
                )
        
        return None
    
    def _IsReplayAttack(self, state: str) -> bool:
        """Check for OAuth replay attacks"""
        # Simple replay prevention (use Redis for production)
        now = datetime.utcnow()
        
        # Clean old states
        self.CSRFTokens = {
            token: timestamp for token, timestamp in self.CSRFTokens.items()
            if now - timestamp < timedelta(minutes=15)
        }
        
        if state in self.CSRFTokens:
            return True  # State already used
        
        self.CSRFTokens[state] = now
        return False
    
    def _AddSuspiciousIP(self, ip: str):
        """Add IP to suspicious list with progressive penalties"""
        # In production, implement proper threat intelligence
        suspicious_key = f"suspicious:{ip}"
        
        if suspicious_key not in self.RateLimitStore:
            self.RateLimitStore[suspicious_key] = []
        
        self.RateLimitStore[suspicious_key].append(datetime.utcnow())
        
        # Block IP after multiple suspicious activities
        if len(self.RateLimitStore[suspicious_key]) >= 5:
            self.BlockedIPs.add(ip)
            self.Logger.warning(f"🚫 IP blocked due to suspicious activity: {ip}")
    
    def _AddSecurityHeaders(self, response: Response):
        """Add security headers to response"""
        for header, value in self.SecurityHeaders.items():
            response.headers[header] = value
        
        # Add unique request ID for tracking
        response.headers["X-Request-ID"] = secrets.token_hex(8)
        
        # Add security timestamp
        response.headers["X-Security-Version"] = "2025.1"
    
    def _LogRequest(self, request: Request, response: Response, duration: float):
        """Log request with security context"""
        client_ip = self._GetClientIP(request)
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "client_ip": client_ip,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": round(duration, 3),
            "user_agent": request.headers.get("user-agent", ""),
            "referer": request.headers.get("referer", "")
        }
        
        # Log OAuth requests specially
        if "/oauth" in request.url.path:
            log_data["oauth_request"] = True
        
        # Log based on status code
        if response.status_code >= 400:
            self.Logger.warning(f"🚨 Security event: {json.dumps(log_data)}")
        elif "/oauth" in request.url.path or "/auth" in request.url.path:
            self.Logger.info(f"🔐 Auth request: {json.dumps(log_data)}")
        
    def GetSecurityStats(self) -> Dict:
        """Get security statistics"""
        now = datetime.utcnow()
        
        # Count recent requests by type
        stats = {
            "blocked_ips": len(self.BlockedIPs),
            "active_sessions": len([
                token for token, timestamp in self.CSRFTokens.items()
                if now - timestamp < timedelta(minutes=15)
            ]),
            "rate_limit_entries": len(self.RateLimitStore),
            "security_version": "2025.1",
            "environment": self.Environment,
            "uptime": (now - datetime.utcnow()).total_seconds()  # This would be start time in production
        }
        
        return stats

class CSRFProtection:
    """CSRF Protection utility"""
    
    @staticmethod
    def GenerateToken() -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def ValidateToken(request: Request, expected_token: str) -> bool:
        """Validate CSRF token from request"""
        # Check header first
        token = request.headers.get("X-CSRF-Token")
        
        # Fallback to form data
        if not token and hasattr(request, 'form'):
            form_data = request.form()
            token = form_data.get("csrf_token")
        
        return token == expected_token if token else False