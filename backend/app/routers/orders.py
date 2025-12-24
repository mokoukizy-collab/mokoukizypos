from flask import Blueprint, request, jsonify
from datetime import datetime
from ..database import SessionLocal
from ..models.orders import Order, OrderItem

blueprint = Blueprint("orders", __name__)

def serialize_order(o: Order):
    return {
        "id": o.id,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "status": o.status,
        "note": o.note or "",
        "subtotal": o.subtotal,
        "discount": o.discount,
        "allowance": o.allowance,
        "total": o.total,
        "count": o.count,
        "table_no": o.table_no,
        "dine_type": o.dine_type,
        "started_at": o.started_at.isoformat() if o.started_at else None,
        "paid_at": o.paid_at.isoformat() if o.paid_at else None,
        "items": [{"id": i.id, "name": i.name, "unit_price": i.unit_price, "quantity": i.quantity, "details": i.details or ""} for i in o.items],
    }

@blueprint.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json(force=True) or {}
    items = data.get("items") or []
    if not items:
        return jsonify({"error": "items required"}), 400
    dine_type = data.get("dine_type") or "外帶"
    table_no = data.get("table_no")
    note = data.get("note") or ""
    client_subtotal = data.get("subtotal")
    client_discount = data.get("discount")
    client_allowance = data.get("allowance")
    client_total = data.get("total")
    computed_subtotal = sum(int(i.get("unit_price", 0)) * int(i.get("quantity", 0)) for i in items)
    apply_discount = bool(data.get("apply_discount", False))
    computed_discount = int(computed_subtotal * 0.10) if apply_discount else 0
    allowance = int(client_allowance if client_allowance is not None else 0)
    subtotal = int(client_subtotal) if client_subtotal is not None else computed_subtotal
    discount = int(client_discount) if client_discount is not None else computed_discount
    total = int(client_total) if client_total is not None else (subtotal - discount - allowance)
    count = sum(int(i.get("quantity", 0)) for i in items)
    db = SessionLocal()
    if dine_type == "內用" and table_no:
        exist = db.query(Order).filter(Order.status == "open", Order.table_no == table_no).first()
        if exist:
            db.close()
            return jsonify({"error": "table occupied"}), 409
    o = Order(
        status="open",
        note=note,
        subtotal=subtotal,
        discount=discount,
        allowance=allowance,
        total=total,
        count=count,
        table_no=table_no,
        dine_type=dine_type,
        started_at=datetime.now(),
    )
    for it in items:
        o.items.append(OrderItem(name=str(it.get("name","")), unit_price=int(it.get("unit_price",0)), quantity=int(it.get("quantity",0)), details=str(it.get("details",""))))
    db.add(o)
    db.commit()
    db.refresh(o)
    res = serialize_order(o)
    db.close()
    return jsonify(res), 201

@blueprint.route("/api/orders", methods=["GET"])
def list_orders():
    status = request.args.get("status")
    limit = min(int(request.args.get("limit", "200")), 1000)
    db = SessionLocal()
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    q = q.order_by(Order.id.desc()).limit(limit)
    rows = [serialize_order(o) for o in q.all()]
    db.close()
    return jsonify(rows)

@blueprint.route("/api/orders/<int:order_id>", methods=["PATCH"])
def update_order_amounts(order_id: int):
    data = request.get_json(force=True) or {}
    db = SessionLocal()
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        db.close()
        return jsonify({"error":"not found"}), 404
    subtotal = data.get("subtotal")
    discount = data.get("discount")
    allowance = data.get("allowance")
    total = data.get("total")
    if subtotal is not None:
        try:
            o.subtotal = int(subtotal)
        except Exception:
            pass
    if discount is not None:
        try:
            o.discount = int(discount)
        except Exception:
            pass
    if allowance is not None:
        try:
            o.allowance = int(allowance)
        except Exception:
            pass
    if total is not None:
        try:
            o.total = int(total)
        except Exception:
            pass
    else:
        o.total = int(o.subtotal) - int(o.discount) - int(o.allowance)
    db.commit()
    db.refresh(o)
    res = serialize_order(o)
    db.close()
    return jsonify(res)
@blueprint.route("/api/orders/<int:order_id>/", methods=["PATCH"])
def update_order_amounts_slash(order_id: int):
    return update_order_amounts(order_id)

@blueprint.route("/api/orders/<int:order_id>/status", methods=["PATCH"])
def update_order_status(order_id: int):
    data = request.get_json(force=True) or {}
    status = str(data.get("status","")).strip().lower()
    if status not in ("served","paid"):
        return jsonify({"error":"invalid status"}), 400
    db = SessionLocal()
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        db.close()
        return jsonify({"error":"not found"}), 404
    if status == "served":
        o.status = "served"
    elif status == "paid":
        o.status = "paid"
        o.paid_at = datetime.now()
    db.commit()
    db.refresh(o)
    res = serialize_order(o)
    db.close()
    return jsonify(res)
@blueprint.route("/api/orders/<int:order_id>/status/", methods=["PATCH"])
def update_order_status_slash(order_id: int):
    return update_order_status(order_id)
