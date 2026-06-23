<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Create a Game</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Left: Chat + Input -->
      <div class="space-y-4">
        <!-- Chat messages -->
        <div class="bg-white rounded-xl border shadow-sm p-4 min-h-[300px] max-h-[500px] overflow-y-auto">
          <div v-if="messages.length === 0" class="text-center text-gray-400 py-12">
            <div class="text-5xl mb-3">✨</div>
            <p class="text-lg font-medium mb-1">Describe your game idea</p>
            <p class="text-sm">Tell me what kind of game you want, and AI will create it for you</p>
            <div class="mt-6 flex flex-wrap justify-center gap-2">
              <button
                v-for="example in examples"
                :key="example"
                @click="useExample(example)"
                class="px-3 py-1.5 text-xs bg-indigo-50 text-indigo-600 rounded-full hover:bg-indigo-100 transition-colors"
              >
                {{ example }}
              </button>
            </div>
          </div>

          <div v-for="(msg, idx) in messages" :key="idx" class="mb-4">
            <!-- User message -->
            <div v-if="msg.role === 'user'" class="flex justify-end">
              <div class="bg-indigo-600 text-white rounded-xl rounded-tr-sm px-4 py-2 max-w-[80%]">
                <p class="text-sm whitespace-pre-wrap">{{ msg.text }}</p>
                <div v-if="msg.files?.length" class="mt-1 flex flex-wrap gap-1">
                  <span v-for="f in msg.files" :key="f.url" class="text-xs opacity-80">📎 {{ f.name }}</span>
                </div>
              </div>
            </div>

            <!-- System message -->
            <div v-else class="flex justify-start">
              <div class="bg-gray-100 rounded-xl rounded-tl-sm px-4 py-2 max-w-[80%]">
                <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ msg.text }}</p>
              </div>
            </div>
          </div>

          <!-- Generating indicator -->
          <div v-if="generating" class="flex justify-start mb-4">
            <div class="bg-blue-50 border border-blue-200 rounded-xl rounded-tl-sm px-4 py-3">
              <div class="flex items-center gap-2 text-sm text-blue-700">
                <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Generating your game...
              </div>
            </div>
          </div>
        </div>

        <!-- Chat input -->
        <ChatInput
          placeholder="Describe your game idea... e.g., 'A puzzle game where you match colored gems'"
          :disabled="generating"
          @send="handleSend"
        />
      </div>

      <!-- Right: Agent Log + Preview -->
      <div class="space-y-4">
        <!-- Agent Log panel -->
        <div v-if="currentGameId" class="bg-white rounded-xl border shadow-sm p-4">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold">Agent Workflow</h2>
            <span
              class="text-xs px-2 py-1 rounded-full"
              :class="{
                'bg-yellow-100 text-yellow-700': gameStatus === 'generating',
                'bg-green-100 text-green-700': gameStatus === 'draft',
                'bg-red-100 text-red-700': gameStatus === 'failed',
              }"
            >
              {{ gameStatus }}
            </span>
          </div>
          <AgentLog :logs="agentLogs" />
        </div>

        <!-- Preview -->
        <div v-if="previewUrl">
          <GamePreview
            :url="previewUrl"
            @reload="previewKey++"
            @open-new="openInNewTab"
          />
          <!-- Action buttons -->
          <div class="flex gap-3 mt-4">
            <button
              v-if="gameStatus === 'draft'"
              @click="publishGame"
              :disabled="publishing"
              class="flex-1 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors font-medium"
            >
              {{ publishing ? 'Publishing...' : '🚀 Publish to Home' }}
            </button>
            <button
              @click="resetCreate"
              class="px-5 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Create Another
            </button>
          </div>
        </div>

        <!-- Empty state for right panel -->
        <div v-if="!currentGameId" class="bg-white rounded-xl border shadow-sm p-8 text-center text-gray-400">
          <div class="text-5xl mb-3">🤖</div>
          <p class="text-lg font-medium mb-1">Agent Workflow</p>
          <p class="text-sm">Send a prompt to see the AI agent in action</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

interface ChatMessage {
  role: 'user' | 'system'
  text: string
  files?: { name: string; url: string; type: string }[]
}

