# Deepfake Detection Pipeline

## 📁 Project Structure

```
DFT-MF/
├── dataset/                  # Dataset storage
│   ├── UADFV/               # UADFV dataset
│   │   ├── fake/            # Fake videos
│   │   ├── real/            # Real videos
│   │   ├── frames/          # Pre-extracted frames
│   │   └── landmarks/       # Face landmarks
│   └── Celeb-DF/            # CelebDF dataset
├── UADFV/                   # UADFV processing structure
│   ├── ExtractFrams/        # Extracted frames
│   │   ├── fake_0000/
│   │   ├── fake_0001/
│   │   ├── real_0000/
│   │   └── real_0001/
│   ├── CroppedMouth/        # Cropped mouth regions
│   │   ├── fake_0000/
│   │   ├── fake_0001/
│   │   ├── real_0000/
│   │   └── real_0001/
│   └── Result.xlsx          # Detection results
├── CelebDF/                 # CelebDF processing structure
│   ├── Videos/              # Input videos
│   ├── ExtractFrams/        # Extracted frames
│   │   ├── video1/
│   │   ├── video2/
│   │   └── ...
│   └── Result.xlsx          # Detection results
├── CroppedMouth/            # CelebDF cropped mouth
│   └── CelebDF/             # Cropped mouth regions
│       ├── video1/
│       ├── video2/
│       └── ...
├── trained_models/          # Trained models
│   ├── CNN_UADFV_YYYYMMDD_HHMMSS_final.h5
│   ├── CNN_UADFV_YYYYMMDD_HHMMSS_best.h5
│   ├── CNN_CelebDF_YYYYMMDD_HHMMSS_final.h5
│   └── CNN_CelebDF_YYYYMMDD_HHMMSS_best.h5
├── shape_predictor_68_face_landmarks.dat
├── extract_frames.py        # Step 0: Extract frames
├── crop_open_mouth_gpu.py   # Step 1: Crop mouth regions
├── train_cnn_generator.py   # Step 2: Train CNN model
├── detect_deepfake.py       # Step 3: Detect deepfakes
├── split_video_by_keyword.py # Optional: Video splitting
├── run_gpu.ps1             # PowerShell script
├── requirements.txt         # Dependencies
└── venv_windows/            # Virtual environment
```

## 🚀 Pipeline Steps

### **Step 0: Extract Frames from Videos**
```bash
# For UADFV dataset
python extract_frames.py UADFV

# For CelebDF dataset (default)
python extract_frames.py CelebDF
python extract_frames.py  # Uses CelebDF by default

# With custom video directory
python extract_frames.py UADFV --video-dir D:\Videos\UADFV
```
- Input: Video files in `{dataset}/Videos/*.mp4`
- Output: `{dataset}/ExtractFrams/{video_name}/image_*.jpg`
- Supported formats: .mp4, .avi, .mov, .mkv
- Features: Automatic video detection, progress tracking, frame counting

### **Step 1: Crop Open Mouth (GPU-Accelerated)**
```bash
# For UADFV dataset
python crop_open_mouth_gpu.py UADFV

# For CelebDF dataset (default)
python crop_open_mouth_gpu.py CelebDF
python crop_open_mouth_gpu.py  # Uses CelebDF by default
```
- Input: `{dataset}/ExtractFrams/{video_name}/image_*.jpg`
- Output: 
  - UADFV: `UADFV/CroppedMouth/{video_name}/Real*.jpg`
  - CelebDF: `CroppedMouth/CelebDF/{video_name}/Real*.jpg`
- Requires: `shape_predictor_68_face_landmarks.dat`
- Features: GPU acceleration, parallel processing, progress tracking

### **Step 2: Train CNN Model**
```bash
# For UADFV dataset
python train_cnn_generator.py UADFV

# For CelebDF dataset (default)
python train_cnn_generator.py CelebDF
python train_cnn_generator.py  # Uses CelebDF by default
```
- Input: Preprocessed training data
- Output: `trained_models/CNN_{dataset}_YYYYMMDD_HHMMSS_final.h5`
- Features: GPU acceleration, TensorBoard logging, checkpoint saving

