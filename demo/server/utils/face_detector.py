import cv2
import numpy as np
from typing import List, Tuple, Optional

class FaceDetector:
    """Service for detecting faces and facial landmarks"""
    
    def __init__(self):
        # Try to load face recognition library, fallback to OpenCV
        self.face_recognition_available = self._check_face_recognition()
        
    def _check_face_recognition(self) -> bool:
        """Check if face_recognition library is available"""
        try:
            import face_recognition
            self.face_recognition = face_recognition
            return True
        except ImportError:
            print("Warning: face_recognition not available, using OpenCV fallback")
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            return False
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces in frame, return bounding boxes (x, y, w, h)"""
        try:
            if self.face_recognition_available:
                # Use face_recognition library
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = self.face_recognition.face_locations(rgb_frame, model="hog")
                
                # Convert to (x, y, w, h) format
                faces = []
                for (top, right, bottom, left) in face_locations:
                    faces.append((left, top, right - left, bottom - top))
                
                return faces
            else:
                # Use OpenCV fallback
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                
                return faces.tolist()
                
        except Exception as e:
            print(f"Face detection error: {str(e)}")
            return []
    
    def get_mouth_landmarks(self, face: Tuple[int, int, int, int], frame: np.ndarray) -> Optional[List[Tuple[int, int]]]:
        """Get mouth landmark points"""
        try:
            if self.face_recognition_available:
                # Use face_recognition library
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = self.face_recognition.face_locations(rgb_frame, model="hog")
                face_landmarks = self.face_recognition.face_landmarks(rgb_frame, face_locations)
                
                if face_landmarks:
                    # Get mouth landmarks from first face
                    landmarks = face_landmarks[0]
                    mouth_points = landmarks.get('top_lip', []) + landmarks.get('bottom_lip', [])
                    return mouth_points
                else:
                    return None
            else:
                # OpenCV fallback - estimate mouth region
                x, y, w, h = face
                mouth_y = y + int(h * 0.7)
                mouth_height = int(h * 0.2)
                mouth_x = x + int(w * 0.2)
                mouth_width = int(w * 0.6)
                
                # Return estimated mouth corners
                return [
                    (mouth_x, mouth_y),
                    (mouth_x + mouth_width // 3, mouth_y),
                    (mouth_x + 2 * mouth_width // 3, mouth_y),
                    (mouth_x + mouth_width, mouth_y),
                    (mouth_x, mouth_y + mouth_height),
                    (mouth_x + mouth_width // 3, mouth_y + mouth_height),
                    (mouth_x + 2 * mouth_width // 3, mouth_y + mouth_height),
                    (mouth_x + mouth_width, mouth_y + mouth_height)
                ]
                
        except Exception as e:
            print(f"Mouth landmark detection error: {str(e)}")
            return None
