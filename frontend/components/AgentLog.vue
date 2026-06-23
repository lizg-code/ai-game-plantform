<template>
  <div class="space-y-3">
    <div
      v-for="log in logs"
      :key="log.id"
      class="border rounded-lg overflow-hidden"
      :class="{
        'border-gray-200': log.status === 'pending',
        'border-blue-300 bg-blue-50': log.status === 'running',
        'border-green-300 bg-green-50': log.status === 'success',
        'border-red-300 bg-red-50': log.status === 'failed',
      }"
    >
      <!-- Step header -->
      <button
        class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-black/5 transition-colors"
        @click="toggleExpand(log.id)"
      >
        <div class="flex items-center gap-3">
          <!-- Status icon -->
          <span class="flex-shrink-0">
            <span v-if="log.status === 'pending'" class="text-gray-400">⏳</span>
            <span v-else-if="log.status === 'running'" class="animate-spin inline-block">🔄</span>
            <span v-else-if="log.status === 'success'" class="text-green-600">✅</span>
            <span v-else-if="log.status === 'failed'" class="text-red-600">❌</span>
          </span>
          <!-- Step name -->
          <span class="font-medium text-sm">{{ stepLabel(log.step_name) }}</span>
        </div>
        <div class="flex items-center gap-2">
          <span
            class="text-xs px-2 py-0.5 rounded-full"
            :class="{
              'bg-gray-200 text-gray-600': log.status === 'pending',
              'bg-blue-200 text-blue-700': log.status === 'running',
              'bg-green-200 text-green-700': log.status === 'success',
              'bg-red-200 text-red-700': log.status === 'failed',
            }"
          >
            {{ log.status }}
          </span>
          <svg
            class="w-4 h-4 text-gray-400 transition-transform"
            :class="{ 'rotate-180': expandedIds.has(log.id) }"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
          </svg>
        </div>
      </button>

      <!-- Expanded content -->
      <div v-if="expandedIds.has(log.id)" class="px-4 pb-3 border-t border-gray-100">
        <!-- Error message -->
        <div v-if="log.error_message" class="mt-3 text-sm text-red-600 bg-red-50 rounded p-2">
          {{ log.error_message }}
        </div>

        <!-- Output data -->
        <div v-if="log.output_data && Object.keys(log.output_data).length > 0" class="mt-3">
          <p class="text-xs text-gray-500 mb-1">Output:</p>
          <pre class="text-xs bg-gray-100 rounded p-2 overflow-x-auto max-h-48">{{ formatJson(log.output_data) }}</pre>
        </div>

        <!-- Timing -->
        <div v-if="log.started_at" class="mt-2 text-xs text-gray-400">
          Started: {{ formatTime(log.started_at) }}
          <span v-if="log.finished_at"> → Finished: {{ formatTime(log.finished_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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

defineProps<{
  logs: AgentLogEntry[]
}>()

const expandedIds = ref<Set<number>>(new Set())

const toggleExpand = (id: number) => {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
}

const stepLabel = (name: string): string => {
  const labels: Record<string, string> = {
    creative_analysis: 'Step 1: Creative Analysis',
    game_design: 'Step 2: Game Design',
    code_generation: 'Step 3: Code Generation',
    upload: 'Step 4: Upload to Cloud',
  }
  return labels[name] || name
}

const formatJson = (obj: Record<string, any>): string => {
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

const formatTime = (t: string | null): string => {
  if (!t) return '-'
  return new Date(t).toLocaleTimeString()
}
</script>
