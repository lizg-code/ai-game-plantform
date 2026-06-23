<template>
  <div class="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer overflow-hidden">
    <div class="h-48 bg-gray-200 flex items-center justify-center text-gray-400">
      <span v-if="!coverUrl">🎮 No Cover</span>
      <img v-else :src="coverUrl" :alt="title" class="w-full h-full object-cover" />
    </div>
    <div class="p-4">
      <h3 class="font-semibold text-lg mb-1">{{ title }}</h3>
      <p class="text-gray-500 text-sm mb-2 line-clamp-2">{{ description }}</p>
      <div class="flex items-center justify-between text-xs text-gray-400">
        <span>{{ author }}</span>
        <div class="flex gap-1">
          <span v-for="tag in tags" :key="tag" class="bg-indigo-100 text-indigo-600 px-2 py-0.5 rounded">
            {{ tag }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description: string
  coverUrl?: string
  author: string
  tags: string[]
}>()
</script>
