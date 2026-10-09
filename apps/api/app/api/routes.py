from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.db.models import Feedback, ScanEvent, User
from app.db.session import get_session
from app.schemas.scan import FeedbackRequest, ScanRequest, ScanResponse, UrlScanRequest
from app.services.ocr import extract_text
from app.services.ollama import OllamaError, enhanced_classification
from app.services.rate_limit import enforce_rate_limit
from app.services.risk_engine import analyze, assess_url
from app.services.web_risk import WebRiskError, lookup_url
from app.api.auth import current_user
from datetime import datetime, timezone

router=APIRouter(prefix='/api/v1',tags=['scans'])

@router.get('/health')
async def health(): return {'status':'ok','service':'safescroll-api','version':settings.app_version}

@router.get('/ready')
async def ready(session: AsyncSession=Depends(get_session)):
    checks={}
    try:
        await session.execute(__import__('sqlalchemy').text('SELECT 1')); checks['postgres']='ok'
    except Exception: checks['postgres']='error'
    from app.services.rate_limit import redis
    try: await redis.ping(); checks['redis']='ok'
    except Exception: checks['redis']='error'
    status='ok' if all(v=='ok' for v in checks.values()) else 'degraded'
    return {'status':status,'checks':checks}

async def persist(result:dict,session:AsyncSession,user_id:int|None=None,cloud_used:bool=False)->ScanEvent:
    ev=ScanEvent(severity=result['severity'],category=result['category'],language=result['language'],score=result['score'],engine_version=settings.app_version,user_id=user_id,cloud_used=cloud_used)
    session.add(ev); await session.flush(); return ev

@router.post('/scan/text',response_model=ScanResponse)
async def scan_text(payload:ScanRequest,request:Request,session:AsyncSession=Depends(get_session)):
    await enforce_rate_limit(request)
    result=analyze(payload.content,str(payload.url) if payload.url else None)
    cloud_used=False
    if payload.enhanced:
        try:
            ai=await enhanced_classification(payload.content,result)
            if isinstance(ai,dict):
                if ai.get('severity')=='SCAM': result['severity']='SCAM'
                elif ai.get('severity')=='SUSPICIOUS' and result['severity']=='LOW_RISK': result['severity']='SUSPICIOUS'
                if isinstance(ai.get('explanation'),str) and ai['explanation'].strip(): result['explanation']=ai['explanation'][:500]
                if isinstance(ai.get('category'),str) and ai['category'].strip(): result['category']=ai['category'][:64]
                cloud_used=True
        except OllamaError:
            pass
    event=await persist(result,session,cloud_used=cloud_used); await session.commit()
    result['scan_id']=event.id; result['engine_version']=settings.app_version
    return result

@router.post('/scan/url')
async def scan_url(payload:UrlScanRequest,request:Request):
    await enforce_rate_limit(request)
    score,reasons=assess_url(str(payload.url)); threat_types=[]; provider='local'
    if payload.enhanced and settings.web_risk_enabled:
        try:
            ti=await lookup_url(str(payload.url)); threat_types=ti.threat_types; provider=ti.provider
            if ti.matched: score=max(score,95); reasons.append('The URL is present on a configured Google Web Risk threat list.')
        except WebRiskError: provider='google_web_risk_unavailable'
    severity='SCAM' if score>=60 else 'SUSPICIOUS' if score>=20 else 'LOW_RISK'
    return {'severity':severity,'score':score,'reasons':reasons,'hostname':payload.url.host,'threat_types':threat_types,'provider':provider}

@router.post('/scan/image',response_model=ScanResponse)
async def scan_image(request:Request,file:UploadFile=File(...),session:AsyncSession=Depends(get_session)):
    await enforce_rate_limit(request)
    raw=await file.read()
    if len(raw)>settings.image_max_bytes: raise HTTPException(413,'Image is too large.')
    if not file.content_type or not file.content_type.startswith('image/'): raise HTTPException(415,'Only image uploads are supported.')
    try: text=extract_text(raw)
    except ValueError as exc: raise HTTPException(400,str(exc)) from exc
    result=analyze(text[:settings.scan_max_chars]); event=await persist(result,session); await session.commit(); result['scan_id']=event.id; result['engine_version']=settings.app_version
    return result

@router.post('/feedback')
async def feedback(payload:FeedbackRequest,session:AsyncSession=Depends(get_session)):
    session.add(Feedback(scan_id=payload.scan_id,verdict=payload.verdict,reason=payload.reason)); await session.commit(); return {'accepted':True}
