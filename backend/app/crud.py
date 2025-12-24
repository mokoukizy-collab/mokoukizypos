from sqlalchemy.orm import Session
from . import models
def get_products(db: Session):
    return db.query(models.Product).all()
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()
def create_product(db: Session, data: dict):
    obj = models.Product(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
def update_product(db: Session, product_id: int, data: dict):
    obj = get_product(db, product_id)
    if not obj:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj
def delete_product(db: Session, product_id: int):
    obj = get_product(db, product_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
