from flask import Flask, render_template


def create_app() -> Flask:
    """Cria a aplicação web do ImportAtlas."""
    app = Flask(__name__)

    @app.get("/")
    def pagina_inicial() -> str:
        return render_template("index.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run()
