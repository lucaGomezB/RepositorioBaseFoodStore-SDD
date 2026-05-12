## Why

The Food Store API currently has no protection against brute-force attacks on the login endpoint. Without rate limiting, an attacker could make unlimited attempts to guess user credentials, which poses a significant security risk. Implementing rate limiting will help protect the API from abuse and ensure fair usage.

## What Changes

- Add slowapi middleware for rate limiting
- Configure rate limits for login endpoint (5 attempts per 15 minutes per IP)
- Add rate limit headers to responses (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- Create a rate limit exceeded response in RFC 7807 format
- Add configuration for rate limit settings in .env

## Capabilities

### New Capabilities

- `rate-limiting`: API rate limiting using slowapi middleware with IP-based limits

### Modified Capabilities

- None

## Impact

- **Backend**: New middleware and configuration in app/core/middleware/
- **Dependencies**: Add slowapi package
- **Configuration**: Add RATE_LIMIT_* settings to .env
- **All endpoints**: Optional rate limiting can be applied to other endpoints as needed