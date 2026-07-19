from services.redis_service import redis
import time
from fastapi import HTTPException ,status
from constants import MAX_WRONG_LOGIN,MAX_WRONG_REFRESH_TOKEN
class AuthRedisService:
    @staticmethod
    def sliding_window_counter(key: str, limit: int, window_seconds: int) -> bool:
        if "unknown" in key:
            return False
        now = int(time.time())
        current_window = now // window_seconds
        previous_window = current_window - 1

        current_key = f"{key}:{current_window}"
        previous_key = f"{key}:{previous_window}"

        current_count = redis.incr(current_key)#login için bir kere artırdık
        if current_count == 1:
            redis.expire(current_key, window_seconds * 2)#burada da sornaki window kullansın diye exprie süresini diğer windowuda kapsayacak şekilde ayarladık

        previous_count_raw = redis.get(previous_key)
        previous_count = int(previous_count_raw) if previous_count_raw else 0

        elapsed_in_window = now % window_seconds#windowun kaçıncı saniyesinde onu bulur
        previous_weight = (window_seconds - elapsed_in_window) / window_seconds#ona göre ağırlığı hesaplar

        estimated_count = current_count + (previous_count * previous_weight)
        return estimated_count > limit
    

    
    @staticmethod
    def check_refresh_lock(lock_key:str):
        if "unknown" in lock_key:
            return False
        ttl=redis.ttl(lock_key)
        if ttl>0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many refresh attempts. Try again in {ttl} seconds."
            )
    @staticmethod
    def acquire_refresh_attempt_mutex(mutex_key):
          is_lock_acquired=redis.set(mutex_key,"1",ex=3,nx=True)
          if not is_lock_acquired:
            ttl=redis.ttl(mutex_key)
        
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many refresh attempts. Try again in {ttl if ttl>0 else 3} seconds."
            )
          
    @staticmethod
    def lock_refresh(lock_key:str,fail_key:str):
        
        fail_count=redis.incr(fail_key,1)
        if fail_count==1:
            redis.expire(fail_key,60*60)
        elif fail_count>=MAX_WRONG_REFRESH_TOKEN:
            redis.setex(lock_key,60*5,"1")
    
    @staticmethod
    def clear_refresh_lock_fail(lock_key:str,fail_key:str):
        if "unknown" in fail_key or "unknown" in lock_key:
            return False
        redis.delete(fail_key,lock_key)


    @staticmethod
    def check_login_lock(lock_key:str)->None:
        ttl=redis.ttl(lock_key)
        if ttl>0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts. Try again in {ttl} seconds."
            )
   
        
    @staticmethod
    def lock_login(lock_key:str,fail_key:str)->None:
        
        fail_count=redis.incr(fail_key)
        if fail_count==1:
            redis.expire(fail_key,60*60)#failed i tutyor 1 saat boyunca eğer sıkıntı olursa count arıtyor ve ona göre lock atıyor
        if fail_count>=15:
            redis.setex(lock_key,60*15,"1")
        elif fail_count>=10:
            redis.setex(lock_key,60*10,"1")
        elif fail_count>=MAX_WRONG_LOGIN:
            redis.setex(lock_key,60*5,"1")
     
    @staticmethod
    def clear_login_lock_fail(lock_key,fail_key):
        redis.delete(lock_key,fail_key)
        



    @staticmethod
    def register_limit_ip_hash(ip_hash:str)->str:
        return f"auth:register:{ip_hash}"
    @staticmethod
    def register_limit_email_hash(email_hash:str)->str:
        return f"auth:register:{email_hash}"
    @staticmethod
    def login_rate_limit(ip_hash:str,email_hash:str)->str:
        return f"auth:login:rate:{ip_hash}:{email_hash}"
    @staticmethod
    def login_fail_rate(ip_hash:str,email_hash:str)->str:
        return f"auth:login:fail:{ip_hash}:{email_hash}"
    @staticmethod
    def login_lock_rate(ip_hash:str,email_hash:str)->str:
        return f"auth:login:lock:{ip_hash}:{email_hash}"
    @staticmethod
    def refresh_token_rate(user_id:int)->str:
        return f"auth:refresh:rate:{user_id}"
    @staticmethod
    def refresh_token_fail(ip_hash:str)->str:
        return f"auth:refresh:fail:{ip_hash}"
    @staticmethod
    def refresh_token_lock(ih_hash:str)->str:
        return f"auth:refresh:lock:{ih_hash}"
    
    @staticmethod
    def refresh_token_mutex(jti:str)->str:
        return f"auth:refresh:mutex:{jti}"