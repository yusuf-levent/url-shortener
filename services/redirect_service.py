from sqlalchemy.orm import Session
from fastapi.requests import Request
from models import Link,ClickLog
from fastapi import status,HTTPException
from fastapi.responses import RedirectResponse
from config import settings
from datetime import datetime,timezone
from constants import MAX_REDIRECTS_PER_MINUTE,RATE_LIMIT_WINDOW_SECONDS,MAX_REDIRECTS_PER_MINUTE_SAME_URL
from services.redis_service import redis
from services.cache_service import CacheService
from services.link_query_service import LinkQueryService
from services.auth_redis_service import AuthRedisService
from loguru import logger
class RedirectService:
    db:Session
    def __init__(self,db):
        self.db=db
        self.query=LinkQueryService(db)
    def redirect(self,code:str,request:Request,ip_hash:str):
        log=logger.bind(code=code)
        log.info("Redirect request received")
        link=self.query.get_link_redirect(code)
        user_agent=(request.headers.get("user-agent") or "unknown").split(",")[0]
        referer=(request.headers.get("referer") or "direct")
        accept_language=(request.headers.get("accept-language") or "unknown").split(",")[0]
        
        key=CacheService.same_ip_redirect_limit(ip_hash)

        
        
        if AuthRedisService.sliding_window_counter(key,MAX_REDIRECTS_PER_MINUTE,RATE_LIMIT_WINDOW_SECONDS):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="too many requests from same ip")
        key=CacheService.redirect_same_url_limit(ip_hash,code)
       
        
        if AuthRedisService.sliding_window_counter(key,MAX_REDIRECTS_PER_MINUTE_SAME_URL,RATE_LIMIT_WINDOW_SECONDS):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="too many requests to same url")  
        

        redis.zincrby(
           CacheService.analytics_top_referrers(link.id),
            1,
            referer
        )
        redis.zincrby(
            CacheService.analytics_top_languages(link.id),
            1,
            accept_language
        )
        redis.zincrby(
            CacheService.analytics_top_user_agents(link.id),
            1,
            user_agent
        )
        
        self.db.query(
            Link).filter(
                Link.id==link.id).update(
                    {Link.click:Link.click+1})


        click_log=ClickLog(
        link_id=link.id,
        ip_hash=ip_hash,
        user_agent=user_agent,
        referer=referer,
        clicked_at=datetime.now(timezone.utc),
        accept_language=accept_language)
        self.db.add(click_log)
        self.db.commit()
        log.success("Redirected.")
        return RedirectResponse(url=link.original_url,status_code=status.HTTP_302_FOUND)#bunun nedeni özel bir response döndermemiz redirect kendi status codeu ile geliyormuş