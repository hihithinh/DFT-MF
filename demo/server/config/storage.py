import os
import json
from pathlib import Path

class StorageConfig:
    """Storage configuration for DFT-MF"""
    
    # Base storage directory (inside server folder like Laravel)
    BASE_STORAGE = Path(__file__).parent.parent / "storage"
    
    # Model paths (from root directory)
    MODEL_CONFIG = {
        'shape_predictor': Path(__file__).parent.parent.parent.parent / "shape_predictor_68_face_landmarks.dat",
        'trained_models': {
            'CelebDF': Path(__file__).parent.parent.parent.parent / "trained_models",
            'UADFV': Path(__file__).parent.parent.parent.parent / "trained_models"
        }
    }
    
    @classmethod
    def get_storage_path(cls, task_id: str, subfolder: str = "") -> Path:
        """Get storage path for task"""
        if subfolder:
            return cls.BASE_STORAGE / task_id / subfolder
        return cls.BASE_STORAGE / task_id
    
    @classmethod
    def get_video_path(cls, task_id: str, filename: str) -> Path:
        """Get video storage path"""
        return cls.get_storage_path(task_id) / filename
    
    @classmethod
    def get_frames_path(cls, task_id: str) -> Path:
        """Get ExtractFrams storage path"""
        return cls.get_storage_path(task_id, "ExtractFrams")
    
    @classmethod
    def get_mouth_path(cls, task_id: str) -> Path:
        """Get CroppedMouth storage path"""
        return cls.get_storage_path(task_id, "CroppedMouth")
    
    @classmethod
    def get_samples_path(cls, task_id: str, sample_type: str = "") -> Path:
        """Get samples storage path (frames, mouths, analyzed)"""
        if sample_type:
            return cls.get_storage_path(task_id, f"samples/{sample_type}")
        return cls.get_storage_path(task_id, "samples")
    
    @classmethod
    def get_sample_urls(cls, task_id: str, sample_type: str) -> list:
        """Get URLs for sample images"""
        import glob
        samples_dir = cls.get_samples_path(task_id, sample_type)
        if not samples_dir.exists():
            return []
        
        sample_files = sorted(glob.glob(str(samples_dir / "*.jpg")))
        # Convert to relative URLs
        urls = []
        for filepath in sample_files:
            # Extract relative path from storage base
            rel_path = Path(filepath).relative_to(cls.BASE_STORAGE)
            url = f"/storage/{rel_path.as_posix()}"
            
            # For analyzed samples, extract label from filename
            filename = Path(filepath).name
            if sample_type == 'analyzed' and '_' in filename:
                parts = filename.rsplit('_', 1)
                if len(parts) == 2:
                    label = parts[1].replace('.jpg', '')
                    urls.append({'url': url, 'label': label})
                else:
                    urls.append({'url': url, 'label': None})
            else:
                urls.append(url)
        
        return urls
    
    @classmethod
    def get_model_path(cls, dataset: str = 'CelebDF') -> Path:
        """Get trained model path for dataset"""
        import glob
        model_dir = cls.MODEL_CONFIG['trained_models'][dataset]
        model_files = list(model_dir.glob(f"CNN_{dataset}_*_final.h5"))
        return sorted(model_files)[-1] if model_files else None
    
    @classmethod
    def get_shape_predictor_path(cls) -> Path:
        """Get shape predictor path"""
        return cls.MODEL_CONFIG['shape_predictor']
    
    @classmethod
    def ensure_storage_dirs(cls, task_id: str):
        """Create all necessary storage directories for task"""
        base_path = cls.get_storage_path(task_id)
        frames_path = cls.get_frames_path(task_id)
        mouth_path = cls.get_mouth_path(task_id)
        samples_frames_path = cls.get_samples_path(task_id, 'frames')
        samples_mouths_path = cls.get_samples_path(task_id, 'mouths')
        samples_analyzed_path = cls.get_samples_path(task_id, 'analyzed')
        
        # Create all directories
        base_path.mkdir(parents=True, exist_ok=True)
        frames_path.mkdir(parents=True, exist_ok=True)
        mouth_path.mkdir(parents=True, exist_ok=True)
        samples_frames_path.mkdir(parents=True, exist_ok=True)
        samples_mouths_path.mkdir(parents=True, exist_ok=True)
        samples_analyzed_path.mkdir(parents=True, exist_ok=True)
        
        return {
            'base': base_path,
            'frames': frames_path,
            'mouth': mouth_path,
            'samples_frames': samples_frames_path,
            'samples_mouths': samples_mouths_path,
            'samples_analyzed': samples_analyzed_path
        }
    
    @classmethod
    def cleanup_storage(cls, task_id: str):
        """Clean up storage for task"""
        try:
            import shutil
            base_path = cls.get_storage_path(task_id)
            if base_path.exists():
                shutil.rmtree(base_path)
            return True
        except Exception as e:
            print(f"Failed to cleanup storage for {task_id}: {e}")
            return False
    
    @classmethod
    def get_status_path(cls, task_id: str) -> Path:
        """Get status.json path for task"""
        return cls.get_storage_path(task_id) / "status.json"
    
    @classmethod
    def write_status(cls, task_id: str, status_data: dict):
        """Write status to status.json"""
        status_path = cls.get_status_path(task_id)
        with open(status_path, 'w') as f:
            json.dump(status_data, f, indent=2)
    
    @classmethod
    def read_status(cls, task_id: str) -> dict:
        """Read status from status.json"""
        status_path = cls.get_status_path(task_id)
        if status_path.exists():
            with open(status_path, 'r') as f:
                return json.load(f)
        return {}
    
    @classmethod
    def get_storage_info(cls, task_id: str) -> dict:
        """Get storage information for task"""
        base_path = cls.get_storage_path(task_id)
        frames_path = cls.get_frames_path(task_id)
        mouth_path = cls.get_mouth_path(task_id)
        
        info = {
            'task_id': task_id,
            'base_path': str(base_path),
            'frames_path': str(frames_path),
            'mouth_path': str(mouth_path),
            'exists': base_path.exists(),
            'video_files': [],
            'frame_count': 0,
            'mouth_count': 0
        }
        
        if base_path.exists():
            # Count video files
            info['video_files'] = [f.name for f in list(base_path.glob("*.mp4")) + list(base_path.glob("*.avi")) + list(base_path.glob("*.mov"))]
            
            # Count frames
            if frames_path.exists():
                info['frame_count'] = len(list(frames_path.glob("*.jpg")))
            
            # Count mouth crops
            if mouth_path.exists():
                info['mouth_count'] = len(list(mouth_path.glob("*.jpg")))
        
        return info
