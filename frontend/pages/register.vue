<template>
  <div class="max-w-md mx-auto mt-20">
    <div class="bg-white rounded-xl shadow-md p-8">
      <h1 class="text-2xl font-bold mb-6 text-center">Create Account</h1>

      <!-- Error message -->
      <div v-if="errorMsg" class="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
        {{ errorMsg }}
      </div>

      <!-- Register form -->
      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nickname</label>
          <input
            v-model="form.nickname"
            type="text"
            placeholder="Your display name"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            placeholder="your@email.com"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            minlength="6"
            placeholder="At least 6 characters"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
          <input
            v-model="form.confirmPassword"
            type="password"
            required
            placeholder="Repeat your password"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ loading ? 'Creating account...' : 'Register' }}
        </button>
      </form>

      <!-- Login link -->
      <p class="mt-6 text-center text-sm text-gray-500">
        Already have an account?
        <NuxtLink to="/login" class="text-indigo-600 hover:text-indigo-700 font-medium">Login</NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { register } = useAuth()

const form = reactive({
  nickname: '',
  email: '',
  password: '',
  confirmPassword: '',
})
const loading = ref(false)
const errorMsg = ref('')

const handleRegister = async () => {
  errorMsg.value = ''

  if (form.password !== form.confirmPassword) {
    errorMsg.value = 'Passwords do not match'
    return
  }
  if (form.password.length < 6) {
    errorMsg.value = 'Password must be at least 6 characters'
    return
  }

  loading.value = true
  try {
    await register(form.email, form.password, form.nickname)
    navigateTo('/')
  } catch (err: any) {
    errorMsg.value = err.message || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
