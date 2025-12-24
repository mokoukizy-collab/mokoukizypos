from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
from ..database import SessionLocal
from .. import crud
blueprint = Blueprint("products", __name__)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def to_dict(p):
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "currency": p.currency,
        "image_url": p.image_url,
        "product_url": p.product_url,
        "stock": p.stock,
    }
@blueprint.get("/")
def list_products():
    db = next(get_db())
    return jsonify([to_dict(p) for p in crud.get_products(db)])
@blueprint.post("/")
def create_product():
    db = next(get_db())
    payload = request.json or {}
    obj = crud.create_product(db, payload)
    return jsonify(to_dict(obj))
@blueprint.get("/<int:product_id>")
def retrieve_product(product_id: int):
    db = next(get_db())
    obj = crud.get_product(db, product_id)
    if not obj:
        return jsonify({"detail":"Not found"}), 404
    return jsonify(to_dict(obj))
@blueprint.put("/<int:product_id>")
def update_product(product_id: int):
    db = next(get_db())
    payload = request.json or {}
    obj = crud.update_product(db, product_id, payload)
    if not obj:
        return jsonify({"detail":"Not found"}), 404
    return jsonify(to_dict(obj))
@blueprint.delete("/<int:product_id>")
def delete_product(product_id: int):
    db = next(get_db())
    ok = crud.delete_product(db, product_id)
    if not ok:
        return jsonify({"detail":"Not found"}), 404
    return jsonify({"ok":True})
@blueprint.post("/<int:product_id>/upload-image")
def upload_image(product_id: int):
    db = next(get_db())
    obj = crud.get_product(db, product_id)
    if not obj:
        return jsonify({"detail":"Not found"}), 404
    file = request.files.get("file")
    if not file:
        return jsonify({"detail":"file required"}), 400
    images_dir = Path("backend/app/static/images")
    images_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename).suffix.lower() or ".jpg"
    name = f"{uuid.uuid4().hex}{ext}"
    path = images_dir / name
    file.save(path)
    public_url = f"/static/images/{name}"
    obj.image_url = public_url
    db.commit()
    db.refresh(obj)
    return jsonify(to_dict(obj))
@blueprint.post("/<int:product_id>/update-link")
def update_link(product_id: int):
    db = next(get_db())
    obj = crud.get_product(db, product_id)
    if not obj:
        return jsonify({"detail":"Not found"}), 404
    product_url = request.form.get("product_url")
    obj.product_url = product_url
    db.commit()
    db.refresh(obj)
    return jsonify(to_dict(obj))
