import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from database import get_db,Base
from main import app
from config import settings
from datetime import datetime ,timedelta,timezone
from models import User ,UserRoles
from services.redis_service import redis
from database import Base
import httpx
TEST_URL=settings.TEST_DATABASE_URL
test_engine=create_engine(url=TEST_URL)
TestSession=sessionmaker(bind=test_engine,autoflush=False,autocommit=False)

def override_get_db():
    db=TestSession()
    try:
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db]=override_get_db
@pytest.fixture
def db():
    db=TestSession()
    try:
        yield db
    finally:
        db.close_all()

@pytest.fixture(autouse=True)
def clean_redis():
    redis.flushdb()
    yield
    redis.flushdb()  


@pytest.fixture(autouse=True)
def temiz_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def user_payload():
    return {"email":"ylevent2000@gmail.com","password":"Yusuf1453*"}

@pytest.fixture
def expires_at():
    return datetime.now(timezone.utc)+timedelta(days=1)



@pytest.fixture
def valid_url(expires_at):
    return {"original_url":"https://github.com/",
            "expires_at":expires_at.isoformat()}





@pytest.fixture
def auth_headers(client,user_payload):
    client.post("/users/",json=user_payload)
    cevap=client.post("/users/login",json=user_payload)
    token=cevap.json()["access_token"]
    return {"Authorization":f"Bearer {token}"}
@pytest.fixture
def auth_headers2(client):
    client.post("/users/",json={"email":"ylevent1998@gmail.com","password":"Yusuf1453*"})
    cevap=client.post("/users/login",json={"email":"ylevent1998@gmail.com","password":"Yusuf1453*"})
    token=cevap.json()["access_token"]
    return {"Authorization":f"Bearer {token}"}



@pytest.fixture
def register(client,user_payload):
    response=client.post("/users/",json=user_payload)
    assert response.status_code==201
    assert response.json()["email"]==user_payload.get("email")
    assert "password" not in response.json()
    return user_payload

@pytest.fixture
def login(client,register):
    response=client.post("/users/login",json=register)
    assert response.status_code==201
    assert len(response.json()["access_token"])>0
    assert len(response.json()["refresh_token"])>0
    assert response.json()["token_type"]=="bearer"
    return response

@pytest.fixture
def refresh(login):
    return login.json()["refresh_token"]


@pytest.fixture
def shortener(client,auth_headers,valid_url):
    
    answer=client.post("/links/",json=valid_url,headers=auth_headers)
    assert answer.status_code==201
    assert answer.json()["original_url"]==valid_url.get("original_url")
    return answer

@pytest.fixture
def get_links(shortener,client,auth_headers):
    code=shortener.json()["code"]
    answer=client.get("/links/",headers=auth_headers)
    assert answer.status_code==200
    links=answer.json()
    assert any(link["code"]==code and link["original_url"]=="https://github.com/"
               for link in links)
    return answer,code


@pytest.fixture
def make_user_admin(db,user_payload,login):
    user=db.query(User).filter(User.email==user_payload.get("email")).first()
    assert user is not None
    user.role=UserRoles.Admin
    db.commit()
    db.refresh(user)
    token=login.json()["access_token"]
    return {"Authorization":f"Bearer {token}"}