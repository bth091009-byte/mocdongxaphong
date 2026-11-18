import os
from datetime import timedelta
from flask import Flask, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
import config
from routes.main_routes import main_bp
from routes.chat_routes import chat_bp
from routes.auth_routes import auth_bp
from routes.learning_routes import learning_bp

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static"),
        static_url_path="/static",
    )

    # Giúp Flask nhận diện đúng giao thức HTTPS và domain thật sau proxy của Vercel
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    app.secret_key = config.SECRET_KEY
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(days=config.SESSION_DAYS),
    )

    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(learning_bp)

    # Route dự phòng đảm bảo thư mục static luôn trả về file nếu CDN không bắt được
    @app.route("/static/<path:filename>")
    def serve_static(filename):
        return send_from_directory(os.path.join(BASE_DIR, "static"), filename)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
