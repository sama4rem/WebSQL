import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .models import db

def create_app():
    app = Flask(__name__)

    # ✅ Use the Supabase Session Pooler link (IPv4-friendly)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres.iucqvevijwcxawkqqdos:sama4remsupabase@aws-0-eu-west-3.pooler.supabase.com:5432/postgres"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    from .routes import app_routes
    app.register_blueprint(app_routes)

    return app
