
from constants import MAX_REFRESH_PER_MINUTE,MAX_WRONG_REFRESH_TOKEN
from services.auth_redis_service import AuthRedisService

def test_refresh_token(client,refresh):

    answer=client.post("/users/refresh",json={"refresh_token":refresh})
    assert answer.status_code==200
    assert  len(answer.json()["access_token"])>0
    assert len(answer.json()["refresh_token"])>0
    assert answer.json()["token_type"]=="bearer"

def test_refresh_token_with_wrong_token(client):
    answer3=client.post("/users/refresh",json={"refresh_token":"refresh_token"})
    assert answer3.status_code==401


def test_refresh_token_cannot_be_used_twice(client,refresh,monkeypatch):
    monkeypatch.setattr(
        AuthRedisService,
        "acquire_refresh_attempt_mutex",
        lambda *args:None
    )
    first_response=client.post("/users/refresh",json={"refresh_token":refresh})
    assert first_response.status_code == 200
    second_response=client.post("/users/refresh",json={"refresh_token":refresh})
    assert second_response.status_code==401

def test_refresh_rate_limit(refresh,client,monkeypatch):
    monkeypatch.setattr(
        AuthRedisService,
        "acquire_refresh_attempt_mutex",
        lambda *args:None
    )
    token=refresh
    for i in range(MAX_REFRESH_PER_MINUTE):
        answer=client.post("/users/refresh",json={"refresh_token":token})
        assert answer.status_code==200
        token=answer.json()["refresh_token"]
    answer=client.post("/users/refresh",json={"refresh_token":token})
    assert answer.status_code==429


    
def test_refresh_lock(client,monkeypatch):
    monkeypatch.setattr(
        AuthRedisService,
        "acquire_refresh_attempt_mutex",
        lambda *args:None
    )
    monkeypatch.setattr(
        AuthRedisService,
        "sliding_window_counter",
        lambda **kwargs:None
    )
    for i in range(MAX_WRONG_REFRESH_TOKEN):
        answer=client.post("/users/refresh",json={"refresh_token":"aaa"})
        assert answer.status_code==401
    answer=client.post("/users/refresh",json={"refresh_token":"aaa"})
    assert answer.status_code==429
    
def test_refresh_clear_lock(client,monkeypatch,refresh):
    monkeypatch.setattr(
        AuthRedisService,
        "acquire_refresh_attempt_mutex",
        lambda *args:None
    )
    monkeypatch.setattr(
        AuthRedisService,
        "sliding_window_counter",
        lambda *args,**kwargs:None
    )
    old_token=refresh
    answer=client.post("/users/refresh",json={"refresh_token":old_token})
    assert answer.status_code==200
    token=answer.json()["refresh_token"]
    for i in range(MAX_WRONG_REFRESH_TOKEN-1):
        answer=client.post("/users/refresh",json={"refresh_token":old_token})
        assert answer.status_code==401

    answer=client.post("/users/refresh",json={"refresh_token":token})
    assert answer.status_code==200
    answer=client.post("/users/refresh",json={"refresh_token":old_token})
    assert answer.status_code==401

def test_refresh_mutex(client,refresh):
    first_response=client.post("/users/refresh",json={"refresh_token":refresh})
    assert first_response.status_code == 200
    second_response=client.post("/users/refresh",json={"refresh_token":refresh})
    assert second_response.status_code==429





