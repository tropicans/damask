# Phase 7: Secure Headers & Rate Limiting Context

## Domain
Hardening API communication and traffic flow through secure HTTP headers and endpoint rate limiting.

## Decisions

- **D-01 (Secure HTTP Headers)**: Implement a custom FastAPI middleware class to set secure HTTP response headers on every response:
  - `Content-Security-Policy`: `"default-src 'self'; frame-ancestors 'none';"`
  - `Strict-Transport-Security`: `"max-age=63072000; includeSubDomains; preload"`
  - `X-Frame-Options`: `"DENY"`
  - `X-Content-Type-Options`: `"nosniff"`
  - `X-XSS-Protection`: `"1; mode=block"`
  - `Referrer-Policy`: `"strict-origin-when-cross-origin"`
- **D-02 (Rate Limiting Implementation)**: Integrate `slowapi` rate limiter in the FastAPI application using standard in-memory storage (no Redis dependency required).
- **D-03 (Rate Limit Thresholds)**:
  - Authentication endpoints (`/api/auth/register`, `/api/auth/login`): limit to `5/minute` per IP address.
  - File masking and preview endpoints (`/api/mask`, `/api/preview`): limit to `10/minute` per IP address.
  - General status and data history endpoints: limit to `100/minute` per IP address.
  - Return a standard `429 Too Many Requests` status code with an appropriate JSON response on limit exceedance.

## Canonical Refs
- [ROADMAP.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/ROADMAP.md)
- [REQUIREMENTS.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/REQUIREMENTS.md)
