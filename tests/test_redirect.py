
from datetime import timedelta
from models import Link
from constants import  MAX_REDIRECTS_PER_MINUTE_SAME_URL


def test_redirect(client,shortener,db):
    answer=shortener
    code=answer.json()["code"]
    link=db.query(Link).filter(Link.code==code).first()
    clicks=link.click
    answer2=client.get(f"/r/{code}",follow_redirects=False)#bunun saysesinde linki test takip etmeeycek
    
    clicks +=1
    db.refresh(link)
    assert clicks==link.click
    assert answer2.status_code==302
    assert answer2.headers["location"] == shortener.json()["original_url"]


def test_cannot_redirect_passive_url(client,auth_headers,valid_url,db):
    payload={"original_url":valid_url.get("original_url"),"expires_at":valid_url.get("expires_at"),"is_active":False}

    answer=client.post("/links/",json=payload,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    link=db.query(Link).filter(Link.code==code).first()
    clicks=link.click
    answer2=client.get(f"/r/{code}",follow_redirects=False)
    assert answer2.status_code==400
    assert clicks==link.click

def test_cannot_redirect_expired_url(client,shortener,db):
    answer=shortener
    code=answer.json()["code"]
    link=db.query(Link).filter(Link.code==code).first()
    assert link is not None
    link.expires_at -=timedelta(days=10)
    db.commit()
    link=db.query(Link).filter(Link.code==code).first()
    clicks=link.click
    redirected_response=client.get(f"/r/{code}",follow_redirects=False)
    assert redirected_response.status_code==400
    assert redirected_response.json()["detail"] == "expires_at must be future time"
    assert clicks==link.click


def test_redirect_global_ip_rate_limit(client,shortener,auth_headers,expires_at,db):
    answer=shortener
    code=answer.json()["code"]
    for i in range(MAX_REDIRECTS_PER_MINUTE_SAME_URL):
        answer2=client.get(f"/r/{code}",follow_redirects=False)
        assert answer2.status_code==302
    

    payload={"original_url":"https://www.sqlalchemy.org/","expires_at":expires_at.isoformat()}
    answer=client.post("/links/",json=payload,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    for i in range(MAX_REDIRECTS_PER_MINUTE_SAME_URL):
        answer2=client.get(f"/r/{code}",follow_redirects=False)
        assert answer2.status_code==302


    payload={"original_url":"https://www.postgresql.org/","expires_at":expires_at.isoformat()}
    answer=client.post("/links/",json=payload,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    for i in range(MAX_REDIRECTS_PER_MINUTE_SAME_URL):
        answer2=client.get(f"/r/{code}",follow_redirects=False)
        assert answer2.status_code==302
    payload={"original_url":"https://alembic.sqlalchemy.org/","expires_at":expires_at.isoformat()}
    answer=client.post("/links/",json=payload,headers=auth_headers)
    assert answer.status_code==201 
    code=answer.json()["code"]
    link=db.query(Link).filter(Link.code==code).first()
    clicks=link.click
    answer2=client.get(f"/r/{code}",follow_redirects=False)
    assert answer2.status_code==429
    assert answer2.json()["detail"] =="too many requests from same ip"
    assert clicks==link.click

def test_redirect_global_ip_rate_limit_same_url(client,shortener,db):
    answer=shortener
    code=answer.json()["code"]
    for i in range(MAX_REDIRECTS_PER_MINUTE_SAME_URL):
        answer2=client.get(f"/r/{code}",follow_redirects=False)
        assert answer2.status_code==302
    link=db.query(Link).filter(Link.code==code).first()
    clicks=link.click
    answer2=client.get(f"/r/{code}",follow_redirects=False)
    assert answer2.status_code==429
    assert clicks==link.click
