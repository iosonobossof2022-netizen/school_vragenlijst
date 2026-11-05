### disclaimer

deze uitleg heb ik laten schrijven door AI dan is het wat duidelijker en overzichtelijker
ik heb de code ook door AI laten opschonen  hij is van 400 regels code naar 600+ gegaan...
maar in elk geval hij doet het en hieronder is de uitleg -->

### nog belangrijke detail

voordat ik je aan de uitleg van AI overlaat ik heb hem zo gemaakt dat je eerst via de admin panel vragen en dimensies toe moet voegen dus nu als je bijvoorbeeld dimensie 10 vraag 1 doet slaat hij niks op omdat die niet in de database bestaat dus eerst moet je in de admin panel de dimensies aanmaken en dan per dimensie 5 vragen nu wel echt de uitleg van AI -->

# Climate Team API

This Flask backend provides JSON endpoints for a separate frontend. Start it
from the project root with:

```powershell
python app.py
```

The frontend should send requests to the deployed server's base URL. For JSON
POST requests, set `Content-Type: application/json`. Successful responses and
errors are JSON. The API does not currently provide authentication or
authorization; protect management and delete endpoints before exposing the
server publicly.

## Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Get all dimensions and questions. |
| GET | `/beheer/teams` | List teams, including their codes and submission counts. |
| GET | `/beheer/vragen` | Get dimensions and questions for question management. |
| GET | `/overzicht` | List teams that have submissions. |
| GET | `/overzicht/team/<team_code>` | Get a team's average scores and submissions. |
| GET | `/overzicht/lid/<inzending_id>` | Get one submission and its answers. |
| POST | `/voeg-team-toe` | Create a team. |
| POST | `/voeg-dimensie-toe` | Create a dimension. |
| POST | `/voeg-vraag-toe` | Create a question for a dimension. |
| POST | `/api/scores` | Save a submission for a team. |
| POST | `/verwijder/team/<team_code>` | Delete a team and its submissions. |
| POST | `/verwijder/beheer-team/<team_id>` | Delete a team by its database ID. |
| POST | `/verwijder/lid/<inzending_id>` | Delete one submission. |
| POST | `/verwijder/vraag/<vraag_id>` | Delete a question. |
| POST | `/verwijder/dimensie/<dimensie_id>` | Delete a dimension. |

### Read endpoints

`GET /` and `GET /beheer/vragen` return:

```json
{
  "dimensies": [{"id": 1, "naam": "Samenwerking"}],
  "vragen": [{"id": 1, "tekst": "Voorbeeldvraag", "dimensie_id": 1}]
}
```

`GET /beheer/teams` returns `{"teams": [...]}`. Each team has `id`, `naam`,
`code`, and `aantal_leden`.

`GET /overzicht` returns `{"teams": [...]}`. Each listed team has `team_naam`,
`team_code`, and `aantal_leden`.

`GET /overzicht/team/<team_code>` returns `team` (name, code, member count, and
overall score), `dimensies` (name and average score), and `leden` (submission
IDs and timestamps).

`GET /overzicht/lid/<inzending_id>` returns `inzending` (ID, timestamp, and
team) and `antwoorden` (question ID, question text, dimension name, and score).

### Create and submit endpoints

Create a team:

```http
POST /voeg-team-toe
Content-Type: application/json
```

```json
{"team_naam": "Team Alpha"}
```

Create a dimension with `{"nieuwe_dimensie": "Samenwerking"}`. Create a
question with `{"select_dimensie": 1, "nieuwe_vraag": "Voorbeeldvraag"}`.

Submit scores using question IDs as keys:

```http
POST /api/scores
Content-Type: application/json
```

```json
{"team_code": "ABCDE", "scores": {"1": 4, "2": 3}}
```

Successful create and score-submission requests return status `201`. Duplicate
team or dimension names return `409`; invalid request data returns `400`; an
unknown team, question, dimension, or record returns `404`.

### Delete endpoints

All delete routes use `POST` and have no request body. They return a JSON
message on success. Use the `id` or `code` values returned by the read
endpoints to construct the path. Deleting a team also deletes its submissions.
