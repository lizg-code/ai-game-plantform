<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold">Discover Interactive Games</h1>
        <p class="text-gray-500 mt-1">Play games created by AI and the community</p>
      </div>
      <NuxtLink
        v-if="isLoggedIn"
        to="/create"
        class="px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
      >
        + Create Game
      </NuxtLink>
    </div>

    <!-- Tag filter -->
    <div class="flex items-center gap-2 mb-6 flex-wrap">
      <button
        @click="filterTag = ''"
        class="px-3 py-1.5 text-sm rounded-full transition-colors"
        :class="filterTag === '' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
      >
        All
      </button>
      <button
        v-for="tag in allTags"
        :key="tag"
        @click="filterTag = tag"
        class="px-3 py-1.5 text-sm rounded-full transition-colors"
        :class="filterTag === tag ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
      >
        {{ tag }}
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="text-gray-400 flex items-center gap-3">
        <svg class="animate-spin h-6 w-6" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        Loading games...
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredGames.length === 0" class="text-center py-20">
      <div class="text-6xl mb-4">🎮</div>
      <h2 class="text-xl font-semibold text-gray-700 mb-2">No games yet</h2>
      <p class="text-gray-500 mb-6">Be the first to create an AI-generated game!</p>
      <NuxtLink
        v-if="isLoggedIn"
        to="/create"
        class="px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
      >
        Create Your First Game
      </NuxtLink>
      <NuxtLink
        v-else
        to="/register"
        class="px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
      >
        Sign Up to Create
      </NuxtLink>
    </div>

    <!-- Game grid -->
    <div v-else-if="filteredGames.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <GameCard
        v-for="game in filteredGames"
        :key="game.id"
        :title="game.title"
        :description="game.description"
        :cover-url="game.cover_url"
        :author="game.author_nickname || `Author #${game.author_id}`"
        :tags="game.tags"
        @click="goToPlay(game.id)"
      />
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
  author_nickname: string
  tags: string[]
  status: string
  remote_url: string
  game_type: string
  created_at: string
  updated_at: string
}

interface GameListResponse {
  total: number
  games: Game[]
}

const { isLoggedIn } = useAuth()
const api = useApi()

const games = ref<Game[]>([])
const loading = ref(true)
const filterTag = ref('')

const allTags = computed(() => {
  const tags = new Set<string>()
  games.value.forEach(g => g.tags.forEach(t => tags.add(t)))
  return Array.from(tags).sort()
})

const filteredGames = computed(() => {
  if (!filterTag.value) return games.value
  return games.value.filter(g => g.tags.includes(filterTag.value))
})

const fetchGames = async () => {
  loading.value = true
  try {
    const data = await api.get<GameListResponse>('/api/games')
    games.value = data.games
  } catch (err) {
    console.error('Failed to fetch games:', err)
  } finally {
    loading.value = false
  }
}

const goToPlay = (id: number) => {
  navigateTo(`/play/${id}`)
}

onMounted(() => {
  fetchGames()
})
</script>
