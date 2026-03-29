from datetime import datetime
from typing import Dict, Any, Optional

class VideoAnalysis:
    """Model for video analysis results"""
    
    def __init__(self, task_id: str, filename: str, original_filename: str, file_size: int):
        self.task_id = task_id
        self.filename = filename
        self.original_filename = original_filename
        self.file_size = file_size
        self.upload_time = datetime.now()
        self.status = 'processing'
        self.total_frames = 0
        self.mouth_frames = 0
        self.predictions = None
        self.processing_time = 0
        self.completed_time = None
        self.error_message = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'task_id': self.task_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'upload_time': self.upload_time.isoformat(),
            'status': self.status,
            'total_frames': self.total_frames,
            'mouth_frames': self.mouth_frames,
            'predictions': self.predictions,
            'processing_time': self.processing_time,
            'completed_time': self.completed_time.isoformat() if self.completed_time else None,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoAnalysis':
        """Create instance from dictionary"""
        analysis = cls(
            task_id=data['task_id'],
            filename=data['filename'],
            original_filename=data['original_filename'],
            file_size=data['file_size']
        )
        
        analysis.upload_time = datetime.fromisoformat(data['upload_time'])
        analysis.status = data['status']
        analysis.total_frames = data.get('total_frames', 0)
        analysis.mouth_frames = data.get('mouth_frames', 0)
        analysis.predictions = data.get('predictions')
        analysis.processing_time = data.get('processing_time', 0)
        analysis.error_message = data.get('error_message')
        
        if data.get('completed_time'):
            analysis.completed_time = datetime.fromisoformat(data['completed_time'])
        
        return analysis
