<template>
  <section class="bg-surface-container p-6 rounded-lg border border-outline-variant/10">
    <h3 class="font-headline text-sm font-semibold uppercase tracking-widest text-secondary mb-4">Thông tin tệp tin</h3>
    <div class="aspect-video bg-surface-container-lowest rounded overflow-hidden relative mb-4">
      <video 
        v-if="videoPreview.url && !videoPreview.error"
        :src="videoPreview.url" 
        class="w-full h-full object-cover"
        controls
        @error="handleVideoError"
      />
      <div v-else class="w-full h-full flex flex-col items-center justify-center">
        <span v-if="videoPreview.error" class="material-symbols-outlined text-5xl text-error/60">error_outline</span>
        <span v-else class="material-symbols-outlined text-5xl text-primary/80">movie</span>
        <p v-if="videoPreview.error" class="text-error text-sm mt-2">Video không hỗ trợ preview</p>
      </div>
    </div>
    <div class="grid grid-cols-2 gap-4">
      <div class="space-y-1">
        <label class="text-[10px] uppercase text-outline font-bold">Tên File</label>
        <p class="text-xs font-medium truncate">{{ selectedFile?.name || 'N/A' }}</p>
      </div>
      <div class="space-y-1">
        <label class="text-[10px] uppercase text-outline font-bold">Dung Lượng</label>
        <p class="text-xs font-medium">{{ formatFileSize(selectedFile?.size) }}</p>
      </div>
      <div class="space-y-1">
        <label class="text-[10px] uppercase text-outline font-bold">Định Dạng</label>
        <p class="text-xs font-medium">{{ selectedFile?.type || 'N/A' }}</p>
      </div>
      <div class="space-y-1">
        <label class="text-[10px] uppercase text-outline font-bold">Trạng Thái</label>
        <p class="text-xs font-medium" :class="videoPreview.error ? 'text-error' : 'text-primary'">
          {{ videoPreview.error ? 'Không hỗ trợ' : 'Sẵn sàng' }}
        </p>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'VideoPreview',
  props: {
    selectedFile: {
      type: File,
      default: null
    },
    videoPreview: {
      type: Object,
      required: true
    }
  },
  emits: ['video-error'],
  methods: {
    handleVideoError() {
      this.$emit('video-error');
    },
    formatFileSize(bytes) {
      if (!bytes) return '0 MB';
      return (bytes / 1024 / 1024).toFixed(2) + ' MB';
    }
  }
}
</script>
