
from urllib.parse import urljoin
import pytest
from constants import RESERVED_CODES,MAX_REDIRECTS_PER_MINUTE_SAME_URL
import re
from datetime import datetime,timezone,timedelta
import httpx
from models import User
from services.cache_service import CacheService
from services.redis_service import redis
import socket
VALID_ALIAS_PATTERN = re.compile(r"^[a-z0-9_-]+$")

VALID_RESERVED_CODES = [
    code for code in RESERVED_CODES
    if 5 <= len(code) <= 30 and VALID_ALIAS_PATTERN.fullmatch(code)
]

INVALID_RESERVED_CODES = [
    code for code in RESERVED_CODES
    if code not in VALID_RESERVED_CODES
]



invalid_custom_codes = [
    "abc",                       # 5 karakterden kısa
    "github/test",               # slash var
    "github test",               # boşluk var
    "<script>",                  # özel karakter var
    "çalışma",                   # Türkçe karakter var
    "github.com",                # nokta var
    "test@123",                  # @ var
    "test#123",                  # # var
    "my$link",                   # $ var
    "a" * 31,                    # 30 karakterden uzun
]
valid_urls = [
    "https://example.com/",
    "https://www.google.com/",
    "https://github.com/",
    "https://www.python.org/",
    "https://www.postgresql.org/",
    "https://www.sqlalchemy.org/",
    "https://docs.pydantic.dev/",
    "https://alembic.sqlalchemy.org/",
    "https://www.docker.com/",
    "https://render.com/",
    "https://www.cloudflare.com/",
    "https://www.wikipedia.org/",
    "https://www.mozilla.org/",
    "https://stackoverflow.com/",
]

invalid_urls = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:5432",
    "http://10.0.0.1",
    "http://10.10.10.10",
    "http://172.16.0.1",
    "http://172.31.255.255",
    "http://192.168.1.1",
    "http://192.168.100.100",
    "http://169.254.169.254",
    "http://224.0.0.1",
    "http://0.0.0.0",
    "http://[::1]",
    "http://[fc00::1]",
    "http://[fe80::1]",
    "http://[::ffff:127.0.0.1]"
]

def test_generate_qr(client,auth_headers,shortener):
    
    code=shortener.json()["code"]
    answer2=client.get(f"/links/{code}/qr",headers=auth_headers)
    assert answer2.status_code==200
    assert answer2.headers["content-type"]=="image/png"
    assert len(answer2.content) > 0#body boşmu yoksa png dönmüşmü diye kontrol 
    assert answer2.content.startswith(b"\x89PNG\r\n\x1a\n")#this checks if png file has the byte signiture at begining
def test_generate_qr_with_wrong_user(client,auth_headers2,shortener):
    
    code=shortener.json()["code"]
    answer2=client.get(f"/links/{code}/qr",headers=auth_headers2)
    assert answer2.status_code==403


def test_generate_qr_with_wrong_code(client,auth_headers):
    answer2=client.get(f"/links/aaa/qr",headers=auth_headers)
    assert answer2.status_code==404


def test_generate_qr_without_token(client,shortener):  
    code=shortener.json()["code"]
    answer2=client.get(f"/links/{code}/qr")
    assert answer2.status_code==401


def test_shortener_same_url(client,auth_headers,shortener,valid_url):
    payload={"original_url":valid_url.get("original_url"),"expires_at":valid_url.get("expires_at")}
    answer=client.post("/links/",json=payload,headers=auth_headers)
    assert answer.status_code==400

def test_shortener_without_token(client,valid_url):
    answer=client.post("/links/",json=valid_url)
    assert answer.status_code==401

def test_shortener_with_custom_code(client,auth_headers,valid_url):
    payload={"original_url":valid_url.get("original_url"),"custom_code":"aaaaa","expires_at":valid_url.get("expires_at")}
    answer=client.post("/links/",json=payload,headers= auth_headers)
    assert answer.status_code==201
    assert answer.json()["code"]==payload.get("custom_code")
    assert answer.json()["original_url"]==valid_url.get("original_url")


    
@pytest.mark.parametrize("custom_code",invalid_custom_codes)
def test_shortener_with_wrong_custom_codes(client,auth_headers,valid_url,custom_code):
    payload={"original_url":valid_url.get("original_url"),"custom_code":custom_code,"expires_at":valid_url.get("expires_at")}
    answer=client.post("/links/",json=payload,headers= auth_headers)
    assert answer.status_code==422

