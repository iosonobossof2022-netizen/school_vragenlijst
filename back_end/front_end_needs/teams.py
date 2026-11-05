from flask import Blueprint, jsonify

from back_end.extensions import db
from back_end.models import Antwoord, Dimensie, Team
from back_end.serializers import inzending_naar_json, team_naar_json
from back_end.utils import json_body, genereer_unieke_code

teams_bp = Blueprint("teams", __name__)


@teams_bp.get("/beheer/teams")
def teams_beheer():
    teams = Team.query.order_by(Team.id).all()
    return jsonify(teams=[team_naar_json(team) for team in teams])


@teams_bp.post("/voeg-team-toe")
def voeg_team_toe():
    data = json_body()
    if data is None:
        return jsonify(error="Verstuur een JSON-object met 'team_naam'."), 400

    team_naam = data.get("team_naam")
    if not isinstance(team_naam, str) or not team_naam.strip():
        return jsonify(error="'team_naam' moet een niet-lege tekst zijn."), 400

    team_naam = team_naam.strip()
    if Team.query.filter_by(naam=team_naam).first():
        return jsonify(error="Er bestaat al een team met deze naam."), 409

    team = Team(naam=team_naam, code=genereer_unieke_code())
    db.session.add(team)
    db.session.commit()
    return jsonify(team=team_naar_json(team)), 201


@teams_bp.get("/overzicht")
def overzicht():
    teams = Team.query.order_by(Team.id).all()
    return jsonify(
        teams=[
            {
                "team_naam": team.naam,
                "team_code": team.code,
                "aantal_leden": len(team.inzendingen),
            }
            for team in teams
            if team.inzendingen
        ]
    )


@teams_bp.get("/overzicht/team/<string:team_code>")
def team_detail(team_code):
    team = Team.query.filter_by(code=team_code.upper().strip()).first_or_404()
    inzendingen = team.inzendingen
    inzending_ids = [inzending.id for inzending in inzendingen]
    dimensies = Dimensie.query.order_by(Dimensie.id).all()
    berekende_dimensies = []
    som_scores = 0

    for dimensie in dimensies:
        vraag_ids = [vraag.id for vraag in dimensie.vragen]
        antwoorden = (
            Antwoord.query.filter(
                Antwoord.vraag_id.in_(vraag_ids),
                Antwoord.inzending_id.in_(inzending_ids),
            ).all()
            if vraag_ids and inzending_ids
            else []
        )
        totaalscore = sum(antwoord.score for antwoord in antwoorden)
        aantal_mogelijke_antwoorden = len(inzendingen) * len(vraag_ids)
        score = (
            totaalscore / aantal_mogelijke_antwoorden
            if aantal_mogelijke_antwoorden
            else 0
        )
        som_scores += score
        berekende_dimensies.append({"naam": dimensie.naam, "score": round(score, 2)})

    team_score = som_scores / len(dimensies) if dimensies else 0
    return jsonify(
        team={
            "naam": team.naam,
            "code": team.code,
            "aantal_leden": len(inzendingen),
            "score": round(team_score, 2),
        },
        dimensies=berekende_dimensies,
        leden=[inzending_naar_json(inzending) for inzending in inzendingen],
    )


@teams_bp.post("/verwijder/team/<string:team_code>")
def verwijder_team(team_code):
    team = Team.query.filter_by(code=team_code.upper().strip()).first_or_404()
    db.session.delete(team)
    db.session.commit()
    return jsonify(
        bericht="Team en bijbehorende inzendingen verwijderd.", team_code=team_code
    )


@teams_bp.post("/verwijder/beheer-team/<int:team_id>")
def verwijder_beheer_team(team_id):
    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    return jsonify(
        bericht="Team en bijbehorende inzendingen verwijderd.", team_id=team_id
    )
