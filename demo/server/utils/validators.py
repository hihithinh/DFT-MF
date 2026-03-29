import os
from werkzeug.utils import secure_filename
from typing import Dict, Any

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def validate_video_file(file) -> Dict[str, Any]:
    """Validate uploaded video file"""
    result = {'valid': True, 'error': None, 'code': None}
    
    # Check if file exists
    if not file or file.filename == '':
        result['valid'] = False
        result['error'] = 'No file selected'
        result['code'] = 'NO_FILE'
        return result
    
    # Check file extension
    filename = secure_filename(file.filename)
    if not ('.' in filename and 
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
        result['valid'] = False
        result['error'] = f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        result['code'] = 'INVALID_TYPE'
        return result
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        result['valid'] = False
        result['error'] = f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'
        result['code'] = 'FILE_TOO_LARGE'
        return result
    
    # Skip content_type check for curl compatibility
    # if not file.content_type or not file.content_type.startswith('video/'):
    #     result['valid'] = False
    #     result['error'] = 'Invalid file format'
    #     result['code'] = 'INVALID_FORMAT'
    #     return result
    
    return result

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for storage"""
    return secure_filename(filename)

def get_file_size_mb(file) -> float:
    """Get file size in MB"""
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    return round(size / (1024 * 1024), 2)
