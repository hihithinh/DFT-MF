<template>
  <div class="bg-background text-on-surface font-body min-h-screen">
    <!-- Main Content -->
    <main class="p-8 lg:p-12">
      <!-- Header Section -->
      <header class="mb-12 text-center">
        <h1 class="font-headline text-5xl font-bold tracking-tight text-on-surface mb-2">DFT-MF Deepfake Detection</h1>
        <p class="text-secondary font-medium tracking-wide">DeepFake Detection using Mouth Features | Phân tích đặc trưng vùng miệng</p>
      </header>

      <!-- Dynamic Layout Container -->
      <div class="relative">
        <!-- Single Column Layout (Before Analysis) -->
        <div 
          v-if="!uploading && !currentTaskId"
          class="max-w-2xl mx-auto space-y-8 transition-all duration-700 ease-in-out"
        >
          <UploadSection 
            :selectedFile="selectedFile"
            :uploading="uploading"
            @file-selected="handleFileSelected"
            @upload="startProcessing"
          />
          
          <VideoPreview 
            v-if="videoPreview.show"
            :selectedFile="selectedFile"
            :video-preview="videoPreview"
            @video-error="handleVideoError"
          />
        </div>

        <!-- Two Column Layout (Always Visible) -->
        <div class="flex flex-col lg:flex-row gap-8">
          <!-- Left Column - Analysis Control -->
          <div v-if="uploading || currentTaskId" class="flex-1 space-y-8 transition-all duration-3000 ease-out"
               :class="(uploading || currentTaskId) ? 'w-5/12' : 'w-full'">
            <UploadSection 
              :selectedFile="selectedFile"
              :uploading="uploading"
              @file-selected="handleFileSelected"
              @upload="startProcessing"
            />
            
            <VideoPreview 
              v-if="videoPreview.show"
              :selectedFile="selectedFile"
              :video-preview="videoPreview"
              @video-error="handleVideoError"
            />
          </div>

          <!-- Right Column - Results (Always Visible Container) -->
          <div ref="rightColumn" 
               class="space-y-8 transition-all duration-3000 ease-out"
               :class="[uploading || currentTaskId ? 'w-7/12 opacity-100 overflow-visible' : 'w-0 opacity-0 overflow-hidden']"
               @transitionend="handleTransitionEnd">
            <div class="transition-all duration-3000 ease-out"
                 :class="uploading || currentTaskId ? 'translate-x-0 opacity-100' : 'translate-x-8 opacity-0'">
              <!-- Loading State with Progress -->
              <LoadingState 
                v-if="uploading"
                :overall-progress="overallProgress"
                :current-step-name="currentStepName"
                :current-step-progress="currentStepProgress"
                :current-step-message="currentStepMessage"
              />
              
              <!-- Analysis Results - Always Show -->
              <ResultsSection 
                v-if="currentTaskId" 
                :results="results"
                @show-frames="openFramesModal"
                @show-mouths="openMouthsModal"
                @show-analyzed="openAnalyzedModal"
              />
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- Separate Modals -->
    <FramesModal
      :show="showFramesModal"
      :frames="sampleFrames"
      @close="closeFramesModal"
    />
    
    <MouthsModal
      :show="showMouthsModal"
      :mouths="sampleMouths"
      :canRetry="canRetryStep2"
      @close="closeMouthsModal"
      @retry-step-2="retryStep2"
    />
    
    <AnalyzedModal
      :show="showAnalyzedModal"
      :analyzed="sampleAnalyzed"
      :canRetry="canRetryStep3"
      @close="closeAnalyzedModal"
      @retry-step-3="retryStep3"
    />
  </div>
</template>

<style scoped>
/* Custom animations for layout transitions */
.slide-in-right {
  animation: slideInRight 0.7s ease-out forwards;
}

.fade-in {
  animation: fadeIn 0.7s ease-out forwards;
}

