from database import Base
from sqlalchemy import Column,Integer,String,ForeignKey,Boolean,DateTime,Text,func,Enum
from sqlalchemy.orm import relationship
from enum import StrEnum,auto
class UserRoles(StrEnum):
    User=auto()
    Admin=auto()


class Link(Base):
    __tablename__="links"
    id=Column(Integer,primary_key= True,autoincrement=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    code=Column(String(20),index=True,unique=True,nullable=False)
    original_url=Column(String(255),nullable=False)
    click=Column(Integer,default=0)
    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at=Column(DateTime(timezone=True),nullable=True)
    is_active=Column(Boolean,default=True,nullable= False)
    expires_at=Column(DateTime(timezone=True),nullable=True)
    description=Column(Text,nullable=True)
    user=relationship("User",back_populates="links")
    click_logs=relationship("ClickLog",back_populates="link",cascade="all,delete-orphan")


class User(Base):
    __tablename__="users"
    id=Column(Integer,autoincrement=True,primary_key=True)
    email=Column(String(255),nullable=False,unique=True)
    password=Column(String(255),nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    role=Column(Enum(UserRoles),default=UserRoles.User,nullable=False)
    links=relationship("Link",back_populates="user")
    refresh_token=relationship("RefreshToken",back_populates="user")

class RefreshToken(Base):
    __tablename__="refresh_tokens"
    id=Column(Integer,primary_key=True,autoincrement=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    is_revoked=Column(Boolean,default=False,nullable=False)
    jti=Column(String(100),unique=True,index=True,nullable= False)
    expires_at=Column(DateTime(timezone=True),nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    revoked_at=Column(DateTime(timezone=True),nullable=True)
    user=relationship("User",back_populates="refresh_token")



class ClickLog(Base):
    __tablename__="click_logs"
    id=Column(Integer,primary_key=True,autoincrement=True)
    link_id=Column(Integer,ForeignKey("links.id",ondelete="CASCADE"),nullable=False)
    clicked_at=Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    ip_hash=Column(String(255),nullable=False)
    user_agent=Column(String(255),nullable=True)
    referer=Column(String(255),nullable=True)
    accept_language=Column(String(255),nullable=True)
    link=relationship("Link",back_populates="click_logs")