@pytest.mark.parametrize("custom_code",VALID_RESERVED_CODES)
def test_reserved_custom_codes_with_400(client,auth_headers,valid_url,custom_code):
    payload={"original_url":valid_url.get("original_url"),"custom_code":custom_code,"expires_at":valid_url.get("expires_at")}
    answer=client.post("/links/",json=payload,headers= auth_headers)
    assert answer.status_code==400

@pytest.mark.parametrize("custom_code",INVALID_RESERVED_CODES)
def test_reserved_custom_codes_with_422(client,auth_headers,valid_url,custom_code):
    payload={"original_url":valid_url.get("original_url"),"custom_code":custom_code,"expires_at":valid_url.get("expires_at")}
    answer=client.post("/links/",json=payload,headers= auth_headers)
    assert answer.status_code==422


def test_expired_expiration_time(client,auth_headers,valid_url):
    expires_at=datetime.now(timezone.utc)-timedelta(hours=2)
    payload={"original_url":valid_url.get("original_url"),"expires_at":expires_at.isoformat()}
    answer=client.post("/links/",json=payload,headers=auth_headers)
    assert answer.status_code==422


def test_too_many_requests_to_create_link(client,auth_headers,expires_at):
    count=0
    for i in range(MAX_REDIRECTS_PER_MINUTE_SAME_URL):
        payload={"original_url":valid_urls[i],"expires_at":expires_at.isoformat()}
        count+=1
        answer=client.post("/links/",json=payload,headers=auth_headers)
        assert answer.status_code==201
    payload={"original_url":valid_urls[count+1],"expires_at":expires_at.isoformat()}
    answer=client.post("/links/",json=payload,headers=auth_headers)
    assert answer.status_code==429
    assert answer.json()["detail"] == "too many requests to create link"


@pytest.mark.parametrize("invalid_url",invalid_urls)
def test_cannot_shorten_invalid_url(client,auth_headers,expires_at,invalid_url):
    payload={"original_url":invalid_url,"expires_at":expires_at.isoformat()}
    answer=client.post("/links/",json=payload,headers=auth_headers)
    assert answer.status_code==400


def test_update(client,auth_headers,shortener):
    
    code=shortener.json()["code"]
    answer2=client.put(f"/links/{code}",json={"original_url":"https://www.google.com/"},headers=auth_headers)
    assert answer2.status_code==200
    assert answer2.json()["original_url"]=="https://www.google.com/"

def test_update_without_token(client,auth_headers,shortener):
    code=shortener.json()["code"]
    answer2=client.put(f"/links/{code}",json={"original_url":"https://www.google.com/"})
    answer3=client.get(f"/links/{code}",headers=auth_headers)
    assert answer2.status_code==401
    assert answer3.json()["original_url"]=="https://github.com/"

@pytest.mark.parametrize("invalid_url",invalid_urls)
def test_cannot_update_with_invalid_url(client,auth_headers,valid_url,invalid_url):
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.put(f"/links/{code}",json={"original_url":invalid_url},headers=auth_headers)
    assert answer2.status_code==400


def test_update_wrong_user(client,auth_headers,auth_headers2,shortener):
    
    code=shortener.json()["code"]
    
    answer2=client.put(f"/links/{code}",json={"original_url":"https://www.google.com/"},headers=auth_headers2)
    answer3=client.get(f"/links/{code}",headers=auth_headers)
    assert answer2.status_code==403
    assert answer3.json()["original_url"]=="https://github.com/"

def test_delete(client,auth_headers,shortener):
    
    code=shortener.json()["code"]
    answer2=client.delete(f"/links/{code}",headers=auth_headers)
    assert answer2.status_code==204


def test_delete_without_token(client,auth_headers,shortener):
   
    code=shortener.json()["code"]
    answer2=client.delete(f"/links/{code}")
    answer3=client.get(f"/links/{code}",headers=auth_headers)
    assert answer3.json()["original_url"]=="https://github.com/"
    assert answer2.status_code==401

def test_delete_wrong_user(client,auth_headers,auth_headers2,shortener):
    code=shortener.json()["code"]
    answer2=client.delete(f"/links/{code}",headers=auth_headers2)
    answer3=client.get(f"/links/{code}",headers=auth_headers)
    assert answer3.json()["original_url"]=="https://github.com/"
    assert answer2.status_code==403


