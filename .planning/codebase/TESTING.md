# Testing Patterns

**Analysis Date:** 2026-07-19

## Test Framework

**Backend (Python):**
- Runner: pytest
- Matchers: standard python assert statements

**Frontend (React/TS):**
- Runner: Vitest
- Assertion Library: Vitest built-in expect
- Matchers: toBe, toEqual, toHaveBeenCalled, toThrow, toContain

**Run Commands:**
```bash
# Backend tests
cd backend && pytest                           # Run all backend tests
cd backend && pytest tests/test_masker.py      # Run specific test file
cd backend && pytest --cov=app                 # Run tests with coverage

# Frontend tests
cd frontend && npm test                        # Run all frontend tests
cd frontend && npm run test:ui                 # Run tests with Vitest UI
cd frontend && npm run test:coverage           # Run test coverage report
```

## Test File Organization

**Backend:**
- Location: `backend/tests/` directory separate from source.
- Naming: files prefix with `test_` (e.g. `test_masker.py`, `test_auth.py`).

**Frontend:**
- Location: collocated `*.test.ts` or `*.test.tsx` alongside source files (e.g., `DragDropUpload.test.tsx` in the same folder as `DragDropUpload.tsx`) or inside `frontend/src/__tests__/`.

## Test Structure

**Backend Suite Organization:**
```python
def test_mask_fake_name():
    # arrange
    data = ["Budi", "Siti", "Andi"]
    
    # act
    masked_data = mask_column(data, strategy="fake_name")
    
    # assert
    assert len(masked_data) == 3
    assert "Budi" not in masked_data
```

**Frontend Suite Organization:**
```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import DragDropUpload from './DragDropUpload';

describe('DragDropUpload', () => {
  it('triggers callback on file drop', () => {
    const onUploadMock = vi.fn();
    render(<DragDropUpload onUpload={onUploadMock} />);
    
    // Test logic here...
    
    expect(onUploadMock).toHaveBeenCalled();
  });
});
```

## Mocking

- Python: Use standard library `unittest.mock` (`patch`, `MagicMock`) to stub database sessions or Faker generation where required.
- TypeScript: Use `vi.mock` for external module imports (e.g. mocking Axios calls to the backend).

---

*Testing analysis: 2026-07-19*
*Update when test patterns change*
