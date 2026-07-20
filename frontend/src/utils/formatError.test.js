import test from 'node:test';
import assert from 'node:assert/strict';
import { extractErrorMessage } from './formatError.js';

test('extractErrorMessage - handles FastAPI 422 array of detail objects without returning an object', () => {
  const fastapi422Response = {
    response: {
      data: {
        detail: [
          {
            type: 'value_error',
            loc: ['body', 'password'],
            msg: 'Password does not meet policy requirements',
            input: ' lemahabis',
            ctx: { reason: 'Must contain uppercase' }
          }
        ]
      }
    }
  };

  const result = extractErrorMessage(fastapi422Response);
  
  // MUST return a string, NOT an object or array of objects which crashes React JSX
  assert.equal(typeof result, 'string', `Expected string but got ${typeof result}`);
  assert.equal(result, 'Password does not meet policy requirements');
});

test('extractErrorMessage - handles string detail error', () => {
  const errorObj = {
    response: {
      data: {
        detail: 'Email sudah terdaftar.'
      }
    }
  };

  const result = extractErrorMessage(errorObj);
  assert.equal(result, 'Email sudah terdaftar.');
});

test('extractErrorMessage - handles fallback default message when error is empty', () => {
  const result = extractErrorMessage({});
  assert.equal(result, 'Terjadi kesalahan sistem. Silakan coba lagi.');
});
