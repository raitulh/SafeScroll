export type Severity = 'SCAM' | 'SUSPICIOUS' | 'LOW_RISK';
export type ScamCategory =
  | 'otp_phishing' | 'bank_phishing' | 'prize_lottery' | 'delivery_scam'
  | 'fake_support' | 'family_emergency' | 'job_scam' | 'investment_scam'
  | 'remote_access' | 'credential_phishing' | 'impersonation' | 'payment_scam' | 'unknown';

export interface Evidence { code: string; label: string; weight: number; }
export interface UrlAssessment { score: number; reasons: string[]; suspicious: boolean; hostname: string | null; }
export interface ScanResult { severity: Severity; score: number; category: ScamCategory; evidence: Evidence[]; explanation: string; actions: string[]; language: 'en' | 'bn' | 'unknown'; url?: UrlAssessment; }

const includesAny = (s: string, terms: string[]) => terms.some((t) => s.includes(t));
const around = (s: string, a: string[], b: string[]) => {
  for (const left of a) {
    let pos = -1;
    while ((pos = s.indexOf(left, pos + 1)) !== -1) {
      const start = Math.max(0, pos - 100);
      const end = Math.min(s.length, pos + left.length + 100);
      if (includesAny(s.slice(start, end), b)) return true;
    }
  }
  return false;
};

const RULES: Array<{ code: string; label: string; weight: number; match: (s: string) => boolean }> = [
  { code: 'otp_request', label: 'Requests a private security code', weight: 28, match: s => around(s, ['otp', 'one-time password', 'verification code', 'security code', 'passcode'], ['send', 'share', 'tell', 'give', 'reply', 'provide', 'submit']) },
  { code: 'urgency', label: 'Creates urgency or pressure', weight: 18, match: s => includesAny(s, ['urgent', 'immediately', 'right now', 'act now', 'today only', 'last warning', 'final notice', 'within 10 minutes', 'within 30 minutes']) },
  { code: 'payment_request', label: 'Requests money or a fee', weight: 22, match: s => (includesAny(s, ['send money', 'pay', 'transfer', 'deposit', 'processing fee', 'service fee', 'gift card', 'crypto', 'payment']) && includesAny(s, ['money', 'taka', '৳', 'fee', 'amount', 'payment'])) },
  { code: 'prize_bait', label: 'Uses a prize or reward as bait', weight: 18, match: s => includesAny(s, ['congratulations', 'you won', 'winner', 'prize', 'reward', 'lottery', 'cash bonus']) && includesAny(s, ['claim', 'receive', 'collect', 'verify', 'fee']) },
  { code: 'remote_access', label: 'Requests remote device access', weight: 30, match: s => includesAny(s, ['anydesk', 'teamviewer', 'remote desktop', 'screen share', 'remote access', 'allow access', 'install this app']) },
  { code: 'account_threat', label: 'Threatens account suspension', weight: 20, match: s => includesAny(s, ['account blocked', 'account suspended', 'account locked', 'account closed', 'card blocked', 'wallet suspended']) },
  { code: 'impersonation', label: 'Claims to be a trusted person or organization', weight: 12, match: s => includesAny(s, ['from your bank', 'bank security', 'support team', 'microsoft support', 'apple support', 'police', 'government', 'your son', 'your daughter', 'your boss']) },
  { code: 'job_bait', label: 'Uses an unusually attractive job offer', weight: 15, match: s => includesAny(s, ['work from home', 'easy money', 'registration fee', 'earn $500', 'earn ৳']) && includesAny(s, ['job', 'work', 'employment', 'position']) },
  { code: 'family_emergency', label: 'Creates a family emergency', weight: 17, match: s => includesAny(s, ['lost my phone', 'new number', 'need money urgently', 'emergency']) && includesAny(s, ['mom', 'dad', 'son', 'daughter', 'brother', 'sister', 'family']) }
];

const BN_RULES: Array<{ code: string; label: string; weight: number; match: (s: string) => boolean }> = [
  { code: 'bn_otp', label: 'আপনার OTP চাওয়া হচ্ছে', weight: 30, match: s => includesAny(s, ['otp', 'ওটিপি', 'ভেরিফিকেশন কোড']) && includesAny(s, ['দিন', 'দাও', 'পাঠান', 'শেয়ার', 'বলুন']) },
  { code: 'bn_urgency', label: 'দ্রুত কাজ করতে চাপ দিচ্ছে', weight: 18, match: s => includesAny(s, ['এখনই', 'জরুরি', 'তাড়াতাড়ি', 'আজই', 'তাৎক্ষণিক', 'বন্ধ হয়ে যাবে', 'বাতিল']) },
  { code: 'bn_prize', label: 'পুরস্কারের লোভ দেখাচ্ছে', weight: 18, match: s => includesAny(s, ['জিতেছেন', 'পুরস্কার', 'লটারি', 'উপহার', 'টাকা', '৳']) && includesAny(s, ['নিতে', 'পেতে', 'দাবি', 'ভেরিফাই', 'ফি']) }
];

