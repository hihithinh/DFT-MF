<template>
  <section class="space-y-6">
    <div class="flex items-end justify-between">
      <h2 class="font-headline text-2xl font-bold">Kết quả phân tích</h2>
      <span class="text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-tighter"
            :class="results?.predictions?.verdict === 'FAKE' ? 'bg-error/10 text-error' : 'bg-tertiary/10 text-tertiary'">
      </span>
    </div>

    <!-- Verdict Card -->
    <div class="glass-panel p-8 rounded-lg relative overflow-hidden">
      <!-- Background Accent -->
      <div class="absolute -right-10 -top-10 w-40 h-40 rounded-full"
           :class="results?.predictions?.verdict === 'FAKE' ? 'bg-error/10' : results?.predictions?.verdict === 'REAL' ? 'bg-tertiary/10' : 'bg-surface-variant/20'"></div>
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
        <div>
          <div class="text-[10px] uppercase font-bold text-outline mb-1">Kết luận cuối cùng</div>
          <div class="text-5xl font-headline font-bold tracking-tighter uppercase"
               :class="results?.predictions?.verdict === 'FAKE' ? 'text-error' : results?.predictions?.verdict === 'REAL' ? 'text-tertiary' : 'text-outline'">
            <span v-if="results?.predictions?.verdict">{{ results?.predictions?.verdict }}</span>
            <span v-else class="cyber-text">{{ analyzingText }}</span>
          </div>
        </div>
        <div class="text-right">
          <div class="text-[10px] uppercase font-bold text-outline mb-1 flex items-center gap-2 justify-end">
            Độ tin cậy
            <div class="relative" @mouseenter="showTooltip = true" @mouseleave="hideTooltipDelayed" ref="tooltipTrigger">
              <div class="w-4 h-4 flex items-center justify-center cursor-help hover:bg-surface-variant/20 rounded-full transition-colors">
                <span class="material-symbols-outlined text-sm text-secondary">help</span>
              </div>
            </div>
            
            <!-- Teleport tooltip to body -->
            <Teleport to="body" v-if="showTooltip">
              <div class="fixed px-3 py-2 bg-surface-container border border-outline-variant rounded-lg shadow-lg z-50 w-64 opacity-100 visible transition-all duration-200 pointer-events-auto"
                   :style="tooltipPosition"
                   @mouseenter="clearTooltipTimeout"
                   @mouseleave="hideTooltipDelayed">
                <div class="text-xs text-on-surface">
                  <p class="font-semibold mb-2">Phương pháp tính Độ tin cậy</p>
                  <p class="text-secondary leading-relaxed mb-2 text-[11px]">
                    Độ tin cậy được tính dựa trên khoảng cách từ giá trị dự đoán đến ngưỡng quyết định (0.5) của mô hình CNN:
                  </p>
                  <div class="bg-surface-variant/30 p-2 rounded mb-2 font-mono text-[10px] text-on-surface">
                    <p>confidence = |pred_value - 0.5| × 2</p>
                    <p class="text-secondary mt-1">pred_value ∈ [0, 1]</p>
                  </div>
                  <div class="text-secondary leading-relaxed text-[11px] space-y-1">
                    <p><span class="font-semibold">• 0.0:</span> Dự đoán ở ngưỡng (không chắc chắn)</p>
                    <p><span class="font-semibold">• 1.0:</span> Dự đoán cực đoan (rất chắc chắn)</p>
                    <p class="mt-2 pt-2 border-t border-outline-variant/20">Giá trị cuối cùng là <b>trung bình</b> của <b>tất cả frame</b> được phân tích.</p>
                  </div>
                </div>
                <!-- Tooltip arrow -->
                <div class="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                  <div class="w-2 h-2 bg-surface-container border-r border-b border-outline-variant/20 transform rotate-45"></div>
                </div>
              </div>
            </Teleport>
          </div>
          <div class="text-4xl font-headline font-bold text-on-surface">
            {{ results?.predictions?.confidence?.toFixed(1) || '--' }}<span class="text-xl text-outline ml-1">%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Detailed Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="bg-surface-container p-6 rounded border border-outline-variant/10 cursor-pointer hover:ring-2 hover:ring-primary/50 transition-all" @click="$emit('show-frames')">
        <div class="flex justify-between items-start mb-4">
          <span class="text-[10px] font-bold text-outline uppercase tracking-wider">Tổng số frames</span>
          <span class="material-symbols-outlined text-secondary text-sm">filter_frames</span>
        </div>
        <p class="font-headline text-lg font-bold">{{ results?.total_frames || 'Đang phân tích' }} <span class="text-xs font-normal text-outline">frames</span></p>
      </div>
      <div class="bg-surface-container p-6 rounded border border-outline-variant/10 cursor-pointer hover:ring-2 hover:ring-primary/50 transition-all" @click="$emit('show-mouths')">
        <div class="flex justify-between items-start mb-4">
          <span class="text-[10px] font-bold text-outline uppercase tracking-wider">Số frame hở miệng</span>
          <span class="material-symbols-outlined text-secondary text-sm">face</span>
        </div>
        <p class="font-headline text-lg font-bold">{{ results?.mouth_frames || 'Đang phân tích' }} <span class="text-xs font-normal text-outline">detected</span></p>
      </div>
      <div class="bg-surface-container p-6 rounded border border-outline-variant/10 cursor-pointer hover:ring-2 hover:ring-primary/50 transition-all" @click="$emit('show-analyzed')">
        <div class="flex justify-between items-start mb-4">
          <span class="text-[10px] font-bold text-outline uppercase tracking-wider">Tỷ lệ giả mạo</span>
          <span class="material-symbols-outlined text-secondary text-sm">warning</span>
        </div>
        <p class="font-headline text-lg font-bold" :class="results?.predictions?.verdict === 'FAKE' ? 'text-error' : results?.predictions?.verdict === 'REAL' ? 'text-tertiary' : 'text-outline'">
          {{ results?.predictions?.fake_percentage === 0 ? 0 : (results?.predictions?.fake_percentage || '--') }}% <span class="text-xs font-normal text-outline">({{ results?.predictions?.fake_count === 0 ? 0 : (results?.predictions?.fake_count || '--') }} frames)</span>
        </p>
      </div>
      <div class="bg-surface-container p-6 rounded border border-outline-variant/10">
        <div class="flex justify-between items-start mb-4">
          <span class="text-[10px] font-bold text-outline uppercase tracking-wider">Phân bố Confidence</span>
          <span class="material-symbols-outlined text-secondary text-sm">analytics</span>
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-secondary">Cao (≥0.7)</span>
            <div class="flex items-center gap-2">
              <div class="w-24 h-2 bg-surface-variant rounded-full overflow-hidden">
                <div class="h-full bg-tertiary" :style="{ width: (results?.confidence_distribution?.high || 0) + '%' }"></div>
              </div>
              <span class="font-semibold text-on-surface w-12 text-right">{{ results?.confidence_distribution?.high || '--' }}%</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-secondary">Trung bình (0.4-0.7)</span>
            <div class="flex items-center gap-2">
              <div class="w-24 h-2 bg-surface-variant rounded-full overflow-hidden">
                <div class="h-full bg-primary" :style="{ width: (results?.confidence_distribution?.medium || 0) + '%' }"></div>
              </div>
              <span class="font-semibold text-on-surface w-12 text-right">{{ results?.confidence_distribution?.medium || '--' }}%</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-secondary">Thấp (<0.4)</span>
            <div class="flex items-center gap-2">
              <div class="w-24 h-2 bg-surface-variant rounded-full overflow-hidden">
                <div class="h-full bg-error" :style="{ width: (results?.confidence_distribution?.low || 0) + '%' }"></div>
              </div>
              <span class="font-semibold text-on-surface w-12 text-right">{{ results?.confidence_distribution?.low || '--' }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Analysis Chart -->
    <TimelineChart 
      :timeline-data="timelineChartData"
      :verdict="results?.predictions?.verdict"
    />
  </section>
</template>

<script>
import TimelineChart from './TimelineChart.vue'

export default {
  name: 'ResultsSection',
  components: {
    TimelineChart
  },
  props: {
    results: {
      type: Object,
      required: true
    }
  },
  emits: ['show-frames', 'show-mouths', 'show-analyzed'],
  data() {
    return {
      analyzingText: 'ĐANG PHÂN TÍCH',
      textOptions: [
        'ĐANG PHÂN TÍCH',
        'ĐANG PHÂN TÍCH.',
        'ĐANG PHÂN TÍCH..',
        'ĐANG PHÂN TÍCH...',
      ],
      currentIndex: 0,
      showTooltip: false,
      tooltipPosition: {},
      tooltipTimeout: null
    }
  },
  computed: {
    timelineChartData() {
      return this.results?.timeline_data || []
    }
  },
  mounted() {
    this.startTextAnimation()
  },
  watch: {
    showTooltip(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          this.updateTooltipPosition()
        })
      }
    }
  },
  beforeUnmount() {
    if (this.textInterval) {
      clearInterval(this.textInterval)
    }
  },
  methods: {
    startTextAnimation() {
      this.textInterval = setInterval(() => {
        this.currentIndex = (this.currentIndex + 1) % this.textOptions.length
        this.analyzingText = this.textOptions[this.currentIndex]
      }, 800)
    },
    
    updateTooltipPosition() {
      if (!this.$refs.tooltipTrigger) return
      
      const rect = this.$refs.tooltipTrigger.getBoundingClientRect()
      const tooltipWidth = 256 // w-64 = 16rem = 256px
      const tooltipHeight = 200 // approximate height
      const offset = 8
      const padding = 16 // padding from viewport edges
      
      // Position tooltip above the trigger element, centered horizontally
      let left = rect.left + rect.width / 2 - tooltipWidth / 2
      let top = rect.top - tooltipHeight - offset
      
      // Keep tooltip within viewport bounds
      if (left < padding) {
        left = padding
      } else if (left + tooltipWidth > window.innerWidth - padding) {
        left = window.innerWidth - tooltipWidth - padding
      }
      
      if (top < padding) {
        // If tooltip doesn't fit above, position it below
        top = rect.bottom + offset
      }
      
      this.tooltipPosition = {
        left: `${left}px`,
        top: `${top}px`
      }
    },
    
    hideTooltipDelayed() {
      // Clear any existing timeout
      if (this.tooltipTimeout) {
        clearTimeout(this.tooltipTimeout)
      }
      
      // Set a small delay to allow moving from trigger to tooltip
      this.tooltipTimeout = setTimeout(() => {
        this.showTooltip = false
      }, 100)
    },
    
    clearTooltipTimeout() {
      // Clear timeout if mouse enters tooltip
      if (this.tooltipTimeout) {
        clearTimeout(this.tooltipTimeout)
        this.tooltipTimeout = null
      }
    }
  }
}
</script>

