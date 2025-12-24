from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os, sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
try:
    from .database import Base, engine
    from .routers.products import blueprint as products_bp
    from .routers.backup import blueprint as backup_bp
    from .routers.orders import blueprint as orders_bp
except ImportError:
    from backend.app.database import Base, engine
    from backend.app.routers.products import blueprint as products_bp
    from backend.app.routers.backup import blueprint as backup_bp
    from backend.app.routers.orders import blueprint as orders_bp
from pathlib import Path
import json
Base.metadata.create_all(bind=engine)
STATIC_DIR = os.path.join(BASE_DIR, "frontend")
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
CORS(app)
app.register_blueprint(products_bp, url_prefix="/api/products")
app.register_blueprint(backup_bp, url_prefix="/api/backup")
app.register_blueprint(orders_bp)
def _read_config():
    path = os.path.join(BASE_DIR, "config.txt")
    tables = 10
    menu = []
    descriptions = {}
    section = None
    if not os.path.exists(path):
        return {"tables": tables, "menu": menu, "descriptions": descriptions}
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip().lower()
                continue
            if section == "tables":
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == "count":
                        try:
                            tables = int(v.strip())
                        except:
                            pass
            elif section == "menu":
                if "=" in line:
                    name, price = line.split("=", 1)
                    try:
                        menu.append({"name": name.strip(), "price": int(price.strip())})
                    except:
                        pass
            elif section == "descriptions":
                if "=" in line:
                    idx, text = line.split("=", 1)
                    try:
                        descriptions[int(idx.strip())] = text.strip()
                    except:
                        pass
    return {"tables": tables, "menu": menu, "descriptions": descriptions}
@app.route("/")
def root():
    # 嘗試以兩種根目錄定位前端檔案：app.static_folder 與 CWD/frontend
    index_path1 = os.path.join(app.static_folder, "index.html")
    index_path2 = os.path.join(os.getcwd(), "frontend", "index.html")
    if os.path.exists(index_path1):
        return send_from_directory(app.static_folder, "index.html")
    if os.path.exists(index_path2):
        return send_from_directory(os.path.join(os.getcwd(), "frontend"), "index.html")
    return jsonify({"ok": True, "name": "E-commerce API", "docs": "/docs"})
@app.route("/index.html")
def index_html():
    index_path = os.path.join(app.static_folder, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, "index.html")
    return jsonify({"error": "index not found"}), 404
@app.route("/health")
def health():
    return jsonify({"ok": True, "name": "E-commerce API", "docs": "/docs"})
@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("backend/app/static", path)
@app.route("/assets/<path:path>")
def asset_files(path):
    return send_from_directory(BASE_DIR, path)
@app.route("/api/config", methods=["GET"])
def config_menu():
    data = _read_config()
    return jsonify(data)
@app.route("/openapi.json")
def openapi():
    path = Path("backend/app/openapi.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    return jsonify(data)
@app.route("/docs")
def docs():
    return send_from_directory("backend/app/static", "swagger.html")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
