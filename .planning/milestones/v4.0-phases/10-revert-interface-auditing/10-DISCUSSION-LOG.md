# Phase 10: Revert Interface & Auditing - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-19
**Phase:** 10-Revert Interface & Auditing
**Areas discussed:** Revert UI & Navigation, Revert Audit Logging, Reversion Key Delivery

---

## Revert UI & Navigation

| Option | Description | Selected |
|--------|-------------|----------|
| Add a new 'Revert Data' tab in the header navigation | Reuses the same styling as 'Masking Engine' and 'Riwayat Audit' tabs in App.tsx | ✓ |
| Add a toggle switch/sub-tab inside the main masking panel | Switch between 'Mask' and 'Revert' modes | |
| You decide | Antigravity will choose the cleanest visual integration | |

**User's choice:** Add a new 'Revert Data' tab in the header navigation (reusing the same styling as 'Masking Engine' and 'Riwayat Audit' tabs in App.tsx)
**Notes:** Access is open to all authenticated users. Errors are shown directly below the inputs.

---

## Revert Audit Logging

| Option | Description | Selected |
|--------|-------------|----------|
| Create a separate DB table/model 'RevertJob' for revert operations | Since they don't have column rules and need a duration/execution time field | ✓ |
| Reuse 'MaskingJob' table | Adds 'job_type' and 'duration_ms' columns and makes masking-specific fields nullable | |
| You decide | | |

**User's choice:** Create a separate DB table/model 'RevertJob' for revert operations (since they don't have column rules and need a duration/execution time field)
**Notes:** Revert jobs will be presented in a separate sub-navigation/toggle inside the 'Riwayat Audit' tab. Detail modal will show metadata only without column rules.

---

## Reversion Key Delivery

| Option | Description | Selected |
|--------|-------------|----------|
| Add a checkbox/switch in the masking configuration panel | 'Generate Reversion Key' / 'Buat Kunci Pemulihan' so users can opt-in | ✓ |
| Always generate the reversion key and download the ZIP file | No UI toggle | |
| You decide | | |

**User's choice:** Add a checkbox/switch in the masking configuration panel ('Generate Reversion Key' / 'Buat Kunci Pemulihan') so users can opt-in
**Notes:** Transition to a clean 'Success' view with download buttons and a security warning reminding the user to keep their key safe.

---

## the agent's Discretion

None. All decisions were fully aligned with the user.

## Deferred Ideas

None.
