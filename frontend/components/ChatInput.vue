<template>
  <div class="border rounded-xl bg-white shadow-sm">
    <!-- Uploaded files preview -->
    <div v-if="uploadedFiles.length > 0" class="px-4 pt-3 flex flex-wrap gap-2">
      <div
        v-for="(file, idx) in uploadedFiles"
        :key="idx"
        class="flex items-center gap-2 bg-gray-100 rounded-lg px-3 py-1.5 text-sm"
      >
        <span v-if="file.type.startsWith('image/')">🖼️</span>
        <span v-else-if="file.type.startsWith('video/')">🎬</span>
        <span v-else>📎</span>
        <span class="max-w-[120px] truncate">{{ file.name }}</span>
        <button @click="removeFile(idx)" class="text-gray-400 hover:text-red-500">×</button>
      </div>
    </div>

    <!-- Input area -->
    <div class="flex items-end gap-2 p-4">
      <!-- File upload button -->
      <label
        class="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-lg border cursor-pointer hover:bg-gray-50 transition-colors"
        :class="{ 'opacity-50 pointer-events-none': disabled }"
      >
        <input
          type="file"
          class="hidden"
          accept="image/*,video/*,.pdf,.txt"
          multiple
          @change="handleFileSelect"
        />
        <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/>
        </svg>
      </label>

      <!-- Text input -->
      <textarea
        v-model="text"
        :placeholder="placeholder"
        :disabled="disabled"
        rows="1"
        class="flex-1 resize-none border-0 outline-none focus:ring-0 text-sm py-2.5 max-h-32"
        @keydown.enter.exact.prevent="handleSend"
        @input="autoResize"
        ref="textareaRef"
      />

      <!-- Send button -->
      <button
        @click="handleSend"
        :disabled="disabled || (!text.trim() && uploadedFiles.length === 0)"
        class="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface UploadedFile {
  name: string
  url: string
  type: string
}

const props = defineProps<{
  placeholder?: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  send: [text: string, files: UploadedFile[]]
}>()

const text = ref('')
const uploadedFiles = ref<UploadedFile[]>([])
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const api = useApi()

const autoResize = () => {
  const el = textareaRef.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 128) + 'px'
  }
}

const handleFileSelect = async (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return

  for (const file of Array.from(input.files)) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      const result = await api.upload<{ file_url: string; file_name: string; file_type: string }>(
        '/api/upload',
        formData
      )
      uploadedFiles.value.push({
        name: result.file_name,
        url: result.file_url,
        type: result.file_type,
      })
    } catch (err) {
      console.error('Upload failed:', err)
      alert(`Upload failed: ${file.name}`)
    }
  }
  // Reset input
  input.value = ''
}

const removeFile = (idx: number) => {
  uploadedFiles.value.splice(idx, 1)
}

const handleSend = () => {
  if (props.disabled) return
  if (!text.value.trim() && uploadedFiles.value.length === 0) return

  emit('send', text.value, [...uploadedFiles.value])
  text.value = ''
  uploadedFiles.value = []
  nextTick(autoResize)
}
</script>
