import cv2
import numpy as np
import os
import sys
from datetime import datetime
from werkzeug.utils import secure_filename
import dlib
import math
import glob
from timeit import default_timer as timer
from server.config.storage import StorageConfig

# Import original pipeline functions
BASE_DIR = StorageConfig.MODEL_CONFIG['trained_models']['CelebDF'].parent.parent
predictor_path = StorageConfig.get_shape_predictor_path()

def get_lip_height(lip):
    """Calculate average height of lip - from original"""
    sum = 0
    for i in [2,3,4]:
        distance = math.sqrt( (lip[i][0] - lip[12-i][0])**2 +
                              (lip[i][1] - lip[12-i][1])**2   )
        sum += distance
    return sum / 3

def get_mouth_height(top_lip, bottom_lip):
    """Get mouth height - from original"""
    sum = 0
    for i in [8,9,10]:
        distance = math.sqrt( (top_lip[i][0] - bottom_lip[18-i][0])**2 + 
                              (top_lip[i][1] - bottom_lip[18-i][1])**2   )
        sum += distance
    return sum / 3

def is_mouth_open(face_landmarks):
    """Check if mouth is open - from original"""
    top_lip = face_landmarks['top_lip']
    bottom_lip = face_landmarks['bottom_lip']

    top_lip_height = get_lip_height(top_lip)
    bottom_lip_height = get_lip_height(bottom_lip)
    mouth_height = get_mouth_height(top_lip, bottom_lip)
    
    ratio = 0.4
    if mouth_height > min(top_lip_height, bottom_lip_height) * ratio:
        return True
    else:
        return False

def Crooped_mouth(frame, detector, predictor):
    """Crop mouth from frame using dlib - from original"""
    dets = detector(frame, 1)
    for k, d in enumerate(dets):
        shape = predictor(frame, d)     
        xmouthpoints = [shape.part(x).x for x in range(48,67)]
        ymouthpoints = [shape.part(x).y for x in range(48,67)]
        maxx = max(xmouthpoints)
        minx = min(xmouthpoints)
        maxy = max(ymouthpoints)
        miny = min(ymouthpoints) 
        pad = 10
        mouth = frame[miny-pad:maxy+pad,minx-pad:maxx+pad]
        crop_image = frame[miny-pad:maxy+pad,minx-pad:maxx+pad]
        Final_image = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)
        return Final_image
    return None

def prepare(filepath):
    """Prepare image for model - from original detect_deepfake.py"""
    IMG_SIZE = 50
    img_array = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
    normalized = new_array / 255.0  # Normalize like training
    return normalized.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

