import re
from dataclasses import dataclass
from urllib.parse import urlparse

@dataclass(frozen=True)
class Evidence:
    code: str
    label: str
    weight: int

def _any(s: str, terms: list[str]) -> bool:
    return any(t in s for t in terms)

def normalize_text(s: str) -> str:
    # Remove zero-width controls and normalize whitespace without changing user-visible language.
    s = re.sub(r'[​-‏⁠﻿]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def assess_url(url: str) -> tuple[int, list[str]]:
    p = urlparse(url.strip())
    host = (p.hostname or '').lower()
    score = 0
    reasons: list[str] = []
    if p.scheme not in {'http', 'https'}:
        score += 25; reasons.append('The link uses an unusual or unsupported web protocol.')
    elif p.scheme != 'https':
        score += 18; reasons.append('The link does not use HTTPS.')
    if host and all(part.isdigit() for part in host.split('.') if part):
        score += 28; reasons.append('The link points directly to an IP address.')
    if host.startswith('xn--') or '.xn--' in host:
        score += 22; reasons.append('The domain uses encoded Unicode characters.')
    if len([x for x in host.split('.') if x]) >= 5:
        score += 12; reasons.append('The domain has an unusually deep subdomain structure.')
    if len(host) > 55:
        score += 10; reasons.append('The hostname is unusually long.')
    if '@' in p.netloc:
        score += 20; reasons.append('The URL contains a username-like segment before the real host.')
    if p.port and p.port not in {80, 443}:
        score += 8; reasons.append('The link uses a non-standard web port.')
    if _any((p.path + ' ' + p.query).lower(), ['login', 'verify', 'secure', 'account', 'update', 'claim', 'support', 'wallet']):
        score += 7; reasons.append('The URL path contains high-risk action words.')
    return min(score, 100), reasons

def detect_language(text: str) -> str:
    return 'bn' if any(0x0980 <= ord(c) <= 0x09FF for c in text) else 'en' if re.search(r'[A-Za-z]', text) else 'unknown'

def analyze(content: str, url: str | None = None) -> dict:
    text = normalize_text(content)[:12000]
    low = text.lower()
    bn = detect_language(text) == 'bn'
    rules = [
      ('otp_request','Requests a private security code',28, lambda s: _any(s,['otp','one-time password','verification code','security code','passcode']) and _any(s,['send','share','tell','give','reply','provide','submit'])),
      ('urgency','Creates urgency or pressure',18, lambda s: _any(s,['urgent','immediately','right now','act now','today only','last warning','final notice','within 10 minutes','within 30 minutes'])),
      ('payment_request','Requests money or a fee',22, lambda s: _any(s,['send money','pay','transfer','deposit','processing fee','service fee','gift card','crypto','payment']) and _any(s,['money','taka','৳','fee','amount','payment'])),
      ('prize_bait','Uses a prize or reward as bait',18, lambda s: _any(s,['congratulations','you won','winner','prize','reward','lottery','cash bonus']) and _any(s,['claim','receive','collect','verify','fee'])),
      ('remote_access','Requests remote device access',30, lambda s: _any(s,['anydesk','teamviewer','remote desktop','screen share','remote access','allow access','install this app'])),
      ('account_threat','Threatens account suspension',20, lambda s: _any(s,['account blocked','account suspended','account locked','account closed','card blocked','wallet suspended'])),
      ('impersonation','Claims to be a trusted person or organization',12, lambda s: _any(s,['from your bank','bank security','support team','microsoft support','apple support','police','government','your son','your daughter','your boss'])),
      ('job_bait','Uses an unusually attractive job offer',15, lambda s: _any(s,['work from home','easy money','registration fee','earn $500','earn ৳']) and _any(s,['job','work','employment','position'])),
      ('family_emergency','Creates a family emergency',17, lambda s: _any(s,['lost my phone','new number','need money urgently','emergency']) and _any(s,['mom','dad','son','daughter','brother','sister','family']))
    ]
    if bn:
        rules += [
          ('bn_otp','আপনার OTP চাওয়া হচ্ছে',30, lambda s: _any(s,['otp','ওটিপি','ভেরিফিকেশন কোড']) and _any(s,['দিন','দাও','পাঠান','শেয়ার','বলুন'])),
          ('bn_urgency','দ্রুত কাজ করতে চাপ দিচ্ছে',18, lambda s: _any(s,['এখনই','জরুরি','তাড়াতাড়ি','আজই','তাৎক্ষণিক','বন্ধ হয়ে যাবে','বাতিল'])),
          ('bn_prize','পুরস্কারের লোভ দেখাচ্ছে',18, lambda s: _any(s,['জিতেছেন','পুরস্কার','লটারি','উপহার','টাকা','৳']) and _any(s,['নিতে','পেতে','দাবি','ভেরিফাই','ফি']))
        ]
    evidence=[]; score=0
    for code,label,weight,match in rules:
        if match(low): evidence.append(Evidence(code,label,weight)); score += weight
    target=url or next((part.strip('.,!?()[]') for part in text.split() if part.startswith(('http://','https://'))),None)
    url_assessment=None
    if target:
        us,reasons=assess_url(target); url_assessment={'score':us,'reasons':reasons,'hostname':urlparse(target).hostname}
        score += min(us,35)
        evidence.extend(Evidence(f'url_{i}',reason,8) for i,reason in enumerate(reasons))
    score=min(100,score)
    hard=(any(e.code in {'otp_request','bn_otp','remote_access'} for e in evidence) and len(evidence)>=2) or (any(e.code in {'otp_request','bn_otp'} for e in evidence) and any(e.code in {'urgency','bn_urgency','payment_request','prize_bait','account_threat','impersonation'} for e in evidence))
    if hard: score=max(score,60)
    severity='SCAM' if hard or score>=60 else 'SUSPICIOUS' if score>=30 else 'LOW_RISK'
    codes={e.code for e in evidence}
    category='otp_phishing' if {'otp_request','bn_otp'} & codes else 'remote_access' if 'remote_access' in codes else 'prize_lottery' if {'prize_bait','bn_prize'} & codes else 'job_scam' if 'job_bait' in codes else 'family_emergency' if 'family_emergency' in codes else 'bank_phishing' if 'account_threat' in codes else 'payment_scam' if 'payment_request' in codes else 'impersonation' if 'impersonation' in codes else 'credential_phishing' if codes else 'unknown'
    explanation=('এই কনটেন্টে ব্যক্তিগত তথ্য চাওয়া বা দ্রুত সিদ্ধান্ত নিতে চাপ দেওয়ার মতো শক্তিশালী ঝুঁকির লক্ষণ আছে।' if bn else 'This content contains strong warning signs such as pressure, requests for sensitive information, or suspicious actions.') if severity=='SCAM' else 'This content has warning signs. Verify it before sharing information, clicking links, or sending money.' if severity=='SUSPICIOUS' else 'We did not find strong scam signals in this content.'
    actions=['Do not click the link.','Do not share an OTP, PIN, password, or card details.','Verify through an official website or a phone number you already trust.'] if severity=='SCAM' else ['Pause before responding.','Verify the sender independently.','Do not send money or security codes until verified.'] if severity=='SUSPICIOUS' else ['No strong warning signs were found.','Still verify unexpected requests before acting.']
    return {'severity':severity,'score':score,'category':category,'evidence':[e.__dict__ for e in evidence],'explanation':explanation,'actions':actions,'language':detect_language(text),'url':url_assessment}
