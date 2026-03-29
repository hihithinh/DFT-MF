<template>
  <div class="container">
    <header>
      <h1>🔍 DFT-MF Deepfake Detection</h1>
      <p class="subtitle">DeepFake Detection using Mouth Features</p>
    </header>
    
    <div class="content">
      <div class="upload-section">
        <h3>Tải video lên để phân tích</h3>
        <div class="upload-box">
          <div class="upload-icon">📹</div>
          <input 
            type="file" 
            id="videoInput" 
            accept="video/*" 
            @change="handleFileChange"
            style="display: none;"
          />
          <label for="videoInput" style="cursor: pointer;">
            <div>Chọn video (tối đa 100MB)</div>
          </label>
          <button 
            class="btn" 
            @click="uploadVideo"
            :disabled="!selectedFile || uploading"
            style="margin-top: 20px;"
          >
            {{ uploading ? 'Đang xử lý...' : 'Bắt đầu phân tích' }}
          </button>
        </div>
        
        <!-- Video Preview -->
        <div v-if="videoPreview.show" class="video-preview">
          <h4>Preview video:</h4>
          <video 
            v-if="videoPreview.url"
            :src="videoPreview.url" 
            controls 
            autoplay 
            muted 
            loop
            style="max-width: 600px; width: 100%;"
            @error="handleVideoError"
          />
          
          <!-- Fallback video info -->
          <div v-if="!videoPreview.url || videoPreview.error" class="video-info">
            <div class="info-item">
              <strong>File name:</strong> {{ selectedFile?.name }}
            </div>
            <div class="info-item">
              <strong>File size:</strong> {{ formatFileSize(selectedFile?.size) }}
            </div>
            <div class="info-item">
              <strong>File type:</strong> {{ selectedFile?.type }}
            </div>
            <div class="info-item">
              <strong>Status:</strong> 
              <span class="status-warning">⚠️ Video preview not supported</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Loading -->
      <div v-if="uploading" class="loading">
        <div class="spinner"></div>
        <p>Đang xử lý video...</p>
      </div>
      
      <!-- Results -->
      <div v-if="results" class="results">
        <h3>Kết quả phân tích:</h3>
        <div class="result-box">
          <p><strong>Video ID:</strong> {{ results.video_id }}</p>
          <p><strong>Tổng frames:</strong> {{ results.total_frames }}</p>
          <p><strong>Frames có miệng mở:</strong> {{ results.mouth_frames }}</p>
          <div v-if="results.predictions">
            <h4>Chi tiết dự đoán:</h4>
            <p><strong>Fake:</strong> {{ results.predictions.fake_count }} ({{ results.predictions.fake_percentage }}%)</p>
            <p><strong>Real:</strong> {{ results.predictions.real_count }} ({{ results.predictions.real_percentage }}%)</p>
            <p><strong>Kết luận:</strong> <strong :class="results.predictions.verdict.toLowerCase()">{{ results.predictions.verdict }}</strong></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'Home',
  setup() {
    const selectedFile = ref(null)
    const uploading = ref(false)
    const results = ref(null)
    const videoPreview = ref({
      show: false,
      url: null,
      error: false
    })

    const handleFileChange = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedFile.value = file
        videoPreview.value.show = true
        videoPreview.value.error = false
        
        // Try to create preview
        if (file.type.startsWith('video/')) {
          const reader = new FileReader()
          reader.onload = (e) => {
            videoPreview.value.url = e.target.result
          }
          reader.onerror = () => {
            videoPreview.value.error = true
          }
          reader.readAsDataURL(file)
        }
      }
    }

    const handleVideoError = () => {
      videoPreview.value.error = true
      videoPreview.value.url = null
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return '0 MB'
      return (bytes / 1024 / 1024).toFixed(2) + ' MB'
    }

    const uploadVideo = async () => {
      if (!selectedFile.value) return
      
      uploading.value = true
      results.value = null
      
      try {
        const formData = new FormData()
        formData.append('video', selectedFile.value)
        
        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData
        })
        
        const data = await response.json()
        
        if (response.ok) {
          results.value = data
        } else {
          alert('Lỗi: ' + (data.error || 'Không thể xử lý video'))
        }
      } catch (error) {
        console.error('Error:', error)
        alert('Lỗi kết nối đến server')
      } finally {
        uploading.value = false
      }
    }

    return {
      selectedFile,
      uploading,
      results,
      videoPreview,
      handleFileChange,
      handleVideoError,
      formatFileSize,
      uploadVideo
    }
  }
}
</script>
