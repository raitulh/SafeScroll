import { describe, expect, it } from 'vitest';
import { analyzeText, assessUrl } from '../src/index';

describe('detection core', () => {
  it('flags OTP urgency as scam', () => {
    const result = analyzeText('Urgent! Send your OTP immediately to verify your account.');
    expect(result.severity).toBe('SCAM');
    expect(result.category).toBe('otp_phishing');
  });

  it('flags suspicious URLs', () => {
    const result = assessUrl('http://192.168.0.20/login/verify');
    expect(result.suspicious).toBe(true);
  });

  it('does not call a generic OTP warning a scam by itself', () => {
    const result = analyzeText('Never share your OTP with anyone, even if they ask.');
    expect(result.severity).not.toBe('SCAM');
  });
});
