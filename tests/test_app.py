import app as app_module


def test_homepage_shows_sample_tasks():
    app_module.app.config.update(TESTING=True)
    client = app_module.app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Student Task Manager" in response.data
    assert b"Revise CI/CD concepts" in response.data


def test_add_task():
    app_module.app.config.update(TESTING=True)
    client = app_module.app.test_client()
    response = client.post("/add", data={"title": "Demo task"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Demo task" in response.data


def test_health_endpoint():
    client = app_module.app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
