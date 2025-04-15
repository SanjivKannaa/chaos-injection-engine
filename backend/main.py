from flask import Flask
from flask_cors import CORS
from extensions import db, migrate
from config import Config
from routes.resource_gathering import resource_gathering_bp
from routes.resource_exhaustion import resource_exhaustion_bp
from routes.microservice_failure import microservice_failure_bp
# from routes.network_failure import network_failure_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Extensions
db.init_app(app)
migrate.init_app(app, db)
CORS(app, resources={r"/*": {"origins": "*"}})

# init DB tables
with app.app_context():
    db.create_all()

# Register Blueprints
app.register_blueprint(resource_gathering_bp, url_prefix='/resource_gathering')
app.register_blueprint(resource_exhaustion_bp, url_prefix='/resource_exhaustion')
app.register_blueprint(microservice_failure_bp, url_prefix='/microservice_failure')

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)