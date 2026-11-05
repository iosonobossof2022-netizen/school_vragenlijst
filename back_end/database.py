from .extensions import db


def initialize_database():
    migrate_legacy_inzending_schema()
    db.create_all()


def migrate_legacy_inzending_schema():
    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    try:
        tables = {
            row[0]
            for row in cursor.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        if "inzending" not in tables:
            return

        columns = {
            row[1] for row in cursor.execute("PRAGMA table_info(inzending)").fetchall()
        }
        if "team_id" in columns or "team_code" not in columns:
            return

        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("BEGIN")
        try:
            team_lookup = {}
            for team_id, naam, code in cursor.execute(
                "SELECT id, naam, code FROM team"
            ).fetchall():
                team_lookup[code] = team_id
                team_lookup.setdefault(naam, team_id)

            submissions = []
            source_ids = {}
            used_ids = set()
            next_id = 1
            for source in ("team_inzending", "inzending"):
                if source not in tables:
                    continue
                for old_id, team_code, ingevuld_op in cursor.execute(
                    f"SELECT id, team_code, ingevuld_op FROM {source}"
                ).fetchall():
                    team_id = team_lookup.get(team_code)
                    if team_id is None:
                        raise RuntimeError(
                            f"Kan oude inzending {old_id} niet koppelen aan team "
                            f"'{team_code}'."
                        )
                    new_id = old_id
                    if new_id in used_ids:
                        next_id = max(next_id, max(used_ids) + 1)
                        new_id = next_id
                    used_ids.add(new_id)
                    next_id = max(next_id, new_id + 1)
                    source_ids[(source, old_id)] = new_id
                    submissions.append((new_id, team_id, ingevuld_op))

            answer_rows = []
            answer_source = None
            if "antwoord" in tables:
                foreign_keys = cursor.execute(
                    "PRAGMA foreign_key_list(antwoord)"
                ).fetchall()
                answer_source = next(
                    (row[2] for row in foreign_keys if row[3] == "inzending_id"),
                    None,
                )
                answer_rows = cursor.execute(
                    "SELECT id, score, inzending_id, vraag_id FROM antwoord"
                ).fetchall()

            cursor.execute("ALTER TABLE inzending RENAME TO inzending_legacy")
            if "antwoord" in tables:
                cursor.execute("ALTER TABLE antwoord RENAME TO antwoord_legacy")

            cursor.execute(
                "CREATE TABLE inzending ("
                "id INTEGER NOT NULL PRIMARY KEY, "
                "team_id INTEGER NOT NULL, "
                "ingevuld_op DATETIME, "
                "FOREIGN KEY(team_id) REFERENCES team (id))"
            )
            cursor.executemany(
                "INSERT INTO inzending (id, team_id, ingevuld_op) VALUES (?, ?, ?)",
                submissions,
            )

            if "antwoord" in tables:
                cursor.execute(
                    "CREATE TABLE antwoord ("
                    "id INTEGER NOT NULL PRIMARY KEY, "
                    "score INTEGER NOT NULL, "
                    "inzending_id INTEGER NOT NULL, "
                    "vraag_id INTEGER NOT NULL, "
                    "FOREIGN KEY(inzending_id) REFERENCES inzending (id), "
                    "FOREIGN KEY(vraag_id) REFERENCES vraag (id))"
                )
                migrated_answers = []
                for answer_id, score, old_submission_id, vraag_id in answer_rows:
                    new_submission_id = source_ids.get(
                        (answer_source, old_submission_id)
                    )
                    if new_submission_id is None:
                        raise RuntimeError(
                            f"Kan antwoord {answer_id} niet koppelen aan een inzending."
                        )
                    migrated_answers.append(
                        (answer_id, score, new_submission_id, vraag_id)
                    )
                cursor.executemany(
                    "INSERT INTO antwoord "
                    "(id, score, inzending_id, vraag_id) VALUES (?, ?, ?, ?)",
                    migrated_answers,
                )
                cursor.execute("DROP TABLE antwoord_legacy")

            cursor.execute("DROP TABLE inzending_legacy")
            if "team_inzending" in tables:
                cursor.execute("DROP TABLE team_inzending")
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.execute("PRAGMA foreign_keys = ON")
    finally:
        cursor.close()
        connection.close()
