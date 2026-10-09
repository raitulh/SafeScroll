# Threat Intelligence

SafeScroll uses a provider interface. The included commercial-oriented adapter is Google Web Risk Lookup. It checks one URL per request and can return matching threat types. Web Risk documentation also describes an Update API that can maintain local hashed threat lists for lower URL disclosure. SafeScroll defaults hosted reputation checks to OFF; enable them only in Enhanced mode with an explicit privacy disclosure.

Configuration:

```env
WEB_RISK_ENABLED=true
WEB_RISK_API_KEY=...
WEB_RISK_THREAT_TYPES=SOCIAL_ENGINEERING,MALWARE,UNWANTED_SOFTWARE
```
