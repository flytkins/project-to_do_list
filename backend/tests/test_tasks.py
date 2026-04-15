def create_user_and_login(client, username, password):
    client.post("/register", json={"username": username, "password": password})
    resp = client.post("/login", json={"username": username, "password": password})
    return resp.json()["id"]

def test_create_task(client):
    user_id = create_user_and_login(client, "tasker", "123")
    response = client.post("/tasks", json={
        "title": "Buy milk",
        "description": "2 liters",
        "status": "pending",
        "owner_id": user_id
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["status"] == "pending"
    assert data["owner_id"] == user_id

def test_get_tasks_empty(client):
    user_id = create_user_and_login(client, "empty_user", "pass")
    response = client.get(f"/tasks?user_id={user_id}")
    assert response.status_code == 200
    assert response.json() == []

def test_get_tasks_with_search(client):
    user_id = create_user_and_login(client, "searcher", "pwd")
    client.post("/tasks", json={"title": "Wash car", "owner_id": user_id})
    client.post("/tasks", json={"title": "Walk dog", "owner_id": user_id})
    client.post("/tasks", json={"title": "Read book", "description": "about dogs", "owner_id": user_id})
    
    response = client.get(f"/tasks?user_id={user_id}&search=dog")
    assert response.status_code == 200
    tasks = response.json()
    titles = [t["title"] for t in tasks]
    assert "Walk dog" in titles
    assert "Read book" in titles  # потому что description содержит "dog"
    assert "Wash car" not in titles

def test_update_task(client):
    user_id = create_user_and_login(client, "updater", "pass")
    create_resp = client.post("/tasks", json={"title": "Old title", "owner_id": user_id})
    task_id = create_resp.json()["id"]
    
    update_resp = client.patch(f"/tasks/{task_id}?user_id={user_id}", json={"title": "New title", "status": "completed"})
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "New title"
    assert update_resp.json()["status"] == "completed"

def test_update_nonexistent_task(client):
    user_id = create_user_and_login(client, "bad_updater", "pass")
    response = client.patch("/tasks/9999?user_id=9999", json={"title": "New"})
    assert response.status_code == 404

def test_update_other_user_task(client):
    user1_id = create_user_and_login(client, "user1", "pass")
    user2_id = create_user_and_login(client, "user2", "pass")
    # user1 создаёт задачу
    task = client.post("/tasks", json={"title": "Secret", "owner_id": user1_id}).json()
    # user2 пытается обновить
    response = client.patch(f"/tasks/{task['id']}?user_id={user2_id}", json={"title": "Hacked"})
    assert response.status_code == 404  # или 403, но мы реализовали 404

def test_delete_task(client):
    user_id = create_user_and_login(client, "deleter", "pass")
    task = client.post("/tasks", json={"title": "To delete", "owner_id": user_id}).json()
    response = client.delete(f"/tasks/{task['id']}?user_id={user_id}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Task {task['id']} deleted"
    # проверяем, что задача действительно удалена
    get_resp = client.get(f"/tasks?user_id={user_id}")
    assert len(get_resp.json()) == 0

def test_delete_other_user_task(client):
    user1_id = create_user_and_login(client, "owner", "pass")
    user2_id = create_user_and_login(client, "intruder", "pass")
    task = client.post("/tasks", json={"title": "Private", "owner_id": user1_id}).json()
    response = client.delete(f"/tasks/{task['id']}?user_id={user2_id}")
    assert response.status_code == 404