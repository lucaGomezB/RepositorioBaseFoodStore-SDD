## 1. Dependencies and Configuration

- [x] 1.1 Add slowapi to backend/requirements.txt
- [x] 1.2 Add RATE_LIMIT_LOGIN_REQUESTS to .env (default: 5)
- [x] 1.3 Add RATE_LIMIT_LOGIN_WINDOW to .env (default: 15 minutes)
- [x] 1.4 Update app/core/config.py with rate limit settings

## 2. Rate Limiting Middleware

- [x] 2.1 Create app/core/middleware/rate_limiter.py
- [x] 2.2 Initialize slowapi limiter with configuration
- [x] 2.3 Add limiter middleware to FastAPI app
- [x] 2.4 Add custom rate limit exceeded handler returning RFC 7807 format

## 3. Login Endpoint Protection

- [x] 3.1 Apply rate limit to POST /auth/login endpoint
- [x] 3.2 Configure IP-based rate limiting
- [x] 3.3 Test rate limiting with multiple requests

## 4. Response Headers

- [x] 4.1 Configure rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- [x] 4.2 Verify headers are present in responses

## 5. Testing

- [x] 5.1 Add unit test for rate limiter configuration
- [x] 5.2 Add integration test for rate limit exceeded scenario
- [x] 5.3 Verify rate limit headers are present

## 6. Verification

- [x] 6.1 Verify backend build succeeds
- [x] 6.2 Verify all tests pass