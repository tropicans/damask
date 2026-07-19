# Phase 9: Reversion Key & Backend Revert Processing - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-19
**Phase:** 9-Reversion Key & Backend Revert Processing
**Areas discussed:** Reversion Key Format & Delivery, Bijectivity Enforcement on Collisions, Revert Endpoint Interface, Mismatched Mapping Validation

---

## Reversion Key Format & Delivery

| Option | Description | Selected |
|--------|-------------|----------|
| In-memory ZIP archive | Package the masked file and JSON key in a .zip file in-memory and stream it back. Conforms to the 50MB file size limit and zero-knowledge constraints without server-side disk writes. | ✓ |
| Base64 JSON Response | Return a JSON response containing the base64-encoded masked file and the raw JSON key. (Incurs significant memory overhead on large files). | |
| You decide | The agent will select the most optimal approach during implementation. | |

**User's choice:** In-memory ZIP archive
**Notes:** Preferred for safety, performance, and compliance with the 50MB file size limits and zero-knowledge constraints.

---

## Bijectivity Enforcement on Collisions

| Option | Description | Selected |
|--------|-------------|----------|
| Regeneration with Unique Suffix/Offset Fallback | Retry generating the fake value up to 100 times. If still colliding, append the original value or a unique counter to make it unique. Guarantees 100% bijectivity and ensures the masking job never fails. | ✓ |
| Fail Job | Abort the masking job and return an error if a collision cannot be resolved within a small number of retries. | |
| You decide | The agent will select the most optimal approach during implementation. | |

**User's choice:** Regeneration with Unique Suffix/Offset Fallback
**Notes:** Guarantees that masking jobs never fail unexpectedly while ensuring strict 1-to-1 mapping.

---

## Revert Endpoint Interface

| Option | Description | Selected |
|--------|-------------|----------|
| Multipart Form-Data Upload | The endpoint accepts two standard file fields: 'file' (masked CSV/Excel) and 'key' (JSON mapping key file). Aligns with existing upload patterns. | ✓ |
| JSON Payload with Base64 File Content | Send base64-encoded file and the mapping key inside a single JSON request body. (Higher memory/CPU overhead). | |
| You decide | The agent will select the most optimal approach. | |

**User's choice:** Multipart Form-Data Upload
**Notes:** Aligns with current file upload and streaming design patterns in the application.

---

## Mismatched Mapping Validation

| Option | Description | Selected |
|--------|-------------|----------|
| Strict Validation (Fail Fast) | Abort and raise a 400 Bad Request with a detailed list of mismatched columns or values. Prevents data corruption or partial leakages. | ✓ |
| Lax Validation (Partial Reversion) | Revert matching values and leave unmatched ones as they are, returning warnings. | |
| You decide | The agent will select the most optimal approach. | |

**User's choice:** Strict Validation (Fail Fast)
**Notes:** Crucial for security and correctness, preventing silent data leakage or corruptions.

---

## Agent's Discretion

None.

## Deferred Ideas

None.