@keyframes slideInRight {
  from {
    transform: translateX(20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Smooth transitions for layout changes */
.transition-layout {
  transition: all 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* Center alignment for single column */
.single-column-center {
  max-width: 2xl;
  margin: 0 auto;
}
</style>

<script>
import { ref, computed, onUnmounted } from 'vue'
import UploadSection from './components/UploadSection.vue'
import VideoPreview from './components/VideoPreview.vue'
import LoadingState from './components/LoadingState.vue'
import ResultsSection from './components/ResultsSection.vue'
import FramesModal from './components/FramesModal.vue'
import MouthsModal from './components/MouthsModal.vue'
import AnalyzedModal from './components/AnalyzedModal.vue'
import ImageGrid from './components/ImageGrid.vue'

export default {
  name: 'App',
  components: {
    UploadSection,
    VideoPreview,
    LoadingState,
    ResultsSection,
    FramesModal,
    MouthsModal,
    AnalyzedModal,
    ImageGrid
  },
  setup() {
    const selectedFile = ref(null)
    const uploading = ref(false)
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
    
    // Modal state
    const showFramesModal = ref(false)
    const showMouthsModal = ref(false)
    const showAnalyzedModal = ref(false)
    
    // Sample data
    const sampleFrames = ref([])
    const sampleMouths = ref([])
    const sampleAnalyzed = ref([])
    
    // Status polling
    let statusInterval = null
    
    // Animation state
    const rightColumnVisible = ref(false)
    const rightColumn = ref(null)

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
      
      // Clear sample data
      sampleFrames.value = []
      sampleMouths.value = []
      sampleAnalyzed.value = []
      
      // Clear status polling
      if (statusInterval) {
        clearInterval(statusInterval)
        statusInterval = null
      }
    }

    // Modal handler functions
    const openFramesModal = () => {
      showFramesModal.value = true
    }

    const openMouthsModal = () => {
      showMouthsModal.value = true
    }

    const openAnalyzedModal = () => {
      showAnalyzedModal.value = true
    }

    const closeFramesModal = () => {
      showFramesModal.value = false
    }

    const closeMouthsModal = () => {
      showMouthsModal.value = false
    }

    const closeAnalyzedModal = () => {
      showAnalyzedModal.value = false
    }

    const startStatusPolling = () => {
      if (statusInterval) return
      
      statusInterval = setInterval(async () => {
        if (!currentTaskId.value) return
        
        try {
          const response = await fetch(`/api/${currentTaskId.value}/status`, {
            signal: AbortSignal.timeout(5000) // 5 seconds timeout for status
          })
          const status = await response.json()
          
          if (response.ok) {
            // Update step 1 progress
            if (status.upload && status.upload.extractedFrames > 0) {
              step1Progress.value = 100
              step1Status.value = 'completed'
              step1Message.value = `Extracted ${status.upload.totalFrames} frames`
              
              // Update step1Results with real-time data
              if (!step1Results.value) {
                step1Results.value = {
                  total_frames: status.upload.totalFrames
                }
              }
              
              // Update sample frames from status.json for real-time display
              if (status.upload.sample_frames && status.upload.sample_frames.length > 0) {
                sampleFrames.value = status.upload.sample_frames
              }
            }
            
            // Update step 2 progress
            if (status.cropMouth && status.cropMouth.extractedFrames > 0) {
              const progress = (status.cropMouth.processedFrames / status.cropMouth.extractedFrames) * 100
              step2Progress.value = Math.round(progress)
              step2Message.value = `Processed ${status.cropMouth.processedFrames}/${status.cropMouth.extractedFrames} frames (${status.cropMouth.croppedMouths} open mouths)`
              
              // Update step2Results with real-time data
              step2Results.value = {
                cropped_mouths: status.cropMouth.croppedMouths,
                processed_frames: status.cropMouth.processedFrames,
                extracted_frames: status.cropMouth.extractedFrames
              }
              
              // Update sample mouths from status.json for real-time display
              if (status.cropMouth.sample_mouths && status.cropMouth.sample_mouths.length > 0) {
                sampleMouths.value = status.cropMouth.sample_mouths
              }
              
              if (status.cropMouth.processedFrames > 0 && step2Status.value !== 'completed') {
                step2Status.value = 'processing'
              }
            }
            
            // Update step 3 progress
            if (status.analyze && status.analyze.croppedMouths > 0) {
              const progress = (status.analyze.analyzedMouths / status.analyze.croppedMouths) * 100
              step3Progress.value = Math.round(progress)
              step3Message.value = `Analyzed ${status.analyze.analyzedMouths}/${status.analyze.croppedMouths} mouths`
              
              // Update step3Results with real-time data
              if (status.analyze.fakeMouths !== undefined && status.analyze.realMouths !== undefined) {
                step3Results.value = {
                  fake_mouths: status.analyze.fakeMouths,
                  real_mouths: status.analyze.realMouths,
                  analyzed_mouths: status.analyze.analyzedMouths,
                  cropped_mouths: status.analyze.croppedMouths,
                  timeline_data: status.analyze.timeline_data || [],
                  confidence_distribution: status.analyze.confidence_distribution || {},
                  confidence: status.analyze.confidence || 0
                }
              }
              
              // Update sample analyzed from status.json for real-time display
              if (status.analyze.sample_analyzed && status.analyze.sample_analyzed.length > 0) {
                sampleAnalyzed.value = status.analyze.sample_analyzed
              }
              
              if (status.analyze.analyzedMouths > 0 && step3Status.value !== 'completed') {
                step3Status.value = 'processing'
              }
            }
          }
        } catch (error) {
          // Silently skip timeout errors - they're expected during long processing
          if (error.name !== 'TimeoutError') {
            console.error('Status polling error:', error)
          }
        }
      }, 1000) // Poll every second
    }

    const startProcessing = async () => {
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
          body: formData,
          signal: AbortSignal.timeout(300000) // 5 minutes timeout
        })
        
        const data = await response.json()
        
        if (response.ok) {
          currentTaskId.value = data.task_id
          step1Results.value = data
          
          // Save sample frames
          sampleFrames.value = data.sample_frames || []
          
          // Start status polling
          startStatusPolling()
          
          // Auto-start step 2
          setTimeout(() => startStep2(), 1000)
        } else {
          throw new Error(data.error || 'Upload failed')
        }
      } catch (error) {
        console.error('Step 1 error:', error)
        step1Status.value = 'failed'
        step1Message.value = 'Error: ' + error.message
        uploading.value = false
        // Stop status polling on error
        if (statusInterval) {
          clearInterval(statusInterval)
          statusInterval = null
        }
      }
    }

    const startStep2 = async () => {
      if (!currentTaskId.value) return
      
      try {
        step2Status.value = 'processing'
        step2Progress.value = 0
        step2Message.value = 'Detecting open mouths...'
        
        const response = await fetch(`/api/${currentTaskId.value}/crop-mouth`, {
          method: 'POST',
          signal: AbortSignal.timeout(600000) // 10 minutes timeout for processing
        })
        
        const data = await response.json()
        
        if (response.ok) {
          console.log('✅ Step 2 completed successfully')
          step2Status.value = 'completed'
          step2Progress.value = 100
          step2Message.value = `Found ${data.cropped_mouths} open mouths`
          step2Results.value = data
          
          // Save sample mouth crops
          sampleMouths.value = data.sample_mouths || []
          
          console.log('⏰ Starting Step 3 in 1 second...')
          // Auto-start step 3
          setTimeout(() => startStep3(), 1000)
        } else {
          console.log('❌ Step 2 failed:', data.error)
          throw new Error(data.error || 'Mouth cropping failed')
        }
      } catch (error) {
        console.error('Step 2 error:', error)
        step2Status.value = 'failed'
        step2Message.value = 'Error: ' + error.message
        uploading.value = false
        // Stop status polling on error
        if (statusInterval) {
          clearInterval(statusInterval)
          statusInterval = null
        }
      }
    }

    const startStep3 = async () => {
      console.log('🚀 Starting Step 3 - Analyze API call')
      if (!currentTaskId.value) {
        console.log('❌ No currentTaskId, skipping Step 3')
        return
      }
      
      console.log(`📞 Calling analyze API for task: ${currentTaskId.value}`)
      
      try {
        step3Status.value = 'processing'
        step3Progress.value = 0
        step3Message.value = 'Analyzing with CNN...'
        
        const response = await fetch(`/api/${currentTaskId.value}/analyze`, {
          method: 'POST',
          signal: AbortSignal.timeout(600000) // 10 minutes timeout for analysis
        })
        
        console.log('📡 Analyze API response status:', response.status)
        const data = await response.json()
        console.log('📊 Analyze API response data:', data)
        
        if (response.ok) {
          step3Status.value = 'completed'
          step3Progress.value = 100
          step3Message.value = `Analysis complete: ${data.fake_mouths} fake, ${data.real_mouths} real`
          step3Results.value = data
          
          // Save sample analyzed mouths with labels
          sampleAnalyzed.value = data.sample_analyzed || []
          
          uploading.value = false
          
          // Stop status polling
          if (statusInterval) {
            clearInterval(statusInterval)
            statusInterval = null
          }
        } else {
          throw new Error(data.error || 'Analysis failed')
        }
      } catch (error) {
        console.error('Step 3 error:', error)
        step3Status.value = 'failed'
        step3Message.value = 'Error: ' + error.message
        uploading.value = false
        // Stop status polling on error
        if (statusInterval) {
          clearInterval(statusInterval)
          statusInterval = null
        }
      }
    }

    // Computed properties for LoadingState
    const overallProgress = computed(() => {
      let total = 0
      if (step1Status.value === 'completed') total += 33
      if (step2Status.value === 'completed') total += 33
      if (step3Status.value === 'completed') total += 34
      
      // Add current step progress
      if (step1Status.value === 'processing') total += Math.round(step1Progress.value * 0.33)
      if (step2Status.value === 'processing') total += Math.round(step2Progress.value * 0.33)
      if (step3Status.value === 'processing') total += Math.round(step3Progress.value * 0.34)
      
      return total
    })

    const currentStepName = computed(() => {
      if (step3Status.value === 'processing' || step3Status.value === 'completed') return 'CNN Deepfake Analysis'
      if (step2Status.value === 'processing' || step2Status.value === 'completed') return 'Mouth Detection'
      if (step1Status.value === 'processing' || step1Status.value === 'completed') return 'Frame Extraction'
      return 'Initializing'
    })

    const currentStepProgress = computed(() => {
      if (step3Status.value === 'processing' || step3Status.value === 'completed') return step3Progress.value
      if (step2Status.value === 'processing' || step2Status.value === 'completed') return step2Progress.value
      if (step1Status.value === 'processing' || step1Status.value === 'completed') return step1Progress.value
      return 0
    })

    const currentStepMessage = computed(() => {
      if (step3Status.value === 'processing' || step3Status.value === 'completed') return step3Message.value
      if (step2Status.value === 'processing' || step2Status.value === 'completed') return step2Message.value
      if (step1Status.value === 'processing' || step1Status.value === 'completed') return step1Message.value
      return ''
    })

    // Computed properties for retry conditions
    const canRetryStep2 = computed(() => {
      return currentTaskId.value && 
             !uploading.value && 
             (step2Status.value === 'failed' || 
              (step2Status.value === '' && step1Status.value === 'completed'))
    })

    const canRetryStep3 = computed(() => {
      return currentTaskId.value && 
             !uploading.value && 
             (step3Status.value === 'failed' || 
              (step3Status.value === '' && step2Status.value === 'completed'))
    })

    // Computed property for results - updates real-time from step results
    const results = computed(() => {
      if (!currentTaskId.value) return {}
      
      const result = {
        video_id: currentTaskId.value ? currentTaskId.value.substring(0, 8) : 'UNKNOWN',
        total_frames: step1Results.value?.total_frames || 0,
        mouth_frames: step2Results.value?.cropped_mouths || 0,
        predictions: null
      }
      
      // Show real-time predictions during processing, but only show verdict when completed
      if (step3Results.value && (step3Results.value.fake_mouths > 0 || step3Results.value.real_mouths > 0)) {
        const totalMouths = step3Results.value.fake_mouths + step3Results.value.real_mouths
        const fakePercentage = totalMouths > 0 ? Math.round((step3Results.value.fake_mouths / totalMouths) * 100) : 0
        const isFake = fakePercentage >= 50
        
        result.predictions = {
          verdict: step3Status.value === 'completed' ? (isFake ? 'FAKE' : 'REAL') : null,
          fake_percentage: fakePercentage,
          fake_count: step3Results.value.fake_mouths,
          real_count: step3Results.value.real_mouths,
          confidence: step3Results.value.confidence || 0.0
        }
        
        // Add confidence distribution if available
        if (step3Results.value.confidence_distribution) {
          result.confidence_distribution = step3Results.value.confidence_distribution
        }
        
        // Add timeline data if available
        if (step3Results.value.timeline_data) {
          result.timeline_data = step3Results.value.timeline_data
        }
        
        if (step3Status.value === 'completed') {
          result.processing_complete = true
        }
      }
      
      return result
    })

    // Retry methods for manual retry
    const retryStep2 = async () => {
      console.log('🔄 Retrying Step 2 - Crop Mouth')
      uploading.value = true  // Set uploading to show loading
      step2Status.value = ''
      step2Progress.value = 0
      step2Message.value = ''
      step2Results.value = null
      sampleMouths.value = []
      await startStep2()
    }

    const retryStep3 = async () => {
      console.log('🔄 Retrying Step 3 - Analyze Deepfake')
      uploading.value = true  // Set uploading to show loading
      step3Status.value = ''
      step3Progress.value = 0
      step3Message.value = ''
      step3Results.value = null
      sampleAnalyzed.value = []
      await startStep3()
    }

    const handleTransitionEnd = (event) => {
      // Check if this is the right column transition
      if (event.target === rightColumn.value) {
        // Update visibility state based on current class
        const isShowing = uploading.value || currentTaskId.value
        rightColumnVisible.value = isShowing
        
        // Remove overflow-hidden when animation completes and column is visible
        if (isShowing && rightColumnVisible.value) {
          rightColumn.value.classList.remove('overflow-hidden')
          rightColumn.value.classList.add('overflow-visible')
        } else {
          rightColumn.value.classList.remove('overflow-visible')
          rightColumn.value.classList.add('overflow-hidden')
        }
      }
    }

    // Cleanup on component unmount
    onUnmounted(() => {
      if (statusInterval) {
        clearInterval(statusInterval)
        statusInterval = null
      }
    })

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
      overallProgress,
      currentStepName,
      currentStepProgress,
      currentStepMessage,
      showFramesModal,
      showMouthsModal,
      showAnalyzedModal,
      sampleFrames,
      sampleMouths,
      sampleAnalyzed,
      canRetryStep2,
      canRetryStep3,
      rightColumnVisible,
      rightColumn,
      openFramesModal,
      openMouthsModal,
      openAnalyzedModal,
      closeFramesModal,
      closeMouthsModal,
      closeAnalyzedModal,
      handleFileSelected,
      handleVideoError,
      startProcessing,
      retryStep2,
      retryStep3,
      handleTransitionEnd
    }
  }
}
</script>
