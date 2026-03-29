# DFT-MF Demo - Giao diện Phát hiện Deepfake

Giao diện web tương tác để phát hiện video deepfake bằng phân tích vùng miệng với xử lý từng bước.

## Tính năng

- **Xử lý Từng Bước**: Upload → Trích xuất Frame → Crop Vùng Miệng → Phân tích CNN
- **Giao diện Hiện đại**: Thiết kế Glassmorphism với Tailwind CSS
- **REST API**: Backend Flask với dlib facial landmarks
- **Phân tích CNN**: Mô hình TensorFlow phát hiện deepfake

## Cài đặt & Chạy

### Backend

```bash
cd demo

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
python server/app.py
```

Server chạy tại: **http://127.0.0.1:8080**

### Frontend

```bash
# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
```

Frontend chạy tại: **http://localhost:5173**

## Sử dụng

1. Mở **http://localhost:5173** trong trình duyệt
2. Upload video (MP4, AVI, MOV)
3. Xem quá trình xử lý real-time:
   - Bước 1: Trích xuất frame
   - Bước 2: Phát hiện & crop vùng miệng
   - Bước 3: Phân tích deepfake bằng CNN
4. Xem kết quả cuối cùng (FAKE/REAL) với độ tin cậy

## API Endpoints

- `POST /api/upload` - Upload video và trích xuất frame
- `POST /api/{task_id}/crop-mouth` - Crop vùng miệng
- `POST /api/{task_id}/analyze` - Phân tích deepfake
- `GET /api/{task_id}/status` - Trạng thái real-time

## Tech Stack

**Backend**: Flask, dlib, OpenCV, TensorFlow <br/>
**Frontend**: Vue 3, Tailwind CSS, Material Icons <br/>
**Design**: Glassmorphism với giao diện bảo mật <br/>

## Lưu ý

- **Bắt buộc dùng virtual environment** cho backend
- Thời gian xử lý: ~15-30 giây mỗi video
- Kích thước file tối đa: 100MB
