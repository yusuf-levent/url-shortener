from sqlalchemy.orm import Session
from schemas import UrlCreate,UrlUpdate,HealthChecker
from fastapi import HTTPException,status
from models import Link
from config import settings
import string,random
from qrcode import QRCode
from io import BytesIO
from fastapi.responses import StreamingResponse
from constants import RESERVED_CODES,MAX_LINKS_PER_MINUTE,RATE_LIMIT_WINDOW_SECONDS
from datetime import datetime,timezone
import time
import httpx
from services.redis_service import redis
from services.cache_service import CacheService
from services.link_query_service import LinkQueryService
from services.auth_redis_service import AuthRedisService
from utils import ssrf_ip_check
from urllib.parse import urljoin
from loguru import logger
REDIRECT_STATUS_CODES=(301,302,303,307,308)
class LinkService:
    db:Session
    
    def __init__(self,db):
        self.db=db
        self.query=LinkQueryService(self.db)
    def create_link(self,url:UrlCreate,user_id:int)->Link:
        log=logger.bind(user_id=user_id,url=url)
        log.info("Shorten link request received")
        original_url=str(url.original_url)
        ssrf_ip_check(original_url)
        if self.db.query(Link).filter(Link.original_url==original_url,Link.user_id==user_id).first():
            log.warning("Same url is already exist in database")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="same url")
        if url.custom_code is not None:

            if self.db.query(Link).filter(Link.code==url.custom_code).first() :
                log.warning("Custom code is already exist in database")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="same code is taken")
            if url.custom_code in RESERVED_CODES :
                log.warning("This custom code is reserved")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="code is reserved")
            code=url.custom_code
        else:
            code=self.benzersiz_code()
        key=CacheService.url_shorener_limit(user_id)
        
        if AuthRedisService.sliding_window_counter(
            key,
            MAX_LINKS_PER_MINUTE,
            RATE_LIMIT_WINDOW_SECONDS
            ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="too many requests to create link")
        
        yeni=Link(
            code=code,
            original_url=original_url,
            user_id=user_id,
            expires_at=url.expires_at,
            description=url.description
            ,is_active=url.is_active)#url acitve kısmı null olursas bir sıkınıt olurmu yoksa null olunca otomatikmen true mu olur
        
        self.db.add(yeni)
        self.db.commit()
        self.db.refresh(yeni)
        log.success("Shortened link successfully")
        return yeni
    
    def list_user_links(self,user_id:int,skip:int,limit:int,min_click:int,search:str)->list[Link]:
        log=logger.bind(user_id=user_id,skip=skip,limit=limit,min_click=min_click,search=search)
        log.info("List user's links request received")
        query=self.db.query(Link).filter(Link.user_id==user_id)
        if min_click is not None:
            query=query.filter(Link.click>=min_click)
        if search:
            query=query.filter(Link.original_url.ilike(f"%{search}%"))#büyük küçük harfe duyarsız containsin aksıne
        links=query.offset(skip).limit(limit=limit).all()#en son query ye all yazınca sorguyu başlatır yoksa şu öncekiler sadece qureye birşeyler eklyordu o kadar
        log.success("Listed user's links successfully")
        return links
    
    
    

    def update_link(self,code:str,update_data:UrlUpdate,user_id:int)->Link:
        log=logger.bind(user_id=user_id,code=code,update_url=str(update_data.original_url))
        log.info("Update link request received")
        original_url=str(update_data.original_url)
        ssrf_ip_check(original_url)
        
        link=self.query.get_link_without_cache(code,user_id)
        CacheService.invalidate_link_cache(code=code,user_id=user_id,link_id=link.id)
        link.original_url=str(original_url)
        link.updated_at=datetime.now(timezone.utc)
        self.db.commit()
        
        log.success("Updated link")
        return link
    
    def delete_link(self,code:str,user_id:int):
        log=logger.bind(user_id=user_id,code=code)
        log.info("Delete link request received")
        link=self.query.get_link_without_cache(code,user_id)
        self.db.delete(link)
        self.db.commit()
        CacheService.invalidate_link_cache(code=code,user_id=user_id,link_id=link.id)
        log.success("Deleted link")

    def generate_qr(self,code:str,user_id:int):
        log=logger.bind(user_id=user_id,code=code)
        log.info("Generate QR request received")
        link=self.query.get_link_without_cache(code,user_id)
        short_url=f"{settings.BASE_URL.rstrip('/')}/r/{link.code}"#şu re stirp çift slash olmasın diye
        qr=QRCode(border=4,box_size=10)
        qr.add_data(short_url)
        qr.make(fit=True)
        img=qr.make_image()
        buffer=BytesIO()#Diskte gerçek dosya oluşturmadan, bellekte dosya gibi davranan alan. # diskte gerçek dosya oluşturmadan bellekte tutuyoruz
        img.save(buffer,format="PNG")#png olarak kayıt ediyoruz 
        buffer.seek(0)#Dosyanın okuma imlecini en başa al.
                    #  Çünkü save() işleminden sonra imleç dosyanın sonunda kalıyor. FastAPI bunu okuyacaksa baştan okumalı.
        log.success("Generated QR")
        return StreamingResponse(buffer,media_type="image/png")#Bu buffer içindeki PNG dosyasını HTTP response olarak gönder. Tarayıcı bunu resim olarak algılasın.




    def code_uret(self,uzunluk:int =5):

        characters=string.ascii_letters+string.digits
        return "".join(random.choices(characters,k=uzunluk))

    def benzersiz_code(self):
        code=self.code_uret()
        while self.db.query(Link).filter(Link.code==code).first():
            code=self.code_uret()
        return code
    def follow_redirect(self,url:str,max_redirects:int=5):
        
        current_url=url
        for i in range(max_redirects):
            ssrf_ip_check(current_url)
            response=httpx.get(
                url=current_url,
                follow_redirects=False,
                timeout=5)
            
            if response.status_code not in REDIRECT_STATUS_CODES:
                return response
            
            location=response.headers.get("location")
            if not location:
                return response
            current_url=urljoin(str(response.url),location)
        print("here aaa")
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="too many redirects")



    def check_link_health(self,code,user_id) ->HealthChecker:
        log=logger.bind(user_id=user_id,code=code)
        log.info("Check  link health request received")
        cache=redis.get(f"link:{user_id}:{code}:health")
        if cache is not None:
            log.success("Checked link health")
            return HealthChecker.model_validate_json(cache)

        else:
            link=self.query.get_user_link(code,user_id)
            original_url=link.original_url
            start_time=time.perf_counter()
           
            try:
                response=self.follow_redirect(original_url)
                response_time_ms=round((time.perf_counter()-start_time)*1000,2)
                
                if 200<=response.status_code<400:
                    health_status="ok"
                else:
                    health_status="broken"
                health_checker= HealthChecker(
                code= link.code,
                original_url=original_url,
                status= health_status,
                status_code= response.status_code,
                response_time_ms= response_time_ms,
                final_url= str(response.url),
                checked_at= datetime.now(timezone.utc),
                error= None
                )
                redis.set(
                    CacheService.check_health(code,user_id),
                    health_checker.model_dump_json(),
                    ex=300)
                log.success("Checked link health")
                return health_checker
            except httpx.RequestError as error:
                response_time_ms=round((time.perf_counter()-start_time)*1000,2)
                health_checker=  HealthChecker(
                code=link.code,
                original_url= link.original_url,
                status="error",
                status_code= None,
                response_time_ms=response_time_ms,
                final_url= None,
                checked_at= datetime.now(timezone.utc),
                error= str(error)
                )
                log.success("Checked link health")
                return health_checker

        
    
