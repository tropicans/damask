# Phase 7: Secure Headers & Rate Limiting Discussion Log

## Discussion Area 1: Secure HTTP Headers
- **Options Considered**:
  1. Add security headers via an external dependency (like `secure` package).
  2. Implement a custom FastAPI middleware (Recommended).
- **Selection**: Option 2 (Custom Middleware).
- **Notes**: A custom middleware gives us direct control over the headers returned, has zero runtime overhead, and adds no external dependencies.

## Discussion Area 2: Rate Limiting Library
- **Options Considered**:
  1. Hand-roll a token-bucket rate limiter.
  2. Use `slowapi` library (Recommended).
- **Selection**: Option 2 (`slowapi`).
- **Notes**: `slowapi` is the standard library for FastAPI rate limiting and works out of the box with `limits` for in-memory storage.

## Discussion Area 3: Rate Limiting Thresholds
- **Options Considered**:
  1. Unified global rate limits across all routes.
  2. Granular per-route rate limits (Recommended).
- **Selection**: Option 2 (Granular).
- **Notes**: Restricting auth endpoints to 5 requests/minute protects against brute-force, while data masking is restricted to 10 requests/minute to protect resource usage. General endpoints can have a higher threshold of 100 requests/minute.
