from pydantic import BaseModel,ConfigDict,EmailStr,HttpUrl,field_validator,Field,computed_field
from typing import Literal
from config import settings
import string
from datetime import datetime,timezone
from models import UserRoles

class LinkCache(BaseModel):
    code:str
    original_url:str
    is_active:bool
    expires_at:datetime|None=None
    description:str|None =None
    updated_at:datetime|None=None
    created_at:datetime
    @computed_field
    @property
    def short_url(self)->str:
        return f"{settings.BASE_URL.rstrip('/')}/r/{self.code}"
    model_config=ConfigDict(from_attributes=True)
class UrlResponse(LinkCache):
    click:int
class UrlCreate(BaseModel):
    original_url:HttpUrl
    expires_at:datetime|None=None
    is_active:bool=True
    description:str|None=None
    custom_code:str|None=Field(
        default=None,
        max_length=30,
        min_length=5,
        pattern=r"^[a-z0-9_-]+$")
    @field_validator("custom_code",mode="before")
    @classmethod
    def validate_custom_code(cls,value:str)->str|None:
        if value is None:
            return None
        value=value.strip().lower()
        if value=="":
            return None
        return value
    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls,value)->datetime|None:

        if value is None :
            return None
        now=datetime.now(timezone.utc)
        if value.tzinfo is None:#burada da kullancıdan naive gelirse zaman dilimi ekliyoruz
            value=value.replace(tzinfo=timezone.utc)
        if value<=now:
            raise ValueError("expires_at must be a future datetime")
        return value
       
    
class UrlUpdate(BaseModel):
    original_url:HttpUrl

class UserCreate(BaseModel):
    email:EmailStr
    password:str=Field(...,min_length=8)
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls,value:str)->str:
        if not any(char in string.punctuation for char in value):
             raise ValueError("password must contains at least special character")
        if not any( char.isdigit() for char in value):
            raise ValueError("password must contains at least one number")
        if not any( char.isupper() for char in value):
             raise ValueError("password must contains at least one uppercase letter")
        if not any( char.islower() for char in value):
             raise ValueError("password must contains at least one lowercase")
        return value
class UserLogin(BaseModel):
    email:EmailStr
    password:str
class UserOut(BaseModel):
    id:int
    email:str
    created_at:datetime
    role:UserRoles
    links:list[UrlResponse]=Field(default_factory=list)
    model_config=ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    refresh_token:str
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ClickLogOut(BaseModel):
    clicked_at:datetime
    ip_hash:str
    user_agent:str|None=None
    referer:str|None=None
    accept_language:str|None=None
    model_config=ConfigDict(from_attributes=True)



class LinkAnalyticsOut(BaseModel):
    code:str
    original_url:str
    expires_at:datetime|None
    is_active:bool
    description:str|None
    filtered_clicks:int
    total_clicks:int
    recent_clicks:list[ClickLogOut]
    @computed_field
    @property
    def short_url(self)->str:
        return f"{settings.BASE_URL.rstrip('/')}/r/{self.code}"
    model_config=ConfigDict(from_attributes=True)

    
class AnalyticsOverviewOut(BaseModel):
    total_links:int
    top_links:list[UrlResponse]
    total_clicks:int
    unique_visitors:int
    active_links:int
    expired_links:int
    latest_clicks:list[ClickLogOut]=Field(default_factory=[])
    

class HealthChecker(BaseModel):
    code:str
    original_url:str
    status:Literal["ok","broken","error"]
    status_code:int|None=None
    response_time_ms:float
    final_url:str|None=None
    checked_at:datetime
    error:str|None=None
    model_config=ConfigDict(from_attributes=True)

class AdminStatsOut(BaseModel):
    total_users:int
    total_links:int
    total_clicks:int
    active_links:int
    inactive_links:int
    expired_links:int
    top_links:list[UrlResponse]=Field(default_factory=list)
    model_config=ConfigDict(from_attributes=True)

class AnalyticsCountOut(BaseModel):
    name:str
    amount:int

class AnalyticsDailyOut(BaseModel):
    date:datetime
    amount:int

class RedirectLink(BaseModel):
    id:int
    original_url:str
    expires_at:datetime|None
    is_active:bool
    model_config=ConfigDict(from_attributes=True)

