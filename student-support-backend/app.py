from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from pathlib import Path

# Load env variables
load_dotenv(Path(__file__).resolve().parent / ".env")

# Import your modules
from routes.auth_routes import auth_routes
from routes.admin_routes import admin_routes
from routes.social_routes import social_routes
from routes.ai_features_routes import ai_features_routes
from services.chat_engine import process_chat_message, warm_chatbot_model
from database import check_mongo_connection, DB_NAME

from student.admission_routes import admission_routes
from student.academic_routes import academic_routes
from student.counseling_routes import counseling_routes
from student.financial_routes import financial_routes
from student.campus_routes import campus_routes

# Initialize app
app = Flask(__name__)

try:
    warm_chatbot_model()
    print("[startup] Chatbot model warmed successfully")
except Exception as e:
    print(f"[startup] Chatbot warmup failed: {e}")

allowed_origins = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.31.211:5173",
    "https://student-assistance-rahul.vercel.app",
    "https://student-assistance-ff0uw1u9r-rahul-kumars-projects-e5816ae5.vercel.app",
}

frontend_base_url = os.getenv("FRONTEND_BASE_URL", "").strip()
if frontend_base_url:
    allowed_origins.add(frontend_base_url.rstrip("/"))

CORS(
    app,
    resources={r"/api/*": {"origins": list(allowed_origins)}},
    supports_credentials=False,
)

# Register routes
app.register_blueprint(auth_routes, url_prefix="/api")
app.register_blueprint(admin_routes, url_prefix="/api")
app.register_blueprint(social_routes, url_prefix="/api")
app.register_blueprint(ai_features_routes, url_prefix="/api")

app.register_blueprint(admission_routes, url_prefix="/api")
app.register_blueprint(academic_routes, url_prefix="/api")
app.register_blueprint(counseling_routes, url_prefix="/api")
app.register_blueprint(financial_routes, url_prefix="/api")
app.register_blueprint(campus_routes, url_prefix="/api")


@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Student support backend is running"
    })


@app.route("/api/db-status", methods=["GET"])
def db_status():
    ok, message = check_mongo_connection()
    status_code = 200 if ok else 503
    return jsonify({
        "connected": ok,
        "database": DB_NAME,
        "message": message
    }), status_code


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    user = data.get("user", "guest")

    result = process_chat_message(message, user=user, save_log=True)

    status = result.pop("status_code", 200)
    if "error" in result:
        return jsonify(result), status

    return jsonify(result), status
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
