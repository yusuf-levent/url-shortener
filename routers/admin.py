from fastapi import Depends,status,APIRouter,Query
from models import User
from database import get_db
from sqlalchemy.orm import Session
from auth import require_admin
from services import admin_service
from schemas import UserOut,UrlResponse,AdminStatsOut
router=APIRouter(prefix="/admin",tags=["admin"])

@router.get("/users",status_code=status.HTTP_200_OK,response_model=list[UserOut])
def get_users(
    db:Session=Depends(get_db),
    current_user:User=Depends(require_admin),
    skip:int=Query(default=0,ge=0),
    limit:int=Query(default=10,ge=1,le=100)):
    service=admin_service.AdminService(db)
    return service.get_users(skip=skip,limit=limit)

@router.get("/users/{id}",status_code=status.HTTP_200_OK,response_model=UserOut)
def get_user(id:int,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    service=admin_service.AdminService(db)
    return service.get_user(id=id)

@router.get("/links",status_code=status.HTTP_200_OK,response_model=list[UrlResponse])
def get_links(
    db:Session=Depends(get_db),
    current_user:User=Depends(require_admin),
    skip:int=Query(default=0,ge=0),
    limit:int=Query(default=10,ge=1,le=100),
    search:str|None=Query(None,min_length=3,max_length=50)):
    service=admin_service.AdminService(db)
    return service.get_links(skip=skip,limit=limit,search=search)

@router.get("/links/{id}",status_code=status.HTTP_200_OK,response_model=UrlResponse)
def get_link(id:int,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    service=admin_service.AdminService(db)
    return service.get_link(id=id)


@router.get("/stats",status_code=status.HTTP_200_OK,response_model=AdminStatsOut)
def get_stats(db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    service=admin_service.AdminService(db)
    return service.get_stats()