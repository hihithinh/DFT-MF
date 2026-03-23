# Deepfake Detection Pipeline

## 📁 Project Structure

```
DFT-MF/
├── data/                    # Input data and intermediate files
│   ├── Videos/              # Input videos
│   ├── ExtractFrams/        # Extracted frames
│   └── CroppedMouth/        # Cropped mouth regions
├── models/                  # Trained models and predictors
│   ├── 64x3-CNN.model       # Trained CNN model
│   └── shape_predictor_68_face_landmarks.dat
├── outputs/                 # Results and outputs
│   └── Result.xlsx          # Detection results
├── extract_frames.py        # Step 1: Extract frames
├── crop_open_mouth.py       # Step 2: Crop mouth regions
├── detect_deepfake.py       # Step 3: Detect deepfakes
├── build_cnn_model.py       # Step 4: Train CNN model
├── split_video_by_keyword.py # Optional: Video splitting
├── requirements.txt         # Dependencies
└── venv/                    # Virtual environment
```

## 🚀 Pipeline Steps

### **Step 1: Extract Frames**
```bash
python extract_frames.py
```
- Input: `data/Videos/DF(i).mp4`
- Output: `data/ExtractFrams/DF(i)/image_*.jpg`

### **Step 2: Crop Open Mouth**
```bash
python crop_open_mouth.py
```
- Input: Frames from Step 1
- Output: `data/CroppedMouth/Deepfake(i)/Real*.jpg`
- Requires: `models/shape_predictor_68_face_landmarks.dat`

### **Step 3: Deepfake Detection**
```bash
python detect_deepfake.py
```
- Input: Cropped mouth images
- Output: `outputs/Result.xlsx`
- Requires: `models/64x3-CNN.model`

### **Step 4: Train CNN Model**
```bash
python build_cnn_model.py
```
- Input: Training dataset with Real/Fake folders
- Output: `models/64x3-CNN.model`

## 📦 Required Files

### **Download:**
1. **shape_predictor_68_face_landmarks.dat**
   - Link: http://dlib.net/files/shape_predictor_68_face_landmarks.dat
   - Place in: `models/`

2. **64x3-CNN.model** (pretrained) OR train your own
   - Train with: `python build_cnn_model.py`
   - Output in: `models/`

### **Input Data:**
- **Videos**: Place in `data/Videos/`
- **Training Data**: For model training (Real/Fake folders)

## ⚙️ Configuration

All paths are automatically configured relative to project root:
- `BASE_DIR`: Project root directory
- `DATA_DIR`: `data/`
- `OUTPUTS_DIR`: `outputs/`
- `MODELS_DIR`: `models/`

## 🎯 Usage

### **Complete Pipeline:**
1. Place videos in `data/Videos/`
2. Download dlib model to `models/`
3. Run steps 1-3 in sequence
4. Check results in `outputs/Result.xlsx`

### **Model Training:**
1. Prepare training data with Real/Fake folders
2. Update `DATADIR` in `build_cnn_model.py`
3. Run training script
4. Model saved to `models/`

## 📊 Output Format

**Result.xlsx** contains:
- Frame counts and processing times
- Real/Fake image counts per video
- Final video classification
- Performance metrics

## 🔧 Dependencies

```bash
pip install -r requirements.txt
```

Main packages:
- OpenCV (video/image processing)
- TensorFlow (CNN model)
- dlib (face landmarks)
- face_recognition (face detection)
- openpyxl (Excel output)

## 🎯 Notes

- All outputs saved to respective directories (no root clutter)
- Paths automatically work across platforms
- Virtual environment recommended
- Model files stored separately from code
