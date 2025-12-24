import io
import os
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.main import app
from backend.app.database import Base
from backend.app.routers.products import get_db as products_get_db
from backend.app.routers.backup import get_db as backup_get_db
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
app.view_functions  # ensure app initialized
products_get_db.__globals__["SessionLocal"] = TestingSessionLocal
backup_get_db.__globals__["SessionLocal"] = TestingSessionLocal
def test_crud_and_upload_and_backup():
    client = app.test_client()
    r = client.post("/api/products/", json={"name":"測試商品","description":"women","price":1290,"currency":"TWD","stock":10})
    assert r.status_code == 200
    prod = r.get_json()
    pid = prod["id"]
    r = client.get("/api/products/")
    assert r.status_code == 200
    assert any(p["id"]==pid for p in r.get_json())
    r = client.get(f"/api/products/{pid}")
    assert r.status_code == 200
    r = client.put(f"/api/products/{pid}", json={"price":1490})
    assert r.status_code == 200
    assert r.get_json()["price"] == 1490
    img_bytes = b"\x89PNG\r\n\x1a\n" + b"0"*64
    data = {"file": (io.BytesIO(img_bytes), "a.png")}
    r = client.post(f"/api/products/{pid}/upload-image", data=data, content_type="multipart/form-data")
    assert r.status_code == 200
    assert r.get_json()["image_url"].startswith("/static/images/")
    r = client.post(f"/api/products/{pid}/update-link", data={"product_url":"https://example.com/buy"})
    assert r.status_code == 200
    assert r.get_json()["product_url"] == "https://example.com/buy"
    r = client.get("/api/backup/export")
    assert r.status_code == 200
    path = r.get_json()["file"]
    assert os.path.exists(path)
    r = client.delete(f"/api/products/{pid}")
    assert r.status_code == 200
