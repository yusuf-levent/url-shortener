from fastapi import Depends,APIRouter,Request
from sqlalchemy.orm import Session
from database import get_db
from services import redirect_service

router=APIRouter(prefix="/r",tags=["redirect"])


@router.get("/{code}")
def redirect(code:str,request:Request,db:Session=Depends(get_db)):
    service=redirect_service.RedirectService(db)
    ip_hash=request.state.ip_hash
    return service.redirect(code,request,ip_hash)