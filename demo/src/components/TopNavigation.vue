<template>
  <nav class="bg-surface border-b border-outline-variant/20">
    <div class="flex justify-between items-center w-full px-8 py-4 max-w-[1920px] mx-auto">
      <div class="flex items-center gap-8">
        <span class="text-xl font-bold text-primary uppercase tracking-widest font-headline">DFT-MF</span>
        <div class="hidden md:flex gap-6">
          <a class="text-primary border-b-2 border-primary pb-1 font-headline font-bold tracking-tight" href="#">Analysis</a>
          <a class="text-secondary hover:text-primary transition-colors font-headline font-bold tracking-tight" href="#">Archive</a>
          <a class="text-secondary hover:text-primary transition-colors font-headline font-bold tracking-tight" href="#">Intelligence</a>
          <a class="text-secondary hover:text-primary transition-colors font-headline font-bold tracking-tight" href="#">Settings</a>
        </div>
      </div>
      <div class="flex items-center gap-4">
        <button class="p-2 text-secondary hover:bg-surface-container-high/50 transition-all duration-200 rounded-lg">
          <span class="material-symbols-outlined">notifications</span>
        </button>
        <button class="p-2 text-secondary hover:bg-surface-container-high/50 transition-all duration-200 rounded-lg">
          <span class="material-symbols-outlined">account_circle</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'TopNavigation'
}
</script>
