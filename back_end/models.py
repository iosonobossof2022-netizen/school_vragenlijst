from .extensions import db


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    inzendingen = db.relationship(
        "Inzending", backref="team", cascade="all, delete-orphan", lazy=True
    )


class Dimensie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(100), unique=True, nullable=False)
    vragen = db.relationship(
        "Vraag", backref="dimensie", cascade="all, delete-orphan", lazy=True
    )


class Vraag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tekst = db.Column(db.Text, nullable=False)
    dimensie_id = db.Column(db.Integer, db.ForeignKey("dimensie.id"), nullable=False)
    antwoorden = db.relationship(
        "Antwoord", backref="vraag", cascade="all, delete-orphan", lazy=True
    )


class Inzending(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    ingevuld_op = db.Column(db.DateTime, default=db.func.current_timestamp())
    antwoorden = db.relationship(
        "Antwoord", backref="inzending", cascade="all, delete-orphan", lazy=True
    )


class Antwoord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    inzending_id = db.Column(db.Integer, db.ForeignKey("inzending.id"), nullable=False)
    vraag_id = db.Column(db.Integer, db.ForeignKey("vraag.id"), nullable=False)
