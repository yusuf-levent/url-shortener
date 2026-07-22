import httpx
def test_check_security_headers():
    response=httpx.get("http://web/health")
    assert response.status_code==200
    
    assert response.headers["X-Frame-Options"]=="DENY"
    assert response.headers["X-Content-Type-Options"]=="nosniff"
    assert response.headers["Referrer-Policy"]=="strict-origin-when-cross-origin"
    assert response.headers["Permissions-Policy"]==(
            "camera=(), microphone=(), geolocation=()")