### **Step 3: Deepfake Detection**
```bash
# For UADFV dataset
python detect_deepfake.py UADFV

# For CelebDF dataset (default)
python detect_deepfake.py CelebDF
python detect_deepfake.py  # Uses CelebDF by default

# With specific model
python detect_deepfake.py UADFV --model trained_models/CNN_UADFV_20260328_103000_final.h5
```
- Input: Cropped mouth images from Step 1
- Output: `{dataset}/Result.xlsx`
- Features: Automatic model selection, batch processing

## 📦 Required Files

### **Download:**
1. **shape_predictor_68_face_landmarks.dat**
   - Link: http://dlib.net/files/shape_predictor_68_face_landmarks.dat
   - Place in: Project root directory

### **Input Data:**
- **UADFV**: Place dataset in `dataset/UADFV/` with `fake/` and `real/` subfolders containing videos
- **CelebDF**: Place videos in `CelebDF/Videos/`

## ⚙️ Configuration

### **Environment Setup:**
```powershell
# Use virtual environment
D:\Hoc\Study\computer-vision\DFT-MF\venv_windows\Scripts\python.exe

# Or use the PowerShell script
.\run_gpu.ps1
```

### **Dataset Structure:**
- **UADFV**: Keeps original structure `UADFV/CroppedMouth/video_name/`
- **CelebDF**: Uses new structure `CroppedMouth/CelebDF/video_name/`
- **Models**: Saved with dataset prefixes in `trained_models/`

## 🎯 Usage

### **Complete Pipeline for UADFV:**
1. Place dataset in `dataset/UADFV/` with `fake/` and `real/` folders
2. Download dlib model to project root
3. Extract: `python extract_frames.py UADFV`
4. Crop: `python crop_open_mouth_gpu.py UADFV`
5. Train: `python train_cnn_generator.py UADFV`
6. Detect: `python detect_deepfake.py UADFV`
7. Check results in `UADFV/Result.xlsx`

### **Complete Pipeline for CelebDF:**
1. Place videos in `CelebDF/Videos/`
2. Download dlib model to project root
3. Extract: `python extract_frames.py CelebDF`
4. Crop: `python crop_open_mouth_gpu.py CelebDF`
5. Train: `python train_cnn_generator.py CelebDF`
6. Detect: `python detect_deepfake.py CelebDF`
7. Check results in `CelebDF/Result.xlsx`

## 📊 Output Format

**Result.xlsx** contains:
- Open mouth frame counts and processing times
- Real/Fake image counts per video
- Final video classification
- Performance metrics
- GPU acceleration statistics

## 🔧 Dependencies

```bash
pip install -r requirements.txt
```

Main packages:
- OpenCV (video/image processing)
- TensorFlow (CNN model)
- dlib (face landmarks)
- imutils (image utilities)
- openpyxl (Excel output)
- numpy (numerical operations)
- scipy (spatial calculations)

## 🎯 Key Features

### **GPU Acceleration:**
- CUDA support for dlib face detection
- TensorFlow GPU training and inference
- Automatic GPU detection and configuration

### **Multi-Dataset Support:**
- Separate processing for UADFV and CelebDF datasets
- Dataset-specific model naming
- Automatic model selection based on dataset

### **Performance Optimizations:**
- Parallel processing with multiprocessing
- Progress tracking and ETA calculation
- Batch processing for large datasets
- Memory-efficient data loading

### **Error Handling:**
- Robust error handling for corrupt files
- Automatic retry mechanisms
- Detailed logging and progress reporting

## 🎯 Notes

- **UADFV**: Maintains original folder structure for compatibility
- **CelebDF**: Uses optimized folder structure for better organization
- **Models**: Automatically saved with dataset prefixes and timestamps
- **GPU**: Requires CUDA-compatible GPU for optimal performance
- **Virtual Environment**: Recommended for dependency isolation
- **Backward Compatibility**: All scripts work with default CelebDF dataset

## 🔄 Migration

For existing UADFV users:
- No changes needed - structure remains the same
- Models will be saved with new naming convention
- All existing functionality preserved

For CelebDF users:
- Move existing `CroppedMouth/video*` folders to `CroppedMouth/CelebDF/`
- Move `ExtractFrams/` and `Result.xlsx` to `CelebDF/` folder
- Re-train models for new dataset-specific naming
