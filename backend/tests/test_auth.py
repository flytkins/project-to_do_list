def test_register_success(client):
    response = client.post("/register", json={"username": "alice", "password": "secret"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert "id" in data

def test_register_duplicate_username(client):
    client.post("/register", json={"username": "bob", "password": "123"})
    response = client.post("/register", json={"username": "bob", "password": "456"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"

def test_login_success(client):
    client.post("/register", json={"username": "carol", "password": "pass"})
    response = client.post("/login", json={"username": "carol", "password": "pass"})
    assert response.status_code == 200
    assert response.json()["username"] == "carol"

def test_login_wrong_password(client):
    client.post("/register", json={"username": "dave", "password": "correct"})
    response = client.post("/login", json={"username": "dave", "password": "wrong"})
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    response = client.post("/login", json={"username": "eve", "password": "any"})
    assert response.status_code == 401