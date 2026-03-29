<template>
  <section class="bg-surface-container-high p-8 rounded-lg border border-outline-variant/10 shadow-lg">
    <div class="flex items-center gap-3 mb-6">
      <span class="material-symbols-outlined text-primary">upload_file</span>
      <h2 class="font-headline text-xl font-medium">Tải video lên để phân tích</h2>
    </div>
    <div 
      id="uploadArea"
      class="border-2 border-dashed border-outline-variant/30 rounded-lg p-10 flex flex-col items-center justify-center text-center hover:border-primary/50 transition-colors group cursor-pointer bg-surface-container-lowest"
      @click="triggerFileInput"
      @dragover.prevent
      @drop.prevent="handleDrop"
    >
      <span class="material-symbols-outlined text-4xl text-outline mb-4 group-hover:text-primary">movie</span>
      <p class="text-sm font-medium mb-1">Kéo và thả file hoặc click để chọn</p>
      <p class="text-xs text-outline">Định dạng hỗ trợ: MP4, AVI, MOV (Tối đa 100MB)</p>
      <input 
        ref="fileInput"
        class="hidden" 
        type="file" 
        accept="video/*"
        @change="handleFileChange"
      />
    </div>
    <button 
      class="w-full mt-6 bg-gradient-to-br from-primary to-on-primary-container text-on-primary font-bold py-4 rounded-md flex items-center justify-center gap-2 hover:shadow-[0_0_20px_rgba(0,218,243,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      @click="$emit('upload')"
      :disabled="!selectedFile || uploading"
    >
      <span class="material-symbols-outlined">analytics</span>
      <span>{{ uploading ? 'Đang xử lý...' : 'Bắt đầu phân tích' }}</span>
    </button>
  </section>
</template>

<script>
export default {
  name: 'UploadSection',
  props: {
    selectedFile: {
      type: File,
      default: null
    },
    uploading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['upload', 'file-selected'],
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        this.$emit('file-selected', file);
      }
    },
    handleDrop(event) {
      const files = event.dataTransfer.files;
      if (files.length > 0) {
        const file = files[0];
        this.$refs.fileInput.files = files;
        this.$emit('file-selected', file);
      }
    }
  }
}
</script>
