<template>
  <nav class="bg-white shadow-sm border-b">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      <!-- Logo & Nav Links -->
      <div class="flex items-center gap-6">
        <NuxtLink to="/" class="text-xl font-bold text-indigo-600">
          🎮 AI Game Platform
        </NuxtLink>
        <NuxtLink to="/" class="text-gray-600 hover:text-gray-900">Home</NuxtLink>
        <NuxtLink v-if="isLoggedIn" to="/create" class="text-gray-600 hover:text-gray-900">
          Create
        </NuxtLink>
      </div>

      <!-- Auth Buttons -->
      <div class="flex items-center gap-4">
        <template v-if="isLoggedIn">
          <span class="text-sm text-gray-600">{{ user?.nickname || user?.email }}</span>
          <button
            @click="logout"
            class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border rounded-lg hover:bg-gray-50"
          >
            Logout
          </button>
        </template>
        <template v-else>
          <NuxtLink
            to="/login"
            class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border rounded-lg hover:bg-gray-50"
          >
            Login
          </NuxtLink>
          <NuxtLink
            to="/register"
            class="px-4 py-2 text-sm text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg"
          >
            Register
          </NuxtLink>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
const { user, isLoggedIn, logout, init } = useAuth()

onMounted(() => {
  init()
})
</script>
