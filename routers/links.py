from fastapi import status,APIRouter,Depends,Query
from models import User
from database import get_db
from sqlalchemy.orm import Session
from schemas import UrlCreate,UrlUpdate,UrlResponse,HealthChecker,LinkCache
from auth import get_current_user
from services import link_service
router=APIRouter(prefix="/links",tags=["links"])





@router.get("/health")
def health():
    return {"status":"ok"}

@router.get("/",status_code=status.HTTP_200_OK,response_model=list[UrlResponse])
def get(db:Session=Depends(get_db),
        current_user:User=Depends(get_current_user),
        skip:int=Query(0,ge=0),
        limit:int=Query(10,ge=1,le=100),
        min_click:int|None=Query(None,ge=0),
        search:str|None=Query(None,min_length=3)):
    service=link_service.LinkService(db)
    return service.list_user_links(current_user.id,skip,limit,min_click,search)

@router.get(
        "/{code}/health",
        status_code=status.HTTP_200_OK,
        response_model=HealthChecker
        )
def check_link_health(
    code:str,
    db:Session=Depends(get_db),
    current_user:User=Depends(
        get_current_user)
        ):
    service=link_service.LinkService(db)
    
    return service.check_link_health(
        code,
        current_user.id)


@router.get("/{code}/qr",status_code=status.HTTP_200_OK)
def generate_qr(code:str,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    service=link_service.LinkService(db)
    return service.generate_qr(code,current_user.id)
    

@router.get("/{code}",status_code=status.HTTP_200_OK,response_model=LinkCache)
def get_one_link(code:str,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    service=link_service.LinkQueryService(db)
    return service.get_user_link(code,current_user.id)



@router.post("/",status_code=status.HTTP_201_CREATED,response_model=UrlResponse)
def shortener(url:UrlCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    service=link_service.LinkService(db)
    return service.create_link(url=url,user_id=current_user.id)


@router.put("/{code}",status_code=status.HTTP_200_OK,response_model=UrlResponse)
def update(code:str,update:UrlUpdate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    service=link_service.LinkService(db)
    return service.update_link(code,update,current_user.id)
    
    
@router.delete("/{code}",status_code=status.HTTP_204_NO_CONTENT)
def delete(code:str,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    service=link_service.LinkService(db)
    service.delete_link(code,current_user.id)
