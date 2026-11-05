import secrets

from flask import request

from .models import Team


def json_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def genereer_unieke_code():
    while True:
        code = secrets.token_hex(3).upper()[:5]
        if not Team.query.filter_by(code=code).first():
            return code
