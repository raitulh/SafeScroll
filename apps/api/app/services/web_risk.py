from dataclasses import dataclass
import httpx
from urllib.parse import urlencode
from app.config import settings

@dataclass(frozen=True)
class ThreatIntelResult:
    matched: bool
    threat_types: list[str]
    provider: str
    cache_expiry: str | None = None

class WebRiskError(RuntimeError):
    pass

async def lookup_url(url: str) -> ThreatIntelResult:
    if not settings.web_risk_enabled or not settings.web_risk_api_key:
        return ThreatIntelResult(False, [], "disabled")
    params: list[tuple[str, str]] = [("key", settings.web_risk_api_key), ("uri", url)]
    params.extend(("threatTypes", value) for value in settings.web_risk_types)
    endpoint = "https://webrisk.googleapis.com/v1/uris:search?" + urlencode(params)
    try:
        async with httpx.AsyncClient(timeout=7.0) as client:
            response = await client.get(endpoint)
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise WebRiskError(str(exc)) from exc
    threat = data.get("threat") or {}
    types = threat.get("threatTypes") or []
    return ThreatIntelResult(bool(types), [str(t) for t in types], "google_web_risk", threat.get("expireTime"))
