<template>
  <div class="border rounded-xl overflow-hidden bg-white shadow-sm">
    <!-- Preview header -->
    <div class="flex items-center justify-between px-4 py-2 bg-gray-50 border-b">
      <div class="flex items-center gap-2">
        <span class="text-sm font-medium text-gray-700">Game Preview</span>
        <span v-if="url" class="text-xs text-gray-400 truncate max-w-[200px]">{{ url }}</span>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="$emit('reload')"
          class="px-3 py-1 text-xs bg-white border rounded hover:bg-gray-50 transition-colors"
        >
          🔄 Reload
        </button>
        <button
          @click="$emit('openNew')"
          class="px-3 py-1 text-xs bg-white border rounded hover:bg-gray-50 transition-colors"
        >
          ↗ Open
        </button>
      </div>
    </div>

    <!-- Iframe container -->
    <div class="relative" style="height: 500px;">
      <iframe
        v-if="url"
        :src="url"
        class="w-full h-full border-0"
        sandbox="allow-scripts allow-same-origin"
        @load="$emit('loaded')"
        @error="$emit('error')"
      />
      <div v-else class="flex items-center justify-center h-full text-gray-400">
        <div class="text-center">
          <div class="text-4xl mb-2">🎮</div>
          <p>No preview available</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  url?: string
}>()

defineEmits<{
  reload: []
  openNew: []
  loaded: []
  error: []
}>()
</script>
