from fastapi import APIRouter,status,Depends,Request
from schemas import UserCreate,UserLogin,UserOut,RefreshTokenRequest,TokenResponse
from database import get_db
from auth import get_current_user
from sqlalchemy.orm import Session
from models import User 
from services import auth_service
router=APIRouter(prefix="/users",tags=["users"])

@router.get("/health")
def health():
    return {"status":"ok"}

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=UserOut)
def creat_user(user:UserCreate,request:Request,db:Session=Depends(get_db)):
    service=auth_service.AuthService(db)
    ip_hash=request.state.ip_hash
    return service.create_user(user,ip_hash)



@router.post("/login",status_code=status.HTTP_201_CREATED,response_model=TokenResponse)
def login(user:UserLogin,request:Request,db:Session=Depends(get_db)):
    service=auth_service.AuthService(db)
    ip_hash=request.state.ip_hash
    return service.login(user,ip_hash)


@router.post("/logout",status_code=status.HTTP_204_NO_CONTENT)
def logout(token_data:RefreshTokenRequest,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    service=auth_service.AuthService(db)
    return service.logout(token_data.refresh_token,current_user.id)




@router.post("/refresh",response_model=TokenResponse,status_code=status.HTTP_200_OK)
def refresh_token(token_data:RefreshTokenRequest,request:Request,db:Session=Depends(get_db)):
    service=auth_service.AuthService(db)
    ip_hash=request.state.ip_hash
    return service.refresh_token(token_data.refresh_token,ip_hash)
