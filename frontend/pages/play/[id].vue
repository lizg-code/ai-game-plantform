<template>
  <div class="max-w-4xl mx-auto">
    <!-- Back button -->
    <NuxtLink to="/" class="inline-flex items-center gap-1 text-gray-500 hover:text-gray-700 mb-4 transition-colors">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
      Back to Home
    </NuxtLink>

    <!-- Loading state -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-32">
      <svg class="animate-spin h-10 w-10 text-indigo-600 mb-4" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
      <p class="text-lg text-gray-600">Loading game files...</p>
      <p class="text-sm text-gray-400 mt-1">Fetching from remote storage</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="flex flex-col items-center justify-center py-32">
      <div class="text-6xl mb-4">😵</div>
      <h2 class="text-xl font-semibold text-gray-700 mb-2">Failed to load game</h2>
      <p class="text-gray-500 mb-6">{{ error }}</p>
      <div class="flex gap-3">
        <button
          @click="fetchGame"
          class="px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          🔄 Retry
        </button>
        <NuxtLink
          to="/"
          class="px-5 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Back to Home
        </NuxtLink>
      </div>
    </div>

    <!-- Game loaded -->
    <div v-else-if="game">
      <!-- Game header -->
      <div class="bg-white rounded-xl border shadow-sm p-4 mb-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold">{{ game.title }}</h1>
            <p class="text-gray-500 text-sm mt-1">{{ game.description }}</p>
          </div>
          <div class="flex items-center gap-2">
            <span
              v-for="tag in game.tags"
              :key="tag"
              class="text-xs bg-indigo-100 text-indigo-600 px-2 py-0.5 rounded"
            >
              {{ tag }}
            </span>
          </div>
        </div>
        <!-- Remote URL proof -->
        <div class="mt-3 flex items-center gap-2 text-xs text-gray-400">
          <span>🌐 Remote source:</span>
          <code class="bg-gray-100 px-2 py-0.5 rounded font-mono break-all">{{ game.remote_url }}</code>
        </div>
      </div>

      <!-- Game iframe -->
      <div class="relative bg-black rounded-xl overflow-hidden shadow-lg" style="height: 600px;">
        <iframe
          v-if="game.remote_url"
          :src="game.remote_url"
          class="w-full h-full border-0"
          sandbox="allow-scripts allow-same-origin"
          @load="onIframeLoad"
          @error="onIframeError"
        />

        <!-- Iframe loading overlay -->
        <div
          v-if="iframeLoading"
          class="absolute inset-0 flex items-center justify-center bg-gray-900/80"
        >
          <div class="text-center text-white">
            <svg class="animate-spin h-8 w-8 mx-auto mb-3" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <p>Initializing game environment...</p>
          </div>
        </div>
      </div>

      <!-- Game controls -->
      <div class="flex items-center justify-between mt-4">
        <div class="flex items-center gap-3">
          <button
            @click="restartGame"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm"
          >
            🔄 Restart
          </button>
          <button
            @click="openInNewTab"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm"
          >
            ↗ Open in New Tab
          </button>
        </div>
        <NuxtLink
          to="/"
          class="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors text-sm"
        >
          🏠 Back to Home
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Game {
  id: number
  title: string
  description: string
  cover_url: string
  author_id: number
  tags: string[]
  status: string
  remote_url: string
  game_type: string
  created_at: string
  updated_at: string
}

const route = useRoute()
const api = useApi()

const game = ref<Game | null>(null)
const loading = ref(true)
const error = ref('')
const iframeLoading = ref(true)

const fetchGame = async () => {
  loading.value = true
  error.value = ''
  iframeLoading.value = true

  try {
    const data = await api.get<Game>(`/api/games/${route.params.id}`)
    game.value = data

    if (!data.remote_url) {
      error.value = 'This game has no playable file yet.'
    }
  } catch (err: any) {
    error.value = err.message || 'Game not found'
  } finally {
    loading.value = false
  }
}

const onIframeLoad = () => {
  iframeLoading.value = false
}

const onIframeError = () => {
  iframeLoading.value = false
  error.value = 'Failed to load game file from remote storage.'
}

const restartGame = () => {
  iframeLoading.value = true
  // Force reload by toggling the src
  const url = game.value?.remote_url
  if (url) {
    game.value!.remote_url = ''
    nextTick(() => {
      game.value!.remote_url = url
    })
  }
}

const openInNewTab = () => {
  if (game.value?.remote_url) {
    window.open(game.value.remote_url, '_blank')
  }
}

onMounted(() => {
  fetchGame()
})
</script>
