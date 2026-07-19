
from models import User,Link


def test_admin_get_users(client,make_user_admin,user_payload): 
    answer=client.get("/admin/users",headers=make_user_admin)
    assert answer.status_code==200
    users=answer.json()
    assert any(user["email"]==user_payload.get("email")
               for user in users )

def test_admin_get_user(client,make_user_admin,user_payload,db):
    user=db.query(User).filter(User.email==user_payload.get("email")).first()
    assert user is not None
    answer=client.get(f"/admin/users/{user.id}",headers=make_user_admin)
    assert answer.status_code==200
    assert answer.json()["email"]==user_payload.get("email")





def test_admin_get_links(client,make_user_admin,valid_url):
    
    answer=client.post("/links/",json=valid_url,headers=make_user_admin)
    assert answer.status_code==201
    answer2=client.get("/admin/links",headers=make_user_admin)
    assert answer2.status_code==200
    assert any(link["original_url"]==answer.json()["original_url"]
               for link in answer2.json())
    
def test_admin_get_link(client,make_user_admin,db,valid_url):

    answer=client.post("/links/",json=valid_url,headers=make_user_admin)

    assert answer.status_code==201
    link=db.query(Link).filter(Link.original_url==answer.json()["original_url"]).first()
    link_id=link.id
    answer2=client.get(f"/admin/links/{link_id}",headers=make_user_admin)
    assert answer2.status_code==200
    assert answer2.json()["original_url"]==link.original_url

def test_normal_user_cannot_access_admin_users(auth_headers,client):
    answer=client.get("/admin/users",headers=auth_headers)
    assert answer.status_code==403

def test_admin_requires_authentication(client):
    answer=client.get("/admin/users")
    assert answer.status_code==401

def test_admin_can_see_others_links(client,make_user_admin,auth_headers2,valid_url):
    answer=client.post("/links/",json=valid_url,headers=auth_headers2)
    assert answer.status_code==201
    answer2=client.get("/admin/links",headers=make_user_admin)
    assert answer2.status_code==200
    assert any( link["original_url"]==valid_url.get("original_url") 
               for link in answer2.json())
    

    
def test_admin_can_see_other_users(client,make_user_admin,auth_headers2):
    answer=client.get("/admin/users",headers=make_user_admin)
    assert answer.status_code==200
    assert len(answer.json())>1


def test_admin_stats(client,make_user_admin,auth_headers2,valid_url):
    answer=client.post("/links/",json=valid_url,headers=auth_headers2)
    assert answer.status_code==201
    answer2=client.get("/admin/stats",headers=make_user_admin)
    data=answer2.json()
    assert data["total_users"]>1
    assert data["total_links"]==1
    assert data["active_links"]==1
    assert data["inactive_links"]==0
    assert data["expired_links"]==0
    assert len(data["top_links"])==1
    assert data["total_clicks"]==0

def test_admin_get_nonexisting_user(client,make_user_admin):
    answer=client.get("/admin/users/123",headers=make_user_admin)
    assert answer.status_code==404

def test_admin_get_nonexisting_link(client,make_user_admin):
    answer=client.get("/admin/links/123",headers=make_user_admin)
    assert answer.status_code==404