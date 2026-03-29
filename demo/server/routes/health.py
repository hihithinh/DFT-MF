from flask import Blueprint
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.services.health_service import HealthService

health_bp = Blueprint('health', __name__)

@health_bp.route('/')
def index():
    """Health check endpoint"""
    service = HealthService()
    health_status = service.get_health_status()
    
    return health_status, 200 if health_status['status'] == 'healthy' else 503
