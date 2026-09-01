import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient
from serve import app, load_data


def test_health_endpoint():
    load_data()
    client = TestClient(app)
    r = client.get("/api/health")
    assert r.status_code == 200
    assert "catalog_ready" in r.json()


def test_titles_endpoint_when_ready():
    load_data()
    client = TestClient(app)
    r = client.get("/api/titles?page_size=3")
    assert r.status_code == 200
    body = r.json()
    if body.get("catalog_ready"):
        assert isinstance(body.get("rows"), list)
