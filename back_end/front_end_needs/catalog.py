from flask import Blueprint, jsonify

from back_end.extensions import db
from back_end.models import Dimensie, Vraag
from back_end.serializers import (
    catalogus_naar_json,
    dimensie_naar_json,
    vraag_naar_json,
)
from back_end.utils import json_body

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.get("/")
def home():
    return jsonify(catalogus_naar_json())


@catalog_bp.get("/beheer/vragen")
def vragen_beheer():
    return jsonify(catalogus_naar_json())


@catalog_bp.post("/voeg-dimensie-toe")
def voeg_dimensie_toe():
    data = json_body()
    if data is None:
        return jsonify(error="Verstuur een JSON-object met 'nieuwe_dimensie'."), 400

    naam = data.get("nieuwe_dimensie")
    if not isinstance(naam, str) or not naam.strip():
        return jsonify(error="'nieuwe_dimensie' moet een niet-lege tekst zijn."), 400

    naam = naam.strip()
    if Dimensie.query.filter_by(naam=naam).first():
        return jsonify(error="Er bestaat al een dimensie met deze naam."), 409

    dimensie = Dimensie(naam=naam)
    db.session.add(dimensie)
    db.session.commit()
    return jsonify(dimensie=dimensie_naar_json(dimensie)), 201


@catalog_bp.post("/voeg-vraag-toe")
def voeg_vraag_toe():
    data = json_body()
    if data is None:
        return (
            jsonify(
                error="Verstuur een JSON-object met 'select_dimensie' en 'nieuwe_vraag'."
            ),
            400,
        )

    vraag_tekst = data.get("nieuwe_vraag")
    dimensie_id = data.get("select_dimensie")
    if not isinstance(vraag_tekst, str) or not vraag_tekst.strip():
        return jsonify(error="'nieuwe_vraag' moet een niet-lege tekst zijn."), 400

    try:
        dimensie_id = int(dimensie_id)
    except (TypeError, ValueError):
        return jsonify(error="'select_dimensie' moet een geldig dimensie-ID zijn."), 400

    if not db.session.get(Dimensie, dimensie_id):
        return jsonify(error="Dimensie niet gevonden."), 404

    vraag = Vraag(tekst=vraag_tekst.strip(), dimensie_id=dimensie_id)
    db.session.add(vraag)
    db.session.commit()
    return jsonify(vraag=vraag_naar_json(vraag)), 201


@catalog_bp.post("/verwijder/vraag/<int:vraag_id>")
def verwijder_vraag(vraag_id):
    vraag = Vraag.query.get_or_404(vraag_id)
    db.session.delete(vraag)
    db.session.commit()
    return jsonify(bericht="Vraag verwijderd.", vraag_id=vraag_id)


@catalog_bp.post("/verwijder/dimensie/<int:dimensie_id>")
def verwijder_dimensie(dimensie_id):
    dimensie = Dimensie.query.get_or_404(dimensie_id)
    db.session.delete(dimensie)
    db.session.commit()
    return jsonify(bericht="Dimensie verwijderd.", dimensie_id=dimensie_id)
