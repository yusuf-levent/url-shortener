
from constants import MAX_REGISTER_EMAIL_PER_MINUTE,MAX_REGISTER_IP_PER_MINUTE
def test_register(register):
    pass

def test_register_same_email(client,register,user_payload):#bu client parametresini pytest otomatik olarak conftest içindeki fixture den alıyor
    second=client.post("/users/",json=user_payload)
    assert second.status_code==400


def test_register_rate_with_ip(client,user_payload):
    
    answer=client.post("/users/",json=user_payload)
    assert answer.status_code==201
    
    for i in range(MAX_REGISTER_IP_PER_MINUTE-1):
        user_payload["email"]="1"+user_payload["email"]
        answer=client.post("/users/",json=user_payload)
        assert answer.status_code==201
    answer=client.post("/users/",json=user_payload)
    assert answer.status_code==429



    
def test_register_rate_with_email(client,user_payload):
    answer=client.post("/users/",json=user_payload)
    assert answer.status_code==201
    for i in range(MAX_REGISTER_EMAIL_PER_MINUTE-1):
        answer=client.post("/users/",json=user_payload)
        assert answer.status_code==400
    answer=client.post("/users/",json=user_payload)
    assert answer.status_code==429
    