interface AgentLogEntry {
  id: number
  game_id: number
  step_name: string
  step_order: number
  status: 'pending' | 'running' | 'success' | 'failed'
  input_data: Record<string, any>
  output_data: Record<string, any>
  error_message: string
  started_at: string | null
  finished_at: string | null
}

const api = useApi()

const messages = ref<ChatMessage[]>([])
const generating = ref(false)
const currentGameId = ref<number | null>(null)
const gameStatus = ref('')
const agentLogs = ref<AgentLogEntry[]>([])
const previewUrl = ref('')
const previewKey = ref(0)
const publishing = ref(false)
let pollTimer: ReturnType<typeof setInterval> | null = null

const examples = [
  'A memory card matching game with emojis',
  'A text adventure about exploring a haunted house',
  'A snake game with a neon theme',
]

const useExample = (text: string) => {
  messages.value.push({ role: 'user', text })
  startGeneration(text, [])
}

const handleSend = (text: string, files: { name: string; url: string; type: string }[]) => {
  messages.value.push({ role: 'user', text, files })
  startGeneration(text, files)
}

const startGeneration = async (prompt: string, files: { name: string; url: string; type: string }[]) => {
  generating.value = true
  gameStatus.value = 'generating'
  agentLogs.value = []
  previewUrl.value = ''

  try {
    // Call generate API
    const result = await api.post<{ game_id: number; status: string; message: string }>(
      '/api/games/generate',
      {
        user_prompt: prompt,
        materials: files.map(f => f.url),
      }
    )

    currentGameId.value = result.game_id
    gameStatus.value = result.status

    messages.value.push({
      role: 'system',
      text: `🎮 Game generation started! Game ID: ${result.game_id}\nI'll analyze your idea, design the game, write the code, and upload it. Watch the progress on the right →`,
    })

    // Start polling
    startPolling(result.game_id)
  } catch (err: any) {
    messages.value.push({
      role: 'system',
      text: `❌ Failed to start generation: ${err.message}`,
    })
    generating.value = false
  }
}

const startPolling = (gameId: number) => {
  if (pollTimer) clearInterval(pollTimer)

  pollTimer = setInterval(async () => {
    try {
      const status = await api.get<{
        game_id: number
        status: string
        remote_url: string
        logs: AgentLogEntry[]
      }>(`/api/games/${gameId}/status`)

      agentLogs.value = status.logs
      gameStatus.value = status.status

      // Check if done
      if (status.status === 'draft' || status.status === 'published') {
        generating.value = false
        previewUrl.value = status.remote_url
        if (pollTimer) clearInterval(pollTimer)

        messages.value.push({
          role: 'system',
          text: '✅ Game generated successfully! You can preview it on the right and publish when ready.',
        })
      } else if (status.status === 'failed') {
        generating.value = false
        if (pollTimer) clearInterval(pollTimer)

        const failedStep = status.logs.find(l => l.status === 'failed')
        messages.value.push({
          role: 'system',
          text: `❌ Generation failed${failedStep ? ` at ${failedStep.step_name}` : ''}: ${failedStep?.error_message || 'Unknown error'}`,
        })
      }
    } catch (err) {
      console.error('Polling error:', err)
    }
  }, 2000) // Poll every 2 seconds
}

const publishGame = async () => {
  if (!currentGameId.value) return
  publishing.value = true
  try {
    await api.post(`/api/games/${currentGameId.value}/publish`)
    gameStatus.value = 'published'
    messages.value.push({
      role: 'system',
      text: '🎉 Game published! It\'s now visible on the Home page. Players can find and play it!',
    })
  } catch (err: any) {
    messages.value.push({
      role: 'system',
      text: `❌ Publish failed: ${err.message}`,
    })
  } finally {
    publishing.value = false
  }
}

const openInNewTab = () => {
  if (previewUrl.value) {
    window.open(previewUrl.value, '_blank')
  }
}

const resetCreate = () => {
  messages.value = []
  generating.value = false
  currentGameId.value = null
  gameStatus.value = ''
  agentLogs.value = []
  previewUrl.value = ''
}

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>