function detectLanguage(text: string): 'en' | 'bn' | 'unknown' {
  for (const char of text) {
    const cp = char.codePointAt(0) ?? 0;
    if (cp >= 0x0980 && cp <= 0x09ff) return 'bn';
  }
  return /[A-Za-z]/.test(text) ? 'en' : 'unknown';
}

function categoryFromEvidence(evidence: Evidence[]): ScamCategory {
  const codes = new Set(evidence.map(e => e.code));
  if (codes.has('otp_request') || codes.has('bn_otp')) return 'otp_phishing';
  if (codes.has('remote_access')) return 'remote_access';
  if (codes.has('prize_bait') || codes.has('bn_prize')) return 'prize_lottery';
  if (codes.has('job_bait')) return 'job_scam';
  if (codes.has('family_emergency')) return 'family_emergency';
  if (codes.has('account_threat')) return 'bank_phishing';
  if (codes.has('payment_request')) return 'payment_scam';
  if (codes.has('impersonation')) return 'impersonation';
  return codes.size ? 'credential_phishing' : 'unknown';
}

export function assessUrl(input: string): UrlAssessment {
  try {
    const url = new URL(input.trim());
    const hostname = url.hostname.toLowerCase();
    let score = 0;
    const reasons: string[] = [];
    if (url.protocol !== 'https:') { score += 18; reasons.push('The link does not use HTTPS.'); }
    if (hostname.split('.').every(part => /^[0-9]+$/.test(part))) { score += 28; reasons.push('The link points directly to an IP address.'); }
    if (hostname.startsWith('xn--') || hostname.includes('.xn--')) { score += 22; reasons.push('The domain uses encoded Unicode characters.'); }
    if (hostname.split('.').filter(Boolean).length >= 5) { score += 12; reasons.push('The domain has an unusually deep subdomain structure.'); }
    if (hostname.length > 55) { score += 10; reasons.push('The hostname is unusually long.'); }
    if (includesAny((url.pathname + ' ' + url.search).toLowerCase(), ['login', 'verify', 'secure', 'account', 'update', 'claim', 'support', 'wallet'])) { score += 7; reasons.push('The URL path contains high-risk action words.'); }
    return { score: Math.min(score, 100), reasons, suspicious: score >= 20, hostname };
  } catch {
    return { score: 12, reasons: ['The link format could not be parsed safely.'], suspicious: true, hostname: null };
  }
}

export function analyzeText(text: string, url?: string): ScanResult {
  const clean = text.replace(/\s+/g, ' ').trim().slice(0, 12000);
  const language = detectLanguage(clean);
  const evidence: Evidence[] = [];
  let score = 0;
  for (const rule of [...RULES, ...(language === 'bn' ? BN_RULES : [])]) {
    if (rule.match(clean.toLowerCase())) {
      evidence.push({ code: rule.code, label: rule.label, weight: rule.weight });
      score += rule.weight;
    }
  }
  const embedded = !url ? clean.split(' ').find(part => part.startsWith('http://') || part.startsWith('https://')) : undefined;
  const urlAssessment = url ? assessUrl(url) : embedded ? assessUrl(embedded) : undefined;
  if (urlAssessment) score += Math.min(urlAssessment.score, 35);
  if (urlAssessment?.reasons.length) {
    urlAssessment.reasons.forEach((reason, i) => evidence.push({ code: `url_${i}`, label: reason, weight: 8 }));
  }
  const bounded = Math.min(100, score);
  const hardScam =
    (evidence.some(e => ['otp_request', 'bn_otp', 'remote_access'].includes(e.code)) && evidence.length >= 2) ||
    (evidence.some(e => ['otp_request', 'bn_otp'].includes(e.code)) &&
      evidence.some(e => ['urgency', 'bn_urgency', 'payment_request', 'prize_bait', 'account_threat', 'impersonation'].includes(e.code)));
  const finalScore = hardScam ? Math.max(bounded, 60) : bounded;
  const severity: Severity = hardScam || finalScore >= 60 ? 'SCAM' : finalScore >= 30 ? 'SUSPICIOUS' : 'LOW_RISK';
  const category = categoryFromEvidence(evidence);
  const explanation = severity === 'SCAM'
    ? language === 'bn' ? 'এই কনটেন্টে ব্যক্তিগত তথ্য চাওয়া বা দ্রুত সিদ্ধান্ত নিতে চাপ দেওয়ার মতো শক্তিশালী ঝুঁকির লক্ষণ আছে।' : 'This content contains strong warning signs such as pressure, requests for sensitive information, or suspicious actions.'
    : severity === 'SUSPICIOUS'
      ? 'This content has warning signs. Verify it before sharing information, clicking links, or sending money.'
      : 'We did not find strong scam signals in this content.';
  const actions = severity === 'SCAM'
    ? ['Do not click the link.', 'Do not share an OTP, PIN, password, or card details.', 'Verify through an official website or a phone number you already trust.']
    : severity === 'SUSPICIOUS'
      ? ['Pause before responding.', 'Verify the sender independently.', 'Do not send money or security codes until verified.']
      : ['No strong warning signs were found.', 'Still verify unexpected requests before acting.'];
  return { severity, score: finalScore, category, evidence, explanation, actions, language, url: urlAssessment };
}
