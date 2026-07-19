

def test_logout(client,refresh,auth_headers):
    response=client.post("/users/logout",json={"refresh_token":refresh},headers=auth_headers)
    assert response.status_code==204

def test_cannot_logout_with_wrong_token(client,refresh,auth_headers):
    response=client.post("/users/logout",json={"refresh_token":"refresh"},headers=auth_headers)
    assert response.status_code==401

def test_cannot_logout_with_same_token_twice(client,refresh,auth_headers):
    response=client.post("/users/logout",json={"refresh_token":refresh},headers=auth_headers)
    assert response.status_code==204
    response2=client.post("/users/logout",json={"refresh_token":refresh},headers=auth_headers)
    assert response2.status_code==401




def test_cannot_logout_with_wrong_user(client,refresh,auth_headers2):
    response=client.post("/users/logout",json={"refresh_token":refresh},headers=auth_headers2)
    assert response.status_code==401