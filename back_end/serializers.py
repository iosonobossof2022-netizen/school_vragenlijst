from .models import Antwoord, Dimensie, Inzending, Vraag


def vraag_naar_json(vraag):
    return {
        "id": vraag.id,
        "tekst": vraag.tekst,
        "dimensie_id": vraag.dimensie_id,
    }


def inzending_naar_json(inzending):
    return {
        "id": inzending.id,
        "ingevuld_op": (
            inzending.ingevuld_op.isoformat() if inzending.ingevuld_op else None
        ),
    }


def dimensie_naar_json(dimensie):
    return {"id": dimensie.id, "naam": dimensie.naam}


def team_naar_json(team):
    return {
        "id": team.id,
        "naam": team.naam,
        "code": team.code,
        "aantal_leden": len(team.inzendingen),
    }


def catalogus_naar_json():
    return {
        "dimensies": [
            dimensie_naar_json(dimensie)
            for dimensie in Dimensie.query.order_by(Dimensie.id).all()
        ],
        "vragen": [
            vraag_naar_json(vraag) for vraag in Vraag.query.order_by(Vraag.id).all()
        ],
    }


def antwoord_naar_json(antwoord: Antwoord):
    vraag = antwoord.vraag
    return {
        "vraag_id": vraag.id,
        "vraag": vraag.tekst,
        "dimensie": vraag.dimensie.naam,
        "score": antwoord.score,
    }
