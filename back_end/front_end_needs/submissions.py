from flask import Blueprint, jsonify

from back_end.extensions import db
from back_end.models import Antwoord, Inzending, Vraag, Team
from back_end.serializers import antwoord_naar_json, inzending_naar_json
from back_end.utils import json_body

submissions_bp = Blueprint("submissions", __name__)


@submissions_bp.post("/api/scores")
def bewaar_scores():
    data = json_body()
    if data is None:
        return (
            jsonify(error="Verstuur een JSON-object met 'team_code' en 'scores'."),
            400,
        )

    team_code = data.get("team_code")
    scores = data.get("scores")
    if not isinstance(team_code, str) or not team_code.strip():
        return jsonify(error="'team_code' moet een niet-lege tekst zijn."), 400
    if not isinstance(scores, dict):
        return (
            jsonify(error="'scores' moet een object zijn met vraag-ID's en scores."),
            400,
        )

    team = Team.query.filter_by(code=team_code.upper().strip()).first()
    if not team:
        return jsonify(error="Deze teamcode bestaat niet."), 404

    vragen = {vraag.id for vraag in Vraag.query.all()}
    gevalideerde_scores = []
    for vraag_id, score in scores.items():
        try:
            vraag_id = int(vraag_id)
            if isinstance(score, bool):
                raise ValueError
            score = int(score)
        except (TypeError, ValueError):
            return (
                jsonify(error="Vraag-ID's en scores moeten gehele getallen zijn."),
                400,
            )

        if vraag_id not in vragen:
            return jsonify(error=f"Vraag {vraag_id} bestaat niet."), 400
        gevalideerde_scores.append((vraag_id, score))

    inzending = Inzending(team_id=team.id)
    db.session.add(inzending)
    db.session.flush()
    for vraag_id, score in gevalideerde_scores:
        db.session.add(
            Antwoord(
                score=score,
                inzending_id=inzending.id,
                vraag_id=vraag_id,
            )
        )
    db.session.commit()

    return (
        jsonify(
            bericht="Scores opgeslagen.",
            inzending={
                **inzending_naar_json(inzending),
                "team_code": team.code,
                "scores": {
                    str(vraag_id): score for vraag_id, score in gevalideerde_scores
                },
            },
        ),
        201,
    )


@submissions_bp.get("/overzicht/lid/<int:inzending_id>")
def lid_detail(inzending_id):
    inzending = Inzending.query.get_or_404(inzending_id)
    return jsonify(
        inzending={
            **inzending_naar_json(inzending),
            "team": {"naam": inzending.team.naam, "code": inzending.team.code},
        },
        antwoorden=[antwoord_naar_json(antwoord) for antwoord in inzending.antwoorden],
    )


@submissions_bp.post("/verwijder/lid/<int:inzending_id>")
def verwijder_lid(inzending_id):
    inzending = Inzending.query.get_or_404(inzending_id)
    db.session.delete(inzending)
    db.session.commit()
    return jsonify(bericht="Inzending verwijderd.", inzending_id=inzending_id)
