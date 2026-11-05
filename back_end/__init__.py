from flask import Flask, jsonify

from .config import Config
from .database import initialize_database
from .extensions import db
from .models import Antwoord, Dimensie, Inzending, Team, Vraag
from .front_end_needs import blueprints


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    @app.errorhandler(400)
    def bad_request(_error):
        return (
            jsonify(error="Ongeldig verzoek. Controleer of de JSON-body geldig is."),
            400,
        )

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify(error="Niet gevonden."), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return (
            jsonify(error="Deze HTTP-methode is niet toegestaan voor dit endpoint."),
            405,
        )

    with app.app_context():
        initialize_database()

    return app


__all__ = [
    "Antwoord",
    "Dimensie",
    "Inzending",
    "Team",
    "Vraag",
    "create_app",
    "db",
]
