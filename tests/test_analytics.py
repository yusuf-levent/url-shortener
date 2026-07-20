from datetime import datetime,timezone,timedelta


def test_get_analytics(get_links,client,auth_headers):
    answer,code=get_links
    answer2=client.get(f"/analytics/links/{code}",headers=auth_headers)
    assert answer2.status_code==200
    assert answer2.json()["code"]==code
    links=answer.json()
    assert any(link["original_url"]==answer2.json()["original_url"] for link in links)

def test_cannot_get_analytics_with_wrong_user(get_links,client,auth_headers2):
    code=get_links[1]
    answer2=client.get(f"/analytics/links/{code}",headers=auth_headers2)
    assert answer2.status_code==403

    
def test_cannot_get_analytics_without_token(get_links,client):
    code=get_links[1]
    answer2=client.get(f"/analytics/links/{code}")
    assert answer2.status_code==401

def test_cannot_get_analytics_of_wrong_url(get_links,client,auth_headers):

    answer=client.get(f"/analytics/links/aaaa",headers=auth_headers)
    assert answer.status_code==404

def test_overview(get_links,client,auth_headers):
    answer=client.get("/analytics/overview",headers=auth_headers)
    assert answer.status_code==200
    assert answer.json()["total_links"]>0
    
def test_cannot_get_overview_without_token(get_links,client):
    answer=client.get("/analytics/overview")
    assert answer.status_code==401

def test_clicks(get_links,client,auth_headers):
    answer,code=get_links
    answer2=client.get(f"/analytics/links/{code}/clicks",headers=auth_headers)
    assert answer2.status_code==200

def test_cannot_get_clicks_with_wrong_user(get_links,client,auth_headers2):
    code=get_links[1]
    answer=client.get(f"/analytics/links/{code}/clicks",headers=auth_headers2)
    assert answer.status_code==403
def test_cannot_get_clicks_without_token(get_links,client):
    code=get_links[1]
    answer=client.get(f"/analytics/links/{code}/clicks")
    assert answer.status_code==401
def test_cannot_get_clicks_of_wrong_url(get_links,client,auth_headers):
    
    answer2=client.get(f"/analytics/links/code/clicks",headers=auth_headers)
    assert answer2.status_code==404


def test_get_analytics_with_date_limiting(get_links,client,auth_headers):
    answer,code=get_links
    one_min_ago=datetime.now(timezone.utc)-timedelta(minutes=1)
    now=datetime.now(timezone.utc)
    params={"start_date":one_min_ago.isoformat(),"end_date":now.isoformat()}
    answer2=client.get(f"/analytics/links/{code}",params=params,headers=auth_headers)
    assert answer2.status_code==200
    assert answer2.json()["code"]==code
    links=answer.json()
    assert any(link["original_url"]==answer2.json()["original_url"] for link in links)

def test_get_analytics_start_date_bigger_than_end_date(get_links,client,auth_headers):
    answer,code=get_links
    one_min_ago=datetime.now(timezone.utc)-timedelta(minutes=1)
    now=datetime.now(timezone.utc)
    params={"start_date":now.isoformat(),"end_date":one_min_ago.isoformat()}
    answer2=client.get(f"/analytics/links/{code}",params=params,headers=auth_headers)
    assert answer2.status_code==400
    
def test_get_daily_clicks(client,auth_headers,valid_url):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/r/{code}",follow_redirects=False)
    assert answer2.status_code==302
    answer3=client.get(f"/analytics/links/{code}/daily-clicks",headers=auth_headers)
    assert answer3.status_code==200
    datas=answer3.json()
    assert any(data["amount"]==1 for data in datas)
    
def test_get_language(client,auth_headers,valid_url):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/r/{code}",follow_redirects=False)
    assert answer2.status_code==302
    answer2=client.get(f"/analytics/links/{code}/languages",headers=auth_headers)
    assert answer2.status_code==200
    datas=answer2.json()
    assert any(data["amount"]==1 for data in datas)

def test_get_user_agent(client,auth_headers,valid_url):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/r/{code}",follow_redirects=False)
    assert answer2.status_code==302
    answer2=client.get(f"/analytics/links/{code}/user-agents",headers=auth_headers)
    assert answer2.status_code==200
    datas=answer2.json()
    assert any(data["amount"]==1 for data in datas)

def test_get_unique_visitors(client,auth_headers,valid_url):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/r/{code}",follow_redirects=False)
    assert answer2.status_code==302
    answer2=client.get(f"/analytics/links/{code}/unique-visitors",headers=auth_headers)
    assert answer2.status_code==200
    assert answer2.json()["unique_visitors"]==1

def test_get_referrers(client,auth_headers,valid_url):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/r/{code}",follow_redirects=False)
    assert answer2.status_code==302
    answer2=client.get(f"/analytics/links/{code}/referrers",headers=auth_headers)
    assert answer2.status_code==200
    datas=answer2.json()
    assert any(data["amount"]==1 for data in datas)

def test_get_referrers_without_token(client,valid_url,auth_headers):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/r/{code}",follow_redirects=False)
    assert answer2.status_code==302
    answer2=client.get(f"/analytics/links/{code}/referrers")
    assert answer2.status_code==401
def test_get_referrers_with_wrong_user(client,valid_url,auth_headers,auth_headers2):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/r/{code}",follow_redirects=False)
    assert answer2.status_code==302
    answer2=client.get(f"/analytics/links/{code}/referrers",headers=auth_headers2)
    assert answer2.status_code==403

