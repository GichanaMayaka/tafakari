import os

from . import create_app

app = create_app()

if __name__ == "__main__":
    os.environ.get("ENV_STATE", "dev")
    app.run(host="0.0.0.0", port=8000, debug=True)
