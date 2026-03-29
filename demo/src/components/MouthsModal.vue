<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm" @click="closeModal">
    <div class="bg-surface-container rounded-xl shadow-2xl max-w-6xl max-h-[90vh] w-full mx-4 overflow-hidden" @click.stop>
      <!-- Header -->
      <div class="bg-surface-container-high p-6 border-b border-outline-variant/20">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-headline font-bold text-on-surface">Sample Mouth Crops</h3>
            <p class="text-sm text-secondary mt-1">Open mouth frames detected</p>
          </div>
          <button 
            @click="closeModal"
            class="p-2 rounded-lg hover:bg-surface-variant/50 transition-colors"
          >
            <span class="material-symbols-outlined text-on-surface">close</span>
          </button>
        </div>
      </div>
      
      <!-- Content -->
      <div class="p-6 overflow-y-auto max-h-[70vh]">
        <ImageGrid :images="mouths" />
      </div>
      
      <!-- Footer -->
      <div class="bg-surface-container-high p-4 border-t border-outline-variant/20">
        <div class="flex justify-between items-center">
          <p class="text-sm text-secondary">
            {{ mouths.length }} sample mouth crops
          </p>
          <div class="flex gap-3">
            <button 
              v-if="canRetry"
              @click="retryStep"
              class="px-6 py-2 bg-secondary text-on-secondary rounded-lg hover:bg-secondary/90 transition-colors flex items-center gap-2"
            >
              <span class="material-symbols-outlined text-sm">refresh</span>
              Retry Step 2
            </button>
            <button 
              @click="closeModal"
              class="px-6 py-2 bg-primary text-on-primary rounded-lg hover:bg-primary/90 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ImageGrid from './ImageGrid.vue'

export default {
  name: 'MouthsModal',
  components: {
    ImageGrid
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    mouths: {
      type: Array,
      default: () => []
    },
    canRetry: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'retry-step-2'],
  methods: {
    closeModal() {
      this.$emit('close')
    },
    retryStep() {
      this.$emit('retry-step-2')
    }
  },
  watch: {
    show(newVal) {
      // Prevent body scroll when modal is open
      if (newVal) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    }
  },
  beforeUnmount() {
    // Clean up body scroll
    document.body.style.overflow = ''
  }
}
</script>

<style scoped>
/* Custom scrollbar for modal content */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: var(--md-sys-color-surface-variant);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: var(--md-sys-color-outline);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: var(--md-sys-color-outline-variant);
}
</style>
