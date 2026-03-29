import os
from pathlib import Path

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8080))
    DEBUG = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # File upload settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_VIDEO_SIZE_MB', 100)) * 1024 * 1024
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
    
    # Video processing settings
    FRAME_EXTRACTION_INTERVAL = int(os.environ.get('FRAME_INTERVAL', 10))
    MAX_FRAMES_PER_VIDEO = int(os.environ.get('MAX_FRAMES', 1000))
    
    # Model settings
    MODEL_PATH = os.environ.get('MODEL_PATH', 'trained_models/CNN_CelebDF_20260325_144921_final.h5')
    
    # Security settings
    RATE_LIMIT = os.environ.get('RATE_LIMIT', '100/hour')
    
    @staticmethod
    def init_app(app):
        """Initialize app with this configuration"""
        # Create upload directory if it doesn't exist
        Path(Config.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    RATE_LIMIT = '1000/hour'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            file_handler = RotatingFileHandler(
                'logs/dft-mf.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('DFT-MF startup')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    UPLOAD_FOLDER = 'test_uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB for testing

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
