#redirect için 2 ayrı alanda test gerekir 1. get 2.setler kısmı 
from services.redis_service import redis
from services.cache_service import CacheService
from models import User,Link

def test_get_link_with_cache(auth_headers,db,client,valid_url):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}",headers=auth_headers)
    assert answer2.status_code==200
    user_id=db.query(User.id).scalar()
    assert user_id is not None
    cache=redis.get(CacheService.get_link(code,user_id))
    assert cache  is not None


def test_get_link_delete_cache(auth_headers,client,valid_url,db):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}",headers=auth_headers)    
    assert answer2.status_code==200
    answer3=client.delete(f"/links/{code}",headers=auth_headers)
    assert answer3.status_code==204
    user_id=db.query(User.id).scalar()
    cache=redis.get(CacheService.get_link(code,user_id))
    assert cache is None

def test_check_health_cache(auth_headers,client,db,valid_url):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}",headers=auth_headers)    
    assert answer2.status_code==200
    answer3=client.get(f"/links/{code}/health",headers=auth_headers)
    assert answer3.status_code==200

    user_id=db.query(User.id).scalar()
    cache=redis.get(CacheService.check_health(code,user_id))
    assert cache is not  None



def test_check_health_delete_cache(auth_headers,client,valid_url,db):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}",headers=auth_headers)    
    assert answer2.status_code==200
    answer3=client.get(f"/links/{code}/health",headers=auth_headers)
    assert answer3.status_code==200

    user_id=db.query(User.id).scalar()
    answer4=client.delete(f"/links/{code}",headers=auth_headers)
    assert answer4.status_code==204
    cache=redis.get(CacheService.check_health(code,user_id))
    assert cache is None


def test_redirect_cache(shortener,client,db):
    code=shortener.json()["code"]
    answer=client.get(f"/r/{code}",follow_redirects=False)
    assert answer.status_code==302
    cache=redis.get(CacheService.redirect(code))
    assert cache is not None
    link_id=db.query(Link.id).scalar()
    cache=redis.zrevrange(CacheService.analytics_top_referrers(link_id),0,-1)
    assert  len(cache)>0
    cache=redis.zrevrange(CacheService.analytics_top_user_agents(link_id),0,-1)
    assert  len(cache)>0
    cache=redis.zrevrange(CacheService.analytics_top_referrers(link_id),0,-1)
    assert  len(cache)>0

def test_redirect_delete_cache(auth_headers,client,valid_url,db):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]

    answer=client.get(f"/r/{code}",follow_redirects=False)
    assert answer.status_code==302
    answer4=client.delete(f"/links/{code}",headers=auth_headers)
    assert answer4.status_code==204
    cache=redis.get(CacheService.redirect(code))
    assert cache is  None
    link_id=db.query(Link.id).scalar()
    assert redis.exists(CacheService.analytics_top_referrers(link_id)) == 0
    assert redis.exists(CacheService.analytics_top_languages(link_id)) == 0
    assert redis.exists(CacheService.analytics_top_user_agents(link_id)) == 0


    
    
    
