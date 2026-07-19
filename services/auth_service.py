from fastapi import HTTPException,status,Request
from schemas import UserCreate,UserLogin
from sqlalchemy.orm import Session
from auth import hash_password,verify_password,create_access_token,create_refresh_token
from models import User ,RefreshToken
from jose import jwt,JWTError
from config import settings
import uuid
from datetime import datetime ,timezone
from services.auth_redis_service import AuthRedisService
import utils
from loguru import logger
from constants import MAX_REGISTER_EMAIL_PER_MINUTE,MAX_REGISTER_IP_PER_MINUTE,MAX_LOGIN_PER_MINUTE,RATE_LIMIT_WINDOW_SECONDS,MAX_REFRESH_PER_MINUTE
class AuthService:
    db:Session
    def __init__(self,db):
        self.db=db
    
        
    def create_user(self,user:UserCreate,ip_hash:str)->User:
        log=logger.bind(email=user.email)
        log.info("Register requested")
        email_hash=utils.hash_email(user.email)
        
        register_ip_hash_key=AuthRedisService.register_limit_ip_hash(ip_hash)
        register_email_hash_key=AuthRedisService.register_limit_email_hash(email_hash)

        ip_rate_limit_check=AuthRedisService.sliding_window_counter(
            key=register_ip_hash_key,
            limit=MAX_REGISTER_IP_PER_MINUTE,
            window_seconds=RATE_LIMIT_WINDOW_SECONDS)
        
        email_rate_limit_check=AuthRedisService.sliding_window_counter(
            key=register_email_hash_key,
            limit=MAX_REGISTER_EMAIL_PER_MINUTE,
            window_seconds=RATE_LIMIT_WINDOW_SECONDS)
        
        if email_rate_limit_check or ip_rate_limit_check:
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many reguest attempts."
                )

        if self.db.query(User).filter(User.email==user.email).first():
            log.warning("This email is already in use")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="email is used")
        
       
        user.password=hash_password(user.password)
        new_user=User(**user.model_dump())
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        log.bind(user_id=new_user.id).success("User registered  successfully")
        return new_user
    
    def login(self,user:UserLogin,ip_hash)->dict:
        log=logger.bind(email=user.email)
        log.info("Login request received")
        email_hash=utils.hash_email(user.email)
        fail_key=AuthRedisService.login_fail_rate(ip_hash,email_hash)
        lock_key=AuthRedisService.login_lock_rate(ip_hash,email_hash)
        AuthRedisService.check_login_lock(lock_key)

        login_rate_key=AuthRedisService.login_rate_limit(ip_hash,email_hash)
        if AuthRedisService.sliding_window_counter(
            key=login_rate_key,
            limit=MAX_LOGIN_PER_MINUTE,
            window_seconds=RATE_LIMIT_WINDOW_SECONDS
            ):

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. "
                )
        db_user=self.db.query(User).filter(User.email==user.email).first()
        
        if  db_user is None or not verify_password(user.password,db_user.password):
            AuthRedisService.lock_login(lock_key,fail_key)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="email or password is wrong "
                                )
        
        AuthRedisService.clear_login_lock_fail(lock_key,fail_key)
        jti=str(uuid.uuid4())
        access_token=create_access_token({
            "email":db_user.email,
            "id":db_user.id,
            "type":"access"
        })
        refresh_token,expires_at=create_refresh_token({
            "email":db_user.email,
            "id":db_user.id,
            "jti":jti,
            "type":"refresh"
        })
        db_refresh_token=RefreshToken(
            user_id=db_user.id,
            jti=jti,
            expires_at=expires_at
        )
        self.db.add(db_refresh_token)
        self.db.commit()
        log.success("User logged in  successfully")
        return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
        }
    
    def logout(self,token_data:str,user_id:int):
        
        log=logger.bind(user_id=user_id)
        log.info("Logout request received")
        try:
            payload=jwt.decode(token_data,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
            if payload.get("type")!="refresh":
                log.warning("Invalid token type")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                     detail="invalid refresh token")
        except JWTError:
            log.warning("JWT decoding failed")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail="invalid refresh token")
        jti=payload.get("jti")
        if jti is None:
            log.warning("JTI claim is missing from refresh token")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail="invalid refresh token")
        
        refresh_token=self.db.query(RefreshToken).filter(
            RefreshToken.jti==jti,
            RefreshToken.user_id==user_id,
            RefreshToken.is_revoked.is_(False)).first()
        
        if refresh_token is None:
            log.warning("Refresh token  not found in Database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                  detail="invalid refresh token")
        
        refresh_token.is_revoked=True
        refresh_token.revoked_at=datetime.now(timezone.utc)
        self.db.commit()
        log.success("User logged out successfully")


    def invalid_refresh(self,lock_key:str,fail_key:str):

        if "unknown" not in lock_key and "unknown" not in fail_key:
            AuthRedisService.lock_refresh(lock_key,fail_key)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="invalid refresh token")





    def refresh_token(self,token_data:str,ip_hash:str):
        logger.info("Refresh access token request received")
        try:
            
            refresh_fail_key=AuthRedisService.refresh_token_fail(ip_hash)
            refresh_lock_key=AuthRedisService.refresh_token_lock(ip_hash)

            AuthRedisService.check_refresh_lock(refresh_lock_key)
            payload=jwt.decode(token_data,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
            
    
            if payload.get("type")!="refresh":
                logger.warning("Invalid token type")
                self.invalid_refresh(refresh_lock_key,refresh_fail_key)
                
        except JWTError:

            self.invalid_refresh(refresh_lock_key,refresh_fail_key)

        old_jti=payload.get("jti")
        user_id=payload.get("id")
        user_email=payload.get("email")

        if old_jti is None or user_email is None or user_id is None:
            logger.warning("JTI claim is missing from refresh token")
            self.invalid_refresh(refresh_lock_key,refresh_fail_key)
        refresh_mutex_key=AuthRedisService.refresh_token_mutex(old_jti)
        
        AuthRedisService.acquire_refresh_attempt_mutex(refresh_mutex_key)  
        
        user=self.db.query(User).filter(User.id==user_id,User.email==user_email).first()
        if user is None:
            self.invalid_refresh(refresh_lock_key,refresh_fail_key)
           

        db_refresh_token=self.db.query(RefreshToken).filter(RefreshToken.jti==old_jti,RefreshToken.user_id==user_id,RefreshToken.is_revoked.is_(False)).first()
        if db_refresh_token  is None:
            self.invalid_refresh(refresh_lock_key,refresh_fail_key)
           
        
        refresh_rate_limit_key=AuthRedisService.refresh_token_rate(user.id)
        rate_check=AuthRedisService.sliding_window_counter(refresh_rate_limit_key,
                                                       MAX_REFRESH_PER_MINUTE,
                                                       RATE_LIMIT_WINDOW_SECONDS)
        if rate_check:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Too many refresh attempts.")


        
        AuthRedisService.clear_refresh_lock_fail(refresh_lock_key,refresh_fail_key)
        db_refresh_token.is_revoked=True
        db_refresh_token.revoked_at=datetime.now(timezone.utc)
        access_token=create_access_token({
            "email":user_email,
            "id":user_id,
            "type":"access"
        })
        jti=str(uuid.uuid4())
        refresh_token,expires_at=create_refresh_token({
            "email":user_email,
            "id":user_id,
            "jti":jti,
            "type":"refresh"
        })
        new_db_refresh_token=RefreshToken(
            user_id=user_id,
            jti=jti,
            expires_at=expires_at
        )
        self.db.add(new_db_refresh_token)
        self.db.commit()
        logger.success("Access token refreshed successfully")
        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "token_type":"bearer"}
