from flask import Blueprint, request, jsonify, current_app
import sys
import os
import uuid
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.controllers.video_controller import VideoController
from server.middleware.rate_limiter import rate_limit
from server.utils.validators import validate_video_file

api_bp = Blueprint('api', __name__)

# Create singleton controller instance to reuse models
controller = VideoController()

# Step 1: Upload video and extract frames
@api_bp.route('/upload', methods=['POST'])
@rate_limit('10/minute')
def upload_video():
    """Step 1: Upload video and extract frames"""
    try:
        # Validate file
        if 'video' not in request.files:
            return jsonify({
                'error': 'No video file provided',
                'code': 'MISSING_FILE'
            }), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'code': 'NO_FILE_SELECTED'
            }), 400
        
        # Validate file type and size
        validation_result = validate_video_file(file)
        if not validation_result['valid']:
            return jsonify({
                'error': validation_result['error'],
                'code': validation_result['code']
            }), 400
        
        # Process step 1: upload and extract frames
        result = controller.upload_and_extract_frames(file)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': str(e) if request.debug else None
        }), 500

# Step 2: Crop mouth frames
@api_bp.route('/<task_id>/crop-mouth', methods=['POST'])
@rate_limit('20/minute')
def crop_mouth(task_id):
    """Step 2: Crop mouth frames from extracted frames"""
    try:
        result = controller.crop_mouth_frames(task_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': str(e) if request.debug else None
        }), 500

# Step 3: Analyze with CNN
@api_bp.route('/<task_id>/analyze', methods=['POST'])
@rate_limit('20/minute')
def analyze_deepfake(task_id):
    """Step 3: Analyze mouth frames with CNN for deepfake detection"""
    try:
        result = controller.analyze_deepfake(task_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': str(e) if current_app.debug else None
        }), 500

# Get task status
@api_bp.route('/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """Get status of all processing steps"""
    try:
        status = controller.get_task_status(task_id)
        
        if not status:
            return jsonify({
                'error': 'Task not found',
                'code': 'TASK_NOT_FOUND'
            }), 404
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': str(e) if request.debug else None
        }), 500

# Cleanup task
@api_bp.route('/<task_id>/cleanup', methods=['DELETE'])
def cleanup_task(task_id):
    """Clean up storage for a task"""
    try:
        result = controller.cleanup_task(task_id)
        
        return jsonify({
            'success': result,
            'task_id': task_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': str(e) if request.debug else None
        }), 500

# Health check
@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'service': 'DFT-MF API',
        'steps': ['upload', 'crop-mouth', 'analyze'],
        'storage': 'server/storage/*'
    })
