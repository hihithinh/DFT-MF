import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory
from flask_cors import CORS
from server.config.settings import Config
from server.routes.api import api_bp
from server.routes.health import health_bp
from server.config.storage import StorageConfig

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/health')
    
    # Serve static files from storage directory
    @app.route('/storage/<path:filepath>')
    def serve_storage(filepath):
        """Serve files from storage directory"""
        return send_from_directory(str(StorageConfig.BASE_STORAGE), filepath)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG'],
        extra_files=[
            'server/**/*.py',
            'server/**/*.json',
            'requirements.txt'
        ]
    )
