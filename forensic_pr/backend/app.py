from flask import Flask
from flask_cors import CORS
from db.database import init_db
from routes.audio_routes import audio_bp
from routes.metadata_routes import metadata_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    CORS(app)  # Allow cross-origin requests (React frontend)
    init_db(app)  # Initialize DB

    # Add root route
    @app.route("/")
    def index():
        return "Backend is running!"

    # Add favicon route
    import os
    from flask import send_from_directory
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')

    # Register Blueprints
    app.register_blueprint(audio_bp, url_prefix='/api/audio')
    app.register_blueprint(metadata_bp, url_prefix='/api/metadata')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
