# Phase 3: User Authentication - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-19
**Phase:** 3-User Authentication
**Areas discussed:** Frontend Navigation, JWT Client-Side Storage, Database Engine & ORM, Password Validation Strength

---

## Frontend Navigation

### Q1: How should the login/registration views be navigated and rendered on the frontend?
| Option | Description | Selected |
|--------|-------------|----------|
| State-based conditional rendering | Keep it simple and within the current App.tsx structure without adding router packages | ✓ |
| React Router | Install react-router-dom and configure path-based routing like /login and /register | |

**User's choice:** State-based conditional rendering
**Notes:** Decided to avoid the overhead of a routing library to keep implementation simple.

### Q2: When should the authentication check restrict access to the application features?
| Option | Description | Selected |
|--------|-------------|----------|
| App-level barrier | Show the login/register screen first; user must log in before they can access the upload or preview screen | ✓ |
| Action-level barrier | Allow users to upload and preview files, but require login only when they click 'Start Masking & Download' | |

**User's choice:** App-level barrier

---

## JWT Client-Side Storage

### Q1: Where should the JWT session token be stored on the client side?
| Option | Description | Selected |
|--------|-------------|----------|
| LocalStorage | Simple to read and write in React, persists across browser refreshes, and requires no special backend cookie setup | ✓ |
| HttpOnly Cookies | Set by backend via Set-Cookie headers, highly secure against XSS, but requires backend/frontend CORS and cookie credential forwarding setup | |

**User's choice:** LocalStorage

### Q2: What should be the expiration duration for the JWT authentication token?
| Option | Description | Selected |
|--------|-------------|----------|
| 24 Hours | Offers a good balance between session security and local convenience | ✓ |
| 1 Hour | Higher security, but users will be logged out frequently unless we implement complex refresh token flows | |
| 30 Days | Convenient for a purely local tool, requires very infrequent log-ins | |

**User's choice:** 24 Hours

---

## Database Engine & ORM

### Q1: Which ORM or database access library should we use for database interactions?
| Option | Description | Selected |
|--------|-------------|----------|
| SQLModel | Recommended in our stack; merges SQLAlchemy ORM and Pydantic schemas into a single model definition, matching FastAPI's design perfectly | ✓ |
| Standard SQLAlchemy | Robust and well-known, but requires duplicating field definitions between database schemas and API request/response models | |
| Direct SQLite/sqlite3 driver queries | Standard library, no external ORM packages, but requires writing manual raw SQL strings and manual mapping | |

**User's choice:** SQLModel

### Q2: Where and how should the SQLite database file be stored?
| Option | Description | Selected |
|--------|-------------|----------|
| File-based SQLite in backend directory | e.g. database path config in .env with fallback to backend/datamask.db to persist accounts across restarts | ✓ |
| In-memory SQLite | Database resides entirely in RAM; no disk files, but user registration will reset every time the server restarts | |

**User's choice:** File-based SQLite in backend directory

---

## Password Validation Strength

### Q1: What password complexity rules should be validated during user registration?
| Option | Description | Selected |
|--------|-------------|----------|
| Basic Length Check | Enforce minimum 8 characters only, simple and user-friendly for a local/internal tool | ✓ |
| Standard Complexity | Enforce minimum 8 characters, with at least one uppercase letter, one lowercase letter, one number, and one special character | |
| Enterprise Complexity | Enforce minimum 12 characters, with strict character type rules and prevention of basic sequential/common patterns | |

**User's choice:** Basic Length Check

### Q2: What password hashing algorithm should be implemented on the backend?
| Option | Description | Selected |
|--------|-------------|----------|
| bcrypt | Industry standard, highly secure, slow hashing to prevent brute-force/GPU cracking attacks; uses passlib/bcrypt | ✓ |
| SHA-256 with a unique salt | Uses standard Python hashlib library, faster to process, but less robust against hardware-accelerated cracking than bcrypt | |

**User's choice:** bcrypt

---

## the agent's Discretion
- Visual representation of login vs registration forms (tabbed layouts).
- Internal layout of database helper modules (session creator, etc.).

## Deferred Ideas
None — discussion stayed within phase scope.
