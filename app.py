from back_end import Antwoord, Dimensie, Inzending, Team, Vraag, create_app, db

app = create_app()


if __name__ == "__main__":
    app.run(debug=False)
