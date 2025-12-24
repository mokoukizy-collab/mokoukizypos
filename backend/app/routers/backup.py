from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from pathlib import Path
import json
import time
from ..database import SessionLocal
from .. import crud
blueprint = Blueprint("backup", __name__)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@blueprint.get("/export")
def export_data():
    db = next(get_db())
    data = []
    for p in crud.get_products(db):
        d = {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "currency": p.currency,
            "image_url": p.image_url,
            "product_url": p.product_url,
            "stock": p.stock,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        data.append(d)
    backups_dir = Path("backend/app/backups")
    backups_dir.mkdir(parents=True, exist_ok=True)
    name = f"products-{int(time.time())}.json"
    path = backups_dir / name
    path.write_text(json.dumps(data, ensure_ascii=False))
    return jsonify({"file": str(path)})
@blueprint.post("/import")
def import_data():
    db = next(get_db())
    file = request.files.get("file")
    if not file:
        return jsonify({"detail":"file required"}), 400
    content = file.read()
    try:
        items = json.loads(content.decode("utf-8"))
    except Exception:
        return jsonify({"detail":"invalid file"}), 400
    for item in items:
        item.pop("id", None)
        crud.create_product(db, item)
    return jsonify({"count": len(items)})
