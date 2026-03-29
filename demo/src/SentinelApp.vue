<template>
  <div id="app" class="bg-background text-on-surface font-body">
    <TopNavigation />
    
    <!-- Main Content -->
    <main class="p-8 lg:p-12">
      <!-- Header Section -->
      <header class="mb-12">
        <h1 class="font-headline text-5xl font-bold tracking-tight text-on-surface mb-2">DFT-MF Deepfake Detection</h1>
        <p class="text-secondary font-medium tracking-wide">DeepFake Detection using Mouth Features | Phân tích đặc trưng vùng miệng</p>
      </header>

      <div class="grid grid-cols-1 xl:grid-cols-12 gap-8">
        <!-- Analysis Control Column -->
        <div class="xl:col-span-5 space-y-8">
          <UploadSection 
            :selectedFile="selectedFile"
            :uploading="uploading"
            @file-selected="handleFileSelected"
            @upload="uploadVideo"
          />
          
          <VideoPreview 
            v-if="videoPreview.show"
            :selectedFile="selectedFile"
            :video-preview="videoPreview"
            @video-error="handleVideoError"
          />
        </div>

        <!-- Results & Processing Column -->
        <div class="xl:col-span-7 space-y-8">
          <!-- Loading State -->
          <LoadingState v-if="uploading" />
          
          <!-- Results Section -->
          <ResultsSection v-if="results" :results="results" />
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>

<script>
import { ref } from 'vue'
import TopNavigation from './components/TopNavigation.vue'
import UploadSection from './components/UploadSection.vue'
import VideoPreview from './components/VideoPreview.vue'
import LoadingState from './components/LoadingState.vue'
import ResultsSection from './components/ResultsSection.vue'
import AppFooter from './components/AppFooter.vue'

export default {
  name: 'App',
  components: {
    TopNavigation,
    UploadSection,
    VideoPreview,
    LoadingState,
    ResultsSection,
    AppFooter
  },
  setup() {
    const selectedFile = ref(null)
    const uploading = ref(false)
    const results = ref(null)
    const videoPreview = ref({
      show: false,
      url: null,
      error: false
    })

    const handleFileSelected = (file) => {
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

    const handleVideoError = () => {
      videoPreview.value.error = true
      videoPreview.value.url = null
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
      handleFileSelected,
      handleVideoError,
      uploadVideo
    }
  }
}
</script>

<style>
.glass-panel {
  background: rgba(45, 52, 73, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(68, 71, 76, 0.2);
}

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
</style>
