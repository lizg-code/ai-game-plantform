export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  modules: ['@nuxtjs/tailwindcss'],

  runtimeConfig: {
    public: {
      apiBase: process.env.BACKEND_URL || 'http://localhost:8000',
    },
  },

  app: {
    head: {
      title: 'AI Game Platform',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AI Native Interactive Game Platform' },
      ],
    },
  },
})
