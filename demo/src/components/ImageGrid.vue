<template>
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
    <div 
      v-for="(item, index) in images" 
      :key="index"
      class="relative group cursor-pointer rounded-lg overflow-hidden bg-surface-variant/50 hover:ring-2 hover:ring-primary/50 transition-all"
    >
      <!-- Image -->
      <img 
        :src="getImageUrl(item)" 
        :alt="`Sample ${index + 1}`"
        class="w-full h-32 object-cover"
        @error="handleImageError($event, index)"
        @load="handleImageLoad($event, index)"
      />
      
      <!-- Badge for analyzed samples -->
      <div 
        v-if="item.label" 
        class="absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-bold"
        :class="badgeClass(item.label)"
      >
        {{ item.label }}
      </div>
      
      <!-- Loading state -->
      <div v-if="loadingImages.has(index)" class="absolute inset-0 bg-surface-variant/80 flex items-center justify-center">
        <span class="material-symbols-outlined animate-spin">refresh</span>
      </div>
      
      <!-- Error state -->
      <div v-if="errorImages.has(index)" class="absolute inset-0 bg-error-container/80 flex items-center justify-center">
        <span class="material-symbols-outlined text-error">broken_image</span>
      </div>
      
      <!-- Hover overlay -->
      <div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
        <span class="material-symbols-outlined text-white opacity-0 group-hover:opacity-100 transition-opacity">
          zoom_in
        </span>
      </div>
    </div>
    
    <!-- Empty state -->
    <div v-if="images.length === 0" class="col-span-full text-center py-12">
      <span class="material-symbols-outlined text-4xl text-outline mb-4">image_not_supported</span>
      <p class="text-secondary">No sample images available</p>
      <p class="text-sm text-outline mt-2">Sample images will appear after processing is complete</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImageGrid',
  props: {
    images: {
      type: Array,
      default: () => []
    },
    baseUrl: {
      type: String,
      default: 'http://127.0.0.1:8080'
    }
  },
  data() {
    return {
      loadingImages: new Set(),
      errorImages: new Set()
    }
  },
  methods: {
    getImageUrl(item) {
      // Handle both string URLs and object with url property
      const url = typeof item === 'string' ? item : item.url
      return url.startsWith('http') ? url : `${this.baseUrl}${url}`
    },
    
    badgeClass(label) {
      switch (label.toUpperCase()) {
        case 'FAKE':
          return 'bg-error text-on-error'
        case 'REAL':
          return 'bg-tertiary text-on-tertiary'
        default:
          return 'bg-surface-variant text-on-surface-variant'
      }
    },
    
    handleImageLoad(event, index) {
      this.loadingImages.delete(index)
    },
    
    handleImageError(event, index) {
      this.loadingImages.delete(index)
      this.errorImages.add(index)
    },
    
    preloadImages() {
      this.images.forEach((item, index) => {
        this.loadingImages.add(index)
        const img = new Image()
        img.onload = (e) => this.handleImageLoad(e, index)
        img.onerror = (e) => this.handleImageError(e, index)
        img.src = this.getImageUrl(item)
      })
    }
  },
  mounted() {
    this.preloadImages()
  },
  watch: {
    images() {
      // Clear previous states and preload new images
      this.loadingImages.clear()
      this.errorImages.clear()
      this.preloadImages()
    }
  }
}
</script>

<style scoped>
/* Add smooth transitions */
.group {
  transition: all 0.2s ease;
}

/* Badge animations */
.badge {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}

/* Loading spinner animation */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
