<template>
  <div class="bg-surface-container-high/80 backdrop-blur-xl border border-primary/20 p-12 rounded-lg flex flex-col items-center justify-center text-center">
    <div class="relative w-20 h-20 mb-6">
      <div class="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
      <div class="absolute inset-0 border-4 border-t-primary rounded-full animate-spin"></div>
      <div class="absolute inset-0 flex items-center justify-center">
        <span class="material-symbols-outlined text-primary text-3xl">fingerprint</span>
      </div>
    </div>
    <h2 class="font-headline text-2xl font-bold text-primary mb-2">Đang xử lý video...</h2>
    <p class="text-secondary max-w-xs mx-auto">Hệ thống đang trích xuất đặc trưng vùng miệng và so sánh với cơ sở dữ liệu pháp y.</p>
    
    <!-- Overall Progress -->
    <div class="w-full max-w-md mt-8">
      <div class="flex justify-between mb-2">
        <span class="text-[10px] font-bold text-outline uppercase">Tổng tiến trình</span>
        <span class="text-[10px] font-bold text-primary uppercase">{{ overallProgress }}%</span>
      </div>
      <div class="w-full bg-surface-container-lowest h-1.5 rounded-full overflow-hidden">
        <div class="bg-primary h-full transition-all duration-300 shadow-[0_0_10px_#00daf3]" 
             :style="{ width: overallProgress + '%' }"></div>
      </div>
    </div>
    
    <!-- Current Step Progress -->
    <div class="w-full max-w-md mt-6">
      <div class="flex justify-between mb-2">
        <span class="text-[10px] font-bold text-outline uppercase">{{ currentStepName }}</span>
        <span class="text-[10px] font-bold text-primary uppercase">{{ currentStepProgress }}%</span>
      </div>
      <div class="w-full bg-surface-container-lowest h-1.5 rounded-full overflow-hidden">
        <div class="bg-tertiary h-full transition-all duration-300 shadow-[0_0_10px_#4edea3]" 
             :style="{ width: currentStepProgress + '%' }"></div>
      </div>
      <p v-if="currentStepMessage" class="text-xs text-secondary mt-2">{{ currentStepMessage }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoadingState',
  props: {
    overallProgress: {
      type: Number,
      default: 0
    },
    currentStepName: {
      type: String,
      default: 'Frame Extraction'
    },
    currentStepProgress: {
      type: Number,
      default: 0
    },
    currentStepMessage: {
      type: String,
      default: ''
    }
  }
}
</script>
