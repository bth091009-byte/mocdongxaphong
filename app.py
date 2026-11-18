from datetime import timedelta
from flask import Flask
import config
from routes.main_routes import main_bp
from routes.chat_routes import chat_bp
from routes.auth_routes import auth_bp
from routes.learning_routes import learning_bp

def create_app():
    app = Flask(__name__)
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
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
