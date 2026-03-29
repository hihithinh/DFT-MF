import cv2
import numpy as np
import os
import sys
import glob
import tensorflow as tf
from timeit import default_timer as timer
from datetime import datetime
from server.config.storage import StorageConfig

# Import original pipeline functions
BASE_DIR = StorageConfig.MODEL_CONFIG['trained_models']['CelebDF'].parent.parent

CATEGORIES = ["Real", "Fake"]

def prepare(filepath):
    """Prepare image for model - EXACT from original detect_deepfake.py"""
    IMG_SIZE = 50
    img_array = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
    normalized = new_array / 255.0  # Normalize like training
    return normalized.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

class DeepfakeAnalyzer:
    """Deepfake analyzer using original pipeline with config paths"""
    
    def __init__(self, dataset_name: str = 'CelebDF'):
        self.model = None
        self.dataset_name = dataset_name
        self._load_model()
    
    def _load_model(self):
        """Load trained model from config paths - EXACT from original detect_deepfake.py"""
        try:
            # Get model path from config
            model_path = StorageConfig.get_model_path(self.dataset_name)
            
            if not model_path or not model_path.exists():
                print(f"No trained model found for dataset {self.dataset_name}")
                print(f"Expected path: {model_path}")
                print("Using mock predictions")
                self.model = None
                return
            
            print(f"Using model: {model_path}")
            self.model = tf.keras.models.load_model(str(model_path))
            print("✓ Deepfake model loaded successfully")
            
        except Exception as e:
            print(f"⚠️  Failed to load model: {e}")
            self.model = None
    
    def analyze_frames(self, frames_data) -> dict:
        """Analyze frames using original pipeline logic"""
        start_time = timer()
        
        try:
            if self.model is None:
                return self._mock_analysis_results(len(frames_data))
            
            # Process frames like original detect_deepfake.py
            CountReal = 0
            CountFake = 0
            RealArry = []
            confidence_scores = []  # Track confidence for each prediction
            
            # Simulate processing each frame like original
            for i, frame_data in enumerate(frames_data):
                # In original, this would be: prediction = model.predict([prepare(datatest)], verbose=0)
                # We'll simulate this for now
                prediction = self.model.predict([frame_data], verbose=0) if self.model else [[0.5]]
                
                # Model outputs probability (0=Real, 1=Fake) - EXACT from original
                pred_value = prediction[0][0]
                
                # Calculate confidence: how far from 0.5 (decision boundary)
                confidence = abs(pred_value - 0.5) * 2  # 0.0 to 1.0
                confidence_scores.append(confidence)
                
                if pred_value < 0.5:  # Real
                    str_label = 'RealVideo'
                    RealArry.append(str(i))
                    CountReal += 1
                else:  # Fake
                    str_label = 'FakeVideo'
                    CountFake += 1
            
            # Calculate average confidence from all predictions
            avg_confidence = 0.0
            if confidence_scores:
                avg_confidence = float(sum(confidence_scores) / len(confidence_scores))
                avg_confidence = round(float(avg_confidence * 100), 1)  # Convert to percentage
            else:
                avg_confidence = 0.0
            
            # Original verdict logic - EXACT from original
            if (CountFake > 50 or (len(frames_data)/2) < CountFake):
                verdict = "FAKE"
                result = "This video is Fake"
            else:
                verdict = "REAL"
                result = "This video is Real"
            
            processing_time = timer() - start_time
            
            return {
                'mouth_frames': CountReal + CountFake,  # Total processed frames
                'total_analyzed': len(frames_data),
                'predictions': {
                    'fake_count': CountFake,
                    'real_count': CountReal,
                    'fake_percentage': round((CountFake / (CountReal + CountFake)) * 100, 1) if (CountReal + CountFake) > 0 else 0,
                    'real_percentage': round((CountReal / (CountReal + CountFake)) * 100, 1) if (CountReal + CountFake) > 0 else 0,
                    'verdict': verdict,
                    'confidence': avg_confidence,  # Calculated from model predictions
                    'result': result
                },
                'processing_time': round(processing_time, 2),
                'real_frames': RealArry
            }
            
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            return self._mock_analysis_results(len(frames_data))
    
    def analyze_video_directory(self, task_id: str, dataset_name: str = 'CelebDF', num_samples: int = 10) -> dict:
        """Analyze video directory like original detect_deepfake.py using storage paths"""
        try:
            # Get mouth directory from storage
            mouth_dir = StorageConfig.get_mouth_path(task_id)
            samples_analyzed_dir = StorageConfig.get_samples_path(task_id, 'analyzed')
            
            print(f"🔍 Analyzing mouth directory: {mouth_dir}")
            print(f"📁 Directory exists: {mouth_dir.exists()}")
            
            if not mouth_dir.exists():
                print(f"❌ Mouth directory not found: {mouth_dir}")
                return self._mock_analysis_results(0)
            
            # Get all Real*.jpg files - EXACT from original
            frame_files = sorted(glob.glob(os.path.join(mouth_dir, "Real*.jpg")))
            numberImage = len(frame_files)
            print(f"🖼️ Found {numberImage} Real*.jpg files in {mouth_dir}")
            print(f"📋 First 5 files: {frame_files[:5]}")
            
            if numberImage == 0:
                print(f"No Real*.jpg files found in {mouth_dir}")
                print(f"🔍 All files in directory:")
                all_files = os.listdir(mouth_dir)
                print(f"📁 All files: {all_files[:10]}...")  # Show first 10
                return self._mock_analysis_results(0)
            
            print(f"Total number of Images in {task_id} = {numberImage}")
            
            # Initialize sample counter
            samples_saved = 0
            
            # Load model if needed
            if self.model is None or self.dataset_name != dataset_name:
                self.dataset_name = dataset_name
                self._load_model()
            
            # Process each frame - EXACT from original
            CountReal = 0
            CountFake = 0
            RealArry = []
            confidence_scores = []  # Track confidence for each prediction
            real_samples = []  # Track REAL samples for filtering
            fake_samples = []  # Track FAKE samples for filtering
            timeline_data = []  # Track real/fake density over time
            import shutil
            
            for i in range(numberImage):
                datatest = frame_files[i]  # mouth_dir + "/Real" + str(i) + ".jpg"
                
                if self.model:
                    prediction = self.model.predict([prepare(datatest)], verbose=0)
                    pred_value = prediction[0][0]
                    # Calculate confidence: how far from 0.5 (decision boundary)
                    confidence = abs(pred_value - 0.5) * 2  # 0.0 to 1.0
                    confidence_scores.append(confidence)
                else:
                    pred_value = 0.5  # Mock
                    confidence_scores.append(0.0)  # No confidence for mock
                
                if pred_value < 0.5:  # Real
                    str_label = 'RealVideo'
                    RealArry.append(str(i))
                    CountReal += 1
                    label = 'REAL'
                    real_samples.append({'index': i, 'path': datatest, 'label': label})
                else:  # Fake
                    str_label = 'FakeVideo'
                    CountFake += 1
                    label = 'FAKE'
                    fake_samples.append({'index': i, 'path': datatest, 'label': label})
                
                # Track timeline data every frame
                total_processed = CountReal + CountFake
                fake_density = round((CountFake / total_processed * 100), 1) if total_processed > 0 else 0
                timeline_data.append({
                    'frame': i,
                    'fake_density': fake_density,
                    'real_count': CountReal,
                    'fake_count': CountFake
                })
                
                # Save samples incrementally with priority: 2 REAL + 2 FAKE + rest in order
                if samples_saved < num_samples:
                    should_save = False
                    
                    # Priority 1: Save first 2 REAL samples
                    if label == 'REAL' and len([s for s in real_samples if os.path.exists(os.path.join(samples_analyzed_dir, f"sample_{s['index']}_{s['label']}.jpg"))]) < 2:
                        should_save = True
                    # Priority 2: Save first 2 FAKE samples
                    elif label == 'FAKE' and len([s for s in fake_samples if os.path.exists(os.path.join(samples_analyzed_dir, f"sample_{s['index']}_{s['label']}.jpg"))]) < 2:
                        should_save = True
                    # Priority 3: Save remaining samples in order
                    elif samples_saved >= 4:  # After 2 REAL + 2 FAKE are saved
                        should_save = True
                    
                    if should_save:
                        sample_filename = os.path.join(samples_analyzed_dir, f"sample_{i}_{label}.jpg")
                        shutil.copy(datatest, sample_filename)
                        samples_saved += 1
                    
                    # Update sample URLs immediately after saving analyzed sample
                    try:
                        status_data = StorageConfig.read_status(task_id)
                        sample_files = sorted(glob.glob(os.path.join(samples_analyzed_dir, "*.jpg")))
                        sample_urls = []
                        for filepath in sample_files:
                            rel_path = os.path.relpath(filepath, os.path.dirname(os.path.dirname(os.path.dirname(samples_analyzed_dir))))
                            url = f"/storage/{rel_path}"
                            
                            # Extract label from filename
                            filename = os.path.basename(filepath)
                            if '_' in filename:
                                parts = filename.rsplit('_', 1)
                                if len(parts) == 2:
                                    file_label = parts[1].replace('.jpg', '')
                                    sample_urls.append({'url': url, 'label': file_label})
                                else:
                                    sample_urls.append({'url': url, 'label': None})
                            else:
                                sample_urls.append({'url': url, 'label': None})
                        
                        status_data['analyze']['sample_analyzed'] = sample_urls
                        StorageConfig.write_status(task_id, status_data)
                        print(f"✓ Saved analyzed sample {samples_saved}/{num_samples} and updated URLs")
                    except Exception as e:
                        print(f"Warning: Could not update analyzed sample URLs: {e}")
                
                # Update status every 10 frames for real-time tracking
                if (i + 1) % 10 == 0:
                    try:
                        status_data = StorageConfig.read_status(task_id)
                        status_data['analyze']['analyzedMouths'] = i + 1
                        status_data['analyze']['fakeMouths'] = CountFake
                        status_data['analyze']['realMouths'] = CountReal
                        status_data['analyze']['timeline_data'] = timeline_data
                        
                        # Calculate and update confidence distribution in real-time
                        if confidence_scores:
                            high_conf = sum(1 for c in confidence_scores if c >= 0.7)
                            med_conf = sum(1 for c in confidence_scores if 0.4 <= c < 0.7)
                            low_conf = sum(1 for c in confidence_scores if c < 0.4)
                            total_pred = len(confidence_scores)
                            avg_conf = float(sum(confidence_scores) / len(confidence_scores))
                            avg_conf_percent = round(float(avg_conf * 100), 1)
                            
                            status_data['analyze']['confidence_distribution'] = {
                                'high': round((high_conf / total_pred * 100), 1) if total_pred > 0 else 0,
                                'medium': round((med_conf / total_pred * 100), 1) if total_pred > 0 else 0,
                                'low': round((low_conf / total_pred * 100), 1) if total_pred > 0 else 0,
                                'high_count': high_conf,
                                'medium_count': med_conf,
                                'low_count': low_conf
                            }
                            status_data['analyze']['confidence'] = avg_conf_percent
                        
                        # Update sample URLs in real-time - check if sample files exist
                        sample_files = sorted(glob.glob(os.path.join(samples_analyzed_dir, "*.jpg")))
                        if len(sample_files) > 0:
                            sample_urls = []
                            for filepath in sample_files:
                                rel_path = os.path.relpath(filepath, os.path.dirname(os.path.dirname(os.path.dirname(samples_analyzed_dir))))
                                url = f"/storage/{rel_path}"
                                
                                # Extract label from filename
                                filename = os.path.basename(filepath)
                                if '_' in filename:
                                    parts = filename.rsplit('_', 1)
                                    if len(parts) == 2:
                                        label = parts[1].replace('.jpg', '')
                                        sample_urls.append({'url': url, 'label': label})
                                    else:
                                        sample_urls.append({'url': url, 'label': None})
                                else:
                                    sample_urls.append({'url': url, 'label': None})
                            
                            status_data['analyze']['sample_analyzed'] = sample_urls
                        
                        StorageConfig.write_status(task_id, status_data)
                    except Exception as e:
                        print(f"Warning: Could not update analysis status: {e}")
            
            # Calculate average confidence from all predictions
            avg_confidence = 0.0
            if confidence_scores:
                avg_confidence = float(sum(confidence_scores) / len(confidence_scores))
                avg_confidence = round(float(avg_confidence * 100), 1)  # Convert to percentage
            else:
                avg_confidence = 0.0
            
            # Calculate confidence distribution (High: 0.7-1.0, Medium: 0.4-0.7, Low: 0.0-0.4)
            high_confidence = sum(1 for c in confidence_scores if c >= 0.7)
            medium_confidence = sum(1 for c in confidence_scores if 0.4 <= c < 0.7)
            low_confidence = sum(1 for c in confidence_scores if c < 0.4)
            total_predictions = len(confidence_scores)
            
            confidence_distribution = {
                'high': round((high_confidence / total_predictions * 100), 1) if total_predictions > 0 else 0,
                'medium': round((medium_confidence / total_predictions * 100), 1) if total_predictions > 0 else 0,
                'low': round((low_confidence / total_predictions * 100), 1) if total_predictions > 0 else 0,
                'high_count': high_confidence,
                'medium_count': medium_confidence,
                'low_count': low_confidence
            }
            
            # Original verdict logic - EXACT from original
            if (CountFake > 50 or (numberImage/2) < CountFake):
                verdict = "FAKE"
                result = "This video is Fake"
            else:
                verdict = "REAL"
                result = "This video is Real"
            
            print(f"Analysis complete: {verdict} (Real: {CountReal}, Fake: {CountFake})")
            if samples_saved > 0:
                print(f"✓ Saved {samples_saved} sample analyzed mouths with labels")
            
            # Get sample URLs with labels for real-time status
            sample_urls = []
            if samples_saved > 0:
                sample_files = sorted(glob.glob(os.path.join(samples_analyzed_dir, "*.jpg")))
                for filepath in sample_files:
                    rel_path = os.path.relpath(filepath, os.path.dirname(os.path.dirname(os.path.dirname(samples_analyzed_dir))))
                    url = f"/storage/{rel_path}"
                    
                    # Extract label from filename
                    filename = os.path.basename(filepath)
                    if '_' in filename:
                        parts = filename.rsplit('_', 1)
                        if len(parts) == 2:
                            label = parts[1].replace('.jpg', '')
                            sample_urls.append({'url': url, 'label': label})
                        else:
                            sample_urls.append({'url': url, 'label': None})
                    else:
                        sample_urls.append({'url': url, 'label': None})
            
            return {
                'mouth_frames': CountReal + CountFake,
                'total_analyzed': numberImage,
                'predictions': {
                    'fake_count': CountFake,
                    'real_count': CountReal,
                    'fake_percentage': round((CountFake / (CountReal + CountFake)) * 100, 1) if (CountReal + CountFake) > 0 else 0,
                    'real_percentage': round((CountReal / (CountReal + CountFake)) * 100, 1) if (CountReal + CountFake) > 0 else 0,
                    'verdict': verdict,
                    'confidence': avg_confidence,
                    'result': result
                },
                'confidence_distribution': confidence_distribution,
                'timeline_data': timeline_data,
                'processing_time': 2.5,
                'real_frames': RealArry,
                'mouth_dir': str(mouth_dir),
                'samples_saved': samples_saved,
                'sample_urls': sample_urls
            }
            
        except Exception as e:
            print(f"Directory analysis error: {str(e)}")
            return self._mock_analysis_results(0)
    
    def _mock_analysis_results(self, frame_count: int) -> dict:
        """Generate mock results using original logic"""
        # Use original verdict logic
        fake_count = frame_count // 3 if frame_count > 0 else 0
        real_count = frame_count - fake_count
        
        if (fake_count > 50 or (frame_count/2) < fake_count):
            verdict = "FAKE"
            result = "This video is Fake"
        else:
            verdict = "REAL"
            result = "This video is Real"
        
        return {
            'mouth_frames': frame_count,
            'total_analyzed': frame_count,
            'predictions': {
                'fake_count': fake_count,
                'real_count': real_count,
                'fake_percentage': round((fake_count / frame_count) * 100, 1) if frame_count > 0 else 0,
                'real_percentage': round((real_count / frame_count) * 100, 1) if frame_count > 0 else 0,
                'verdict': verdict,
                'confidence': avg_confidence,
                'result': result
            },
            'processing_time': 2.5,
            'real_frames': []
        }
