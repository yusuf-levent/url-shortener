from fastapi import HTTPException,status
from models import ClickLog,Link
from sqlalchemy.orm import Session
from datetime import datetime,timezone
from sqlalchemy import func
from services.link_query_service import LinkQueryService
from services.redis_service import redis
from services.cache_service import CacheService
from loguru import logger
class AnalyticsService:
    db:Session
    def __init__(self,db):
        self.db=db
        self.query=LinkQueryService(self.db)

   
    def get_analytics(
            self,
            code:str,
            user_id:int,
            skip:int,
            limit:int,
            start_date:datetime|None,
            end_date:datetime|None)->dict:
        log=logger.bind(#these will be appear in extra
            user_id=user_id,
            code=code,skip=skip,
            limit=limit,
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None)
        log.info("Link analytics search initiated")
        link=self.query.get_link_without_cache(code,user_id)
        query=self.db.query(ClickLog).filter(ClickLog.link_id==link.id)


        if start_date is not None:
            if start_date.tzinfo is None:
                start_date=start_date.replace(tzinfo=timezone.utc)
        if end_date is not None:
            if end_date.tzinfo is None:
                end_date=end_date.replace(tzinfo=timezone.utc)
        if start_date is not None and end_date is not None and start_date>=end_date:

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="start and end dates must be valid")
        

        
        if start_date is not None:
            query=query.filter(ClickLog.clicked_at>=start_date)
        if end_date is not None:
            query=query.filter(ClickLog.clicked_at<=end_date)
        filtered_clicks=query.count()
        total_clicks=self.db.query(ClickLog).filter(ClickLog.link_id==link.id).count()


        click_logs=query.order_by(ClickLog.clicked_at.desc()).offset(skip).limit(limit).all()
        
        log.bind(
            filtered_clicks=filtered_clicks,
            total_clicks=total_clicks
            ).success("Link analytic search successful")
        return {"code":link.code,
            "original_url":link.original_url,
            "total_clicks":total_clicks,
            "filtered_clicks":filtered_clicks,
            "recent_clicks":click_logs,
            "expires_at":link.expires_at.isoformat() if link.expires_at else None,
            "is_active":link.is_active,
            "description":link.description}
    
    
    def get_overview(self,
                     user_id)->dict:
        log=logger.bind(user_id=user_id)
        log.info("Link analytics overview search initiated")

        links=self.db.query(Link).filter(
                            Link.user_id==user_id).all()
        top_links=list(sorted(links,key=lambda x:x.click,reverse=True))[:5]
        
        total_clicks=sum(link.click for link in links)
        
        links_id=[link.id for link in links]

        if not links_id:
            unique_visitors=0
            latest_clicks=[]
        else: 
            unique_visitors=self.db.query(
                                        func.count(
                                        func.distinct(
                                        ClickLog.ip_hash))).filter(
                                        ClickLog.link_id.in_(links_id) ).scalar()
            
            latest_clicks=self.db.query(
                                        ClickLog).filter(
                                        ClickLog.link_id.in_(links_id)).order_by(
                                        ClickLog.clicked_at.desc()).limit(5).all()
     
        active_links=self.db.query(
                                    Link).filter(
                                    Link.user_id==user_id,
                                    Link.is_active.is_(True)).count()
       
        expired_links=self.db.query(
                                    Link).filter(
                                    Link.user_id==user_id,
                                    Link.expires_at<=datetime.now(timezone.utc)).count()
        log.bind(total_links=len(links),total_clicks=total_clicks).success("Link analytics overview search successful")
        return {"total_links":len(links),
                "top_links":top_links,
                "total_clicks":total_clicks,
                "unique_visitors":unique_visitors,
                "active_links":active_links,
                "expired_links":expired_links,
                "latest_clicks":latest_clicks}
    


    def get_clicks(
            self,
            code:str,
            user_id:int,
            skip:int,
            limit:int,
           )->list[ClickLog]:
        logger=logger.bind(user_id=user_id,code=code,skip=skip,limit=limit)
        logger.info("Link click logs search initiated")
        link=self.query.get_link_without_cache(code,user_id)
       
        
        click_log=self.db.query(ClickLog).filter(
                ClickLog.link_id==link.id).order_by(
                    ClickLog.clicked_at.desc()).offset(skip).limit(limit).all()
        logger.bind(total_clicks=len(click_log)).success("Link click logs search successful")
        return click_log
    def get_daily_clicks(self,code:str,user_id:int):
        log=logger.bind(user_id=user_id,code=code)
        log.info("Link daily click analytics search initiated")
        link=self.query.get_link_without_cache(code,user_id)
        day=func.date(ClickLog.clicked_at)
        clicks=self.db.query(
            day,func.count(
                ClickLog.id)).filter(
                    ClickLog.link_id==link.id).group_by(day).order_by(day.asc()).all()
        log.success("Link daily click analytics search successful")
        return [{"date":date,
                 "amount":amount}
                 for date,amount in clicks]



        
    def get_referrers(self,code,user_id)->list[dict]:
        log=logger.bind(user_id=user_id,code=code)
        log.info("Link top referrers  search initiated")
        link=self.query.get_link_without_cache(code,user_id)
        rows=redis.zrevrange(
            CacheService.analytics_top_referrers(link.id),
            0,
            9,
            withscores=True
        )
        
        log.success("Link top referrers search successful")
        return [{"name":referer if referer is not None else "direct",
                "amount":int(amount)}
                for referer,amount in rows]

    def get_languages(self,code:str,user_id:int)->list[dict]:
        log=logger.bind(user_id=user_id,code=code)
        log.info("Link top languages search initiated")
        link=self.query.get_link_without_cache(code,user_id)
        rows=redis.zrevrange(
            CacheService.analytics_top_languages(link.id),
            0,
            9,
            withscores=True
        )
        log.success("Link top languages search successful")
        return [{"name":language if language is not None else "unknown",
                 "amount":int(amount)}
                 for language,amount in rows]
    def get_user_agents(self,code:str,user_id:int)->list[dict]:
        log=logger.bind(user_id=user_id,code=code)
        log.info("Link top user agents search initiated")
        link=self.query.get_link_without_cache(code,user_id)
        rows=redis.zrevrange(
            CacheService.analytics_top_user_agents(link.id),
            0,
            9,
            withscores=True
        )
        log.success("Link top user agents search successful")
        return [{"name":user_agent if user_agent is not None else "unknown",
                 "amount":int(amount)}
                 for user_agent,amount in rows]
    def get_unique_visitors(self,code:str,user_id:int)->dict:
        log=logger.bind(user_id=user_id,code=code)
        log.info("Request for unique visitors of link")
        link=self.query.get_link_without_cache(code,user_id)
        visitors=self.db.query(
            func.count(func.distinct(ClickLog.ip_hash))).filter(
                ClickLog.link_id==link.id).scalar()

        log.bind(unique_visitors=visitors).success("Request for unique visitors of link successfull")
        return {"unique_visitors":visitors}
               