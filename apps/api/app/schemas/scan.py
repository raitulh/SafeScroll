from pydantic import AnyHttpUrl, BaseModel, Field
class ScanRequest(BaseModel):
    content: str = Field(min_length=1, max_length=12000)
    url: AnyHttpUrl | None = None
    enhanced: bool = False
class UrlScanRequest(BaseModel):
    url: AnyHttpUrl
    enhanced: bool = False
class FeedbackRequest(BaseModel):
    scan_id: int | None = None
    verdict: str = Field(min_length=1,max_length=32)
    reason: str | None = Field(default=None,max_length=500)
class ScanResponse(BaseModel):
    severity: str
    score: int
    category: str
    evidence: list[dict]
    explanation: str
    actions: list[str]
    language: str
    url: dict | None = None
    scan_id: int | None = None
    engine_version: str | None = None
