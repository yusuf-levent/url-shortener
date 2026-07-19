from fastapi import Depends,status,APIRouter,Query
from models import User
from database import get_db
from sqlalchemy.orm import Session
from auth import get_current_user
from schemas import LinkAnalyticsOut,ClickLogOut,AnalyticsOverviewOut,AnalyticsCountOut,AnalyticsDailyOut
from services import analytics_service
from datetime import datetime
router=APIRouter(prefix="/analytics",tags=["analytics"])



@router.get(
          "/links/{code}/daily-clicks",
          status_code=status.HTTP_200_OK,
          response_model=list[AnalyticsDailyOut]
          )
def get_daily_clicks(
     code:str, 
     db:Session=Depends(get_db),
     current_user:User=Depends(get_current_user)):
     service=analytics_service.AnalyticsService(db)
     return service.get_daily_clicks(code,current_user.id)

@router.get(
          "/links/{code}/referrers",
          status_code=status.HTTP_200_OK,
          response_model=list[AnalyticsCountOut]
          )
def get_referrers(
     code:str,
     db:Session=Depends(get_db),
     current_user:User=Depends(get_current_user)
     ):
     service=analytics_service.AnalyticsService(db)
     return service.get_referrers(code,current_user.id)


@router.get(
          "/links/{code}/languages",
          status_code=status.HTTP_200_OK,
          response_model=list[AnalyticsCountOut]
          )
def get_languages(
     code:str,
     db:Session=Depends(get_db),
     current_user:User=Depends(get_current_user)
     ):
     service=analytics_service.AnalyticsService(db)
     return service.get_languages(code,current_user.id)

@router.get(
          "/links/{code}/user-agents",
          status_code=status.HTTP_200_OK,
          response_model=list[AnalyticsCountOut]
          )
def get_user_agents(
     code:str,
     db:Session=Depends(get_db),
     current_user:User=Depends(get_current_user)
     ):
     service=analytics_service.AnalyticsService(db)
     return service.get_user_agents(code,current_user.id)


@router.get(
          "/links/{code}/unique-visitors",
          status_code=status.HTTP_200_OK
          )
def get_unique_visitors(
     code:str,
     db:Session=Depends(get_db),
     current_user:User=Depends(get_current_user)
     ):
     service=analytics_service.AnalyticsService(db)
     return service.get_unique_visitors(code,current_user.id)

@router.get(
          "/links/{code}",
          status_code=status.HTTP_200_OK,
          response_model=LinkAnalyticsOut
          )
def get_analytics(
    code:str,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user),
    skip:int=Query(default=0,ge=0),
    limit:int=Query(default=10,ge=1,le=100),
    start_date:datetime|None=Query(
                   None,
                   description="Start date for searching . Format: YYYY-MM-DDTHH:MM:SS",
                    examples=["2026-07-06T23:59:59"]),
    end_date:datetime|None=Query(
                   None,
                   description="End date for searching. Format: YYYY-MM-DDTHH:MM:SS",
                    examples=["2026-07-06T23:59:59"])):
    service=analytics_service.AnalyticsService(db)
    return service.get_analytics(code,current_user.id,skip,limit,start_date,end_date)






@router.get(
          "/overview",
          status_code=status.HTTP_200_OK,
          response_model=AnalyticsOverviewOut
          )
def get_overview(
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user),
    ):
    service=analytics_service.AnalyticsService(db)
    return service.get_overview(current_user.id)



@router.get(
          "/links/{code}/clicks",
          status_code=status.HTTP_200_OK,
          response_model=list[ClickLogOut]
          )
def get_clicks(code:str,
              db:Session=Depends(get_db),
              current_user:User=Depends(get_current_user),
              skip:int=Query(default=0,ge=0),
              limit:int=Query(default=10,ge=1,le=100)
              ):
        service=analytics_service.AnalyticsService(db)
        return service.get_clicks(code,current_user.id,skip,limit)


