from services.redis_service import redis
class CacheService:

    
    @staticmethod
    def invalidate_link_cache(code:str,user_id:int,link_id:int)->None:
        redis.delete(
            f"link:{user_id}:{code}",
            f"link:{user_id}:{code}:health",
            f"redirect:{code}",
            f"top_referrers:{link_id}",
            f"top_languages:{link_id}",
             f"top_user_agents:{link_id}"
        )
   
  
    @staticmethod
    def redirect(code:str)->str:
        return f"redirect:{code}"
    @staticmethod
    def get_link(code:str,user_id:int)->str:
        return f"link:{user_id}:{code}"
    @staticmethod
    def check_health(code:str,user_id:int)->str:
        return f"link:{user_id}:{code}:health"
    @staticmethod
    def same_ip_redirect_limit(ip_hash:str)->str:
        return f"redirect:ratelimit:ip:{ip_hash}"
    @staticmethod 
    def redirect_same_url_limit(ip_hash:str,code:str)->str:
        return f"redirect:ratelimit:ip:{ip_hash}:{code}"
    @staticmethod
    def url_shorener_limit(user_id:int)->str:
        return f"create:{user_id}"
    @staticmethod
    def analytics_top_referrers(link_id:int)->str:
        return  f"top_referrers:{link_id}"
    @staticmethod
    def analytics_top_languages(link_id:int)->str:
        return f"top_languages:{link_id}"
    @staticmethod
    def analytics_top_user_agents(link_id:int)->str:
        return f"top_user_agents:{link_id}"
    