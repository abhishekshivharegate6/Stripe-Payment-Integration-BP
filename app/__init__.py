from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from .models import db

migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints (routes)
    from .routes.main import main_bp
    from .routes.onboarding import onboarding_bp
    from .routes.payments import payments_bp
    from .routes.webhooks import webhooks_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(webhooks_bp)

    return app