<style scoped>
/* Popper.js Tooltip Styles */
.confidence-tooltip {
  position: absolute;
  top: 0;
  left: 0;
}

.tooltip-arrow {
  position: absolute;
  width: 8px;
  height: 8px;
  background: inherit;
  border-right: inherit;
  border-bottom: inherit;
}

.tooltip-arrow::before {
  content: '';
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--md-sys-color-surface-container-high);
  border-right: 1px solid var(--md-sys-color-outline-variant);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  transform: rotate(45deg);
}

/* Cyber Security Text Animation */
.cyber-text {
  position: relative;
  display: inline-block;
  color: #64ffda;
  text-shadow: 
    0 0 10px #64ffda,
    0 0 20px #64ffda,
    0 0 30px #64ffda;
  animation: cyber-glow 2s ease-in-out infinite alternate, glitch 3s infinite;
}

@keyframes cyber-glow {
  0% {
    text-shadow: 
      0 0 10px #64ffda,
      0 0 20px #64ffda,
      0 0 30px #64ffda;
    opacity: 0.8;
  }
  50% {
    text-shadow: 
      0 0 5px #64ffda,
      0 0 10px #64ffda,
      0 0 15px #64ffda;
    opacity: 1;
  }
  100% {
    text-shadow: 
      0 0 20px #64ffda,
      0 0 30px #64ffda,
      0 0 40px #64ffda;
    opacity: 0.9;
  }
}

@keyframes glitch {
  0%, 100% {
    text-transform: uppercase;
    filter: none;
  }
  20% {
    text-transform: uppercase;
    filter: hue-rotate(90deg);
  }
  40% {
    text-transform: uppercase;
    filter: hue-rotate(180deg);
  }
  60% {
    text-transform: uppercase;
    filter: hue-rotate(270deg);
  }
  80% {
    text-transform: uppercase;
    filter: hue-rotate(360deg);
  }
}

/* Scanning line effect */
.cyber-text::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(100, 255, 218, 0.4), transparent);
  animation: scan 3s infinite;
}

@keyframes scan {
  0% {
    left: -100%;
  }
  50%, 100% {
    left: 100%;
  }
}

/* Matrix rain effect (subtle) */
.cyber-text::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(100, 255, 218, 0.03) 2px,
    rgba(100, 255, 218, 0.03) 4px
  );
  animation: matrix-rain 20s linear infinite;
  pointer-events: none;
}

@keyframes matrix-rain {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 0 100px;
  }
}
</style>
