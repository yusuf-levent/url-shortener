from fastapi import HTTPException,status
from models import Link
from services.redis_service import redis
from services.cache_service import CacheService
from schemas import UrlResponse,RedirectLink
from datetime import datetime,timezone
class LinkQueryService:
    def __init__(self,db):
        self.db=db
    def get_user_link(self,code:str,user_id:int)->Link|UrlResponse:
        link=redis.get(
            f"link:{user_id}:{code}"
            )
        if link is not None:
            link=UrlResponse.model_validate_json(link)
            
        else:
            link=self.db.query(
                Link).filter(
                    Link.code==code).first()
            
            if link is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail= "url does not exist"
                    )
            if link.user_id!=user_id:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="cannot get another user's link"
                    )
            response=UrlResponse.model_validate(link)
            redis.set(
                CacheService.get_link(code,user_id),
                response.model_dump_json(),
                ex=300
                )
        
        return link
    
    def get_link_redirect(self,code)->RedirectLink:
        cache=redis.get(f"redirect:{code}")
        if cache is not None:
            link=RedirectLink.model_validate_json(cache)
            
        else:
            link=self.db.query(Link).filter(Link.code==code).first()
            if link is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="url is not found")
            response=RedirectLink.model_validate(link).model_dump_json()
            redis.set(
                    CacheService.redirect(code),
                    response,
                    ex=300
                    )
        

            
        if link.expires_at is not None:
            expires_at=link.expires_at
            if expires_at.tzinfo is None:
                expires_at=expires_at.replace(tzinfo=timezone.utc)
            if expires_at<datetime.now(timezone.utc):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="expires_at must be future time") 
        if not link.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="link is not active")
        return link
    def get_link_without_cache(self,code:str,user_id:int)->Link:
        link=self.db.query(
                Link).filter(
                    Link.code==code).first()
            
        if link is None:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail= "url does not exist"
                    )
        if link.user_id!=user_id:
                log
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="cannot get another user's link"
                    )
        response=UrlResponse.model_validate(link)
        redis.set(
                CacheService.get_link(code,user_id),
                response.model_dump_json(),
                ex=300
                )
        
        return link