def test_health_checker(shortener,client,auth_headers):
    answer=shortener
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}/health",headers=auth_headers)
    data = answer2.json()
    assert 200<=data["status_code"]<400
    assert answer2.status_code==200
    assert data["original_url"]==answer.json()["original_url"]
    assert data["error"] is None
    assert data["code"]==code
    assert data["status"]=="ok"
    assert data["final_url"] is not None



def test_check_broken_url_health(client,auth_headers,expires_at,monkeypatch):

    def get_fake(*args,**kwargs):
        return httpx.Response(status_code=404,request=httpx.Request("GET", "https://httpbin.org/status/404"))
    monkeypatch.setattr(httpx, "get", get_fake)

    payload={"original_url":"https://httpbin.org/status/404","expires_at":expires_at.isoformat()}
    answer=client.post("/links/",json=payload,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}/health",headers=auth_headers)
    data = answer2.json()
    assert answer2.status_code==200
    assert data["status_code"] is not None
    assert 400 <= answer2.json()["status_code"] < 600
    assert data["original_url"]==answer.json()["original_url"]
    assert data["code"]==code
    assert data["status"]=="broken"
    assert data["final_url"] is not None
    assert data["error"] is None


def test_health_follows_public_redirect(auth_headers,client,valid_url,httpx_mock):
    header=httpx.Headers({"Location":valid_urls[1]})
    httpx_mock.add_response(
        url=valid_url.get("original_url"),
        headers=header,
        status_code=302
    )
    httpx_mock.add_response(
        url=valid_urls[1],
        status_code=200,
    )

    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}/health",headers= auth_headers)
    assert answer2.status_code==200
    assert answer2.json()["final_url"]==valid_urls[1]
    


def test_health_blocks_private_ip_redirect(client,auth_headers,valid_url,httpx_mock):
    header=httpx.Headers({"Location":invalid_urls[2]})
    httpx_mock.add_response(
        url=valid_url.get("original_url"),
        headers=header,
        status_code=302
    )
    
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}/health",headers= auth_headers)
    assert answer2.status_code==400
    



def test_health_blocks_private_ipv6_redirect(client,auth_headers,httpx_mock,valid_url):
    header=httpx.Headers({"Location":invalid_urls[13]})
    httpx_mock.add_response(
        url=valid_url.get("original_url"),
        headers=header,
        status_code=302
    )
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}/health",headers= auth_headers)
    assert answer2.status_code==400


def test_health_follows_relative_redirect(client,auth_headers,httpx_mock,valid_url):
    header=httpx.Headers({"Location":"/new"})
    original_url=valid_url.get("original_url")
    httpx_mock.add_response(
        url=original_url,
        headers=header,
        status_code=302
    )
    url=urljoin(original_url,"/new")
    httpx_mock.add_response(
        url=url,
        status_code=200,
    )
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}/health",headers= auth_headers)
    assert answer2.json()["final_url"]==url

    assert answer2.status_code==200
   



def test_health_redirect_without_location(client,auth_headers,httpx_mock,valid_url):
    httpx_mock.add_response(
        url=valid_url.get("original_url"),
        status_code=302
    )
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}/health",headers= auth_headers)
    assert answer2.status_code==200
    assert  answer2.json()["final_url"]==valid_url.get("original_url")

def test_health_too_many_redirects(client,auth_headers,httpx_mock,valid_url):
    for i in range(5):
        header=httpx.Headers({"Location":valid_urls[i+1]})
        httpx_mock.add_response(
        url=valid_urls[i],
        headers=header,
        status_code=302
    )
    

    valid_url["original_url"]=valid_urls[0]
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}/health",headers= auth_headers)
    assert answer2.status_code==400

def test_health_does_not_cache_blocked_ssrf_result(db,client,httpx_mock,auth_headers,valid_url):
    header=httpx.Headers({"Location":invalid_urls[13]})
    httpx_mock.add_response(
        url=valid_url.get("original_url"),
        headers=header,
        status_code=302
    )
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    code=answer.json()["code"]
    answer2=client.get(f"/links/{code}/health",headers= auth_headers)
    assert answer2.status_code==400
    user_id=db.query(User.id).scalar()
    assert redis.get(CacheService.check_health(code,user_id)) is None





