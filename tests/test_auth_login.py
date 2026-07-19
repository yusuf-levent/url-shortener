from constants import MAX_LOGIN_PER_MINUTE,RATE_LIMIT_WINDOW_SECONDS,MAX_WRONG_LOGIN
from services.auth_redis_service import AuthRedisService
def test_login(login):
    assert login.status_code==201
   
def test_login_wrong_password(client,register):
    answer=client.post("/users/login",json={"email":"ylevent2000@gmail.com","password":"Yusuf153*"})
    assert answer.status_code==401

def test_login_wrong_email(client,register):
    answer=client.post("/users/login",json={"email":"ylevent2000@gmail.co","password":"Yusuf1453*"})
    assert answer.status_code==401


#lock ,rate limit
def test_login_rate_limit(client,register):
    payload=register
    for i in range(MAX_LOGIN_PER_MINUTE):
        answer=client.post("/users/login",json=payload)
        assert answer.status_code==201
    answer=client.post("/users/login",json=payload)
    assert answer.status_code==429
    
def test_login_lock(client,register):
    payload={"email":"ylevent2000@gmail.com","password":"Yusuf1453"}
    for i in range(MAX_LOGIN_PER_MINUTE):
         answer=client.post("/users/login",json=payload)
         assert answer.status_code==401
    answer=client.post("/users/login",json=payload)
    assert answer.status_code==429

def test_login_clear_lock(client,register,monkeypatch):
    monkeypatch.setattr(
        AuthRedisService,
        "sliding_window_counter",
        lambda **kwargs:None
    )
    payload=register
    wrong_payload={"email":"ylevent2000@gmail.com","password":"Yusuf1453"}
    for i in range(MAX_WRONG_LOGIN-1):
         answer=client.post("/users/login",json=wrong_payload)
         assert answer.status_code==401
    answer=client.post("/users/login",json=payload)
    assert answer.status_code==201
    for i in range(MAX_LOGIN_PER_MINUTE):
         answer=client.post("/users/login",json=wrong_payload)
         assert answer.status_code==401
    answer=client.post("/users/login",json=wrong_payload)
    assert answer.status_code==429