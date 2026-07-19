from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from models import User ,Link,ClickLog
from datetime import datetime ,timezone
from loguru import logger

class AdminService:
    db:Session
    def __init__(self,db):
        self.db=db


    def get_users(self,skip,limit)->list[User]:
        users=self.db.query(User).offset(skip).limit(limit).all()
        return users
    
    def get_user(self,id)->User|None:
        user=self.db.query(User).filter(User.id==id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= "user is not found")
        return user
    
    def get_links(self,skip,limit,search:str|None=None)->list[Link]:
        if search:
            query=self.db.query(Link).filter(Link.original_url.ilike(f"%{search}%"))
        else:
            query=self.db.query(Link)
        links=query.offset(skip).limit(limit).all()
        return links

    def get_link(self,id)->User|None:
        link=self.db.query(Link).filter(Link.id==id).first()
        if link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= "Link is not found")
        return link
    
    def get_stats(self)->dict:
        total_users=self.db.query(User).count()
        total_links=self.db.query(Link).count()
        total_clicks=self.db.query(ClickLog).count()

        active_links=self.db.query(Link).filter(Link.is_active.is_(True)).count()
        inactive_links=self.db.query(Link).filter(Link.is_active.is_(False)).count()
        now=datetime.now(timezone.utc)
        expired_links=self.db.query(Link).filter(Link.expires_at.isnot(None),Link.expires_at<now).count()

        top_links=self.db.query(Link).order_by(Link.click.desc()).limit(5).all()
        return {
        "total_users": total_users,
        "total_links": total_links,
        "total_clicks": total_clicks,
        "active_links": active_links,
        "inactive_links": inactive_links,
        "expired_links": expired_links,
        "top_links": top_links
    }