class VideoProcessor:
    """Video processor using original pipeline with proper storage"""
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv']
        self.detector = None
        self.predictor = None
        self._load_models()
    
    def _load_models(self):
        """Load dlib models from config paths"""
        try:
            self.detector = dlib.get_frontal_face_detector()
            self.predictor = dlib.shape_predictor(str(predictor_path))
            print("✓ Dlib models loaded successfully")
        except Exception as e:
            print(f"⚠️  Failed to load dlib models: {e}")
            self.detector = None
            self.predictor = None
    
    def extract_frames(self, video_path: str, output_dir: str, samples_dir: str = None, max_frames: int = 1000, num_samples: int = 10) -> dict:
        """Extract frames from video - using original extract_frames.py logic"""
        frames = []
        frame_count = 0
        sample_indices = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            frame_rate = cap.get(cv2.CAP_PROP_FPS)
            total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"Extracting frames: FPS={frame_rate}, Total={total_video_frames}")
            
            # Calculate sample interval for evenly distributed samples
            expected_frames = min(max_frames, total_video_frames)
            if expected_frames > num_samples:
                sample_interval = expected_frames // num_samples
                sample_indices = [i * sample_interval for i in range(num_samples)]
            
            while cap.isOpened():
                frameId = cap.get(cv2.CAP_PROP_POS_FRAMES)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                if frameId % 1 == 0:  # Extract every frame like original
                    # Save frame to output directory
                    filename = os.path.join(output_dir, f"image_{int(frameId)}.jpg")
                    cv2.imwrite(filename, frame)
                    frames.append(frame)
                    
                    # Save sample frame if this is a sample index
                    if samples_dir and frame_count in sample_indices:
                        sample_filename = os.path.join(samples_dir, f"sample_{frame_count}.jpg")
                        cv2.imwrite(sample_filename, frame)
                    
                    frame_count += 1
                
                if frame_count >= max_frames:
                    break
            
            cap.release()
            
            if not frames:
                raise ValueError("No frames extracted from video")
            
            print(f"✓ Extracted {frame_count} frames to {output_dir}")
            if samples_dir:
                print(f"✓ Saved {len(sample_indices)} sample frames to {samples_dir}")
            
            # Get sample URLs for real-time status
            sample_urls = []
            if samples_dir and sample_indices:
                sample_files = sorted(glob.glob(os.path.join(samples_dir, "*.jpg")))
                for filepath in sample_files:
                    rel_path = os.path.relpath(filepath, os.path.dirname(os.path.dirname(samples_dir)))
                    url = f"/storage/{rel_path}"
                    sample_urls.append(url)
            
            return {
                'frames': frames,
                'count': frame_count,
                'output_dir': output_dir,
                'samples_saved': len(sample_indices) if samples_dir else 0,
                'sample_urls': sample_urls
            }
            
        except Exception as e:
            raise RuntimeError(f"Frame extraction failed: {str(e)}")
    
    def process_video_frames(self, video_path: str, task_id: str, num_samples: int = 10) -> dict:
        """Process video frames like original crop_open_mouth_gpu.py with proper storage"""
        try:
            if not self.detector or not self.predictor:
                raise RuntimeError("Dlib models not loaded")
            
            # Get storage paths
            frames_dir = StorageConfig.get_frames_path(task_id)
            mouth_dir = StorageConfig.get_mouth_path(task_id)
            samples_mouths_dir = StorageConfig.get_samples_path(task_id, 'mouths')
            
            print(f"Processing frames: {frames_dir} -> {mouth_dir}")
            
            M = 0
            processed_frames = 0
            open_mouth_count = 0
            samples_saved = 0
            
            # Get all frame files
            frame_files = sorted(glob.glob(os.path.join(frames_dir, "*.jpg")))
            total_frames = len(frame_files)
            
            print(f"Found {total_frames} frames to process")
            
            for i, frame_file in enumerate(frame_files):
                processed_frames += 1
                
                # Progress logging and status update
                if processed_frames % 10 == 0:  # Update every 10 frames for real-time tracking
                    progress = (processed_frames / total_frames) * 100
                    print(f"  Progress: {processed_frames}/{total_frames} ({progress:.0f}%) - Open mouths: {M}")
                    
                    # Update status.json in real-time
                    try:
                        status_data = StorageConfig.read_status(task_id)
                        status_data['cropMouth']['processedFrames'] = processed_frames
                        status_data['cropMouth']['croppedMouths'] = M
                        status_data['analyze']['croppedMouths'] = M
                        
                        # Update sample URLs in real-time - check if sample files exist
                        sample_files = sorted(glob.glob(os.path.join(samples_mouths_dir, "*.jpg")))
                        if len(sample_files) > 0:
                            sample_urls = []
                            for filepath in sample_files:
                                rel_path = os.path.relpath(filepath, os.path.dirname(os.path.dirname(os.path.dirname(samples_mouths_dir))))
                                url = f"/storage/{rel_path}"
                                sample_urls.append(url)
                            status_data['cropMouth']['sample_mouths'] = sample_urls
                            status_data['analyze']['sample_mouths'] = sample_urls
                        
                        StorageConfig.write_status(task_id, status_data)
                    except Exception as e:
                        print(f"Warning: Could not update status: {e}")
                
                # Load frame
                try:
                    frame = cv2.imread(frame_file)
                    if frame is None or frame.size == 0:
                        print(f"Warning: Could not load frame {frame_file}")
                        continue
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                except Exception as e:
                    print(f"Error loading frame {frame_file}: {e}")
                    continue
                
                # Find faces using dlib
                faces = self.detector(frame_rgb, 1)
                
                if len(faces) == 0:
                    continue
                    
                print(f"Found {len(faces)} face(s) in frame {processed_frames}")
                
                # Get face landmarks using dlib
                face_landmarks_list = []
                for face_idx, face in enumerate(faces):
                    try:
                        shape = self.predictor(frame_rgb, face)
                        
                        # Convert dlib points to numpy array like face_utils.shape_to_np
                        landmarks = np.array([[shape.part(i).x, shape.part(i).y] for i in range(68)])
                        
                        # Convert to face_recognition format like original
                        top_lip_outer = landmarks[48:55].tolist()
                        top_lip_inner = landmarks[60:65].tolist()[::-1]
                        bottom_lip_outer = (landmarks[54:60].tolist() + [landmarks[48].tolist()])
                        bottom_lip_inner = landmarks[64:68].tolist() + [landmarks[60].tolist()]
                        
                        face_landmarks_dict = {
                            'top_lip': top_lip_outer + top_lip_inner,
                            'bottom_lip': bottom_lip_outer + bottom_lip_inner
                        }
                        face_landmarks_list.append(face_landmarks_dict)
                    except Exception as e:
                        print(f"Error processing face {face_idx}: {e}")
                        continue
                    
                # Process each face
                for face_landmarks in face_landmarks_list:
                    ret_mouth_open = is_mouth_open(face_landmarks)
                    if ret_mouth_open is True:
                        open_mouth_count += 1
                        cropped = Crooped_mouth(frame, self.detector, self.predictor)
                        if cropped is not None:
                            # Save cropped mouth image with original naming
                            filename = os.path.join(mouth_dir, f"Real{M}.jpg")
                            cv2.imwrite(filename, cropped)
                            
                            # Save sample if we haven't reached the limit yet
                            if samples_saved < num_samples:
                                sample_filename = os.path.join(samples_mouths_dir, f"sample_{M}.jpg")
                                cv2.imwrite(sample_filename, cropped)
                                samples_saved += 1
                                
                                # Update sample URLs immediately after saving sample
                                try:
                                    status_data = StorageConfig.read_status(task_id)
                                    sample_files = sorted(glob.glob(os.path.join(samples_mouths_dir, "*.jpg")))
                                    sample_urls = []
                                    for filepath in sample_files:
                                        rel_path = os.path.relpath(filepath, os.path.dirname(os.path.dirname(os.path.dirname(samples_mouths_dir))))
                                        url = f"/storage/{rel_path}"
                                        sample_urls.append(url)
                                    status_data['cropMouth']['sample_mouths'] = sample_urls
                                    status_data['analyze']['sample_mouths'] = sample_urls
                                    StorageConfig.write_status(task_id, status_data)
                                    print(f"✓ Saved sample {samples_saved}/{num_samples} and updated URLs")
                                except Exception as e:
                                    print(f"Warning: Could not update sample URLs: {e}")
                            
                            M += 1
            
            print(f"✓ Processed {processed_frames} frames, found {M} open mouth frames")
            if samples_saved > 0:
                print(f"✓ Saved {samples_saved} sample mouth crops")
            
            # Get sample URLs for real-time status
            sample_urls = []
            if samples_saved > 0:
                sample_files = sorted(glob.glob(os.path.join(samples_mouths_dir, "*.jpg")))
                for filepath in sample_files:
                    rel_path = os.path.relpath(filepath, os.path.dirname(os.path.dirname(os.path.dirname(samples_mouths_dir))))
                    url = f"/storage/{rel_path}"
                    sample_urls.append(url)
            
            return {
                'total_frames': processed_frames,
                'processed_frames': processed_frames,
                'mouth_frames': M,
                'open_mouth_count': open_mouth_count,
                'frames_dir': str(frames_dir),
                'mouth_dir': str(mouth_dir),
                'samples_saved': samples_saved,
                'sample_urls': sample_urls
            }
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"ERROR in process_video_frames: {str(e)}")
            print(f"TRACEBACK: {error_detail}")
            raise RuntimeError(f"Mouth cropping failed: {str(e)}")
    
    def get_video_info(self, video_path: str) -> dict:
        """Get video metadata"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            info = {
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
            }
            
            cap.release()
            return info
            
        except Exception as e:
            raise RuntimeError(f"Failed to get video info: {str(e)}")
    
    def is_valid_video(self, file_path: str) -> bool:
        """Check if file is a valid video"""
        try:
            cap = cv2.VideoCapture(file_path)
            is_valid = cap.isOpened()
            cap.release()
            return is_valid
        except:
            return False
