<template>
  <div class="bg-background text-on-surface font-body">
    <TopNavigation />
    
    <!-- Main Content -->
    <main class="p-8 lg:p-12">
      <!-- Header Section -->
      <header class="mb-12">
        <h1 class="font-headline text-5xl font-bold tracking-tight text-on-surface mb-2">DFT-MF Deepfake Detection</h1>
        <p class="text-secondary font-medium tracking-wide">DeepFake Detection using Mouth Features | Step-by-Step Processing</p>
      </header>

      <div class="grid grid-cols-1 xl:grid-cols-12 gap-8">
        <!-- Upload & Control Column -->
        <div class="xl:col-span-5 space-y-8">
          <UploadSection 
            :selectedFile="selectedFile"
            :uploading="uploading"
            @file-selected="handleFileSelected"
            @upload="startStep1"
          />
          
          <!-- Step Progress -->
          <div class="glass-panel rounded-xl p-6 space-y-4">
            <h3 class="font-headline text-xl font-semibold text-on-surface mb-4">Processing Progress</h3>
            
            <!-- Step 1 -->
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium">Step 1: Upload & Extract Frames</span>
                <span v-if="step1Status" class="text-xs px-2 py-1 rounded-full" 
                      :class="step1Status === 'completed' ? 'bg-tertiary/20 text-tertiary' : 'bg-surface-variant/50 text-on-surface-variant'">
                  {{ step1Status }}
                </span>
              </div>
              <div class="w-full bg-surface-variant rounded-full h-2">
                <div class="bg-tertiary h-2 rounded-full transition-all duration-300" 
                     :style="{ width: step1Progress + '%' }"></div>
              </div>
              <p v-if="step1Message" class="text-xs text-secondary">{{ step1Message }}</p>
            </div>
            
            <!-- Step 2 -->
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium">Step 2: Crop Mouth Frames</span>
                <span v-if="step2Status" class="text-xs px-2 py-1 rounded-full"
                      :class="step2Status === 'completed' ? 'bg-tertiary/20 text-tertiary' : 'bg-surface-variant/50 text-on-surface-variant'">
                  {{ step2Status }}
                </span>
              </div>
              <div class="w-full bg-surface-variant rounded-full h-2">
                <div class="bg-tertiary h-2 rounded-full transition-all duration-300" 
                     :style="{ width: step2Progress + '%' }"></div>
              </div>
              <p v-if="step2Message" class="text-xs text-secondary">{{ step2Message }}</p>
            </div>
            
            <!-- Step 3 -->
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium">Step 3: CNN Deepfake Analysis</span>
                <span v-if="step3Status" class="text-xs px-2 py-1 rounded-full"
                      :class="step3Status === 'completed' ? 'bg-tertiary/20 text-tertiary' : 'bg-surface-variant/50 text-on-surface-variant'">
                  {{ step3Status }}
                </span>
              </div>
              <div class="w-full bg-surface-variant rounded-full h-2">
                <div class="bg-tertiary h-2 rounded-full transition-all duration-300" 
                     :style="{ width: step3Progress + '%' }"></div>
              </div>
              <p v-if="step3Message" class="text-xs text-secondary">{{ step3Message }}</p>
            </div>
          </div>
          
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
          
          <!-- Step Results -->
          <div v-if="currentTaskId" class="space-y-6">
            <!-- Step 1 Results -->
            <div v-if="step1Results" class="glass-panel rounded-xl p-6">
              <h3 class="font-headline text-xl font-semibold text-on-surface mb-4">Frame Extraction Results</h3>
              <div class="grid grid-cols-2 gap-4">
                <div class="space-y-2">
                  <p class="text-sm text-secondary">Total Frames</p>
                  <p class="text-2xl font-bold text-tertiary">{{ step1Results.total_frames }}</p>
                </div>
                <div class="space-y-2">
                  <p class="text-sm text-secondary">Processing Time</p>
                  <p class="text-2xl font-bold text-primary">{{ step1Results.processing_time }}s</p>
                </div>
              </div>
            </div>
            
            <!-- Step 2 Results -->
            <div v-if="step2Results" class="glass-panel rounded-xl p-6">
              <h3 class="font-headline text-xl font-semibold text-on-surface mb-4">Mouth Detection Results</h3>
              <div class="grid grid-cols-2 gap-4">
                <div class="space-y-2">
                  <p class="text-sm text-secondary">Open Mouth Frames</p>
                  <p class="text-2xl font-bold text-tertiary">{{ step2Results.mouth_frames }}</p>
                </div>
                <div class="space-y-2">
                  <p class="text-sm text-secondary">Detection Rate</p>
                  <p class="text-2xl font-bold text-primary">
                    {{ Math.round((step2Results.mouth_frames / step2Results.total_frames) * 100) }}%
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Final Results -->
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
    
    // Step processing state
    const currentTaskId = ref(null)
    const step1Status = ref('')
    const step1Progress = ref(0)
    const step1Message = ref('')
    const step1Results = ref(null)
    
    const step2Status = ref('')
    const step2Progress = ref(0)
    const step2Message = ref('')
    const step2Results = ref(null)
    
    const step3Status = ref('')
    const step3Progress = ref(0)
    const step3Message = ref('')
    const step3Results = ref(null)

    const handleFileSelected = (file) => {
      selectedFile.value = file
      videoPreview.value.show = true
      videoPreview.value.error = false
      
      // Reset all steps
      resetSteps()
      
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

    const resetSteps = () => {
      currentTaskId.value = null
      step1Status.value = ''
      step1Progress.value = 0
      step1Message.value = ''
      step1Results.value = null
      
      step2Status.value = ''
      step2Progress.value = 0
      step2Message.value = ''
      step2Results.value = null
      
      step3Status.value = ''
      step3Progress.value = 0
      step3Message.value = ''
      step3Results.value = null
      
      results.value = null
    }

    const startStep1 = async () => {
      if (!selectedFile.value) return
      
      uploading.value = true
      resetSteps()
      
      try {
        // Step 1: Upload and extract frames
        step1Status.value = 'processing'
        step1Progress.value = 0
        step1Message.value = 'Uploading video...'
        
        const formData = new FormData()
        formData.append('video', selectedFile.value)
        
        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData
        })
        
        const data = await response.json()
        
        if (response.ok) {
          currentTaskId.value = data.task_id
          step1Status.value = 'completed'
          step1Progress.value = 100
          step1Message.value = data.message
          step1Results.value = data
          
          // Auto-start step 2
          setTimeout(() => startStep2(), 1000)
        } else {
          throw new Error(data.error || 'Upload failed')
        }
      } catch (error) {
        console.error('Step 1 error:', error)
        step1Status.value = 'failed'
        step1Message.value = 'Error: ' + error.message
      }
    }

    const startStep2 = async () => {
      if (!currentTaskId.value) return
      
      try {
        step2Status.value = 'processing'
        step2Progress.value = 0
        step2Message.value = 'Detecting open mouths...'
        
        const response = await fetch(`/api/crop-mouth/${currentTaskId.value}`, {
          method: 'POST'
        })
        
        const data = await response.json()
        
        if (response.ok) {
          step2Status.value = 'completed'
          step2Progress.value = 100
          step2Message.value = data.message
          step2Results.value = data
          
          // Auto-start step 3
          setTimeout(() => startStep3(), 1000)
        } else {
          throw new Error(data.error || 'Mouth cropping failed')
        }
      } catch (error) {
        console.error('Step 2 error:', error)
        step2Status.value = 'failed'
        step2Message.value = 'Error: ' + error.message
      }
    }

    const startStep3 = async () => {
      if (!currentTaskId.value) return
      
      try {
        step3Status.value = 'processing'
        step3Progress.value = 0
        step3Message.value = 'Analyzing with CNN...'
        
        const response = await fetch(`/api/analyze/${currentTaskId.value}`, {
          method: 'POST'
        })
        
        const data = await response.json()
        
        if (response.ok) {
          step3Status.value = 'completed'
          step3Progress.value = 100
          step3Message.value = data.message
          step3Results.value = data
          results.value = data
          
          uploading.value = false
        } else {
          throw new Error(data.error || 'Analysis failed')
        }
      } catch (error) {
        console.error('Step 3 error:', error)
        step3Status.value = 'failed'
        step3Message.value = 'Error: ' + error.message
        uploading.value = false
      }
    }

    return {
      selectedFile,
      uploading,
      results,
      videoPreview,
      currentTaskId,
      step1Status,
      step1Progress,
      step1Message,
      step1Results,
      step2Status,
      step2Progress,
      step2Message,
      step2Results,
      step3Status,
      step3Progress,
      step3Message,
      step3Results,
      handleFileSelected,
      handleVideoError,
      startStep1
    }
  }
}
</script>
