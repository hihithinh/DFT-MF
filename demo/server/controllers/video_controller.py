import cv2
import numpy as np
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from server.services.video_processor import VideoProcessor
from server.services.deepfake_analyzer import DeepfakeAnalyzer
from server.models.video_analysis import VideoAnalysis
from server.config.storage import StorageConfig

class VideoController:
    """Controller with step-by-step processing"""
    
    def __init__(self):
        self.processor = VideoProcessor()
        self.analyzer = DeepfakeAnalyzer()
    
    def upload_and_extract_frames(self, file):
        """Step 1: Upload video and extract frames"""
        try:
            # Generate unique task ID
            task_id = str(uuid.uuid4())
            
            # Create storage directories
            storage_paths = StorageConfig.ensure_storage_dirs(task_id)
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_filename = f"{timestamp}_{filename}"
            
            video_path = StorageConfig.get_video_path(task_id, safe_filename)
            file.save(video_path)
            
            # Extract frames
            print(f"Step 1: Extracting frames for {task_id}")
            frames_result = self.processor.extract_frames(
                video_path, 
                str(storage_paths['frames']),
                str(storage_paths['samples_frames'])
            )
            
            # Initialize status
            status_data = {
                "upload": {
                    "totalFrames": frames_result['count'],
                    "extractedFrames": frames_result['count']
                },
                "cropMouth": {
                    "extractedFrames": frames_result['count'],
                    "processedFrames": 0,
                    "croppedMouths": 0
                },
                "analyze": {
                    "croppedMouths": 0,
                    "analyzedMouths": 0,
                    "fakeMouths": 0,
                    "realMouths": 0
                }
            }
            
            # Write status to file
            StorageConfig.write_status(task_id, status_data)
            
            # Get sample frame URLs and save to status for real-time updates
            sample_frames = StorageConfig.get_sample_urls(task_id, 'frames')
            status_data['upload']['sample_frames'] = sample_frames
            StorageConfig.write_status(task_id, status_data)
            
            # Return simplified response
            return {
                'task_id': task_id,
                'total_frames': frames_result['count'],
                'sample_frames': sample_frames
            }
            
        except Exception as e:
            print(f"Step 1 error: {str(e)}")
            return {
                'error': 'Frame extraction failed',
                'details': str(e),
                'step': 'upload_failed'
            }
    
    def crop_mouth_frames(self, task_id):
        """Step 2: Crop mouth frames from extracted frames"""
        try:
            print(f"DEBUG: Starting crop_mouth_frames for task_id: {task_id}")
            
            # Check if task exists
            frames_path = StorageConfig.get_frames_path(task_id)
            print(f"DEBUG: Frames path: {frames_path}, exists: {frames_path.exists()}")
            
            if not frames_path.exists():
                return {
                    'error': 'Task not found or frames not extracted',
                    'code': 'TASK_NOT_FOUND'
                }
            
            # Get video path for processing
            storage_info = StorageConfig.get_storage_info(task_id)
            print(f"DEBUG: Storage info: {storage_info}")
            
            if not storage_info['video_files']:
                return {
                    'error': 'No video file found',
                    'code': 'NO_VIDEO'
                }
            
            video_path = StorageConfig.get_video_path(task_id, storage_info['video_files'][0])
            print(f"DEBUG: Video path: {video_path}")
            
            print(f"Step 2: Cropping mouth frames for {task_id}")
            mouth_result = self.processor.process_video_frames(str(video_path), task_id, num_samples=10)
            print(f"DEBUG: Mouth result: {mouth_result}")
            
            # Read current status
            status_data = StorageConfig.read_status(task_id)
            
            # Update cropMouth status
            status_data['cropMouth']['croppedMouths'] = mouth_result['mouth_frames']
            status_data['analyze']['croppedMouths'] = mouth_result['mouth_frames']
            
            # Write updated status
            StorageConfig.write_status(task_id, status_data)
            
            # Get sample mouth URLs and save to status for real-time updates
            sample_mouths = StorageConfig.get_sample_urls(task_id, 'mouths')
            status_data['cropMouth']['sample_mouths'] = sample_mouths
            status_data['analyze']['sample_mouths'] = sample_mouths
            StorageConfig.write_status(task_id, status_data)
            
            # Return simplified response
            return {
                'cropped_mouths': mouth_result['mouth_frames'],
                'sample_mouths': sample_mouths
            }
            
        except Exception as e:
            print(f"Step 2 error: {str(e)}")
            return {
                'error': 'Mouth cropping failed',
                'details': str(e),
                'step': 'crop_mouth_failed'
            }
    
    def analyze_deepfake(self, task_id):
        """Step 3: Analyze mouth frames with CNN"""
        try:
            # Check if mouth frames exist
            mouth_path = StorageConfig.get_mouth_path(task_id)
            if not mouth_path.exists():
                return {
                    'error': 'No mouth frames found',
                    'code': 'NO_MOUTH_FRAMES'
                }
            
            print(f"Step 3: Analyzing deepfake for {task_id}")
            analysis_result = self.analyzer.analyze_video_directory(task_id, num_samples=10)
            
            # Read current status
            status_data = StorageConfig.read_status(task_id)
            
            # Extract real/fake counts from predictions
            predictions = analysis_result.get('predictions', {})
            fake_count = predictions.get('fake_count', 0)
            real_count = predictions.get('real_count', 0)
            total_analyzed = analysis_result.get('total_analyzed', 0)
            
            # Update analyze status
            status_data['analyze']['analyzedMouths'] = total_analyzed
            status_data['analyze']['fakeMouths'] = fake_count
            status_data['analyze']['realMouths'] = real_count
            
            # Write updated status
            StorageConfig.write_status(task_id, status_data)
            
            # Get sample analyzed mouth URLs with labels and save to status for real-time updates
            sample_analyzed = StorageConfig.get_sample_urls(task_id, 'analyzed')
            status_data['analyze']['sample_analyzed'] = sample_analyzed
            StorageConfig.write_status(task_id, status_data)
            
            # Return complete response with all analysis data
            return {
                'fake_mouths': fake_count,
                'real_mouths': real_count,
                'sample_analyzed': sample_analyzed,
                'confidence': analysis_result.get('predictions', {}).get('confidence', 0.0),
                'confidence_distribution': analysis_result.get('confidence_distribution', {}),
                'timeline_data': analysis_result.get('timeline_data', [])
            }
            
        except Exception as e:
            print(f"Step 3 error: {str(e)}")
            return {
                'error': 'Deepfake analysis failed',
                'details': str(e),
                'step': 'analysis_failed'
            }
    
    def get_task_status(self, task_id):
        """Get complete task status from status.json"""
        try:
            status_data = StorageConfig.read_status(task_id)
            
            if not status_data:
                return None
                
            return status_data
                
        except Exception as e:
            print(f"Status check error: {str(e)}")
            return None
    
    def cleanup_task(self, task_id):
        """Clean up storage for a task"""
        return StorageConfig.cleanup_storage(task_id)
