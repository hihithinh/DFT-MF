# Hướng Dẫn Sử Dụng - Deepfake Detection

## Mô tả Project
Project phát hiện deepfake video sử dụng CNN với dữ liệu Celeb-DF dataset. Model được train trên vùng miệng (mouth region) để phát hiện video giả mạo.

## Cấu trúc Project

### Files chính:
- `crop_open_mouth_gpu.py` - Trích xuất vùng miệng từ video (sử dụng GPU)
- `train_cnn_generator.py` - Train CNN model với GPU
- `detect_deepfake.py` - Phát hiện deepfake từ video đã crop
- `run_gpu.ps1` - Script chạy crop mouth với GPU
- `run_train_conda.ps1` - Script train model với GPU

### Thư mục:
- `dataset/Celeb-DF/` - Dataset gốc (videos)
- `CroppedMouth/` - Ảnh vùng miệng đã crop
- `preprocessed_data/` - Data đã xử lý (pickle files)
- `trained_models/` - Model đã train
- `training_logs/` - Logs quá trình training
- `callbacks/` - Model checkpoints
- `logs/` - TensorBoard logs

### Files hỗ trợ:
- `shape_predictor_68_face_landmarks.dat` - Model dlib detect facial landmarks
- `requirements.txt` - Python dependencies
- `Result.xlsx` - Kết quả detection

## Yêu cầu hệ thống

### Phần cứng:
- GPU NVIDIA (hỗ trợ CUDA)
- RAM: >= 16GB
- Disk: >= 50GB

### Phần mềm:
- Python 3.10
- CUDA 11.2
- cuDNN 8.1
- Conda/Miniconda

## Cài đặt

### 1. Tạo môi trường Conda:
```bash
conda create -n tf_gpu python=3.10
conda activate tf_gpu
```

### 2. Cài đặt dependencies:
```bash
pip install tensorflow==2.10.0
pip install opencv-python dlib numpy scipy matplotlib openpyxl tqdm
```

### 3. Kiểm tra GPU:
```python
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
```

## Quy trình sử dụng

### Bước 1: Crop vùng miệng từ video
```powershell
.\run_gpu.ps1
```
- Input: Videos trong `dataset/Celeb-DF/`
- Output: Ảnh vùng miệng trong `CroppedMouth/`

### Bước 2: Train CNN model
```powershell
.\run_train_conda.ps1
```
- Input: Ảnh trong `CroppedMouth/`
- Output: Model trong `trained_models/`
- Thời gian: ~3-4 giờ (với GPU)

### Bước 3: Detect deepfake
```python
python detect_deepfake.py
```
- Input: Ảnh trong `CroppedMouth/`
- Output: Kết quả trong `Result.xlsx`

## Kết quả Model

**Model hiện tại:** `CNN_CelebDF_20260325_144921_final.h5`

**Metrics:**
- Test Accuracy: 80.16%
- Test Precision: 84.93%
- Test Recall: 81.78%
- F1-Score: 83.33%

**Training:**
- Epochs: 13 (EarlyStopping)
- Training time: ~50 phút
- Dataset: 443,686 training samples, 37,633 test samples

## Xem TensorBoard

```bash
tensorboard --logdir=logs/CNN_CelebDF_20260325_144921
```

## Lưu ý

1. **GPU Memory**: Model sử dụng custom data generator để tránh tràn RAM
2. **Class Imbalance**: Sử dụng class weights để cân bằng Real/Fake
3. **EarlyStopping**: Training tự động dừng khi validation loss không cải thiện
4. **Normalization**: Ảnh được normalize (chia 255) trước khi đưa vào model

## Troubleshooting

### GPU không được detect:
- Kiểm tra CUDA 11.2 và cuDNN 8.1 đã cài đúng
- Thêm CUDA path vào PATH environment

### Out of Memory:
- Giảm batch_size trong `train_cnn_generator.py`
- Sử dụng data generator (đã implement)

### Model accuracy thấp:
- Tăng epochs (tắt EarlyStopping)
- Thêm data augmentation
- Điều chỉnh architecture

## Tác giả
Project deepfake detection sử dụng CNN và Celeb-DF dataset
