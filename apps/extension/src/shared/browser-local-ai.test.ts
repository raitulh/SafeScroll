import { describe, expect, it } from 'vitest';
import { localModelRisk } from './browser-local-ai';

describe('small local model',()=>{
  it('returns a bounded probability without network access',()=>{
    const r=localModelRisk('URGENT send your OTP immediately to unlock your account');
    expect(r.probability).toBeGreaterThanOrEqual(0);
    expect(r.probability).toBeLessThanOrEqual(1);
    expect(r.version).toMatch(/^small-linear/);
  });
});
