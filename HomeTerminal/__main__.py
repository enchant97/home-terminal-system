"""
For running the HTS
"""
from . import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(host="localhost", port=5050, debug=True)
