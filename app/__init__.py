# app/__init__.py
from flask import Flask

def create_app():
    # Initialize Flask app with static and template folders relative to 'app'
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    # Import and register the blueprint from routes
    from .routes import bp
    app.register_blueprint(bp)
    
    return app